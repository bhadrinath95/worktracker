document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("chatForm");
    const input = document.getElementById("messageInput");
    const messages = document.getElementById("messages");

    if (!form || !input || !messages) {
        return;
    }

    form.addEventListener("submit", async function(event) {
        event.preventDefault();

        const message = input.value.trim();

        if (!message) {
            return;
        }

        input.value = "";

        // -------------------------
        // User message
        // -------------------------
        const userMessage = document.createElement("div");
        userMessage.className = "mb-4";

        userMessage.innerHTML = `
            <strong>You</strong>
            <div class="mt-1"></div>
        `;

        userMessage.querySelector("div").textContent = message;
        messages.appendChild(userMessage);

        // -------------------------
        // Luna message
        // -------------------------
        const assistantMessage = document.createElement("div");
        assistantMessage.className = "mb-4";

        assistantMessage.innerHTML = `
            <strong>Luna</strong>
            <div class="mt-1"></div>
        `;

        messages.appendChild(assistantMessage);

        const assistantContent =
            assistantMessage.querySelector("div");

        // -------------------------
        // Form data
        // -------------------------
        const formData = new FormData();
        formData.append("message", message);

        const csrfElement = document.querySelector(
            "[name=csrfmiddlewaretoken]"
        );

        if (!csrfElement) {
            assistantContent.textContent = "CSRF token not found.";
            return;
        }

        try {
            const response = await fetch(form.action, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfElement.value,
                    "Accept": "application/json"
                },
                body: formData
            });

            if (!response.ok) {
                assistantContent.textContent =
                    "Error generating response.";
                return;
            }

            // -------------------------
            // Get JSON from Django
            // -------------------------
            const data = await response.json();

            console.log("JSON received:", data);

            // -------------------------
            // Display ONLY response
            // -------------------------
            assistantContent.textContent =
                data.response || "No response received.";

            messages.scrollTop = messages.scrollHeight;

        } catch (error) {
            console.error("Chat error:", error);

            assistantContent.textContent =
                "Error connecting to Luna.";
        }
    });
});
