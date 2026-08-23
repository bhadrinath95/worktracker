document.addEventListener("DOMContentLoaded", function () {

    const editor = document.getElementById("note-content");
    const preview = document.getElementById("markdown-preview");
    const saveStatus = document.getElementById("save-status");


    /*
     * Render Markdown
     */

    function updatePreview() {

        const markdownText = editor.value;

        if (!markdownText.trim()) {

            preview.innerHTML = `
                <div class="text-muted text-center mt-5">
                    <i class="bi bi-eye-slash fs-2"></i>
                    <p class="mt-2">
                        Preview will appear here...
                    </p>
                </div>
            `;

            return;
        }

        preview.innerHTML = marked.parse(markdownText);
    }


    /*
     * Initial preview
     */

    updatePreview();


    /*
     * Update preview while typing
     */

    editor.addEventListener("input", function () {
        updatePreview();
    });


    /*
     * Export Preview as PDF
     */

    window.exportNotePDF = function () {

        if (!editor.value.trim()) {
            alert("There is no content to export.");
            return;
        }

        const printWindow = window.open("", "_blank");

        if (!printWindow) {
            alert("Please allow pop-ups to export the PDF.");
            return;
        }

        printWindow.document.write(`
            <!DOCTYPE html>

            <html>

            <head>

                <meta charset="UTF-8">

                <title>My Note</title>

                <style>

                    @page {
                        size: A4;
                        margin: 20mm;
                    }

                    body {
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                        line-height: 1.6;
                        color: #333;
                        margin: 0;
                        padding: 0;
                    }

                    h1 {
                        font-size: 28px;
                        margin-top: 0;
                        margin-bottom: 20px;
                    }

                    h2 {
                        font-size: 22px;
                        margin-top: 25px;
                    }

                    h3 {
                        font-size: 18px;
                        margin-top: 20px;
                    }

                    h4,
                    h5,
                    h6 {
                        margin-top: 18px;
                    }

                    p {
                        margin-bottom: 12px;
                    }

                    ul,
                    ol {
                        margin-bottom: 15px;
                    }

                    blockquote {
                        border-left: 4px solid #999;
                        padding-left: 15px;
                        margin-left: 0;
                        color: #666;
                    }

                    code {
                        background-color: #f3f3f3;
                        padding: 2px 5px;
                        border-radius: 3px;
                        font-family: monospace;
                    }

                    pre {
                        background-color: #f5f5f5;
                        padding: 15px;
                        border-radius: 6px;
                        white-space: pre-wrap;
                        overflow-wrap: break-word;
                        font-family: monospace;
                    }

                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin: 15px 0;
                    }

                    th,
                    td {
                        border: 1px solid #ccc;
                        padding: 8px;
                        text-align: left;
                    }

                    th {
                        background-color: #f2f2f2;
                    }

                    hr {
                        border: none;
                        border-top: 1px solid #ccc;
                        margin: 20px 0;
                    }

                    img {
                        max-width: 100%;
                    }

                    a {
                        color: #333;
                        text-decoration: none;
                    }

                </style>

            </head>

            <body>

                ${preview.innerHTML}

            </body>

            </html>
        `);

        printWindow.document.close();

        printWindow.onload = function () {

            printWindow.focus();

            printWindow.print();

        };

    };


    /*
     * Change status before HTMX request
     */

    document.body.addEventListener(
        "htmx:beforeRequest",
        function (event) {

            if (
                event.detail &&
                event.detail.elt &&
                event.detail.elt.id === "note-content"
            ) {

                saveStatus.innerHTML =
                    '<span class="text-warning">' +
                    '<i class="bi bi-cloud-arrow-up"></i> ' +
                    'Saving...' +
                    '</span>';
            }
        }
    );


    /*
     * Successful save
     */

    document.body.addEventListener(
        "htmx:afterRequest",
        function (event) {

            if (
                event.detail &&
                event.detail.elt &&
                event.detail.elt.id === "note-content"
            ) {

                if (event.detail.successful) {

                    saveStatus.innerHTML =
                        '<span class="text-success">' +
                        '<i class="bi bi-check-circle"></i> ' +
                        'Saved' +
                        '</span>';
                }
            }
        }
    );


    /*
     * Save error
     */

    document.body.addEventListener(
        "htmx:responseError",
        function (event) {

            if (
                event.detail &&
                event.detail.elt &&
                event.detail.elt.id === "note-content"
            ) {

                saveStatus.innerHTML =
                    '<span class="text-danger">' +
                    '<i class="bi bi-exclamation-circle"></i> ' +
                    'Save failed' +
                    '</span>';
            }
        }
    );

});