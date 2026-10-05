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

    if (item.edit_url || item.delete_url) {
        const cardActions = document.createElement("div");
        cardActions.className = "project-card-actions";
        const actions = document.createElement("div");
        actions.className = "project-actions";

        if (item.edit_url) {
            const edit = educationText("a", "button", "Edit");
            edit.href = item.edit_url;
            actions.append(edit);
        }

        if (item.delete_url) {
            const token = document.querySelector("#education-csrf-form [name=csrfmiddlewaretoken]");
            if (token) {
                const form = document.createElement("form");
                form.method = "post";
                form.action = item.delete_url;
                const csrfInput = document.createElement("input");
                csrfInput.type = "hidden";
                csrfInput.name = "csrfmiddlewaretoken";
                csrfInput.value = token.value;
                const remove = educationText("button", "button button-danger", "Hapus");
                remove.type = "submit";
                form.append(csrfInput, remove);
                actions.append(form);
            }
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
        const response = await fetch(url, { signal: educationRequest.signal });
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
            const response = await fetch(educationForm.action, {
                method: "POST",
                body: new FormData(educationForm),
            });
            const result = await response.json();

            if (response.status === 201) {
                educationForm.reset();
                educationSearch.value = "";
                document.getElementById("add-education-modal").hidePopover();
                showToast("Education berhasil ditambahkan", result.message, "success");
                loadEducation();
                return;
            }

            const errors = result.errors
                ? Object.entries(result.errors).flatMap(function ([field, items]) {
                    return items.map(function ({ message }) {
                        return `${field}: ${message}`;
                    });
                })
                : [result.message || `Terjadi kesalahan (status ${response.status}).`];
            showToast("Gagal menambahkan Education", errors.join(" "), "error");
        } catch {
            showToast("Gagal menambahkan Education", "Tidak dapat terhubung ke server. Silakan coba lagi.", "error");
        } finally {
            submitButton.disabled = false;
        }
    });
}

loadEducation();
