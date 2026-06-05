function showNodeDetails(node) {

    document.getElementById("nodeTitle").textContent =
        node.dataset.title;

    document.getElementById("nodeDescription").textContent =
        node.dataset.description || "No description available.";

    const modal = new bootstrap.Modal(
        document.getElementById("nodeModal")
    );

    modal.show();
}