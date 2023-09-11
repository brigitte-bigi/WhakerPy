/**
 * ADAPTED FOR SPPAS WEBSITE by B. Bigi, 2023-08-27
 *
 * Generates a table of contents for your document based on the headings
 *  present. Anchors are injected into the document and the
 *  entries in the table of contents are linked to them. The table of
 *  contents will be generated inside of the first element with the id `toc`.
 * @param {HTMLDOMDocument} documentRef Optional A reference to the document
 *  object. Defaults to `document`.
 * @author Matthew Christopher Kastor-Inare III
 * @version 20130726
 * @example
 * // call this after the page has loaded
 * htmlTableOfContents();
 */
function htmlTableOfContents(documentRef) {

    var documentRef = documentRef || document;
    var toc = documentRef.getElementById('toc');
    var tocContent = documentRef.getElementById('toc-content');
    var headings = [].slice.call(tocContent.querySelectorAll('h2, h3, h4'));
    headings.forEach(function (heading, index) {
        /* Add the anchor right before the heading */
        var anchor = documentRef.createElement('a');
        anchor.setAttribute('name', 'toc' + index);
        anchor.setAttribute('id', 'toc' + index);

        /* Add an entry into the table of content */
        var link = documentRef.createElement('a');
        link.setAttribute('href', '#toc' + index);
        link.textContent = heading.textContent;

        var div = documentRef.createElement('li');
        div.setAttribute('class', heading.tagName.toLowerCase());

        div.appendChild(link);
        toc.appendChild(div);
        heading.parentNode.insertBefore(anchor, heading);
    });
}
