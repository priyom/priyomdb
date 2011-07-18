class ServletError(Exception):
    def __init__(self, code, message=None):
        self.code = code
        self.message = message
        
class ServletInvalidQueryError(ServletError):
    def __init__(self, message = "Invalid query"):
        super(ServletInvalidQueryError, self).__init__(400, message)
        
class ServletUnknownCommand(ServletInvalidQueryError):
    def __init__(self):
        super(ServletUnknownCommand, self).__init__("Unknown command")
        
class ServletUnsupportedMethod(ServletInvalidQueryError):
    def __init__(self, httpCommand):
        super(ServletUnsupportedMethod, self).__init__("This HTTP command (%s) is not supported by the requested method.")

class ServletMissingArgument(ServletError):
    def __init__(self, argumentName):
        super(ServletMissingArgument, self).__init__(400, "Missing argument '%s'" % (argumentName))

class ServletInvalidArgumentValue(ServletError):
    def __init__(self, argumentName, got, expected):
        super(ServletInvalidArgumentValue, self).__init__(400, "Invalid value %r for argument %s (%s expected)" % (got, argumentName, expected))
