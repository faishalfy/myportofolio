const educationList = document.getElementById("education-list");
const educationStatus = document.getElementById("education-status");
const educationSearch = document.getElementById("education-search");
const educationSearchForm = document.getElementById("education-search-form");
let educationSearchTimer;
let educationRequest;

function educationText(tag, className, value) {
    const element = document.createElement(tag);
    element.className = className;
    element.textContent = value;
    return element;
}

function renderEducation(item) {
    const card = document.createElement("article");
    card.className = "experience-card";

    if (item.logo_url) {
        const logo = document.createElement("img");
        logo.className = "company-logo";
        logo.src = item.logo_url;
        logo.alt = `Logo ${item.institution}`;
        logo.loading = "lazy";
        card.append(logo);
    }

    card.append(
        educationText("span", "experience-category", item.education_level),
        educationText("h2", "", item.institution),
    );

    if (item.study_program) {
        card.append(educationText("p", "experience-description", item.study_program));
    }

    const endYear = item.end_year || "Sekarang";
    card.append(educationText("p", "experience-status", `${item.start_year}—${endYear}`));

    if (educationList.dataset.canEdit === "true" || educationList.dataset.isOwner === "true") {
        const cardActions = document.createElement("div");
        cardActions.className = "project-card-actions";
        const actions = document.createElement("div");
        actions.className = "project-actions";

        if (educationList.dataset.canEdit === "true") {
            const edit = educationText("a", "button", "Edit");
            edit.href = educationList.dataset.editUrl.replace("00000000-0000-0000-0000-000000000000", item.id);
            actions.append(edit);
        }

        if (educationList.dataset.isOwner === "true") {
            const remove = educationText("button", "button button-danger", "Hapus");
            remove.type = "button";
            remove.dataset.deleteId = item.id;
            actions.append(remove);
        }

        cardActions.append(actions);
        card.append(cardActions);
    }

    return card;
}

async function loadEducation() {
    if (educationRequest) educationRequest.abort();
    educationRequest = new AbortController();
    educationList.replaceChildren();
    educationStatus.hidden = false;
    educationStatus.textContent = "Memuat data pendidikan...";

    const url = new URL(educationList.dataset.apiUrl, window.location.href);
    url.searchParams.set("q", educationSearch.value.trim());

    try {
        const response = await fetch(url, { headers: { Accept: "application/json" }, signal: educationRequest.signal });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const educations = await response.json();
        educationList.replaceChildren(...educations.map(renderEducation));
        educationStatus.hidden = educations.length > 0;
        if (!educations.length) {
            educationStatus.textContent = educationSearch.value.trim()
                ? "Tidak ada riwayat pendidikan yang cocok."
                : "Belum ada riwayat pendidikan yang ditambahkan.";
        }
    } catch (error) {
        if (error.name === "AbortError") return;
        educationStatus.hidden = false;
        educationStatus.textContent = "Data pendidikan gagal dimuat. Coba lagi.";
        showToast("Gagal memuat Education", educationStatus.textContent, "error");
    }
}

educationSearch.addEventListener("input", function () {
    clearTimeout(educationSearchTimer);
    educationSearchTimer = setTimeout(loadEducation, 300);
});

educationSearchForm.addEventListener("submit", function (event) {
    event.preventDefault();
    clearTimeout(educationSearchTimer);
    loadEducation();
});

const educationForm = document.getElementById("education-form");
if (educationForm) {
    educationForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        const submitButton = educationForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        try {
            const fields = new FormData(educationForm);
            const payload = Object.fromEntries(
                ["institution", "education_level", "study_program", "start_year", "end_year", "logo_url"]
                    .map(name => [name, fields.get(name) || (name === "end_year" ? null : "")])
            );
            const response = await fetch(educationForm.action, {
                method: "POST",
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify(payload),
            });
            const result = await response.json();

            if (response.status === 201) {
                educationForm.reset();
                educationSearch.value = "";
                document.getElementById("add-education-modal").hidePopover();
                showToast("Education berhasil ditambahkan", "Pendidikan ditambahkan.", "success");
                loadEducation();
                return;
            }

            const errors = Object.entries(result).flatMap(([field, items]) =>
                (Array.isArray(items) ? items : [items]).map(message => `${field}: ${message}`));
            if (!errors.length) errors.push(`Terjadi kesalahan (status ${response.status}).`);
            showToast("Gagal menambahkan Education", errors.join(" "), "error");
        } catch {
            showToast("Gagal menambahkan Education", "Tidak dapat terhubung ke server. Silakan coba lagi.", "error");
        } finally {
            submitButton.disabled = false;
        }
    });
}

educationList.addEventListener("click", async event => {
    const remove = event.target.closest("button[data-delete-id]");
    if (!remove || remove.disabled || !confirm("Hapus pendidikan ini?")) return;
    remove.disabled = true;
    try {
        const url = educationList.dataset.detailUrl.replace("00000000-0000-0000-0000-000000000000", remove.dataset.deleteId);
        const response = await fetch(url, {
            method: "DELETE",
            headers: { Accept: "application/json", "X-CSRFToken": getCookie("csrftoken") },
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        showToast("Berhasil", "Pendidikan dihapus.", "success");
        await loadEducation();
    } catch (error) {
        showToast("Gagal menghapus Education", error.message, "error");
    } finally { remove.disabled = false; }
});

loadEducation();
