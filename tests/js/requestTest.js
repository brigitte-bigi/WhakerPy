/**
:filename: tests.js.requestTest.js
:author: Florian Lopitaux
:contact: contact@sppas.org
:summary: Test file of the RequestManager class.

.. _This file is part of WhakerPy: https://sourceforge.net/projects/whakerpy/ ,
.. on 2024-02-28.
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
let request_manager_tests = new UnitTest();


// Getters methods test
request_manager_tests.add_test(() => {
    const request_manager = new RequestManager();
    const url = new URL(window.location.href);

    UnitTest.assert_values_equals(request_manager.status, null, "status_getter_test");
    UnitTest.assert_values_equals(request_manager.port, url.port, "port_getter_test");
    UnitTest.assert_values_equals(request_manager.protocol, url.protocol, "protocol_getter_test");
    UnitTest.assert_values_equals(request_manager.request_url, url.href, "url_getter_test");
});

// -----------------------------------------------------------------------

// Post request method test
request_manager_tests.add_test(async () => {
    const request_manager = new RequestManager();

    // test unknown event
    request_manager.send_post_request({"event_unknown": 1}, true)
        .then(response => {
            // the server return an empty json because it doesn't understand the event send
            UnitTest.assert_object_equals(response, {}, "json_response_empty_test");
    });
});

// -----------------------------------------------------------------------

// Get request method test
request_manager_tests.add_test(() => {
    const request_manager = new RequestManager();

    // test get request with this html page
    request_manager.send_get_request("")
        .then(response => {
            // check the status of the response is ok
            UnitTest.assert_values_equals(request_manager.status, 200, "correct_status_get_request_test");

            let content_to_cut = response.indexOf("<html");
            let formatted_response = response.substring(content_to_cut).replace(/\s+/g, '');

            let formatted_response_expected = document.documentElement.outerHTML.replace("cz-shortcut-listen=\"true\"", "");
            formatted_response_expected = formatted_response_expected.replace(/\s+/g, '');

            // check if the content response is the same of our page
            UnitTest.assert_values_equals(formatted_response, formatted_response_expected, "content_get_request_test");
        });
});

// -----------------------------------------------------------------------

// Get request method test with wrong file path
request_manager_tests.add_test(() => {
    const request_manager = new RequestManager();

    // test get request with wrong path
    request_manager.send_get_request("/unknown.txt")
        .then(response => {
            UnitTest.assert_values_equals(request_manager.status, 404, "wrong_status_get_request_test");
        });
})


// launch all unit tests added
request_manager_tests.launch_unit_test();
