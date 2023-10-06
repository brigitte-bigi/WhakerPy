"""
:filename: sppas.ui.htmlmaker.hnode.py
:author:   Brigitte Bigi
:contact:  develop@sppas.org
:summary: Node classes to generate HTML elements.

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

Since the early days of the World Wide Web, there have been many versions:
[source: <https://www.w3schools.com/html/html_intro.asp>]

-    1989: 	Tim Berners-Lee invented www
-    1991: 	Tim Berners-Lee invented HTML
-    1993: 	Dave Raggett drafted HTML+
-    1995: 	HTML Working Group defined HTML 2.0
-    1997: 	W3C Recommendation: HTML 3.2
-    1999: 	W3C Recommendation: HTML 4.01
-    2000: 	W3C Recommendation: XHTML 1.0
-    2008: 	WHATWG HTML5 First Public Draft
-    2012: 	WHATWG HTML5 Living Standard
-    2014: 	W3C Recommendation: HTML5
-    2016: 	W3C Candidate Recommendation: HTML 5.1
-    2017: 	W3C Recommendation: HTML5.1 2nd Edition
-    2017: 	W3C Recommendation: HTML5.2

HTML elements are generally made of a start tag, an optional element content,
and an end tag. However, several elements have only a start tag, like <br/>
or <img/>, and a few elements don't have tag at all, like comments.

"""

import re
import uuid
import logging
import traceback

from .hexc import NodeInvalidIdentifierError
from .hexc import NodeParentIdentifierError
from .hexc import NodeTagError
from .hexc import NodeChildTagError
from .hexc import NodeAttributeError
from .hexc import NodeKeyError

# ---------------------------------------------------------------------------


class BaseNode(object):
    """A base class for any node in an HTML tree.

    """

    def __init__(self, parent: str = None, identifier: str = None):
        """Create a new base node.

        :param parent: (str) Parent identifier
        :param identifier: (str) This node identifier
        :raises: NodeInvalidIdentifierError:

        """
        # The node identifier.
        if identifier is not None:
            ident = BaseNode.validate_identifier(identifier)
            self.__identifier = ident
        else:
            self.__identifier = str(uuid.uuid1())

        # Identifier of the parent node
        self._parent = None
        self.set_parent(parent)

    # -----------------------------------------------------------------------

    @staticmethod
    def validate_identifier(identifier: str) -> str:
        """Return the given identifier if it matches the requirements.

        An identifier should contain at least 1 character and no whitespace.

        :param identifier: (str) Key to be validated
        :raises: NodeInvalidIdentifierError: if it contains invalid characters
        :raises: NodeInvalidIdentifierError: if invalid length
        :returns: (str)

        """
        entry = BaseNode.full_strip(identifier)
        if len(entry) != len(identifier):
            raise NodeInvalidIdentifierError(identifier)

        if len(identifier) == 0:
            raise NodeInvalidIdentifierError(identifier)

        return identifier

    # -----------------------------------------------------------------------

    @staticmethod
    def full_strip(entry):
        """Fully strip the string: multiple whitespace, tab and CR/LF.

        Remove all whitespace, tab and CR/LF inside the string.

        :returns: (str)

        """
        e = re.sub("[\s]+", r"", entry)
        e = re.sub("[\t]+", r"", e)
        e = re.sub("[\n]+", r"", e)
        e = re.sub("[\r]+", r"", e)
        if "\ufeff" in e:
            e = re.sub("\ufeff", r"", e)
        return e

    # -----------------------------------------------------------------------

    @property
    def identifier(self) -> str:
        """Return the unique ID of the node within the scope of a tree. """
        return self.__identifier

    # -----------------------------------------------------------------------

    def is_leaf(self) -> bool:
        """Return true if node has no children."""
        return True

    # -----------------------------------------------------------------------

    def is_root(self) -> bool:
        """Return true if node has no parent, i.e. as root."""
        return self._parent is None

    # -----------------------------------------------------------------------

    def get_parent(self) -> str:
        """The parent identifier.

        :return: (str) node identifier

        """
        return self._parent

    # -----------------------------------------------------------------------

    def set_parent(self, node_id: str) -> None:
        """Set the parent identifier.

        :param node_id: (str) Identifier of the parent

        """
        if self.__identifier == node_id:
            raise NodeKeyError(self.__identifier, node_id)

        self._parent = node_id

    # -----------------------------------------------------------------------

    def has_child(self, node_id: str) -> bool:
        """Return True if the given node is a direct child.

        :param node_id: (str) Identifier of the node
        :return: (bool) True if given identifier is a direct child.

        """
        return not self.is_leaf()

    # -----------------------------------------------------------------------

    def serialize(self, nbs: int = 4) -> str:
        """To be overriden. Serialize the node into HTML.

        :param nbs: (int) Number of spaces for the indentation
        :return: (str)

        """
        return ""

# ---------------------------------------------------------------------------


class EmptyNode(BaseNode):
    """A class for HTML empty nodes in a tree.

    An HTML element without content is called an empty node. It has a
    start tag but neither a content nor an end tag.

    Compared to the parent class BaseNode, this class adds 2 members:

    1. the required element tag;
    2. its optional attributes.

    For example, it can deal with elements like:

        - &lt;tag /&gt;
        - &lt;tag k=v /&gt;
        - &lt;tag k1=v2 k2=v2 k3 /&gt;

    """

    # This is the whole list of HTML tags. It should be split into 2:
    # the ones that can be empty and the ones that can't (in HTMLNode).
    # Moreover, each tag should be linked to its possible attributes.
    HTML_TAGS = {
        "a": "hyperlink",
        "abbr": "abbreviation",
        "address": "address element",
        "area": "area inside an image map",
        "article": "article",
        "aside": "content aside from the page content",
        "audio": "sound content",
        "b": "bold text",
        "base": "base URL for all the links in a page",
        "bdi": "for bi-directional text formatting",
        "bdo": "the direction of text display",
        "blockquote": "long quotation",
        "body": "the body element",
        "br": "inserts a single line break",
        "button": "button form control",
        "canvas": "define graphics",
        "caption": "table caption",
        "cite": "citation",
        "code": "computer code text",
        "col": "attributes for table columns",
        "colgroup": "groups of table columns",
        "data": "allows for machine-readable data to be provided",
        "datalist": "autocomplete dropdown list",
        "dd": "definition description",
        "del": "deleted text",
        "details": "details of an element",
        "dfn": "defines a definition term",
        "dialog": "that part of an application is interactive",
        "div": "section in a document",
        "dl": "definition list",
        "dt": "definition term",
        "em": "emphasized text",
        "embed": "external application or interactive content",
        "fieldset": "fieldset",
        "figcaption": "caption for the figure element",
        "figure": "group of media content, and their caption",
        "footer": "footer for a section or page",
        "form": "form",
        "h1": "heading level 1",
        "h2": "heading level 2",
        "h3": "heading level 3",
        "h4": "heading level 4",
        "h5": "heading level 5",
        "h6": "heading level 6",
        "head": "information about the document",
        "header": "group of introductory or navigational aids, including hgroup elements",
        "hgroup": "header for a section or page",
        "hr": "horizontal rule",
        "html": "html document",
        "i": "italic text",
        "iframe": "inline sub window (frame)",
        "img": "image",
        "input": "input field",
        "ins": "inserted text",
        "kbd": "keyboard text",
        "label": "label for a form control",
        "legend": "title in a fieldset",
        "li": "list item",
        "link": "resource reference",
        "main": "the main content area of an HTML document",
        "map": "image map",
        "mark": "marked text",
        "menu": "toolbar consisting of its contents, in the form of an unordered list of items",
        "meta": "meta information",
        "meter": "measurement within a predefined range",
        "nav": "navigation links",
        "noscript": "noscript section",
        "object": "embedded object",
        "ol": "ordered list",
        "optgroup": "option group",
        "option": "option in a drop-down list",
        "output": "some types of output",
        "p": "paragraph",
        "param": "parameter for an object",
        "picture": "container that provides multiple sources to its contained img element",
        "pre": "preformatted text",
        "progress": "progress of a task of any kind",
        "q": "short quotation",
        "rb": "marks the base text component of a ruby annotation",
        "rp": "used for the benefit of browsers that don't support ruby annotations",
        "rt": "ruby text component of a ruby annotation",
        "rtc": "marks the ruby text container for ruby text components in a ruby annotation",
        "ruby": "ruby annotation (used in East Asian typography)",
        "s": "Indicates text that's no longer accurate or relevant",
        "samp": "sample computer code",
        "script": "script",
        "section": "section",
        "select": "selectable list",
        "slot": "defines a slot, typically in a shadow tree",
        "small": "small text",
        "source": "media resources",
        "span": "section in a document",
        "strong": "strong text",
        "style": "style definition",
        "sub": "subscripted text",
        "summary": "summary / caption for the <details> element",
        "sup": "superscripted text",
        "table": "table",
        "tbody": "table body",
        "td": "table cell",
        "template": "allows to declare an HTML fragment that can be cloned and inserted in the document by script",
        "textarea": "text area",
        "tfoot": "table footer",
        "th": "table header",
        "thead": "table header",
        "time": "date/time",
        "title": "the document title",
        "tr": "table row",
        "track": "text track for media such as video and audio",
        "u": "text with a non-textual annotation",
        "ul": "unordered list",
        "var": "variable",
        "video": "video",
        "wbr": "line break opportunity for very long words and strings of text with no spaces"
    }

    HTML_GLOBAL_ATTR = (
        "accesskey",
        "class",
        "contenteditable",
        "data-*",
        "dir",
        "draggable",
        "hidden",
        "id",
        "lang",
        "spellcheck",
        "style",
        "tabindex",
        "title",
        "translate",
    )

    HTML_VISIBLE_ATTR = (
        "onblur",
        "onchange",
        "onclick",
        "oncontextmenu",
        "oncopy",
        "oncut",
        "ondblclick",
        "ondrag",
        "ondragend",
        "ondragenter",
        "ondragleave",
        "ondragover",
        "ondragstart",
        "ondrop",
        "onfocus",
        "oninput",
        "oninvalid",
        "onkeydown",
        "onkeypress",
        "onkeyup",
        "onmousedown",
        "onmousemove",
        "onmouseout",
        "onmouseover",
        "onmouseup",
        "onmousewheel",
        "onpaste",
        "onscroll",
        "onselect",
        "onwheel",
    )

    HTML_TAG_ATTR = {
        "accept": ("input", ),
        "accept-charset": ("form", ),
        "action": ("form", ),
        "alt": ("area", "img", "input"),
        "async": ("script", ),
        "autocomplete": ("form", "input"),
        "autofocus": ("button", "input", "select", "textarea"),
        "autoplay": ("audio", "video"),
        "charset": ("meta", "script"),
        "checked": ("input",),
        "cite": ("blockquote", "del", "ins", "q"),
        "cols": ("textarea", ),
        "colspan": ("td", "th"),
        "content": ("meta", ),
        "controls": ("audio", "video"),
        "coords": ("area", ),
        "data": ("object", ),
        "datetime": ("del", "ins", "time"),
        "default": ("track", ),
        "defer": ("script", ),
        "dirname": ("input", "textarea", ),
        "disabled": ("button", "fieldset", "input", "optgroup", "option", "select", "textarea"),
        "download": ("a", "area"),
        "enctype": ("form", ),
        "for": ("label", "output"),
        "form": ("button", "fieldset", "input", "label", "meter", "object", "output", "select", "textarea"),
        "formaction": ("button", "input"),
        "headers": ("td", "th"),
        "height": ("canvas", "embed", "iframe", "img", "input", "object", "video"),
        "high": ("meter", ),
        "href": ("a", "area", "base", "link"),
        "hreflang": ("a", "area", "link"),
        "http-equiv": ("meta", ),
        "ismap": ("img", ),
        "kind": ("track", ),
        "label": ("track", "option", "optgroup"),
        "list": ("input", ),
        "loop": ("audio", "video"),
        "low": ("meter", ),
        "max": ("input", "meter", "progress"),
        "maxlength": ("input", "textarea"),
        "media": ("a", "area", "link", "source", "style"),
        "method": ("form", ),
        "min": ("input", "meter"),
        "multiple": ("input", "select"),
        "muted": ("video", "audio"),
        "name": ("button", "fieldset", "form", "iframe", "input", "map", "meta",
                  "object", "output", "param", "select", "textarea"),
        "novalidate": ("form", ),
        "onabort": ("audio", "embed", "img", "object", "video"),
        "onafterprint": ("body", ),
        "onbeforeprint": ("body", ),
        "onbeforeunload": ("body", ),
        "oncanplay": ("audio", "embed", "object", "video"),
        "oncanplaythrough": ("audio", "video"),
        "oncuechange": ("track", ),
        "ondurationchange": ("audio", "video"),
        "onemptied": ("audio", "video"),
        "onended": ("audio", "video"),
        "onerror": ("audio", "body", "embed", "img", "object", "script", "style", "video"),
        "onhashchange": ("body", ),
        "onload": ("body", "iframe", "img", "input", "link", "script", "style"),
        "onloadeddata": ("audio", "video"),
        "onloadedmetadata": ("audio", "video"),
        "onloadstart": ("audio", "video"),
        "onoffline": ("body", ),
        "ononline": ("body", ),
        "onpagehide": ("body", ),
        "onpageshow": ("body", ),
        "onpause": ("audio", "video"),
        "onplay": ("audio", "video"),
        "onplaying": ("audio", "video"),
        "onpopstate": "(body )",
        "onprogress": ("audio", "video"),
        "onratechange": ("audio", "video"),
        "onreset": ("form", ),
        "onresize": ("body", ),
        "onsearch": ("input", ),
        "onseeked": ("audio", "video"),
        "onseeking": ("audio", "video"),
        "onstalled": ("audio", "video"),
        "onstorage": ("body", ),
        "onsubmit": ("form", ),
        "onsuspend": ("audio", "video"),
        "ontimeupdate": ("audio", "video"),
        "ontoggle": ("details", ),
        "onunload": ("body", ),
        "onvolumechange": ("audio", "video"),
        "onwaiting": ("audio", "video"),
        "open": ("details", ),
        "optimum": "(meter )",
        "pattern": ("input", ),
        "placeholder": ("input", "textarea"),
        "poster": ("video", ),
        "preload": ("audio", "video"),
        "readonly": ("input", "textarea"),
        "rel": ("a", "area", "form", "link"),
        "required": ("input", "select", "textarea"),
        "reversed": ("ol", ),
        "rows": ("textarea", ),
        "rowspan": ("td", "th"),
        "sandbox": ("iframe", ),
        "scope": ("th", ),
        "selected": ("option", ),
        "shape": ("area", ),
        "size": ("input", "select"),
        "sizes": ("img", "link", "source"),
        "span": ("col", "colgroup"),
        "src": ("audio", "embed", "iframe", "img", "input", "script", "source", "track", "video"),
        "srcdoc": ("iframe", ),
        "srclang": ("track", ),
        "srcset": ("img", "source"),
        "start": ("ol", ),
        "step": ("input", ),
        "target": ("a", "area", "base", "form"),
        "type": ("a", "button", "embed", "input", "link", "menu", "object", "script", "source", "style"),
        "usemap": ("img", "object"),
        "value": ("button", "input", "li", "option", "meter", "progress", "param"),
        "width": ("canvas", "embed", "iframe", "img", "input", "object", "video"),
        "wrap": ("textarea", )
    }

    ARIA_TAG_ATTR = {
        "role": ("none", "generic", "contentinfo", "banner"),
        "aria-labelledby": None,
        "aria-label": None,
        "aria-pressed": ("true", "false")
    }

    def __init__(self, parent: str, identifier: str, tag: str, attributes: dict =dict()):
        """Create a new leaf node.

        :param parent: (str) Parent identifier
        :param identifier: (str) This node identifier
        :param tag: (str) The element tag
        :param attributes: (dict) key=(str) value=(str or None)
        :raises: NodeInvalidIdentifierError:
        :raises: NodeTagError:
        :raises: TypeError:

        """
        super(EmptyNode, self).__init__(parent, identifier)

        # The node data: a tag and its attributes
        tag = str(tag)
        if tag not in HTMLNode.HTML_TAGS.keys():
            raise NodeTagError(tag)
        self.__tag = tag
        self._attributes = dict()

        # Fill in the attributes' dictionary
        if isinstance(attributes, dict) is False:
            raise TypeError("Expected a dict for the attributes.")
        for key in attributes:
            value = attributes[key]
            self.add_attribute(key, value)

    # -----------------------------------------------------------------------
    # HTML management: getters and setters
    # -----------------------------------------------------------------------

    @property
    def tag(self):
        """Return the HTML tag. """
        return self.__tag

    # -----------------------------------------------------------------------

    def check_attribute(self, key) -> str:
        """Raises NodeAttributeError if key is not a valid attribute.

        :return: key (Any) A unique identifier, anything that we can cast to string
        :raises: NodeAttributeError: The attribute can't be assigned to this element.
        :raises: NodeAttributeError: if given key can't be converted to string

        """
        try:
            key = str(key)
        except Exception:
            raise NodeAttributeError(key)

        if key not in EmptyNode.HTML_GLOBAL_ATTR and \
                key not in EmptyNode.HTML_VISIBLE_ATTR and \
                key not in EmptyNode.HTML_TAG_ATTR.keys() and \
                key not in EmptyNode.ARIA_TAG_ATTR.keys():
            raise NodeAttributeError(key)

        return key

    # -----------------------------------------------------------------------

    def get_attribute_keys(self):
        """Return the list of attribute keys. """
        return [k for k in self._attributes.keys()]

    # -----------------------------------------------------------------------

    def set_attribute(self, key, value):
        """Set a property to the node. Delete the existing one, if any.

        :param key: Key property
        :param value:

        """
        key = self.check_attribute(key)
        if isinstance(value, (list, tuple)) is True:
            value = " ".join(value)
        self._attributes[key] = value

    # -----------------------------------------------------------------------

    def add_attribute(self, key, value):
        """Add a property to the node. Append the value if existing.

        :param key: (str) Key property
        :param value:

        """
        if key not in self._attributes:
            self.set_attribute(key, value)
        else:
            if self._attributes[key] is not None:
                self._attributes[key] += " " + value
            else:
                self._attributes[key] = value

    # -----------------------------------------------------------------------

    def get_attribute_value(self, key):
        """Return the attribute value if the node has this attribute.

        :param key: (str)
        :return: None if the attribute does not exist or has no value

        """
        if key in self._attributes:
            return self._attributes[key]
        return None

    # -----------------------------------------------------------------------

    def has_attribute(self, key) -> bool:
        """Return true if the node has the attribute."""
        return key in self._attributes

    # -----------------------------------------------------------------------

    def remove_attribute(self, key) -> None:
        """Remove the attribute to the node. """
        if key in self._attributes:
            del self._attributes[key]

    # -----------------------------------------------------------------------

    def remove_attribute_value(self, key, value) -> None:
        """Remove the value of an attribute of the node. """
        if key in self._attributes:
            values = self._attributes[key].split(" ")
            if value in values:
                values.remove(value)
                if len(values) == 0:
                    del self._attributes[key]
                else:
                    self.set_attribute(key, " ".join(values))

    # -----------------------------------------------------------------------

    def nb_attributes(self) -> int:
        """Return the number of attributes. """
        return len(self._attributes)

    # -----------------------------------------------------------------------
    # HTML management: HTML generator
    # -----------------------------------------------------------------------

    def serialize(self, nbs: int = 4) -> str:
        """Serialize the node into HTML.

        :param nbs: (int) Number of spaces for the indentation
        :return: (str)

        """
        indent = " "*nbs
        html = indent + "<" + self.__tag
        for key in self._attributes:
            html += " "
            html += key
            value = self._attributes[key]
            if value is not None:
                html += '="'
                html += value
                html += '"'
        html += " />\n"

        return html

# ---------------------------------------------------------------------------


class HTMLNode(EmptyNode):
    """A node for HTML elements.

    This node can't check the integrity of the tree: it knows only both its
    direct parent and children but not all its predecessors nor all its
    successors. And no recursive search is implemented.

    This class can deal with elements like for example:

        - &lt;tag/&gt;
        - &lt;tag k=v /&gt;
        - &lt;tag k1=v1 k2=v2 k3/&gt;
        - &lt;tag&gt; value [children]* &lt;/tag&gt;
        - &lt;tag k=v&gt; value &lt;/tag&gt;
        - &lt;tag k1=v1 k2=v2 k3&gt; value &lt;/tag&gt;
        - ...

    This class can't have children inside its value like for example:

        - &lt;tag&gt; value_part1 &lt;b&gt; text_bold &lt;/b&gt; value_part2 &lt;/tag&gt;

    To work around this limitation, let value be the whole content of the
    tag. In the example, value is "value_part1 <b> text_bold </b> value_part2"
    and the tag has no <b> child.

    """

    def __init__(self, parent, identifier, tag, attributes=dict(), value=None):
        """Create a node."""
        # Identifier(s) of the children' node(s) :
        self._children = list()

        super(HTMLNode, self).__init__(parent, identifier, tag, attributes)

        # The node data
        self._value = value

    # -----------------------------------------------------------------------
    # Tree management: getters and setters
    # -----------------------------------------------------------------------

    def get_nidx_child(self, child_idx):
        """Return a direct child of the node or None.

        :param child_idx: (int) Child index
        :return: (HTMLNode)
        :raises: IndexError

        """
        child_idx = int(child_idx)
        if 0 <= child_idx < len(self._children):
            return self._children[child_idx]
        raise IndexError

    # -----------------------------------------------------------------------

    def get_child(self, child_id):
        """Return a direct child of the node or None.

        :param child_id: (str) Child identifier
        :return: (HTMLNode | None)

        """
        for child in self._children:
            if child.identifier == child_id:
                return child
        return None

    # -----------------------------------------------------------------------

    def children_size(self) -> int:
        """Return the number of direct children.

        :return: (int)

        """
        return len(self._children)

    # -----------------------------------------------------------------------

    def has_child(self, node_id: str) -> bool:
        """Return True if the given node is a direct child.

        :param node_id: (str) Identifier of the node
        :return: (bool) True if given identifier is a direct child.

        """
        return node_id in [child.identifier for child in self._children]

    # -----------------------------------------------------------------------

    def append_child(self, node) -> None:
        """Append a child node.

        :param node: (Node)
        :raises: NodeKeyError:
        :raises: TypeError:
        :raises: Exception:

        """
        if node.identifier == self._parent or node.identifier == self.identifier:
            raise NodeKeyError(self.identifier, node.identifier)

        if isinstance(node, BaseNode) is False:
            raise TypeError("Node expected.")

        if node.get_parent() != self.identifier:
            raise NodeParentIdentifierError(self.identifier, node.get_parent())

        if node not in self._children:
            self._children.append(node)

    # -----------------------------------------------------------------------

    def insert_child(self, pos, node):
        """Insert a child node at the given index.

        :param pos: (int) Index position
        :param node: (Node)
        :raises: NodeKeyError:
        :raises: TypeError:
        :raises: Exception:

        """
        if node.identifier == self._parent or node.identifier == self.identifier:
            raise NodeKeyError(self.identifier, node.identifier)

        if isinstance(node, EmptyNode) is False:
            raise TypeError("Node expected.")

        if node.get_parent() != self.identifier:
            raise NodeParentIdentifierError(self.identifier, node.get_parent())

        if node not in self._children:
            self._children.insert(pos, node)

    # -----------------------------------------------------------------------

    def remove_child(self, node_id):
        """Remove a child node.

        :param node_id: (str)

        """
        node = None
        for n in self._children:
            if n.identifier == node_id:
                node = n
                break
        if node is not None:
            self._children.remove(node)

    # -----------------------------------------------------------------------

    def pop_child(self, pos):
        """Remove a child node from its index.

        :param pos: (int)

        """
        self._children.pop(pos)

    # -----------------------------------------------------------------------

    def clear_children(self):
        """Remove all children of the node."""
        self._children.clear()

    # -----------------------------------------------------------------------
    # HTML management: getters and setters
    # -----------------------------------------------------------------------

    def is_leaf(self):
        """Return true if node has no children."""
        return len(self._children) == 0

    # -----------------------------------------------------------------------

    def get_value(self):
        """Return the tag content value."""
        return self._value

    # -----------------------------------------------------------------------

    def set_value(self, value):
        """Set or re-set the tag content value."""
        self._value = str(value)

    # -----------------------------------------------------------------------
    # HTML management: HTML generator
    # -----------------------------------------------------------------------

    def serialize(self, nbs: int = 4) -> str:
        """Serialize the node into HTML.

        :param nbs: (int) Number of spaces for the indentation
        :return: (str)

        """
        indent = " "*nbs
        # Element begin tag
        html = indent + "<" + self.tag
        for key in self._attributes:
            html += " "
            html += key
            if self._attributes[key] is not None:
                html += '="'
                html += self._attributes[key]
                html += '"'
        html += ">"
        # Element value or children nodes
        if self._value is not None or len(self._children) > 0:
            html += "\n"
            if self._value is not None:
                html += self.__serialize_value(indent, nbs)
            for node_id in self._children:
                html += node_id.serialize(nbs+4)
            html += indent
        # Element end tag
        html += "</" + self.tag + ">\n"
        return html

    # -----------------------------------------------------------------------

    def __serialize_value(self, indent, nbs):
        html = ""
        try:
            # For some tags, the space char is meaningful. textarea is one of them. others???
            if self.tag != "textarea":
                html += indent + " " * nbs
            html += self._value
            html += "\n"
        except TypeError as e:
            logging.error(str(e))
            if logging.getLogger().getEffectiveLevel() == 0:
                traceback.print_exc()
            html += indent + "    'Unexpected data type'"
            html += "\n"
        return html

    # -----------------------------------------------------------------------
    #
    # -----------------------------------------------------------------------

    def __repr__(self):
        name = self.__class__.__name__
        kwargs = [
            "tag={0}".format(self.tag),
            "identifier={0}".format(self.identifier),
            "attributes={0}".format(self._attributes),
        ]
        return "%s(%s)" % (name, ", ".join(kwargs))

# ---------------------------------------------------------------------------


class HTMLHeadNode(HTMLNode):
    """Convenient class to represent the head node of an HTML tree.

    """

    # List of accepted child tags in an HTML header.
    HEADER_TAGS = ("title", "meta", "link", "style", "script")

    # -----------------------------------------------------------------------

    def __init__(self, parent):
        """Create the head node."""
        super(HTMLHeadNode, self).__init__(parent, "head", "head")

    # -----------------------------------------------------------------------
    # Invalidate some of the Node methods.
    # -----------------------------------------------------------------------

    def append_child(self, node) -> None:
        """Append a child node.

        :param node: (Node)

        """
        if node.tag not in HTMLHeadNode.HEADER_TAGS:
            raise NodeChildTagError(node.tag)
        HTMLNode.append_child(self, node)

    # -----------------------------------------------------------------------

    def insert_child(self, pos, node) -> None:
        """Insert a child node at the given index.

        :param pos: (int) Index position
        :param node: (Node)

        """
        if node.get_tag() not in HTMLHeadNode.HEADER_TAGS:
            raise NodeChildTagError(node.tag)
        HTMLNode.insert_child(self, pos, node)

    # -----------------------------------------------------------------------
    # Add convenient methods to manage the head
    # -----------------------------------------------------------------------

    def title(self, title) -> None:
        """Set the title to the header.

        :param title: (str) The page title (expected short!)

        """
        for child in self._children:
            if child.identifier == "title":
                child.set_value(title)
                break

    # -----------------------------------------------------------------------

    def meta(self, metadict) -> None:
        """Append a new meta tag to the header.

        :param metadict: (dict)

        """
        if isinstance(metadict, dict) is False:
            raise TypeError("Expected a dict.")

        child_node = EmptyNode(self.identifier, None, "meta", attributes=metadict)
        self._children.append(child_node)

    # -----------------------------------------------------------------------

    def link(self, rel, href, link_type=None) -> None:
        """Add a link tag to the header.

        :param rel: (str)
        :param href: (str) Path and/or name of the link reference
        :param link_type: (str) Mimetype of the link file

        """
        d = dict()
        d["rel"] = rel
        d["href"] = href
        if link_type is not None:
            d["type"] = link_type
        child_node = EmptyNode(self.identifier, None, "link", attributes=d)
        self._children.append(child_node)

    # -----------------------------------------------------------------------

    def script(self, src, script_type) -> None:
        """Add a meta tag to the header.

        :param src: (str) Script source file
        :param script_type: (str) Script type

        """
        d = dict()
        d["src"] = src
        d["type"] = script_type

        child_node = HTMLNode(self.identifier, None, "script", attributes=d)
        self._children.append(child_node)

    # -----------------------------------------------------------------------

    def css(self, script_content) -> None:
        """Append css style content.

        :param script_content: (str) CSS content

        """
        child_node = HTMLNode(self.identifier, None, "style", value=str(script_content))
        self._children.append(child_node)


class HTMLHeaderNode(HTMLNode):
    """Convenient class to represent the header node of an HTML tree.

    """
    def __init__(self, parent):
        """Create the main node.

        """
        super(HTMLHeaderNode, self).__init__(parent, "body_header", "header")


class HTMLNavNode(HTMLNode):
    """Convenient class to represent the nav node of an HTML tree.

    """
    def __init__(self, parent):
        """Create the nav node."""
        super(HTMLNavNode, self).__init__(parent, "body_nav", "nav")


class HTMLMainNode(HTMLNode):
    """Convenient class to represent the main node of an HTML tree.

    """
    def __init__(self, parent):
        """Create the main node."""
        super(HTMLMainNode, self).__init__(parent, "body_main", "main")


class HTMLFooterNode(HTMLNode):
    """Convenient class to represent the footer node of an HTML tree.

    """

    def __init__(self, parent):
        """Create the footer node."""
        super(HTMLFooterNode, self).__init__(parent, "body_footer", "footer")


class HTMLScriptNode(HTMLNode):
    """Convenient class to represent the scripts node of an HTML tree."""

    def __init__(self, parent):
        """Create the script node."""
        super(HTMLScriptNode, self).__init__(parent, "body_script", "script")