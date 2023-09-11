# This file is part of SPPAS: https://sppas.org/
#
# -------------------------------------------------------------------------
#
#  ___   __    __    __    ___
# /     |  \  |  \  |  \  /              the automatic
# \__   |__/  |__/  |___| \__             annotation and
#    \  |     |     |   |    \             analysis
# ___/  |     |     |   | ___/              of speech
#
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# This banner notice must not be removed.
#
# -------------------------------------------------------------------------
#

"""
# HTMLMaker Package

Create an HTML tree and to serialize into a page.

* Filename: sppas.ui.htmlmaker.__init__.py
* Author:   Brigitte Bigi
* Contact:  develop@sppas.org
* Copyright (C) 2011-2023 Brigitte Bigi,
Laboratoire Parole et Langage, Aix-en-Provence, France

## Description

HTMLMaker is a minimalist web framework that can be used to serve HTML
content from Python applications. It does not support templating engines
for generating HTML. Actually, this is a minimalistic system to work with
an HTML Tree and to serialize it into an HTML page. The HTML content is
then created **fully dynamically**.

>Notice that neither the integrity of the tree nor the compliance with HTML
standard are verified.

## Typical usage example

>>> # Create a tree. By default, it contains a head node and a body.
>>> # The body is made of several children:
>>> #   body_header, body_nav, body_main, body_footer, body_script
>>> tree = HTMLTree("Home Page")
>>> # Add a title node to the main of the body with the generic method 'element'
>>> tree.element("h1")
>>> # Add a paragraph node to the main of the body
>>> p_node = HTMLNode(tree.body_main.identifier, "my_p_id", 'p', value="This is a paragraph.")
>>> tree.body_main.append_child(p_node)
>>> # Serialize the HTML tree into a string
>>> html_content = tree.serialize()
>>> # Serialize the HTML tree into a file
>>> tree.serialize("/path/to/my/file.html")


## List of classes

<section class="cards">
    <article class="card-pyclass">
        <header></header>
        <main>
            <h2>HTMLTree</h2>
            <p>Root of the tree to store HTML elements.</p>
        </main>
        <footer><pre>tree = HTMLTree("Home Page")</pre></footer>
    </article>

    <article class="card">
        <header></header>
        <main>
            <h2>Doctype</h2>
            <p></p>
        </main>
        <footer></footer>
    </article>
</section>

"""

from .hexc import NodeTypeError
from .hexc import NodeTagError
from .hexc import NodeKeyError
from .hexc import NodeAttributeError
from .hexc import NodeChildTagError
from .hexc import NodeInvalidIdentifierError
from .hexc import NodeIdentifierError
from .hleaf import Doctype
from .hleaf import HTMLComment
from .hleaf import HTMLImage
from .hleaf import HTMLHr
from .hnodetags import HTMLInputText
from .hnodetags import HTMLRadioBox
from .hnodetags import HTMLButtonNode
from .hnode import BaseNode
from .hnode import EmptyNode
from .hnode import HTMLNode
from .hnode import HTMLHeadNode
from .hnode import HTMLHeaderNode
from .hnode import HTMLNavNode
from .hnode import HTMLMainNode
from .hnode import HTMLFooterNode
from .hnode import HTMLScriptNode
from .htree import HTMLTree

__all__ = (
    "NodeTypeError",
    "NodeTagError",
    "NodeKeyError",
    "NodeAttributeError",
    "NodeChildTagError",
    "NodeInvalidIdentifierError",
    "NodeIdentifierError",
    "Doctype",
    "HTMLComment",
    "HTMLImage",
    "HTMLHr",
    "HTMLInputText",
    "HTMLRadioBox",
    "HTMLButtonNode",
    "BaseNode",
    "EmptyNode",
    "HTMLNode",
    "HTMLHeadNode",
    "HTMLHeaderNode",
    "HTMLNavNode",
    "HTMLMainNode",
    "HTMLFooterNode",
    "HTMLScriptNode",
    "HTMLTree"
)
