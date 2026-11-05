
let tableRows = 3;
let tableColumns = 3;

let selectedRow = 0;
let selectedColumn = 0;

// Initialize table
document.addEventListener("DOMContentLoaded", function () {
    renderMarkdownTable();
});

// Render table while preserving values
function renderMarkdownTable() {
    const tbody = document.getElementById("markdown-table-body");
    if (!tbody) return;

    const existingValues = Array.from(tbody.querySelectorAll("tr"))
        .map(row => Array.from(row.querySelectorAll("input"))
            .map(input => input.value));

    tbody.innerHTML = "";

    for (let i = 0; i < tableRows; i++) {
        const tr = document.createElement("tr");

        for (let j = 0; j < tableColumns; j++) {
            const td = document.createElement("td");
            const input = document.createElement("input");

            input.type = "text";
            input.className = "form-control form-control-sm text-center";
            input.placeholder = i === 0 ? "Header" : "Enter value";
            input.value = existingValues[i]?.[j] ?? "";

            if (i === 0) {
                input.style.fontWeight = "bold";
            }

            input.addEventListener("focus", function () {
                selectedRow = i;
                selectedColumn = j;
                updateSelection();
            });

            input.addEventListener("input", generateMarkdown);

            td.appendChild(input);
            tr.appendChild(td);
        }

        tbody.appendChild(tr);
    }

    updateSelection();
    generateMarkdown();
}

// Highlight selected row and column
function updateSelection() {
    const rows = document.querySelectorAll("#markdown-table-body tr");

    rows.forEach((row, i) => {
        Array.from(row.children).forEach((cell, j) => {
            cell.style.backgroundColor =
                (i === selectedRow || j === selectedColumn)
                    ? "#e7f1ff"
                    : "";
        });
    });
}

// Add selected row
function addSelectedRow(position) {
    const tbody = document.getElementById("markdown-table-body");

    const values = Array.from(tbody.querySelectorAll("tr"))
        .map(row => Array.from(row.querySelectorAll("input"))
            .map(input => input.value));

    const insertIndex = position === "above"
        ? selectedRow
        : selectedRow + 1;

    values.splice(insertIndex, 0, Array(tableColumns).fill(""));

    tableRows++;
    selectedRow = insertIndex;

    rebuildTable(values);
}

// Remove selected row
function removeSelectedRow() {
    if (tableRows <= 2) {
        alert("Minimum 2 rows required (header + 1 data row).");
        return;
    }

    const values = getTableValues();
    values.splice(selectedRow, 1);

    tableRows--;
    selectedRow = Math.min(selectedRow, tableRows - 1);

    rebuildTable(values);
}

// Add selected column
function addSelectedColumn(position) {
    const values = getTableValues();

    const insertIndex = position === "left"
        ? selectedColumn
        : selectedColumn + 1;

    values.forEach(row => {
        row.splice(insertIndex, 0, "");
    });

    tableColumns++;
    selectedColumn = insertIndex;

    rebuildTable(values);
}

// Remove selected column
function removeSelectedColumn() {
    if (tableColumns <= 1) {
        alert("At least one column is required.");
        return;
    }

    const values = getTableValues();

    values.forEach(row => {
        row.splice(selectedColumn, 1);
    });

    tableColumns--;
    selectedColumn = Math.min(selectedColumn, tableColumns - 1);

    rebuildTable(values);
}

// Get current table values
function getTableValues() {
    return Array.from(
        document.querySelectorAll("#markdown-table-body tr")
    ).map(row =>
        Array.from(row.querySelectorAll("input"))
            .map(input => input.value)
    );
}

// Rebuild table
function rebuildTable(values) {
    const tbody = document.getElementById("markdown-table-body");

    tbody.innerHTML = "";

    values.forEach((row, i) => {
        const tr = document.createElement("tr");

        row.forEach((value, j) => {
            const td = document.createElement("td");
            const input = document.createElement("input");

            input.type = "text";
            input.className = "form-control form-control-sm text-center";
            input.placeholder = i === 0 ? "Header" : "Enter value";
            input.value = value;

            if (i === 0) {
                input.style.fontWeight = "bold";
            }

            input.addEventListener("focus", function () {
                selectedRow = i;
                selectedColumn = j;
                updateSelection();
            });

            input.addEventListener("input", generateMarkdown);

            td.appendChild(input);
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });

    updateSelection();
    generateMarkdown();
}

// Generate Markdown
function generateMarkdown() {
    const rows = getTableValues();

    let markdown = "";

    rows.forEach((row, index) => {
        const escapedValues = row.map(value =>
            value
                .replace(/\\/g, "\\\\")
                .replace(/\|/g, "\\|")
                .replace(/\r?\n/g, " ")
        );

        markdown += "| " + escapedValues.join(" | ") + " |\n";

        if (index === 0) {
            markdown += "| " +
                row.map(() => "---").join(" | ") +
                " |\n";
        }
    });

    document.getElementById("markdown-output").value = markdown;
}

// Copy Markdown
async function copyMarkdownTable() {
    const output = document.getElementById("markdown-output");
    const message = document.getElementById("markdown-copy-message");

    try {
        await navigator.clipboard.writeText(output.value);
        message.textContent = "Markdown table copied successfully!";
    } catch (error) {
        output.select();
        document.execCommand("copy");
        message.textContent = "Markdown table copied!";
    }
}
