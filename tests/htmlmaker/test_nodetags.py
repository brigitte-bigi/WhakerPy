"""
:filename: test_nodetags.py
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

from whakerpy.htmlmaker.hexc import NodeAttributeError
from whakerpy.htmlmaker.hnodetags import HTMLInputText
from whakerpy.htmlmaker.hnodetags import HTMLRadioBox
from whakerpy.htmlmaker.hnodetags import HTMLButtonNode
from whakerpy.htmlmaker.hleaf import HTMLHr
from whakerpy.htmlmaker.hleaf import HTMLImage
from whakerpy.htmlmaker.hleaf import HTMLComment
from whakerpy.htmlmaker.hleaf import Doctype

# ---------------------------------------------------------------------------


class TestBaseNode(unittest.TestCase):

    def test_doctype(self):
        d = Doctype()
        self.assertEqual('<!DOCTYPE html>\n\n', d.serialize())

    def test_comment(self):
        c = HTMLComment("parent_id", "this is a comment")
        self.assertEqual('\n<!-- -------------------------- this is a comment -------------------------- -->\n\n',
                         c.serialize(nbs=0))

    def test_image(self):
        i = HTMLImage("parent_id", "img_id", src="/path/to/image.png")
        self.assertTrue(i.has_attribute("src"))
        self.assertTrue(i.has_attribute("alt"))

    def test_hr(self):
        hr = HTMLHr("parent_id")
        hr.set_attribute("class", "nidehr")
        self.assertTrue(hr.has_attribute("class"))
        with self.assertRaises(NodeAttributeError):
            hr.set_attribute("required", None)

    # -----------------------------------------------------------------------

    def test_init_tags(self):
        node = HTMLInputText(parent="parent_id", identifier="input0")
        self.assertTrue(node.has_attribute("type"))
        self.assertEqual("text", node.get_attribute_value("type"))
        self.assertEqual("input0", node.get_attribute_value("id"))
        self.assertEqual("input0", node.get_attribute_value("name"))

        node = HTMLRadioBox(parent="parent_id", identifier="radiobox")
        self.assertEqual("POST", node.get_attribute_value("method"))
        self.assertEqual("radiobox", node.get_attribute_value("id"))
        self.assertEqual("radiobox", node.get_attribute_value("name"))

        node1 = HTMLButtonNode(parent="parent_id", identifier="button1")
        self.assertEqual("button", node1.get_attribute_value("type"))
        self.assertEqual("button1", node1.get_attribute_value("id"))
        self.assertEqual("button1", node1.get_attribute_value("name"))

        node2 = HTMLButtonNode(parent="parent_id", identifier="button2", attributes={"type": "submit"})
        self.assertEqual("submit", node2.get_attribute_value("type"))
        self.assertEqual("button2", node2.get_attribute_value("id"))
        self.assertEqual("button2", node2.get_attribute_value("name"))

        node3 = HTMLButtonNode(parent="parent_id", identifier="button3", attributes={"id": "but3"})
        self.assertEqual("button", node3.get_attribute_value("type"))
        self.assertEqual("but3", node3.get_attribute_value("id"))
        self.assertEqual("button3", node3.get_attribute_value("name"))

        node4 = HTMLButtonNode(parent="parent_id", identifier="button4", attributes={"name": "but4"})
        self.assertEqual("button", node4.get_attribute_value("type"))
        self.assertEqual("button4", node4.get_attribute_value("id"))
        self.assertEqual("but4", node4.get_attribute_value("name"))

    # -----------------------------------------------------------------------

    def test_input(self):
        node = HTMLInputText(parent="parent_id", identifier="input0")
        node.set_name("newname")
        self.assertEqual("newname", node.get_attribute_value("name"))

    def test_radiobox(self):
        node = HTMLRadioBox(parent="parent_id", identifier="radiobox")
        node.append_input("nice", "Input value", "Input text", checked=False)
        self.assertEqual(1, node.children_size())

    def test_button(self):
        node = HTMLButtonNode(parent="parent_id", identifier="button")
        node.set_text("button_text", "Click me")
        self.assertEqual(1, node.children_size())
        node.set_icon("/path/to/icon.png")
        self.assertEqual(2, node.children_size())

