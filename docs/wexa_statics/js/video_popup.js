/**
:filename: statics.js.video_popup.js
:author: Florian Lopitaux
:contact: contact@sppas.org
:summary: Functions to open the close the video popup.

.. _This file is part of Whakerexa: https://sourceforge.net/projects/whakerexa/ ,
.. on 2024-03-01.
    -------------------------------------------------------------------------

    Copyright (C) 2011-2024  Brigitte Bigi
    Laboratoire Parole et Langage, Aix-en-Provence, France

    Use of this software is governed by the GNU Public License, version 3.

    Whakerexa is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Whakerexa is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Whakerexa. If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------

*/

/**
 * Open the video popup and get the video file from the server.
 *
 * @param id_popup The identifier of the video popup node defined in the python code.
 */
async function play_popup_video(id_popup) {
    let modal = document.getElementById("popup-" + id_popup);
    let video = document.getElementById("popup-video-" + id_popup);

    // quick start of the video to the client get the video file
    await video.play();
    video.pause();

    modal.showModal();
}

/**
 * Close the video popup and stop the video.
 *
 * @param id_popup the identifier of the video popup node defined in the python code.
 */
function close_popup_video(id_popup) {
    let modal = document.getElementById("popup-" + id_popup);
    let video = document.getElementById("popup-video-" + id_popup);

    video.pause();
    modal.close();
}
