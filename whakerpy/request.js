/**
:filename: sppas.ui.swapp.static.js.request.js
:author: Florian Lopitaux
:contact: develop@sppas.org
:summary: A class to simplify the sending of request (on the Javascript side) to the python server of the localhost client and gets data in return.

.. _This file is part of SPPAS: https://sppas.org/
..
    -------------------------------------------------------------------------

     ___   __    __    __    ___
    /     |  \  |  \  |  \  /              the automatic
    \__   |__/  |__/  |___| \__             annotation and
       \  |     |     |   |    \             analysis
    ___/  |     |     |   | ___/              of speech

    Copyright (C) 2011-2023  Brigitte Bigi
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

A class to simplify the sending of request (on the Javascript side) to the
python server of the localhost client and gets data in return.

Careful, this class communicate with the python server with HTTP request,
so the class are asynchronous methods. If you are uncomfortable with this
paradigm consult the javascript documentation:
https://developer.mozilla.org/fr/docs/Learn/JavaScript/Asynchronous
(only async and await keywords are necessary to understand to used the
asynchronous class methods)

*/

class RequestManager {
    // FIELDS
    // The declaration outside the constructor and the '#' symbol notify a private attribute in Javascript.
    #protocol;
    #port;
    #url;
    #status;


    // CONSTRUCTOR
    /**
     * The constructor of the RequestManager class.
     * Initialize private member attributes.
     */
    constructor() {
        this.#protocol = window.location.protocol;
        this.#port = window.location.port;
        this.#url = this.#protocol + "//" + window.location.hostname + ":" + this.#port + "/";
        this.#status = null;
    }


    // GETTERS
    /**
     * Get the protocol of the connexion of the client (In the SPPAS web application case the protocol is 'http').
     *
     * @returns {string} The protocol used.
     */
    get protocol() {
        return this.#protocol;
    }

    /**
     * Get the port of the client and server address.
     *
     * @returns {string} - The port used.
     */
    get port() {
        return this.#port;
    }

    /**
     * Get the url of the client and server address.
     *
     * Format: {protocol}://{hostname}:{port}/
     * Example: http://localhost:8080/
     *
     * @returns {string} The url of the localhost address.
     */
    get requestUrl() {
        return this.#url;
    }

    get request_url() {
        return this.#url;
    }

    /**
     * Get the status of the last response of the server.
     *
     * @returns {int} The code of the response.
     */
    get status() {
        return this.#status;
    }

    // METHODS
    /**
     * This method is used to send a GET HTTP request to the python server.
     *
     * @param uri {string} - The parameters (after the url) of the GET request.
     * @param is_json_response {boolean} - False by default.
     *                                     Boolean value to know if the response is a json object to parse.
     *
     * @returns {Promise<*>} - The server data response in the json format.
     */
    async send_get_request(uri, is_json_response = false) {
        let request_response_data = null;

        // send request to the server
        await fetch(this.request_url + uri)
            // then gets content of the gateway file to gets the server data
            .then(async response =>  {
                this.#status = response.status

                if (is_json_response) {
                    request_response_data = await response.json();
                } else {
                    request_response_data = await response.text();
                }
            });

        return request_response_data;
    }


    /**
     * This method is used to send a POST HTTP request to the python server.
     * The content of the posted data can be in JSON format or "text" format (see 'httpd/handler.py' documentation
     * to the syntax of "text" format)
     *
     * @param post_parameters {Object|string} - The posted data to send to the server.
     *                                          Object (dictionary) if it's JSON data or string to "text" data.
     * @param is_json_post_data {boolean} - False by default
     *                                      Boolean value to know if the data to send are in JSON format.
     *
     * @returns {Promise<*>} - The server data response stocked in the gateway file.
     *                         Or null if the 'returnKey' parameter doesn't give.
     */
    async send_post_request(post_parameters, is_json_post_data = false) {
        let request_response_data = null;

        // build request header and body depending on parameter passed to the method
        const request_body = (is_json_post_data) ? JSON.stringify(post_parameters) : post_parameters;
        let request_header = {
            'Content-Length': JSON.stringify(request_body).length.toString(),
            'Accept': "application/json"
        };

        if (is_json_post_data) {
            request_header['Content-Type'] = "application/json; charset=utf-8";
        }

        // send request to the server
        await fetch(this.request_url, {
            method: "POST",
            headers: request_header,
            body: request_body
        })
            // then gets content of the gateway file to gets the server data
            .then(async response =>  {
                this.#status = response.status
                request_response_data = await response.json();
            });

        return request_response_data;
    }
}
