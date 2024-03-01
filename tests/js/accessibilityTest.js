/**
:filename: tests.js.accessibilityTest.js
:author: Florian Lopitaux
:contact: contact@sppas.org
:summary: Test file of the accessibility functions.

.. _This file is part of WhakerPy: https://sourceforge.net/projects/whakerpy/ ,
.. on 2024-03-01.
    -------------------------------------------------------------------------

    Copyright (C) 2024 Brigitte Bigi
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

*/

// instantiate unit tests class
let accessibility_tests = new UnitTest();


// body load classes test
accessibility_tests.add_test(() => {
    // wait page finished to load to get the body element
    OnLoadManager.addLoadFunction(() => {
        const url = new URLSearchParams(document.location.search);
        let body_classes = Array.from(document.body.classList);

        // test color scheme
        if (url.has("color_scheme")) {
            UnitTest.assert_array_contains(url.get("color_scheme"), body_classes, "color_parameter_test");

        } else {
            UnitTest.assert_array_contains("light", body_classes, "default_color_test");
            UnitTest.assert_array_not_contains("dark", body_classes, "default_color_not_dark_test");
        }

        // test contrast scheme
        if (url.has("contrast")) {
            const contrast_parameter_value = url.get("contrast");

            if (contrast_parameter_value === "true") {
                UnitTest.assert_array_contains("sp-contrast", body_classes, "parameter_contrast_true_test");
            } else {
                UnitTest.assert_array_not_contains("sp-contrast", body_classes, "parameter_contrast_false_test");
            }
        } else {
            UnitTest.assert_array_not_contains("sp-contrast", body_classes, "default_contrast_test");
        }
    });
});

// -----------------------------------------------------------------------

// color_scheme switch test
accessibility_tests.add_test(() => {
    // wait page finished to load to get the body element
    OnLoadManager.addLoadFunction(() => {
        let body_classes = Array.from(document.body.classList);
        let old_color_scheme;

        if (body_classes.includes("light")) {
            old_color_scheme = "light";
        } else {
            old_color_scheme = "dark";
        }

        // switch color_scheme
        color_scheme_switch();

        UnitTest.assert_array_not_contains(old_color_scheme, Array.from(document.body.classList), "color_switch_test_1");
        color_scheme_switch();
        UnitTest.assert_array_contains(old_color_scheme, Array.from(document.body.classList), "color_switch_test_2");
    });
});

// -----------------------------------------------------------------------

// contrast_scheme switch test
accessibility_tests.add_test(() => {
    // wait page finished to load to get the body element
    OnLoadManager.addLoadFunction(() => {
        let body_classes = Array.from(document.body.classList);
        let old_contrast_scheme = "";

        if (body_classes.includes("sp-contrast")) {
            old_contrast_scheme = "sp-contrast";
        }

        // switch color_scheme
        contrast_scheme_switch();

        if (old_contrast_scheme === "") {
            UnitTest.assert_array_contains("sp-contrast", Array.from(document.body.classList), "contrast_switch_test_1");
        } else {
            UnitTest.assert_array_not_contains("sp-contrast", Array.from(document.body.classList), "contrast_switch_test_1");
        }

        contrast_scheme_switch();

        if (old_contrast_scheme === "") {
            UnitTest.assert_array_not_contains("sp-contrast", Array.from(document.body.classList), "contrast_switch_test_2");
        } else {
            UnitTest.assert_array_contains("sp-contrast", Array.from(document.body.classList), "contrast_switch_test_2");
        }
    });
});


// launch all unit tests added
accessibility_tests.launch_unit_test();
