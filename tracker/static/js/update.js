document.getElementById('add-more').addEventListener('click', function() {
    const formsetDiv = document.getElementById('formset');
    const totalForms = document.getElementById('id_form-TOTAL_FORMS');
    const currentCount = parseInt(totalForms.value);
    const newForm = formsetDiv.querySelector('.card').cloneNode(true);

    // Clear previous values
    newForm.querySelectorAll('input').forEach(input => {
        input.value = '';
    });

    // Update form index names and IDs (important!)
    newForm.innerHTML = newForm.innerHTML.replace(/form-(\d+)-/g, `form-${currentCount}-`);

    // Append to formset
    formsetDiv.appendChild(newForm);

    // Increment management form count
    totalForms.value = currentCount + 1;
});