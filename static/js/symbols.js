document.querySelectorAll(".symbol-btn").forEach(btn => {
    btn.addEventListener("click", function (e) {
        e.preventDefault();

        const symbol = this.textContent.trim();

        navigator.clipboard.writeText(symbol).then(() => {
            document.getElementById("copy-message").textContent =
                `"${symbol}" copied!`;

            setTimeout(() => {
                document.getElementById("copy-message").textContent = "";
            }, 1500);
        });
    });
});