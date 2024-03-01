/**
:filename: tests.js.UnitTest.js
:author: Florian Lopitaux
:contact: florian.lopitaux@gmail.com
:summary: file that contains the UnitTest class.

.. _This file is part of PureJS-UnitTest : https://sourceforge.net/projects/purejs-unittest/
..
    -------------------------------------------------------------------------

    Copyright (C) 2024  Florian LOPITAUX
    13100 Aix-en-Provence, France

    Use of this software is governed by the GNU Public License, version 3.

    PureJS-UnitTest is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PureJS-UnitTest is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PureJS-UnitTest. If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------
*/

class UnitTest {
    // FIELDS
    #tests;


    // CONSTRUCTOR
    constructor() {
        // array which stocks all test function to called
        this.#tests = [];
    }


    // PUBLIC METHODS
    /**
     * Added a new unit test function to launch.
     *
     * @param func_test The test function to add
     */
    add_test(func_test) {
        this.#tests.push(func_test);
    }

    /**
     * Launch all unit tests put in the list.
     * This function serves like a run function.
     */
    launch_unit_test() {
        this.#tests.forEach(async (func) => {
            await func();
        });
    }


    // PUBLIC STATIC METHODS
    /**
     * Assertion between two values if there are equals.
     * Print in the console if the assertion is succeeded (green message) or failed (red message).
     *
     * @param value_to_compare the value to test
     * @param value_expected the value expected by the test
     * @param assertion_name The name of the test, used in the log to know which tests succeed and failed
     */
    static assert_values_equals(value_to_compare, value_expected, assertion_name) {
        if (value_to_compare !== value_expected) {
            this.print_assert_failed(value_to_compare, value_expected, assertion_name);
        } else {
            this.print_assert_success(assertion_name);
        }
    }

    /**
     * Assertion between two values if there aren't equals.
     * Print in the console if the assertion is succeeded (green message) or failed (red message).
     *
     * @param first_value the first value to compare
     * @param second_value the second value to compare
     * @param assertion_name The name of the test, used in the log to know which tests succeed and failed
     */
    static assert_values_not_equals(first_value, second_value, assertion_name) {
        if (first_value === second_value) {
            this.print_assert_failed(first_value, second_value, assertion_name);
        } else {
            this.print_assert_success(assertion_name);
        }
    }

    /**
     * Assertion between two objects if there are equals.
     * Print in the console if the assertion is succeeded (green message) or failed (red message).
     *
     * @param object_to_compare the object to test
     * @param object_expected the object expected by the test
     * @param assertion_name The name of the test, used in the log to know which tests succeed and failed
     */
    static assert_object_equals(object_to_compare, object_expected, assertion_name) {
        const first_object = JSON.stringify(object_to_compare);
        const second_object = JSON.stringify(object_expected);

        if (first_object !== second_object) {
            this.print_assert_failed(object_to_compare, object_expected, assertion_name);
        } else {
            this.print_assert_success(assertion_name);
        }
    }

    /**
     * Assertion between two objects if there aren't equals.
     * Print in the console if the assertion is succeeded (green message) or failed (red message).
     *
     * @param first_object the first object to compare
     * @param second_object the second object to compare
     * @param assertion_name The name of the test, used in the log to know which tests succeed and failed
     */
    static assert_object_not_equals(first_object, second_object, assertion_name) {
        const first_object_stringify = JSON.stringify(first_object);
        const second_object_stringify = JSON.stringify(second_object);

        if (first_object === second_object) {
            this.print_assert_failed(first_object_stringify, second_object_stringify, assertion_name);
        } else {
            this.print_assert_success(assertion_name);
        }
    }


    // PRIVATE STATIC METHODS
    /**
     * Print an assertion failed in the console.
     *
     * @param value_compared the value tested
     * @param value_expected the value expected
     * @param assertion_name the name of the test
     */
    static print_assert_failed(value_compared, value_expected, assertion_name) {
        console.error("Assertion : " + assertion_name + " failed !"
                + " Value expected : " + value_expected + ", value obtain : " + value_compared);
    }

    /**
     * Print an assertion succeed in the console.
     *
     * @param assertion_name the name of the test
     */
    static print_assert_success(assertion_name) {
        console.info("%cAssertion : " + assertion_name + " success !", 'color: green');
    }
}
