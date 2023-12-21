# -*- coding: UTF-8 -*-
"""
:filename: sample.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Example of custom application based on a web-frontend for Py backend.

"""

import os
import webbrowser
import logging

from whakerpy.htmlmaker import HTMLTree
from whakerpy.httpd.hserver import BaseHTTPDServer
from whakerpy.webapp import WebSiteData
from whakerpy.webapp import WebSiteApplication
from samples.response import SampleAppResponse
from samples.response import SampleWebResponse

# Enable debug level
logging.getLogger().setLevel(0)

# ---------------------------------------------------------------------------


class AppServer(BaseHTTPDServer):
    """A custom HTTPD server for `sample` web front-end.

    """

    def create_pages(self, app: str = "app"):
        """Override. Add bakeries for dynamic HTML pages of this app.

        :param app: (str) Un-used parameter.

        """
        logging.debug("HTTPD server initialization...")

        # The "ResponseRecipe" is the interface between the HTTPD server
        # (frontend) and your API - Application Programming Interface
        # (backend). In this sample, the response is generating random
        # colors/text; it's a fully dynamic content with one page only.
        app_bakery = SampleAppResponse()
        self._pages[app_bakery.page()] = app_bakery
        self._default = app_bakery.page()

        # Extract the config data of the sample webapp from a JSON file
        data = WebSiteData(os.path.join("samples", "webapp.json"))

        # Create the dynamic tree for each page described in data
        tree = HTMLTree("sample")
        for page_name in data:
            page_path = os.path.join("samples", data.filename(page_name))
            bakery = SampleWebResponse(page_path, tree)
            self._pages[page_name] = bakery

# ---------------------------------------------------------------------------


app = WebSiteApplication(AppServer)
url = app.client_url()
webbrowser.open_new_tab(url)
logging.info(url)
app.run()
# Stop the server app with CTRL+C
