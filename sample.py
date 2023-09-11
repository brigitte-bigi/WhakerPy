# -*- coding: UTF-8 -*-
"""
:filename: response.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: develop@sppas.org
:summary: An example of custom response with HTML, JS and JSON.

"""

import webbrowser
import logging

from whakerpy.httpd.handler import sppasHTTPDHandler
from whakerpy.httpd.hserver import sppasBaseHTTPDServer
from samples.response import TestsResponseRecipe

logging.getLogger().setLevel(0)

# ---------------------------------------------------------------------------


class TestServer(sppasBaseHTTPDServer):
    """A custom HTTPD server for a custom python application!

    """

    def create_pages(self, app_type="app"):
        """Override."""
        logging.debug("HTTPD server initialization..")
        # The "ResponseRecipe" is the interface between the HTTPD server (frontend)
        # and your API - Application Programming Interface (backend).
        # In the sample, the response is generating random colors/text.
        bakery = TestsResponseRecipe()
        self._pages[bakery.page()] = bakery
        self._default = bakery.page()
        # other responses to create other html contents can be added here.

# ---------------------------------------------------------------------------


location = "localhost"
port = 8080
server_address = (location, port)
server = TestServer(server_address, sppasHTTPDHandler)
server.create_pages()

url = "http://{:s}:{:d}/".format(location, port)
webbrowser.open_new_tab(url)
logging.info(url)

try:
    # Start the main loop of the HTTP server
    server.serve_forever()
    # Notice that the sppasHTTPDHandler can shut down the server --
    # it is allowed because it's a local application, not a web-service.
except KeyboardInterrupt:
    # Stop the server
    server.shutdown()


