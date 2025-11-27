document.addEventListener('DOMContentLoaded', () => {
    const templateSelect = document.querySelector("select[name='template']");
    const descriptionField = document.querySelector("textarea[name='description']");

    templateSelect.addEventListener('change', function () {
        const templateId = this.value;

        if (!templateId) {
            descriptionField.value = "";   // No selection → empty
            return;
        }

        fetch(`/template/${templateId}/description/`)
            .then(response => response.json())
            .then(data => {
                descriptionField.value = data.description;   // Auto-fill description
            });
    });
});