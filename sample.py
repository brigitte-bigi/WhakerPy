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

from whakerpy import WebSiteResponse
from whakerpy.httpd.hserver import BaseHTTPDServer
from whakerpy.webapp import WSGIApplication
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
        self._pages.update(data.create_pages(web_response=SampleWebResponse, default_path="samples"))

# ---------------------------------------------------------------------------


if __name__ == "__main__":
    # Launch a local web server and handler
    app = WebSiteApplication(AppServer)
    url = app.client_url()
    webbrowser.open_new_tab(url)
    logging.info(url)
    logging.info(" *******  Stop the server app with CTRL+C ******* ")
    app.run()

else:
    class SampleWebData(WebSiteData):
        """A custom WebSiteData for `sample` web front-end.

        Create the requested page name from webapp.json.

        """
        def bake_response(self, page_name: str, default: str = "") -> WebSiteResponse:
            # Possibly test the page_name to return another response
            # if page_name == "whakerpy.html": return SampleAppResponse()
            # or return the response matching a page_name in webapp.json
            return SampleWebResponse(os.path.join(default, self.filename(page_name)))

    # The WSGI server is searching for an "application(environ, start_response)"
    # function. It is invoked every time a request is received by either POST,
    # or GET, or ... method.
    # uwsgi --http :9090 --wsgi-file sample.py
    app = WSGIApplication(
        default_path="samples",
        default_filename="whakerpy.html",
        web_page_maker=SampleWebData,
        default_web_json="webapp.json"
    )

    # This is another solution to add 'whakerpy.html' page response,
    # which is a page not in json file. Add as many page as wanted.
    httpd_app = SampleAppResponse()
    app.add_page(httpd_app.page(), httpd_app)

    application = app
