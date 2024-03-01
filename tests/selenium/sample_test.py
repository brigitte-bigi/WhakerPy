"""
:filename: tests.sample_test.py
:author:   Florian LOPITAUX
:contact:  contact@sppas.org
:summary: Tests for the sample webapp of the whakerpy library.

    -------------------------------------------------------------------------

    Copyright (C) 2011-2023 Brigitte Bigi
    Laboratoire Parole et Langage, Aix-en-Provence, France

    Use of this software is governed by the GNU Public License, version 3.

    Whakerpy is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Whakerpy is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Whakerpy. If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------

"""

import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By

# ---------------------------------------------------------------------------

# put the right local port of the webapp here
LOCAL_PORT = "8989"

# put the navigator name that you want the tests use
# VALUES = ["FIREFOX", "CHROME", "EDGE", "SAFARI"]
# Safari is only possible in a macOS system, possible that edge doesn't work on macOS
NAVIGATOR_USED = "FIREFOX"

# ---------------------------------------------------------------------------


class SampleTest(unittest.TestCase):
    """Class to test the sample webapp with selenium tools.
    The sample webapp needs to be start aside and the port register in the global variable 'LOCAL_PORT'.

    """

    def setUp(self) -> None:
        """Method called before each unit test to initialize the webdriver.
        The method needs to be called 'setUp' for the program recognized it.

        """
        self.app_url = f"http://localhost:{LOCAL_PORT}/"

        match NAVIGATOR_USED:
            case "FIREFOX":
                self.driver = webdriver.Firefox()
            case "CHROME":
                self.driver = webdriver.Chrome()
            case "EDGE":
                self.driver = webdriver.Edge()
            case "SAFARI":
                self.driver = webdriver.Safari()
            case _:  # default case
                print(f"Unknown navigator set : {NAVIGATOR_USED}, start Firefox by default.")
                self.driver = webdriver.Firefox()

        self.driver.get(self.app_url)

    def tearDown(self) -> None:
        """Method called after each unit test to close the webdriver.
        The method needs to be called 'tearDown' for the program recognized it.

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
