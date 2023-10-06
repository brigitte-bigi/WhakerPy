"""
:filename: sppas.ui.htmlmaker.hleaf.py
:author:   Brigitte Bigi
:contact:  develop@sppas.org
:summary: A set of specific nodes of the tree.

.. _This file is part of SPPAS: https://sppas.org/
..
    -------------------------------------------------------------------------

     ___   __    __    __    ___
    /     |  \  |  \  |  \  /              the automatic
    \__   |__/  |__/  |___| \__             annotation and
       \  |     |     |   |    \             analysis
    ___/  |     |     |   | ___/              of speech

    Copyright (C) 2011-2023 Brigitte Bigi
    Laboratoire Parole et Langage, Aix-en-Provence, France

    Use of this software is governed by the GNU Public License, version 3.

    SPPAS is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    SPPAS is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------

"""

import uuid

from .hexc import NodeAttributeError
from .hnode import BaseNode
from .hnode import EmptyNode

# ---------------------------------------------------------------------------


class Doctype(BaseNode):
    """Represent the HTML doctype of an HTML page.

    :Example:
        >>> d = Doctype()
        >>> d.serialize()
        >>> '<!DOCTYPE html>'

    All HTML documents must start with a &lt;!DOCTYPE&gt; declaration.
    The declaration is **not** an HTML tag. It is an "information" to the
    browser about what document type to expect. Contrariwise to previous
    versions, HTML5 does not require any other information.

    """

    def __init__(self):
        """Create a doctype node with no defined parent."""
        # no parent means no invalidated
        super(Doctype, self).__init__(None, str(uuid.uuid1()))

        # In HTML 5, the doctype declaration does not need to refer to a DTD.
        self._value = "<!DOCTYPE html>"

    # -----------------------------------------------------------------------
    # HTML management: HTML generator
    # -----------------------------------------------------------------------

    def serialize(self, nbs: int = 4) -> str:
        """Override. Serialize the doctype.

        :param nbs: (int) Number of spaces for the indentation. Un-used.
        :return: (str)

        """
        return self._value + "\n\n"

# ---------------------------------------------------------------------------


class HTMLComment(BaseNode):
    """Represent a comment element.

    The comment tag does not support any standard attributes.

    """

    def __init__(self, parent, content=" --- "):
        """Create an input node. Default type is 'text'."""
        super(HTMLComment, self).__init__(parent, str(uuid.uuid1()))
        self._value = content

    # -----------------------------------------------------------------------
    # HTML management: HTML generator
    # -----------------------------------------------------------------------

    def serialize(self, nbs: int = 4) -> str:
        """Serialize the comment into HTML.

        :param nbs: (int) Number of spaces for the indentation
        :return: (str)

        """
        indent = " "*nbs
        html = "\n"
        html += indent + "<!-- "
        r = (70 - len(self._value)) // 2
        if r > 0:
            html += "-"*r
        html += " " + self._value + " "
        if r > 0:
            html += "-"*r
        html += " -->\n\n"
        return html

# ---------------------------------------------------------------------------


class HTMLImage(EmptyNode):
    """Represent an image element.

    The set_attribute method should be overridden to check if the given key
    is in the list of accepted attributes.

    """
    def __init__(self, parent, identifier, src):
        """Create an image leaf node.

        """
        super(HTMLImage, self).__init__(parent, identifier, "img")
        self.add_attribute("src", src)
        self.add_attribute("alt", "")

# ---------------------------------------------------------------------------


class HTMLHr(EmptyNode):
    """Represent an horizontal line with <hr> tag.

    The &lt;hr&gt; tag only supports the Global Attributes in HTML.

    """

    def __init__(self, parent):
        """Create a node for <hr> tag.

        """
        super(HTMLHr, self).__init__(parent, None, "hr")

    # -----------------------------------------------------------------------

    def check_attribute(self, key):
        """Override.

        :return: key (str)
        :raises: NodeAttributeError: if given key can't be converted to string
        :raises: NodeAttributeError: The attribute can't be assigned to this element.

        """
        try:
            key = str(key)
        except Exception:
            raise NodeAttributeError(key)

        if key not in EmptyNode.HTML_GLOBAL_ATTR:
            raise NodeAttributeError(key)

        return key
