import baseServlet
from ..errors import ServletError, ServletInvalidQueryError
from ..servlets import register

class EmptyServlet(baseServlet.Servlet):
	def empty(self, httpRequest):
		httpRequest.setHeader("Content-Type", "text/html");
		httpRequest.wfile.write('<html><head><title>api.priyom.org</title></head><body><h1>Welcome!</h1><p>Welcome to the <a href="http://priyom.org">priyom.org</a> api server.</p><p><a href="doc/">API Documentation</a></p></body></html>');


register("empty", EmptyServlet, True, "empty.py")

