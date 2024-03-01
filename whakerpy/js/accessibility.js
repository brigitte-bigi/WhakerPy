/**
:filename: whakerpy.js.request.js
:author: Florian Lopitaux
:contact: contact@sppas.org
:summary: Functions to manage the color theme and contrast of the client with data persistent by url parameters.

.. _This file is part of WhakerPy: https://sourceforge.net/projects/whakerpy/ ,
.. on 2024-03-01.
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

*/

/**
 * Loads body css classes to set the color and contrast scheme of the webapp.
 * This function has to be called in the 'onload' property of the body element.
 *
 * By default, the color scheme is set to 'light' and the contrast is disabled.
 */
function loadBodyClasses() {
    const params = new URLSearchParams(window.location.search);
    let body = document.body;

    // manage color theme
    let color_scheme = "light";

    if (params.has("color_scheme")) {
        const color_parameter = params.get("color_scheme").toLowerCase();

        if (["light", "dark"].includes(color_scheme)) {
            color_scheme = color_parameter;
        } else {
            console.log("'color_scheme' get parameter unknown : " + color_parameter);
        }
    }

    body.classList.add(color_scheme);

    // manage contrast
    if (params.has("contrast")) {
        const contrast_param = params.get("contrast").toLowerCase();

        if  (contrast_param === "true") {
            body.classList.add("sp-contrast");
        }
    }
}

// add loadBodyClasses in the onLoad event
OnLoadManager.addLoadFunction(loadBodyClasses);

// -----------------------------------------------------------------------

/**
 * Changes the color scheme of the webapp.
 * Values switched : 'light' <=> 'dark'
 */
function color_scheme_switch() {
    let body = document.body;
    let oldTheme;
    let newTheme;

    // check which class is the old theme to replace
    if (body.classList.contains("light")) {
        oldTheme = "light";
        newTheme = "dark";
    } else {
        oldTheme = "dark";
        newTheme = "light";
    }

    // Take the new color scheme into account.
    body.classList.remove(oldTheme);
    body.classList.add(newTheme);
}

// -----------------------------------------------------------------------

/**
 * Changes the contrast scheme of the webapp.
 * Values switched : '' <=> 'sp-contrast'
 */
function contrast_scheme_switch() {
    let body = document.body;

    // switch contrast scheme
    if (body.classList.contains("sp-contrast")) {
        body.classList.remove("sp-contrast")
    } else {
        body.classList.add("sp-contrast")
    }
}

// -----------------------------------------------------------------------

/**
 * Customs the link before redirect the client.
 *
 * If the link target an external server, nothing changes.
 * If the link target a resource of our server, apply get parameters for the color and contrast scheme.
 *
 * @param element The 'a' html element which contains the url to custom
 */
function goToLink(element) {
    // check if it's an external link to another server
    if (element.host !== window.location.host) {
        document.location.href = element.href;
        return;
    }

    // it's an internal link, we add get parameters for the color and contrast scheme
    const body = document.body;
    let custom_url = new URL(element.href);

    // manage the color_scheme parameter
    const color_scheme_value = (body.classList.contains("light")) ? "light" : "dark";
    custom_url.searchParams.append("color_scheme", color_scheme_value);

    // manage the contrast_scheme parameter
    const contrast_scheme_value = (body.classList.contains("sp-contrast")) ? "true" : "false";
    custom_url.searchParams.append("contrast", contrast_scheme_value);

    // set the new url to redirect the client
    document.location.href = custom_url.href;
}

// -----------------------------------------------------------------------

function setAllLinksCustom() {
    let link_elements = Array.from(document.querySelectorAll("a"));

    link_elements.forEach(element => {
        element.addEventListener("click", event => {
            event.preventDefault();
            goToLink(element);
        });
    });
}

OnLoadManager.addLoadFunction(setAllLinksCustom);
