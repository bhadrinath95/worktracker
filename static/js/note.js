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