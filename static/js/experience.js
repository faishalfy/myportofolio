const experienceList = document.getElementById("experience-list");
const experienceStatus = document.getElementById("experience-status");
const experienceSearch = document.getElementById("experience-search");
const experienceSearchForm = document.getElementById("experience-search-form");
let experienceSearchTimer;
let experienceRequest;

function experienceText(tag, className, value) {
    const element = document.createElement(tag);
    element.className = className;
    element.textContent = value;
    return element;
}

function renderExperience(item) {
    const card = document.createElement("article");
    card.className = "experience-card";

    if (item.thumbnail) {
        const thumbnail = document.createElement("img");
        thumbnail.className = "company-logo";
        thumbnail.src = item.thumbnail;
        thumbnail.alt = `Gambar ${item.title}`;
        thumbnail.loading = "lazy";
        card.append(thumbnail);
    }

    card.append(experienceText("span", "experience-category", item.category));
    if (item.company) {
        card.append(experienceText("p", "experience-company", item.company));
    }
    card.append(
        experienceText("h2", "", item.title),
        experienceText("p", "experience-description", item.description),
        experienceText(
            "p",
            "experience-status",
            item.is_ongoing ? "Sedang berlangsung" : "Selesai",
        ),
    );
    return card;
}

async function loadExperience() {
    if (experienceRequest) experienceRequest.abort();
    experienceRequest = new AbortController();
    experienceList.replaceChildren();
    experienceStatus.hidden = false;
    experienceStatus.textContent = "Memuat data pengalaman...";

    const url = new URL(experienceList.dataset.apiUrl, window.location.href);
    url.searchParams.set("q", experienceSearch.value.trim());

    try {
        const response = await fetch(url, { signal: experienceRequest.signal });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const experiences = await response.json();
        experienceList.replaceChildren(...experiences.map(renderExperience));
        experienceStatus.hidden = experiences.length > 0;
        if (!experiences.length) {
            experienceStatus.textContent = experienceSearch.value.trim()
                ? "Tidak ada pengalaman yang cocok."
                : "Belum ada pengalaman yang ditambahkan.";
        }
    } catch (error) {
        if (error.name === "AbortError") return;
        experienceStatus.hidden = false;
        experienceStatus.textContent = "Data pengalaman gagal dimuat. Coba lagi.";
        showToast("Gagal memuat Experience", experienceStatus.textContent, "error");
    }
}

experienceSearch.addEventListener("input", function () {
    clearTimeout(experienceSearchTimer);
    experienceSearchTimer = setTimeout(loadExperience, 300);
});

experienceSearchForm.addEventListener("submit", function (event) {
    event.preventDefault();
    clearTimeout(experienceSearchTimer);
    loadExperience();
});

const experienceForm = document.getElementById("experience-form");
if (experienceForm) {
    experienceForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        const submitButton = experienceForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        try {
            const response = await fetch(experienceForm.action, {
                method: "POST",
                body: new FormData(experienceForm),
            });
            const result = await response.json();

            if (response.status === 201) {
                experienceForm.reset();
                experienceSearch.value = "";
                document.getElementById("add-experience-modal").hidePopover();
                showToast("Experience berhasil ditambahkan", result.message, "success");
                loadExperience();
                return;
            }

            const errors = result.errors
                ? Object.entries(result.errors).flatMap(function ([field, items]) {
                    return items.map(function ({ message }) {
                        return `${field}: ${message}`;
                    });
                })
                : [result.message || `Terjadi kesalahan (status ${response.status}).`];
            showToast("Gagal menambahkan Experience", errors.join(" "), "error");
        } catch {
            showToast("Gagal menambahkan Experience", "Tidak dapat terhubung ke server. Silakan coba lagi.", "error");
        } finally {
            submitButton.disabled = false;
        }
    });
}

loadExperience();
