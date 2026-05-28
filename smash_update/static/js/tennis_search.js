// tennis_search.js — nav search for SmashRater pages

(function () {
  const input    = document.getElementById("tennis-search");
  const dropdown = document.getElementById("tennis-search-results");
  if (!input || !dropdown) return;

  let timer;
  input.addEventListener("input", () => {
    const q = input.value.trim().toLowerCase();
    clearTimeout(timer);
    if (q.length < 2) { dropdown.classList.add("hidden"); return; }
    timer = setTimeout(async () => {
      const res     = await fetch(`/tennis/api/search?q=${encodeURIComponent(q)}`);
      const players = await res.json();
      if (!players.length) { dropdown.classList.add("hidden"); return; }
      dropdown.innerHTML = players.map(p => `
        <a href="/tennis/player/${p.rank}">
          <span class="sr-name">${p.flag} ${p.name}</span>
          <span class="sr-team">#${p.rank} · ${p.country}</span>
        </a>
      `).join("");
      dropdown.classList.remove("hidden");
    }, 200);
  });

  document.addEventListener("click", e => {
    if (!input.contains(e.target) && !dropdown.contains(e.target))
      dropdown.classList.add("hidden");
  });
})();
