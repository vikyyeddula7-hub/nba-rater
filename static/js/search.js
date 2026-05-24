// search.js — Nav search bar autocomplete

(function () {
  const input = document.getElementById("search-input");
  const dropdown = document.getElementById("search-results");
  if (!input || !dropdown) return;

  let debounceTimer;

  input.addEventListener("input", () => {
    const q = input.value.trim();
    clearTimeout(debounceTimer);
    if (q.length < 2) { dropdown.classList.add("hidden"); return; }

    debounceTimer = setTimeout(async () => {
      try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
        const players = await res.json();
        renderDropdown(dropdown, players);
      } catch (e) { console.error(e); }
    }, 250);
  });

  document.addEventListener("click", (e) => {
    if (!input.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.classList.add("hidden");
    }
  });

  function renderDropdown(el, players) {
    if (!players.length) { el.classList.add("hidden"); return; }
    el.innerHTML = players.map(p => `
      <a href="/player/${p.id}">
        <span class="sr-name">${p.name}</span>
        ${p.team ? `<span class="sr-team">${p.team}</span>` : ""}
      </a>
    `).join("");
    el.classList.remove("hidden");
  }
})();
