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

    card.append(
        experienceText("span", "experience-category", item.category),
        experienceText("h2", "", item.title),
        experienceText("p", "experience-description", item.description),
        experienceText("p", "experience-status", item.is_ongoing ? "Sedang berlangsung" : "Selesai"),
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

experienceSearch.addEventListener("input", () => {
    clearTimeout(experienceSearchTimer);
    experienceSearchTimer = setTimeout(loadExperience, 300);
});

experienceSearchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    clearTimeout(experienceSearchTimer);
    loadExperience();
});

loadExperience();
