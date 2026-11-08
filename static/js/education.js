const educationList = document.getElementById("education-list");
const educationStatus = document.getElementById("education-status");
const educationSearch = document.getElementById("education-search");
const educationSearchForm = document.getElementById("education-search-form");
let educationSearchTimer;
let educationRequest;

function textElement(tag, className, value) {
    const element = document.createElement(tag);
    element.className = className;
    element.textContent = value ?? "";
    return element;
}

function educationUrl(template, id) {
    return template.replace("00000000-0000-0000-0000-000000000000", id);
}

function apiErrorMessage(data, status) {
    if (data?.detail) return data.detail;
    const messages = Object.entries(data || {}).flatMap(([field, errors]) =>
        (Array.isArray(errors) ? errors : [errors]).map(error =>
            `${field}: ${error?.message ?? error}`
        )
    );
    return messages.join(" ") || `Permintaan gagal (HTTP ${status}).`;
}

async function educationApi(url, { method = "GET", payload, signal } = {}) {
    const headers = { Accept: "application/json" };
    if (method !== "GET") headers["X-CSRFToken"] = getCookie("csrftoken");
    if (payload !== undefined) headers["Content-Type"] = "application/json";

    const response = await fetch(url, {
        method, headers, signal, body: JSON.stringify(payload),
    });
    if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(apiErrorMessage(data, response.status));
    }
    if (response.status !== 204) return response.json();
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
        textElement("span", "experience-category", item.education_level),
        textElement("h2", "", item.institution),
    );
    if (item.study_program) card.append(textElement("p", "experience-description", item.study_program));
    card.append(textElement("p", "experience-status", `${item.start_year}—${item.end_year || "Sekarang"}`));

    const actions = document.createElement("div");
    actions.className = "project-actions";

    if (educationList.dataset.isAuthenticated === "true") {
        const star = textElement("button", `button button-star${item.is_starred ? " is-starred" : ""}`, `${item.is_starred ? "Unstar" : "Star"} (${item.star_count})`);
        star.type = "button";
        star.dataset.starId = item.id;
        actions.append(star);
    } else {
        actions.append(textElement("span", "experience-status", `★ ${item.star_count}`));
    }

    if (educationList.dataset.canEdit === "true") {
        const edit = textElement("button", "button", "Edit");
        edit.type = "button";
        edit.dataset.editId = item.id;
        actions.append(edit);
    }
    if (educationList.dataset.isOwner === "true") {
        const remove = textElement("button", "button button-danger", "Hapus");
        remove.type = "button";
        remove.dataset.deleteId = item.id;
        actions.append(remove);
    }
    card.append(actions);
    return card;
}

async function loadEducation() {
    educationRequest?.abort();
    educationRequest = new AbortController();
    educationList.replaceChildren();
    educationStatus.hidden = false;
    educationStatus.textContent = "Memuat data pendidikan...";
    const url = new URL(educationList.dataset.apiUrl, window.location.href);
    url.searchParams.set("q", educationSearch.value.trim());

    try {
        const data = await educationApi(url, { signal: educationRequest.signal });
        educationList.replaceChildren(...data.map(renderEducation));
        educationStatus.hidden = data.length > 0;
        if (!data.length) {
            educationStatus.textContent = educationSearch.value.trim()
                ? "Tidak ada riwayat pendidikan yang cocok."
                : "Belum ada riwayat pendidikan yang ditambahkan.";
        }
    } catch (error) {
        if (error.name === "AbortError") return;
        educationStatus.hidden = false;
        educationStatus.textContent = "Data pendidikan gagal dimuat. Coba lagi.";
        showToast("Gagal memuat Education", error.message, "error");
    }
}

educationSearch.addEventListener("input", () => {
    clearTimeout(educationSearchTimer);
    educationSearchTimer = setTimeout(loadEducation, 300);
});
educationSearchForm.addEventListener("submit", event => {
    event.preventDefault();
    clearTimeout(educationSearchTimer);
    loadEducation();
});

const educationForm = document.getElementById("education-form");
if (educationForm) {
    educationForm.addEventListener("submit", async event => {
        event.preventDefault();
        const submit = educationForm.querySelector('button[type="submit"]');
        submit.disabled = true;
        const formData = new FormData(educationForm);
        const payload = Object.fromEntries(["institution", "education_level", "study_program", "start_year", "end_year", "logo_url"].map(name => [name, formData.get(name) || (name === "end_year" ? null : "")]));
        payload.start_year = Number(payload.start_year);
        if (payload.end_year !== null) payload.end_year = Number(payload.end_year);
        try {
            await educationApi(educationForm.action, { method: "POST", payload });
            educationForm.reset();
            educationSearch.value = "";
            document.getElementById("add-education-modal").hidePopover();
            showToast("Berhasil", "Pendidikan ditambahkan.", "success");
            await loadEducation();
        } catch (error) {
            showToast("Gagal menambahkan Education", error.message, "error");
        } finally {
            submit.disabled = false;
        }
    });
}

const editForm = document.getElementById("education-edit-form");
if (editForm) {
    editForm.addEventListener("submit", async event => {
        event.preventDefault();
        const submit = editForm.querySelector('button[type="submit"]');
        submit.disabled = true;
        const value = name => editForm.elements.namedItem(`edit-${name}`).value;
        const payload = {
            institution: value("institution"),
            education_level: value("education_level"),
            study_program: value("study_program"),
            start_year: Number(value("start_year")),
            end_year: value("end_year") ? Number(value("end_year")) : null,
            logo_url: value("logo_url"),
        };
        try {
            const url = educationUrl(educationList.dataset.detailUrl, editForm.dataset.educationId);
            await educationApi(url, { method: "PATCH", payload });
            editForm.reset();
            document.getElementById("edit-education-modal").hidePopover();
            showToast("Berhasil", "Pendidikan diperbarui.", "success");
            await loadEducation();
        } catch (error) {
            showToast("Gagal mengubah Education", error.message, "error");
        } finally {
            submit.disabled = false;
        }
    });
}

educationList.addEventListener("click", async event => {
    const star = event.target.closest("button[data-star-id]");
    const edit = event.target.closest("button[data-edit-id]");
    const remove = event.target.closest("button[data-delete-id]");

    if (edit && editForm) {
        try {
            const url = educationUrl(educationList.dataset.detailUrl, edit.dataset.editId);
            const item = await educationApi(url);
            for (const name of ["institution", "education_level", "study_program", "start_year", "end_year", "logo_url"]) {
                editForm.elements.namedItem(`edit-${name}`).value = item[name] ?? "";
            }
            editForm.dataset.educationId = item.id;
            document.getElementById("edit-education-modal").showPopover();
        } catch (error) {
            showToast("Gagal memuat Education", error.message, "error");
        }
        return;
    }

    if (!star && !remove) return;
    if (remove && !confirm("Hapus pendidikan ini?")) return;
    const button = star || remove;
    button.disabled = true;
    const url = star
        ? educationUrl(educationList.dataset.starUrl, star.dataset.starId)
        : educationUrl(educationList.dataset.detailUrl, remove.dataset.deleteId);
    try {
        await educationApi(url, { method: star ? "POST" : "DELETE" });
        showToast("Berhasil", star ? "Star diperbarui." : "Pendidikan dihapus.", "success");
        await loadEducation();
    } catch (error) {
        showToast(star ? "Gagal memberi star" : "Gagal menghapus Education", error.message, "error");
    } finally {
        button.disabled = false;
    }
});

loadEducation();
