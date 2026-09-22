let appState = null;
let activeView = "catalog";
let activeCoinId = null;

const elements = {
  catalogView: document.querySelector("#catalogView"),
  sourcesView: document.querySelector("#sourcesView"),
  searchInput: document.querySelector("#searchInput"),
  denominationFilter: document.querySelector("#denominationFilter"),
  programFilter: document.querySelector("#programFilter"),
  ownedFilter: document.querySelector("#ownedFilter"),
  ownedCount: document.querySelector("#ownedCount"),
  catalogCount: document.querySelector("#catalogCount"),
  completionRate: document.querySelector("#completionRate"),
  totalQuantity: document.querySelector("#totalQuantity"),
  resultCount: document.querySelector("#resultCount"),
  viewTitle: document.querySelector("#viewTitle"),
  catalogTab: document.querySelector("#catalogTab"),
  collectionTab: document.querySelector("#collectionTab"),
  sourcesTab: document.querySelector("#sourcesTab"),
  coinDialog: document.querySelector("#coinDialog"),
  holdingForm: document.querySelector("#holdingForm"),
  dialogTitle: document.querySelector("#dialogTitle"),
  dialogMeta: document.querySelector("#dialogMeta"),
  holdingsList: document.querySelector("#holdingsList"),
  issueYearInput: document.querySelector("#issueYearInput"),
  mintMarkInput: document.querySelector("#mintMarkInput"),
  quantityInput: document.querySelector("#quantityInput"),
  gradeInput: document.querySelector("#gradeInput"),
  locationInput: document.querySelector("#locationInput"),
  acquiredAtInput: document.querySelector("#acquiredAtInput"),
  notesInput: document.querySelector("#notesInput"),
  addCustomButton: document.querySelector("#addCustomButton"),
  customDialog: document.querySelector("#customDialog"),
  customForm: document.querySelector("#customForm"),
  customNameInput: document.querySelector("#customNameInput"),
  customYearsInput: document.querySelector("#customYearsInput"),
  customDenominationInput: document.querySelector("#customDenominationInput"),
  customProgramInput: document.querySelector("#customProgramInput"),
  customCategoryInput: document.querySelector("#customCategoryInput"),
  customSourceInput: document.querySelector("#customSourceInput"),
  customObverseImageInput: document.querySelector("#customObverseImageInput"),
  customReverseImageInput: document.querySelector("#customReverseImageInput"),
  customDescriptionInput: document.querySelector("#customDescriptionInput"),
  exportButton: document.querySelector("#exportButton"),
  importInput: document.querySelector("#importInput")
};

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;
    try {
      const payload = await response.json();
      message = payload.error || message;
    } catch {
      // Keep the HTTP message.
    }
    throw new Error(message);
  }
  return response.json();
}

async function loadState() {
  appState = await api("/api/state");
  setupFilters();
  render();
}

function setupFilters() {
  fillSelect(elements.denominationFilter, "All denominations", appState.facets.denominations);
  fillSelect(elements.programFilter, "All programs", appState.facets.programs);
}

function fillSelect(select, label, values) {
  const current = select.value;
  select.innerHTML = `<option value="all">${label}</option>` + values.map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`).join("");
  select.value = [...values, "all"].includes(current) ? current : "all";
}

function filteredCoins() {
  const text = elements.searchInput.value.trim().toLowerCase();
  const denomination = elements.denominationFilter.value;
  const program = elements.programFilter.value;
  const ownership = activeView === "collection" ? "owned" : elements.ownedFilter.value;

  return appState.coins.filter((coin) => {
    const owned = coin.owned_quantity > 0;
    const haystack = [
      coin.name,
      coin.denomination,
      coin.years,
      coin.program,
      coin.category,
      coin.description,
      coin.source,
      ...(coin.tags || [])
    ].join(" ").toLowerCase();

    return (!text || haystack.includes(text)) &&
      (denomination === "all" || coin.denomination === denomination) &&
      (program === "all" || coin.program === program) &&
      (ownership === "all" || (ownership === "owned" ? owned : !owned));
  });
}

function holdingsForCoin(coinId) {
  return appState.holdings.filter((holding) => holding.coin_id === coinId);
}

function render() {
  const coins = filteredCoins();
  const stats = appState.stats;

  elements.ownedCount.textContent = stats.owned_coin_count;
  elements.catalogCount.textContent = stats.catalog_count;
  elements.completionRate.textContent = `${stats.completion_rate}%`;
  elements.totalQuantity.textContent = stats.total_quantity;
  elements.resultCount.textContent = `${coins.length} ${coins.length === 1 ? "coin" : "coins"}`;

  elements.catalogView.classList.toggle("hidden", activeView === "sources");
  elements.sourcesView.classList.toggle("hidden", activeView !== "sources");
  elements.catalogTab.classList.toggle("active", activeView === "catalog");
  elements.collectionTab.classList.toggle("active", activeView === "collection");
  elements.sourcesTab.classList.toggle("active", activeView === "sources");
  elements.viewTitle.textContent = activeView === "collection" ? "My collection" : activeView === "sources" ? "Sources and data" : "Catalogue";

  if (activeView === "sources") return;

  elements.catalogView.innerHTML = coins.length
    ? coins.map(renderCard).join("")
    : `<div class="empty"><h3>No matches</h3><p>Adjust the search or filters.</p></div>`;
}

function renderCard(coin) {
  const holdings = holdingsForCoin(coin.id);
  const denomination = denominationLabel(coin.denomination);
  const imageMarkup = renderCoinImages(coin, denomination);
  const ownedLine = coin.owned_quantity > 0
    ? `${coin.owned_quantity} owned across ${coin.holding_count} ${coin.holding_count === 1 ? "entry" : "entries"}`
    : "Missing";

  return `
    <article class="coin-card ${coin.owned_quantity > 0 ? "owned" : ""}">
      ${imageMarkup}
      <div class="card-top">
        <div>
          <div class="card-title">${escapeHtml(coin.name)}</div>
          <div class="card-meta">${escapeHtml(coin.years)} - ${escapeHtml(coin.denomination)}</div>
        </div>
        <div class="coin-face" aria-hidden="true">${escapeHtml(denomination)}</div>
      </div>
      <p class="card-description">${escapeHtml(coin.description || "")}</p>
      <div class="chips">
        <span class="chip">${escapeHtml(coin.program)}</span>
        <span class="chip">${escapeHtml(coin.category)}</span>
        ${holdings.slice(0, 2).map((item) => `<span class="chip">${escapeHtml(compactHolding(item))}</span>`).join("")}
      </div>
      <div class="card-actions">
        <span class="owned-label">${escapeHtml(ownedLine)}</span>
        <button type="button" class="${coin.owned_quantity > 0 ? "secondary" : ""}" data-edit="${escapeHtml(coin.id)}">${coin.owned_quantity > 0 ? "Manage" : "Add"}</button>
      </div>
    </article>
  `;
}

function renderCoinImages(coin, denomination) {
  if (coin.obverse_image && coin.reverse_image) {
    return `
      <div class="coin-image pair">
        <img src="${escapeHtml(coin.obverse_image)}" alt="${escapeHtml(coin.name)} obverse" loading="lazy">
        <img src="${escapeHtml(coin.reverse_image)}" alt="${escapeHtml(coin.name)} reverse" loading="lazy">
      </div>
    `;
  }
  const imageUrl = coin.obverse_image || coin.reverse_image;
  if (imageUrl) {
    return `
      <div class="coin-image">
        <img src="${escapeHtml(imageUrl)}" alt="${escapeHtml(coin.name)}" loading="lazy">
      </div>
    `;
  }
  return `
    <div class="coin-image empty-image">
      <span>${escapeHtml(denomination)}</span>
    </div>
  `;
}

function compactHolding(item) {
  return [item.issue_year, item.mint_mark, item.grade, item.album_location].filter(Boolean).join(" / ") || `${item.quantity} owned`;
}

function denominationLabel(denomination) {
  const labels = {
    "Cent": "1c",
    "Two cent": "2c",
    "Three cent": "3c",
    "Half dime": "5c",
    "Nickel": "5c",
    "Dime": "10c",
    "Twenty cent": "20c",
    "Quarter": "25c",
    "Half dollar": "50c",
    "Dollar": "$1"
  };
  return labels[denomination] || denomination;
}

function openCoinDialog(coinId) {
  const coin = appState.coins.find((item) => item.id === coinId);
  if (!coin) return;
  activeCoinId = coinId;
  elements.dialogTitle.textContent = coin.name;
  elements.dialogMeta.textContent = `${coin.years} - ${coin.denomination} - ${coin.program}`;
  elements.issueYearInput.value = guessFirstYear(coin.years);
  elements.mintMarkInput.value = "";
  elements.quantityInput.value = 1;
  elements.gradeInput.value = "";
  elements.locationInput.value = "";
  elements.acquiredAtInput.value = "";
  elements.notesInput.value = "";
  renderHoldingsList(coinId);
  elements.coinDialog.showModal();
}

function renderHoldingsList(coinId) {
  const holdings = holdingsForCoin(coinId);
  elements.holdingsList.innerHTML = holdings.length
    ? holdings.map((item) => `
      <div class="holding-row">
        <div>
          <strong>${escapeHtml(compactHolding(item))}</strong>
          <span>${escapeHtml(item.quantity)} owned${item.notes ? ` - ${escapeHtml(item.notes)}` : ""}</span>
        </div>
        <button class="danger small" type="button" data-delete-holding="${item.id}">Remove</button>
      </div>
    `).join("")
    : `<p class="muted">No holdings saved for this coin yet.</p>`;
}

function guessFirstYear(years) {
  const match = String(years).match(/\d{4}/);
  return match ? match[0] : "";
}

async function saveHolding() {
  await api("/api/collection", {
    method: "POST",
    body: JSON.stringify({
      coin_id: activeCoinId,
      issue_year: elements.issueYearInput.value,
      mint_mark: elements.mintMarkInput.value,
      quantity: Number(elements.quantityInput.value || 1),
      grade: elements.gradeInput.value,
      album_location: elements.locationInput.value,
      acquired_at: elements.acquiredAtInput.value,
      notes: elements.notesInput.value
    })
  });
  await loadState();
  renderHoldingsList(activeCoinId);
  elements.mintMarkInput.value = "";
  elements.quantityInput.value = 1;
  elements.gradeInput.value = "";
  elements.locationInput.value = "";
  elements.acquiredAtInput.value = "";
  elements.notesInput.value = "";
}

async function deleteHolding(id) {
  await api(`/api/collection/${id}`, { method: "DELETE" });
  await loadState();
  renderHoldingsList(activeCoinId);
}

async function addCustomCoin() {
  await api("/api/catalog", {
    method: "POST",
    body: JSON.stringify({
      name: elements.customNameInput.value,
      years: elements.customYearsInput.value,
      denomination: elements.customDenominationInput.value,
      program: elements.customProgramInput.value,
      category: elements.customCategoryInput.value,
      source: elements.customSourceInput.value,
      obverse_image: elements.customObverseImageInput.value,
      reverse_image: elements.customReverseImageInput.value,
      description: elements.customDescriptionInput.value
    })
  });
  elements.customForm.reset();
  await loadState();
}

async function exportCollection() {
  const payload = await api("/api/export");
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `numismatics-${new Date().toISOString().slice(0, 10)}.json`;
  anchor.click();
  URL.revokeObjectURL(url);
}

function importCollection(file) {
  const reader = new FileReader();
  reader.onload = async () => {
    try {
      await api("/api/import", { method: "POST", body: reader.result });
      await loadState();
    } catch (error) {
      alert(error.message);
    }
  };
  reader.readAsText(file);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  }[char]));
}

elements.catalogView.addEventListener("click", (event) => {
  const button = event.target.closest("[data-edit]");
  if (button) openCoinDialog(button.dataset.edit);
});

elements.holdingsList.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-delete-holding]");
  if (button) await deleteHolding(button.dataset.deleteHolding);
});

[elements.searchInput, elements.denominationFilter, elements.programFilter, elements.ownedFilter].forEach((input) => {
  input.addEventListener("input", render);
});

elements.catalogTab.addEventListener("click", () => {
  activeView = "catalog";
  render();
});

elements.collectionTab.addEventListener("click", () => {
  activeView = "collection";
  render();
});

elements.sourcesTab.addEventListener("click", () => {
  activeView = "sources";
  render();
});

elements.holdingForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await saveHolding();
});

elements.addCustomButton.addEventListener("click", () => elements.customDialog.showModal());
elements.customForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await addCustomCoin();
  elements.customDialog.close();
});
elements.exportButton.addEventListener("click", exportCollection);
elements.importInput.addEventListener("change", (event) => {
  const [file] = event.target.files;
  if (file) importCollection(file);
  event.target.value = "";
});

loadState().catch((error) => {
  elements.catalogView.innerHTML = `<div class="empty"><h3>App failed to load</h3><p>${escapeHtml(error.message)}</p></div>`;
});
