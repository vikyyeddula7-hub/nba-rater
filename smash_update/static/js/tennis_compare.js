// tennis_compare.js — SmashRater compare page

(function () {
  const state = { a: null, b: null };
  setupPicker("search-a", "results-a", "card-a", "a");
  setupPicker("search-b", "results-b", "card-b", "b");

  function setupPicker(inputId, dropdownId, cardId, slot) {
    const input    = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);
    const card     = document.getElementById(cardId);
    if (!input) return;
    let timer;

    input.addEventListener("input", () => {
      const q = input.value.trim().toLowerCase();
      clearTimeout(timer);
      if (q.length < 2) { dropdown.classList.add("hidden"); return; }
      timer = setTimeout(async () => {
        const res = await fetch(`/tennis/api/search?q=${encodeURIComponent(q)}`);
        const players = await res.json();
        renderDropdown(dropdown, players, slot, card, input);
      }, 200);
    });

    input.addEventListener("click", () => input.select());
    document.addEventListener("click", e => {
      if (!input.contains(e.target) && !dropdown.contains(e.target))
        dropdown.classList.add("hidden");
    });
  }

  function renderDropdown(el, players, slot, card, input) {
    if (!players.length) { el.classList.add("hidden"); return; }
    el.innerHTML = players.map(p => `
      <a href="#" data-rank="${p.rank}" data-name="${p.name}">
        <span class="sr-name">${p.flag} ${p.name}</span>
        <span class="sr-team">#${p.rank} · ${p.country}</span>
      </a>
    `).join("");
    el.classList.remove("hidden");
    el.querySelectorAll("a").forEach(a => {
      a.addEventListener("click", async e => {
        e.preventDefault();
        input.value = a.dataset.name;
        el.classList.add("hidden");
        const res  = await fetch(`/tennis/api/player/${a.dataset.rank}`);
        const data = await res.json();
        state[slot] = data;
        renderCard(card, data);
        if (state.a && state.b) renderTable();
      });
    });
  }

  function renderCard(el, p) {
    el.classList.remove("empty");
    el.innerHTML = `
      <div style="text-align:center;padding:1rem;">
        <div style="font-size:3.5rem;">${p.flag}</div>
        <div style="font-family:var(--font-head);font-weight:900;font-size:1.1rem;text-transform:uppercase;margin-top:.4rem;">${p.name}</div>
        <div style="font-family:var(--font-mono);font-size:.7rem;color:var(--text-dim);">#${p.rank} · ${p.country}</div>
        <div style="font-family:var(--font-head);font-size:3rem;font-weight:900;color:#4caf7d;line-height:1;margin-top:.75rem;">${p.rating}</div>
        <div style="font-family:var(--font-mono);font-size:.6rem;color:var(--text-dim);letter-spacing:.12em;">SmashRater OVR</div>
      </div>`;
  }

  function renderTable() {
    const a = state.a, b = state.b;
    const rows = [
      { label: "SmashRater OVR", va: a.rating,       vb: b.rating,       fmt: v => v,         higher: true },
      { label: "ATP Ranking",    va: a.rank,          vb: b.rank,         fmt: v => "#"+v,      higher: false },
      { label: "ATP Points",     va: a.points,        vb: b.points,       fmt: v => v,         higher: true },
      { label: "Grand Slams",    va: a.grand_slams,   vb: b.grand_slams,  fmt: v => v,         higher: true },
      { label: "Career High",    va: a.career_high,   vb: b.career_high,  fmt: v => "#"+v,      higher: false },
      { label: "Age",            va: a.age,           vb: b.age,          fmt: v => v+" yrs",   higher: false },
      { label: "Turned Pro",     va: a.turned_pro,    vb: b.turned_pro,   fmt: v => v,         higher: false },
    ];
    const trs = rows.map(row => {
      const aBetter = row.higher ? row.va > row.vb : row.va < row.vb;
      const bBetter = row.higher ? row.vb > row.va : row.vb < row.va;
      return `<tr>
        <td class="cat-col">${row.label}</td>
        <td class="${aBetter?"better":""}">${row.fmt(row.va)}</td>
        <td class="${bBetter?"better":""}">${row.fmt(row.vb)}</td>
      </tr>`;
    }).join("");
    const wrap = document.getElementById("compare-table-wrap");
    wrap.innerHTML = `<div class="compare-table-outer"><table class="compare-table">
      <thead><tr><th class="cat-col">Stat</th><th>${a.name}</th><th>${b.name}</th></tr></thead>
      <tbody>${trs}</tbody>
    </table></div>`;
    wrap.classList.remove("hidden");
  }
})();
