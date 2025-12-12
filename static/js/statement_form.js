document.addEventListener("DOMContentLoaded", function () {
    const addBtn = document.getElementById("add-option");
    const optionsArea = document.getElementById("options-area");

    if (!addBtn) return; // Prevent error on pages without the button

    // This value will be injected dynamically by Django inside the template
    const emptyFormHtml = window.EMPTY_FORM_HTML;
    const formsetPrefix = window.FORMSET_PREFIX;

    addBtn.addEventListener("click", () => {
        const totalForms = document.querySelector(
            `input[name="${formsetPrefix}-TOTAL_FORMS"]`
        );
        
        let formIndex = parseInt(totalForms.value);

        let newForm = document.createElement("div");
        newForm.classList = "card border-primary mb-3 p-3 option-form";
        newForm.innerHTML = emptyFormHtml.replace(/__prefix__/g, formIndex);

        optionsArea.appendChild(newForm);
        totalForms.value = formIndex + 1;

        $(newForm).find('.select2-multi').select2({
            width: '100%',
            placeholder: "Select Life Principles",
            allowClear: true
        });
    });
});
