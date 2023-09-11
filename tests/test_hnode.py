"""
:filename: test_hnode.py
:author:   Brigitte Bigi
:contact:  develop@sppas.org
:summary: Tests for HTML nodes in package htmlmaker.

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

import unittest

from whakerpy.htmlmaker.hexc import NodeTypeError
from whakerpy.htmlmaker.hexc import NodeInvalidIdentifierError
from whakerpy.htmlmaker.hexc import NodeTagError
from whakerpy.htmlmaker.hexc import NodeChildTagError
from whakerpy.htmlmaker.hexc import NodeKeyError

from whakerpy.htmlmaker.hnode import BaseNode
from whakerpy.htmlmaker.hnode import EmptyNode
from whakerpy.htmlmaker.hnode import HTMLNode
from whakerpy.htmlmaker.hnode import HTMLHeadNode

# ---------------------------------------------------------------------------


class TestBaseNode(unittest.TestCase):

    def test_init_successfully(self):
        # Default identifier and default parent
        node = BaseNode()
        self.assertIsNotNone(node.identifier)
        self.assertIsInstance(node, BaseNode)
        self.assertEqual(36, len(node.identifier))
        self.assertTrue(node.is_leaf())
        self.assertTrue(node.is_root())
        self.assertFalse(node.has_child("lol"))
        self.assertIsNone(node.get_parent())

        # Custom identifier and default parent
        node = BaseNode(parent=None, identifier="toto")
        self.assertEqual("toto", node.identifier)

        # Custom identifier and custom parent
        node = BaseNode(parent="dad", identifier="toto")
        self.assertEqual("dad", node.get_parent())
        self.assertEqual("toto", node.identifier)

        # Custom parent and default identifier
        node = BaseNode(parent="dad")
        self.assertEqual("dad", node.get_parent())
        self.assertEqual(36, len(node.identifier))

    # -----------------------------------------------------------------------

    def test_init_errors(self):
        with self.assertRaises(NodeInvalidIdentifierError):
            BaseNode(parent=None, identifier="")

        with self.assertRaises(NodeInvalidIdentifierError):
            BaseNode(parent=None, identifier="  ")

        with self.assertRaises(NodeInvalidIdentifierError):
            BaseNode(parent=None, identifier="my id")

        with self.assertRaises(NodeInvalidIdentifierError):
            BaseNode(parent=None, identifier=" my_id")

        with self.assertRaises(NodeKeyError):
            BaseNode(parent="dad", identifier="dad")

    # -----------------------------------------------------------------------

    def test_validate_identifier(self):
        # Check identifier validation
        with self.assertRaises(NodeInvalidIdentifierError):
            # Empty identifier should raise an exception
            BaseNode.validate_identifier("")

        with self.assertRaises(NodeInvalidIdentifierError):
            # Identifier with space should raise an exception
            BaseNode.validate_identifier(" ")

        # Valid identifier should not raise an exception
        self.assertEqual(BaseNode.validate_identifier("valid_id"), "valid_id")

    # -----------------------------------------------------------------------

    def test_is_leaf(self):
        node1 = BaseNode()
        node2 = BaseNode(identifier="test_id")
        node3 = BaseNode(parent="parent_id", identifier="test_id")
        # Check if node is a leaf (should always be true for BaseNode)
        self.assertTrue(node1.is_leaf())
        self.assertTrue(node2.is_leaf())
        self.assertTrue(node3.is_leaf())

    # -----------------------------------------------------------------------

    def test_is_root(self):
        node1 = BaseNode()
        node2 = BaseNode(identifier="test_id")
        node3 = BaseNode(parent="parent_id", identifier="test_id")
        # Check if node is a root (should be true only for node1)
        self.assertTrue(node1.is_root())
        self.assertTrue(node2.is_root())
        self.assertFalse(node3.is_root())

    # -----------------------------------------------------------------------

    def test_get_set_parent(self):
        node1 = BaseNode()
        node3 = BaseNode(parent="parent_id", identifier="test_id")
        # Check getter and setter for parent
        self.assertIsNone(node1.get_parent())
        self.assertEqual(node3.get_parent(), "parent_id")

        node1.set_parent("new_parent_id")
        self.assertEqual(node1.get_parent(), "new_parent_id")

        # Check that the setter raises an exception when the
        # parent's identifier is the same as the node's identifier
        with self.assertRaises(NodeKeyError):
            node1.set_parent(node1.identifier)

    # -----------------------------------------------------------------------

    def test_has_child(self):
        node1 = BaseNode()
        node2 = BaseNode(identifier="test_id")
        node3 = BaseNode(parent="parent_id", identifier="test_id")
        # Check that has_child returns True for node3 (as it has a parent)
        self.assertFalse(node3.has_child(node1))
        self.assertFalse(node1.has_child(node2))
        self.assertFalse(node2.has_child(node3))

# ---------------------------------------------------------------------------


class TestEmptyNode(unittest.TestCase):

    def test_init_successfully(self):
        node = EmptyNode(None, None, "br")
        self.assertEqual(36, len(node.identifier))
        self.assertTrue(node.is_leaf())
        self.assertTrue(node.is_root())
        self.assertFalse(node.has_child("lol"))
        self.assertIsNone(node.get_parent())
        self.assertEqual(0, node.nb_attributes())

        node = EmptyNode(None, None, "img", {"src": "path/file"})
        self.assertEqual(1, node.nb_attributes())

    # -----------------------------------------------------------------------

    def test_init_errors(self):
        with self.assertRaises(NodeTagError):
            EmptyNode(None, None, "invented")

        with self.assertRaises(TypeError):
            EmptyNode(None, None, "img", "src")

        with self.assertRaises(ValueError):
            EmptyNode(None, None, "img", {"key": "value"})

    # -----------------------------------------------------------------------

    def test_tag(self):
        # Check if tag property returns the correct tag
        empty_node = EmptyNode("parent_id", "test_id", "a", {"href": "https://example.com", "target": "_blank"})
        self.assertEqual(empty_node.tag, "a")

    # -----------------------------------------------------------------------

    def test_add_attribute(self):
        empty_node = EmptyNode("parent_id", "test_id", "a", {"href": "https://example.com", "target": "_blank"})
        # Check if add_attribute method adds the attribute correctly
        empty_node.add_attribute("rel", "nofollow")
        self.assertTrue(empty_node.has_attribute("rel"))
        self.assertEqual(empty_node.get_attribute_value("rel"), "nofollow")

    def test_get_set_attribute(self):
        empty_node = EmptyNode("parent_id", "test_id", "a", {"href": "https://example.com", "target": "_blank"})
        # Check if set_attribute method sets the attribute correctly and replaces existing one
        empty_node.set_attribute("href", "https://example.org")
        self.assertEqual(empty_node.get_attribute_value("href"), "https://example.org")
        # Check if get_attribute_keys method returns the list of attribute keys
        self.assertEqual(empty_node.get_attribute_keys(), ["href", "target"])

    def test_has_attribute(self):
        empty_node = EmptyNode("parent_id", "test_id", "a", {"href": "https://example.com", "target": "_blank"})
        # Check if has_attribute method returns True for existing attribute, False otherwise
        self.assertTrue(empty_node.has_attribute("href"))
        self.assertFalse(empty_node.has_attribute("class"))

    def test_remove_attribute(self):
        empty_node = EmptyNode("parent_id", "test_id", "a", {"href": "https://example.com", "target": "_blank"})
        # Check if remove_attribute method removes the attribute correctly
        empty_node.remove_attribute("href")
        self.assertFalse(empty_node.has_attribute("href"))

    def test_remove_attribute_value(self):
        empty_node = EmptyNode("parent_id", "test_id", "a", {"href": "https://example.com", "target": "_blank"})
        # Check if remove_attribute_value method removes the value from the attribute correctly
        empty_node.add_attribute("class", "active selected")
        empty_node.remove_attribute_value("class", "active")
        self.assertTrue(empty_node.has_attribute("class"))
        self.assertEqual(empty_node.get_attribute_value("class"), "selected")

    def test_nb_attributes(self):
        empty_node = EmptyNode("parent_id", "test_id", "a", {"href": "https://example.com", "target": "_blank"})
        # Check if nb_attributes method returns the correct number of attributes
        self.assertEqual(empty_node.nb_attributes(), 2)

    def test_browse_attributes(self):
        node = EmptyNode(None, None, "img", {"src": "path/file"})
        self.assertEqual(1, len(node.get_attribute_keys()))
        node.add_attribute("alt", "")
        self.assertEqual(2, len(node.get_attribute_keys()))

    # -----------------------------------------------------------------------

    def test_serialize(self):
        empty_node = EmptyNode("parent_id", "test_id", "a", {"href": "https://example.com", "target": "_blank"})
        # Check if serialize method generates the correct HTML string
        expected_html = '    <a href="https://example.com" target="_blank" />\n'
        self.assertEqual(empty_node.serialize(), expected_html)

# ---------------------------------------------------------------------------


class TestNode(unittest.TestCase):

    def test_init_successfully(self):
        node = HTMLNode(parent=None, identifier="id01", tag="p")

    def test_init_error(self):
        with self.assertRaises(NodeTagError):
            HTMLNode(parent=None, identifier="id01", tag="tag")

    def test_child(self):
        # Append a child
        # Insert a child
        # Pop a child
        # Remove a child
        pass

    def test_attribute(self):
        node = HTMLNode(parent=None, identifier="id01", tag="p")
        self.assertFalse(node.is_attribute("class"))
        self.assertIsNone(node.get_attribute_value("class"))

        node.add_attribute("class", None)
        self.assertTrue(node.is_attribute("class"))
        self.assertIsNone(node.get_attribute_value("class"))

        node.set_attribute("class", "toto")
        self.assertTrue(node.is_attribute("class"))
        self.assertEqual(node.get_attribute_value("class"), "toto")

        node.add_attribute("class", "titi")
        self.assertEqual(node.get_attribute_value("class"), "toto titi")

        node.set_attribute("class", "tata")
        self.assertEqual(node.get_attribute_value("class"), "tata")

    def test_value(self):
        node = HTMLNode(parent=None, identifier="id01", tag="p")
        self.assertIsNone(node.get_value())

        node.set_value("text")
        self.assertEqual("text", node.get_value())

        node.set_value(3)
        self.assertEqual("3", node.get_value())


# ---------------------------------------------------------------------------


class TestHeadNode(unittest.TestCase):

    def test_init(self):
        node = HTMLHeadNode(parent=None)
        self.assertTrue("head", node.identifier)

    def test_error(self):
        node = HTMLHeadNode(parent=None)
        with self.assertRaises(NodeChildTagError):
            node.append_child(HTMLNode(parent=node.identifier, identifier=None, tag="p"))

    def test_title(self):
        pass

    def test_meta(self):
        pass

    def test_link(self):
        pass

    def test_script(self):
        pass

    def test_css(self):
        pass
