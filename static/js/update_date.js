document.addEventListener("DOMContentLoaded", function () {
  const picker = document.getElementById("date-picker");
  const hidden = document.getElementById("id_dates");
  const list = document.getElementById("selected-dates");

  let dates = [];

  picker.addEventListener("change", function () {
    if (this.value && !dates.includes(this.value)) {
      dates.push(this.value);
      render();
    }
    this.value = "";
  });

  function render() {
    hidden.value = dates.join(",");
    list.innerHTML = "";

    dates.forEach((date, index) => {
      const badge = document.createElement("span");
      badge.className = "badge bg-primary me-2 mb-2";
      badge.innerText = date + " ✕";
      badge.style.cursor = "pointer";
      badge.onclick = () => {
        dates.splice(index, 1);
        render();
      };
      list.appendChild(badge);
    });
  }
});
