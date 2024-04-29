/**
:filename: whakerpy.request.js
:author: Florian Lopitaux
:contact: contact@sppas.org
:summary: A class to simplify the sending of request (on the Javascript side) to the python server of the localhost
          client and gets data in return.

.. _This file is part of WhakerPy: https://sourceforge.net/projects/whakerpy/ ,
.. on 2024-02-28.
    -------------------------------------------------------------------------

    Copyright (C) 2011-2024  Brigitte Bigi
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
    #path;
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
        this.#path = window.location.pathname;
        this.#url = this.#protocol + "//" + window.location.hostname + ":" + this.#port + this.#path;
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
     * Get the url path.
     *
     * @returns {string} - The path of the url
     */
    get path() {
        return this.#path;
    }

    /**
     * Get the url of the client and server address.
     *
     * Format: {protocol}://{hostname}:{port}/
     * Example: http://localhost:8080/
     *
     * @returns {string} The url of the localhost address.
     */
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
     *                                     Boolean value to know if the server response is a json object to parse.
     *
     * @returns {Promise<*>} - The server data response.
     */
    async send_get_request(uri, is_json_response = false) {
        const complete_url = this.request_url + uri;
        let request_response_data = null;

        // send request to the server
        await fetch(complete_url)
            // then gets content of the server response
            .then(async response =>  {
                // get the status response and check if there is an error
                this.#status = response.status;

                // get the content of the server response and parse them if it's a json format
                if (is_json_response) {
                    request_response_data = await response.json();
                } else {
                    request_response_data = await response.text();
                }
            })
            // handle error
            .catch(error => {
                this.#status = error.status;
                request_response_data = error;
            });

        return request_response_data;
    }


    /**
     * This method is used to send a POST HTTP request to the python server.
     * The content of the posted data must be in JSON format.
     *
     * @param post_parameters {Object} - Object (dictionary), the posted data to send to the server.
     * @param accept_type {string} - mime type of the server response, json by default.
     *
     * @returns {Promise<*>} - The server data response.
     */
    async send_post_request(post_parameters, accept_type = "application/json") {
        let request_response_data = null;

        // build request header and body depending on parameter passed to the method
        post_parameters = JSON.stringify(post_parameters);
        let request_header = {
            'Accept': accept_type,
            'Content-Type': "application/json; charset=utf-8",
            'Content-Length': post_parameters.length.toString()
        }

        // send request to the server
        await fetch(this.request_url, {
            method: "POST",
            headers: request_header,
            body: post_parameters
        })
            // then gets content of the server response
            .then(async response =>  {
                // get the status response and check if there is an error
                this.#status = response.status;

                if (accept_type.includes("application/json")) {
                    request_response_data = await response.json();
                } else {
                    request_response_data = await response.blob();
                }
            })
            // handle error
            .catch(error => {
                this.#status = error.status;
                request_response_data = error;
            })
        ;

        return request_response_data;
    }

    /**
     * This method upload a file (only one) from an input to the server.
     * Returns the server response in json format (already decoded).
     *
     * @param input {HTMLInputElement} - the input that contains the file to upload
     * @param accept_type {string} - mime type of the server response, json by default.
     *
     * @returns {Promise<*>} The server response.
     */
    async upload_file(input, accept_type = "application/json") {
        let response_data = null;

        // format file to upload to the server
        let data = new FormData();
        data.append('file', input.files[0]);

        // send request to the back-end and wait the response (response in json)
        await fetch(this.request_url, {
            method: 'POST',
            headers: {
                "Accept": accept_type
            },
            body: data
        })
            // get the response and update the current status code
            .then(async response => {
                this.#status = response.status;
                response_data = await response.json();
            });

        return response_data;
    }
}
