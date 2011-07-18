import re
from errors import ServletMissingArgument, ServletUnknownCommand, ServletInvalidArgumentValue

class flagCast(object):
    def __call__(self, arg):
        return True
    
    def __str__(self):
        return "flag"
        

class invFlagCast(object):
    def __call__(self, arg):
        return False
    
    def __str__(self):
        return "flag"
        
class flagsCast(object):
    def __call__(self, arg):
        return frozenset(arg.split(','))
    
    def __str__(self):
        return "comma-delimited set of export flags"

class commaList(object):
    def __init__(self, description, cast = None):
        self.description = description
        self.cast = cast
    
    def __call__(self, arg):
        if self.cast is not None:
            return [self.cast(x) for x in arg.split(',')]
        else:
            return [x for x in arg.split(',')]
    
    def __str__(self):
        return self.description

class intRange(object):
    pattern = re.compile("^([0-9]+)(-([0-9]+))?$")
    
    def __call__(self, arg):
        groups = re.match(intRange.pattern, arg).groups()
        if groups[2] is not None:
            return (int(groups[0]), int(groups[2]))
        else:
            return int(groups[0])
    
    def __str__(self):
        return "int or int range (e.g. '10-20' or '20')"

class MethodDescriptionError(Exception):
    pass

class MethodArgumentMapping(object):
    def __init__(self, mapTo, index, cast = None, description = None):
        if not (mapTo in ["args", "kwargs"]):
            raise MethodDescriptionError("Invalid mapTo value.")
        self.mapTo = mapTo
        if mapTo == "args":
            try:
                i = int(index)
            except ValueError:
                raise MethodDescriptionError("index must be integer for mapTo == 'args'.")
        self.index = index
        self.cast = cast
        self.description = description
    
    def html(self):
        result = ""
        if self.cast is not None:
            result += (" (%s)" % (self.cast)).replace('<', '').replace('>', '')
        if self.description is not None:
            result += "<p>"+self.description+"</p>"
        return result

class Export(object):
    def supports(self, httpCommand):
        return True
        
    def __str__(self):
        return "Undocumented export."
    
class ExportNamespace(Export):
    def __init__(self, exports, restrictCommandsTo = None):
        self.exports = exports
        self.restrictCommandsTo = restrictCommandsTo
        self.fullPath = ""
    
    def __contains__(self, index):
        return index in self.exports
    
    def __getitem__(self, index):
        return self.exports[index]
        
    def __setitem__(self, index, value):
        self.exports[index] = value
        
    def __iter__(self):
        return self.exports.iteritems()
        
    def __str__(self):
        return "Namespace"
        
    def supports(self, httpCommand):
        if self.restrictCommandsTo is not None:
            return httpCommand in self.restrictCommandsTo
        else:
            return True
    
    def html_listExports(self):
        exportFmt = '<a href="%s">%s</a>'
        exports = "</li><li>".join(exportFmt % (obj.fullPath, str(export)) for export, obj in self.exports.iteritems())
        if exports != "":
            exports = "<li>"+exports+"</li>"
        return exports
    
    def html(self):
        return "<h1>%s</h1><h2>Namespace</h2><p>Contains the following elements:</p><ul>%s</ul>" % (self.fullPath, self.html_listExports())
        
class ExportMethod(ExportNamespace):
    defaultSupportedHTTPCommands = {"GET": True}
    
    def __init__(self, method, requiredArguments = {}, optionalArguments = {}, 
        supportedHTTPCommands = None, exports = {}):
        super(ExportMethod, self).__init__(exports, supportedHTTPCommands)
        
        if supportedHTTPCommands is None:
            self.supportedHTTPCommands = ExportMethod.defaultSupportedHTTPCommands
        else:
            self.supportedHTTPCommands = {}
            for cmd in supportedHTTPCommands:
                self.supportedHTTPCommands[cmd] = True
        self.method = method
        self.requiredArguments = requiredArguments
        self.optionalArguments = optionalArguments
    
    def __call__(self, httpRequest, arguments):
        args = {}
        kwargs = {}
        for key, value in self.requiredArguments.items():
            if not (key in arguments):
                raise ServletMissingArgument(key)
            if value is not None:
                arg = arguments[key]
                if value.cast is not None:
                    try:
                        arg = value.cast(arg)
                    except ValueError:
                        raise ServletInvalidArgumentValue(key, arg, str(value.cast))
                if value.mapTo == "args":
                    args[value.index] = arg
                else:
                    if value.index is None:
                        kwargs[key] = arg
                    else:
                        kwargs[value.index] = arg
            else:
                kwargs[key] = arg
        for key, value in self.optionalArguments.items():
            if not (key in arguments):
                continue
            if value is not None:
                arg = arguments[key]
                if value.cast is not None:
                    try:
                        arg = value.cast(arg)
                    except ValueError:
                        raise ServletInvalidArgumentValue(key, arg, str(value.cast))
                if value.index is None:
                    kwargs[key] = arg
                else:
                    kwargs[value.index] = arg
            else:
                kwargs[key] = arg
        arglist = args.items()
        arglist.sort(None, lambda x: x[0])
        args = [x[1] for x in arglist]
        args.append(httpRequest)
        return self.method(*args, **kwargs)
        
    def __str__(self):
        return self.method.func_name
        
    def html(self):
        argFormat = "<b>%s</b>%s"
        reqArgs = [item for item in self.requiredArguments.iteritems()]
        reqArgs.sort(None, lambda x: x[1].index if x[1].mapTo == "args" else 10000000)
        reqArgStr = "</li><li>".join((argFormat % (key, value.html() if value is not None else "") for key, value in reqArgs))
        if reqArgStr != "":
            reqArgStr = "<li>"+reqArgStr+"</li>"
        optArgStr = "</li><li>".join((argFormat % (key, value.html() if value is not None else "") for key, value in self.optionalArguments.iteritems()))
        if optArgStr != "":
            optArgStr = "<li>"+optArgStr+"</li>"
        exportsStr = self.html_listExports()
        if exportsStr != "":
            namespaceStr = "<h2>Namespace</h2>This namespace also contains the following items: <ul>%s</ul>" % exportsStr
        else:
            namespaceStr = ""
        return "<h1>%s</h1><h2>Callable</h2><h3>Required arguments</h3><ul>%s</ul><h3>Optional arguments</h3><ul>%s</ul>%s" % (
            self.fullPath,
            reqArgStr,
            optArgStr,
            namespaceStr
        )
    
    def supports(self, httpCommand):
        return httpCommand in self.supportedHTTPCommands


class DefaultArguments(object):
    flags = MethodArgumentMapping("kwargs", "flags", flagsCast(),
        description="""The usual export flags. Valid are:
            <i>to be documented</i>""")
    offset = MethodArgumentMapping("kwargs", "offset", int,
        description="Restricts the result set; Only the results after the first <i>offset</i> results will be shown.")
    limit = MethodArgumentMapping("kwargs", "limit", int,
        description="Restricts the result set; Only up to <i>limit</i> results will be returned.")
    distinct = MethodArgumentMapping("kwargs", "distinct", flagCast(),
        description="Restricts the result set; Will eliminate duplicates from the result set (should not occur anyways).")
