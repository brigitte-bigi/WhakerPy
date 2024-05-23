"""
:filename: tests.sample_test.py
:author: Florian LOPITAUX
:contact: contact@sppas.org
:summary: Tests for the sample webapp of the whakerpy library.

.. _This file is part of WhakerPy: https://whakerpy.sourceforge.io
..
    -------------------------------------------------------------------------

    Copyright (C) 2023-2024 Brigitte Bigi
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

import sys
import time
import unittest
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By

# ---------------------------------------------------------------------------

LOCAL_PORT = 8080
NAVIGATOR = "FIREFOX"

# ---------------------------------------------------------------------------


class SampleTest(unittest.TestCase):
    """Class to test the sample webapp with selenium tools.
    The sample webapp needs to be start aside and the port register in the global variable 'LOCAL_PORT'.

    """

    def setUp(self) -> None:
        """Method called before each unit test to redirect the webdriver to the home page.
        The method needs to be called 'setUp' for the program recognized it.

        """
        self.app_url = f"http://localhost:{LOCAL_PORT}/"

        if NAVIGATOR == "FIREFOX":
            self.driver = webdriver.Firefox()
        elif NAVIGATOR == "CHROME":
            self.driver = webdriver.Chrome()
        elif NAVIGATOR == "EDGE":
            self.driver = webdriver.Edge()
        elif NAVIGATOR == "SAFARI":
            self.driver = webdriver.Safari()
        else:
            print(f"Unknown navigator set : {NAVIGATOR}, start Firefox by default.")
            self.driver = webdriver.Firefox()

        self.driver.get(self.app_url)

    def tearDown(self) -> None:
        """Method called after all the unit test to close the webdriver.
        The method needs to be called 'tearDownClass' for the program recognized it.

        """
        self.driver.close()

    # ---------------------------------------------------------------------------

    def test_sample_webapp_launch(self) -> None:
        html_element = self.driver.find_element(By.TAG_NAME, "html")
        self.assertEqual(html_element.get_attribute("id"), "whakerpy")

    # ---------------------------------------------------------------------------

    def test_button(self) -> None:
        # get the button element and its text before change with the click
        button_element = self.driver.find_element(By.ID, "update_btn_text")
        button_text = button_element.text

        # click on button to change its text
        button_element.click()

        # re-find button element because the page refreshed after the button click
        button_element = self.driver.find_element(By.ID, "update_btn_text")

        self.assertNotEqual(button_text, button_element.text)

    # ---------------------------------------------------------------------------

    # sometimes (rarely) this test doesn't pass because the new random color is the same that the precedent
    def test_color_text_change(self) -> None:
        colored_text = self.driver.find_element(By.TAG_NAME, "h2")
        color = colored_text.value_of_css_property("color")

        # wait 4 seconds that the color change
        time.sleep(4)

        self.assertNotEqual(color, colored_text.value_of_css_property("color"))

    # ---------------------------------------------------------------------------

    def test_nav_links(self) -> None:
        # test over.html page
        other_page_link = self.driver.find_element(By.XPATH, '//a[@href="other.html"]')
        other_page_link.click()

        # check if the page change
        self.assertEqual(self.driver.current_url, self.app_url + "other.html")

        # check if the page content changes
        page_content = self.driver.find_element(By.TAG_NAME, "h2")
        self.assertEqual(page_content.text, "Other content here")

        # test any.html page
        any_page_link = self.driver.find_element(By.XPATH, '//a[@href="any.html"]')
        any_page_link.click()

        self.assertEqual(self.driver.current_url, self.app_url + "any.html")

        page_content = self.driver.find_element(By.TAG_NAME, "h2")
        self.assertEqual(page_content.text, "Any content here")


# ---------------------------------------------------------------------------
# use CLI to run this file, example : python ./sample_test.py 8080 [--browser FIREFOX]
# you have to start the webapp aside and launch this program with the local port used by the webapp
# requires "test" optional dependencies to run this file, following the README.md

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="Sample unit test", description="Run the unit test of the sample webapp")

    parser.add_argument("port", type=int, help="The local port where the webapp run.")
    parser.add_argument("-b", "--browser", type=str, dest="browser", choices=["FIREFOX", "CHROME", "EDGE", "SAFARI"],
                        help="The navigator used to do the unit test, by default is Firefox.")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    LOCAL_PORT = args.port
    if args.browser is not None:
        NAVIGATOR = args.browser

    # reset arguments for the unittest main, if we don't do that the unittest take arguments and try to process them
    sys.argv[1:] = []
    unittest.main()
