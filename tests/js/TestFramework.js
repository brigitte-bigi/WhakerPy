/**
:filename: tests.js.TestFramework.js
:author: Florian Lopitaux
:contact: contact@sppas.org
:summary: UnitTest class to do easily our unit tests for JS code.

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

class UnitTest {
    // FIELDS
    #tests;


    // CONSTRUCTOR
    constructor() {
        this.#tests = [];
    }


    // PUBLIC METHODS
    add_test(func_test) {
        this.#tests.push(func_test);
    }

    launch_unit_test() {
        this.#tests.forEach(async (func) => {
            await func();
        });
    }


    // PUBLIC STATIC METHODS
    static assert_values(value_to_compare, value_expected, assertion_name) {
        if (value_to_compare !== value_expected) {
            this.print_assert_failed(value_to_compare, value_expected, assertion_name);
        } else {
            this.print_assert_success(assertion_name);
        }
    }

    static assert_object(object_to_compare, object_expected, assertion_name) {
        const first_object = JSON.stringify(object_to_compare);
        const second_object = JSON.stringify(object_expected);

        if (first_object !== second_object) {
            this.print_assert_failed(object_to_compare, object_expected, assertion_name);
        } else {
            this.print_assert_success(assertion_name);
        }
    }


    // PRIVATE STATIC METHODS
    static print_assert_failed(value_to_compare, value_expected, assertion_name) {
        console.error("Assertion : " + assertion_name + " failed !"
                + " Value expected : " + value_expected + ", value obtain : " + value_to_compare);
    }

    static print_assert_success(assertion_name) {
        console.info("%cAssertion : " + assertion_name + " success !", 'color: green');
    }
}
