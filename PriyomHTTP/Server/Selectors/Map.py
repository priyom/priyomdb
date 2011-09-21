# encoding=utf-8
from WebStack.Generic import EndOfResponse, ContentType
from cfg_priyomhttpd import application, misc, doc

class MapSelector(object):
    path_encoding = "utf-8"
    
    def __init__(self, title, mapping, path_encoding=None, urlencoding=None):
        self.title = title
        self.mapping = mapping
        self.path_encoding = path_encoding or urlencoding or self.path_encoding
        
    def findResource(self, trans):
        parts = trans.get_virtual_path_info(self.path_encoding).split("/")
        
        if len(parts) > 1:
            name = parts[1]
        else:
            self.send_redirect(trans)
        
        resource = self.mapping.get(name)
        catch_all = False
        if resource is None:
            resource = self.mapping.get(None)
            catch_all = True
        if resource is None:
            self.send_error(trans)
        
        if not catch_all:
            new_path = parts[0:1] + parts[2:]
            new_path_info = "/".join(new_path)
            trans.set_virtual_path_info(new_path_info)
        
        return resource, name
        
    def formatListing(self):
        items = [(name, resource) for name, resource in self.mapping.iteritems() if name is not None]
        items.sort(lambda a,b: cmp(a[0], b[0]))
        return u"\n".join(
                (
                    u"""<li><a href="{0}">/{0}</a> ({1})</li>""".format(name, resource.shortDescription) if hasattr(resource, "shortDescription") else 
                    u"""<li><a href="{0}">/{0}</a></li>""".format(name) for name, resource in items
                ))
        
    def listing(self, trans):
        self.out = trans.get_response_stream()
        trans.set_response_code(200)
        trans.set_content_type(ContentType("text/html", "utf-8"))
        print >>self.out, u"""<html>
    <head>
        <title>{0}{1}{2}</title>
    </head>
    <body>
        <h1>Index of {0}</h1>
        <ul>
            {3}
        </ul>
    </body>
</html>""".format(
            self.title,
            (misc.get("titleSeparator", u" ") + application["name"]) if "name" in application else u"",
            (misc.get("titleSeparator", u" ") + application["host"]) if "host" in application else u"",
            self.formatListing()
        ).encode("utf-8")
        
    def respond(self, trans):
        resource, name = self.findResource(trans)
        if resource == self:
            self.listing(trans)
        else:
            return resource.respond(trans)
            
    def docListing(self, trans):
        print >>trans.get_response_stream(), u"""<p>Directory listing</p>
<ul>
{0}
</ul>""".format(self.formatListing()).encode(trans.encoding)
    
    def doc(self, trans, breadcrumbs):
        resource, name = self.findResource(trans)
        if resource == self:
            self.docListing(trans)
        else:
            breadcrumbs.append((resource, name))
            return resource.doc(trans, breadcrumbs)
        
    def send_error(self, trans):
        trans.rollback()
        trans.set_response_code(404)
        trans.set_content_type(ContentType("text/plain", "utf-8"))
        print >>trans.get_response_stream(), u"Resource not found: \"{0}\".".format(trans.get_path_info(self.path_encoding))
        raise EndOfResponse
        
    def send_redirect(self, trans):
        trans.rollback()
        path_without_query = trans.get_path_without_query(self.path_encoding)
        query_string = trans.get_query_string()
        if query_string:
            query_string = "?" + query_string
        trans.redirect(trans.encode_path(path_without_query, self.path_encoding) + "/" + query_string)
        raise EndOfResponse

