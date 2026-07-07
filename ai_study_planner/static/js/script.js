document.addEventListener("DOMContentLoaded", function () {
    const addBtn = document.getElementById("add-subject-btn");
    const container = document.getElementById("subject-rows");

    if (addBtn && container) {
        addBtn.addEventListener("click", function () {
            const row = document.createElement("div");
            row.className = "row g-2 mb-2 subject-row";
            row.innerHTML = `
                <div class="col-7">
                    <input type="text" name="subject_name[]" class="form-control" placeholder="e.g. Physics">
                </div>
                <div class="col-4">
                    <select name="subject_priority[]" class="form-select">
                        <option value="1">1 - Low</option>
                        <option value="2">2</option>
                        <option value="3" selected>3 - Medium</option>
                        <option value="4">4</option>
                        <option value="5">5 - High</option>
                    </select>
                </div>
                <div class="col-1">
                    <button type="button" class="btn btn-outline-danger remove-row-btn">&times;</button>
                </div>
            `;
            container.appendChild(row);
        });

        container.addEventListener("click", function (e) {
            if (e.target.classList.contains("remove-row-btn")) {
                e.target.closest(".subject-row").remove();
            }
        });
    }
});
