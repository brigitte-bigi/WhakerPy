import os

from whakerpy.webapp.webwsgi import WSGIApplication

# ---------------------------------------------------------------------------


# The WSGI server is searching for an "application(environ, start_response)"
# function. It is invoked every time a request is received by either POST,
# or GET, or ... method.
application = WSGIApplication(os.getcwd())
