document.addEventListener('DOMContentLoaded', function () {
    const tagSelect = document.getElementById('tagSelect');
    if (!tagSelect) return;

    tagSelect.addEventListener('change', function () {
        const syntax = this.value;
        if (!syntax) return;

        const textarea = document.querySelector('textarea');
        if (!textarea) return;

        const cursorPos = textarea.selectionStart;
        const text = textarea.value;

        textarea.value =
            text.slice(0, cursorPos) + syntax + 
            text.slice(cursorPos);

        textarea.focus();
        textarea.selectionStart = textarea.selectionEnd =
            cursorPos + syntax.length + 6;

        this.selectedIndex = 0; // reset dropdown
    });
});
