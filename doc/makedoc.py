# -*- coding: UTF-8 -*-
# makedoc.py
# Summary: Create the documentation of WhakerPy, using Clamming library.
# Usage: python makedoc.py
#
# This file is part of WhakerPy tool.
# (C) 2023 Brigitte Bigi, Laboratoire Parole et Langage,
# Aix-en-Provence, France.
#
# Use of this software is governed by the GNU Public License, version 3.
#
# Clamming is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Clamming is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Clamming. If not, see <https://www.gnu.org/licenses/>.
#
# This banner notice must not be removed.
#
# ---------------------------------------------------------------------------

from __future__ import annotations
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from whakerpy.htmlmaker import *
from whakerpy.httpd import *
from whakerpy.webapp import *
try:
    from clamming import ClamsClass
    from clamming import ClammingClassParser
except ImportError:
    print("This program requires `Clamming` documentation generator.")
    print("It can be installed with: pip install Clamming.")
    print("See <https://pypi.org/project/Clamming/> for details.")
    sys.exit(-1)

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

HTML_TOP = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes" />
        <title>WhakerPy Doc</title>
        <link rel="logo icon" href="../etc/whakerpy32x32.ico" />
        <link rel="stylesheet" href="../etc/colors_light.css" type="text/css" />
        <link rel="stylesheet" href="../etc/main.css" type="text/css" />
        <link rel="stylesheet" href="../etc/main_sppas.css" type="text/css" />
        <link rel="stylesheet" href="../etc/code.css" type="text/css" />
        <link rel="stylesheet" href="../etc/cards.css" type="text/css" />
        <script src="../etc/toc.js" type="text/javascript"></script>
   </head>
<body class="light">
     <header></header>
     <nav id="nav-book" class="side-nav">
         <p><strong>WhakerPy doc</strong></p>
         <ul>
             <li class="center">
                 <a class="width-three-quarters" role="button" tabindex="0" {prev}> 
                 &uarr; Prev. Class</a>
             </li>
             <li class="center">
                 <a class="width-three-quarters" role="button" tabindex="0" href="index.html">
                 &#8962; Doc Home</a>
             </li>
             <li class="center">
                 <a class="width-three-quarters" role="button" tabindex="0" {next}>
                  &darr; Next Class</a>
             </li>
         </ul>
     
         <p><strong>Table of Contents</strong></p>
         <ul id="toc"></ul>
     
     </nav>
     <main id="toc-content">

        <h1>
            <img class="center small-logo" src="../etc/whakerpy.png" alt="WhakerPy logo">
            <img class="center small-logo" src="../etc/whakerpy.png" alt="WhakerPy logo">
            <img class="center small-logo" src="../etc/whakerpy.png" alt="WhakerPy logo">
            <p class="center">WhakerPy tool documentation</p>
        </h1>

"""

HTML_BOTTOM = """
    </main>
    <footer>
        <p class="copyright"> Copyright (C) Brigitte Bigi - LPL 2023 </p>
    </footer>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
                 htmlTableOfContents();
             }
         );
    
         try {
             module.exports = htmlTableOfContents;
         } catch (e) {
             // module.exports is not defined
         }
    </script>
    <script src="../etc/accordion.js" type="text/javascript"></script>
 </body>
</html>

"""

# ---------------------------------------------------------------------------
# Useful function to export a class into a valid HTML file.
# ---------------------------------------------------------------------------


def html_top(prev_link: str | None, next_link: str | None) -> str:
    """Return the custom top part of the HTML output file.

    """
    if prev_link is None:
        a_prev = 'aria-disabled="true"'
    else:
        a_prev = 'href="{:s}"'.format(prev_link)
    if next_link is None:
        a_next = 'aria-disabled="true"'
    else:
        a_next = 'href="{:s}"'.format(next_link)
    return HTML_TOP.format(prev=a_prev, next=a_next)

# ---------------------------------------------------------------------------


def html_index_page(all_pages: dict) -> None:
    """Write the index.html file from the given pages.

    :param all_pages: A dictionary with all HTML pages.

    """
    with open(os.path.join("", "index.html"), "w", encoding="utf-8") as fp:
        fp.write(html_top(prev_link=None, next_link=None))

        for package in all_pages:
            fp.write('<section id="{:s}">\n'.format(package))
            fp.write("<h2>WhakerPy.{:s} classes</h2>\n".format(package))

            fp.write('<section class="cards-panel">\n')
            for ip in range(len(all_pages[package])):
                py_obj, page_name = all_pages[package][ip]
                fp.write('    <article class="card">\n')
                fp.write('        <header><span>{:d}</span></header>'.format(ip+1))
                fp.write('        <main>')
                fp.write('            <h3>{:s}</h3>'.format(py_obj.__name__))
                fp.write('        </main>')
                fp.write('        <footer>')
                fp.write(_add_link("Read me →", page_name))
                fp.write('        </footer>')
                fp.write('    </article>')

            fp.write("</section>\n")

        fp.write(HTML_BOTTOM)


def _add_link(name: str, href: str) -> str:
    return '            <a role="button" href="{:s}">{:s}</a>'.format(href, name)

# ---------------------------------------------------------------------------


def obj_to_html(pyobj, out_html, prev_page=None, next_page=None) -> None:
    """Return the custom documentation HTML output file of the given object.

    :param pyobj: (Any) A python class object
    :param out_html: (str) Output filename
    :param prev_page: (str|None) Previous page name
    :param next_page: (str|None) Previous page name

    """
    # Parse the object and store collected information = clamming
    clamming = ClammingClassParser(pyobj)

    # Export the collected clams to HTML
    clams = ClamsClass(clamming)
    html_content = clams.html()
    with open(out_html, "w", encoding="utf-8") as fp:
        fp.write(html_top(prev_page, next_page))
        fp.write(html_content)
        fp.write(HTML_BOTTOM)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    # List of HTML pages dynamically created by Clamming,
    # split by package for clarity reasons...
    pack1 = [
        (BaseNode, "basenode.html"),
        (BaseTagNode, "tagnode.html"),
        (EmptyNode, "emptynode.html"),
        (HTMLNode, "node.html"),
        (HTMLTree, "tree.html")
        ]
    pack2 = [
        (HTTPDHandler, "handler.html"),
        (BaseHTTPDServer, "server.html"),
        (BaseResponseRecipe, "response.html")
    ]
    pack3 = [
        (WebSiteData, "websitedata.html"),
        (WebSiteResponse, "websiteresponse.html"),
        (WebSiteApplication, "websiteapp.html")
    ]
    pages = {
        "htmlmaker": pack1,
        "httpd": pack2,
        "webapp": pack3
    }

    # Create the index.html page. It's a table of content.
    html_index_page(pages)

    # HTML export of all documented classes.
    for pack in pages:
        for i in range(len(pages[pack])):
            obj, page = pages[pack][i]
            p = None if i == 0 else pages[pack][i-1][1]
            n = None if i+1 == len(pages[pack]) else pages[pack][i+1][1]
            print("{:s}".format(page))
            obj_to_html(obj, page, prev_page=p, next_page=n)
