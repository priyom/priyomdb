import baseServlet
from baseServlet import ServletError, ServletInvalidQueryError
from ..servlets import register

class EmptyServlet(baseServlet.Servlet):
	def do_GET(self, pathSegments, arguments, rfile, wfile):
		self.setHeader("Content-Type", "text/html");
		wfile.write("<html><head><title>api.priyom.org</title></head><body><h1>Welcome!</h1><p>Welcome to the <a href=\"http://priyom.org\">priyom.org</a> api server.</p></body></html>");


register("", EmptyServlet, True, "empty.py")

