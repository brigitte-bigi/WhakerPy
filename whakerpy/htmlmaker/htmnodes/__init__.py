"""
:filename: whakerpy.htmlmaker.htmnodes.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Classes to generate various HTML elements.

.. _This file was initially part of SPPAS: https://sppas.org/
.. _This file is now part of WhakerPy: https://whakerpy.sourceforge.io
..
    -------------------------------------------------------------------------

    Copyright (C) 2023-2026 Brigitte Bigi, CNRS
    Laboratoire Parole et Langage, Aix-en-Provence, France

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------

"""

from .htmnode import TagNode
from .htmnode import HTMLNode
from .htmelts import HTMLRadioBox
from .htmelts import HTMLButtonNode

__all__ = (
    "TagNode",
    "HTMLNode",
    "HTMLRadioBox",
    "HTMLButtonNode"
)
