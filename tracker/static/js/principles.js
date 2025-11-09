document.addEventListener("DOMContentLoaded", function() {
  const rows = document.querySelectorAll(".principle-row");
  let openRowId = null; // Track which row is currently expanded

  rows.forEach(row => {
    row.addEventListener("click", function(e) {
      e.preventDefault();

      const thisRowId = this.getAttribute("data-id");
      const existingMeaning = document.querySelector(".meaning-row");

      // If this same row is open, toggle it off
      if (openRowId === thisRowId && existingMeaning) {
        existingMeaning.remove();
        openRowId = null;
        return;
      }

      // Remove any previous meaning row
      if (existingMeaning) existingMeaning.remove();

      // Decode any escaped unicode like \u002D
      const raw = this.getAttribute("data-meaning");
      const meaningText = JSON.parse('"' + raw + '"');

      // Create new meaning row
      const newRow = document.createElement("tr");
      newRow.classList.add("meaning-row");
      newRow.innerHTML = `
        <td colspan="2">
          <div class="card border-0 bg-light shadow-sm p-3 mt-1">
            <p class="mb-0">${meaningText}</p>
          </div>
        </td>
      `;

      // Insert below clicked row
      this.insertAdjacentElement("afterend", newRow);
      openRowId = thisRowId;
    });
  });
});
