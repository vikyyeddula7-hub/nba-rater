// compare.js — Player comparison page (with re-select support)

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

    // Allow re-typing to search again at any time
    input.addEventListener("input", () => {
      const q = input.value.trim();
      clearTimeout(timer);
      if (q.length < 2) { dropdown.classList.add("hidden"); return; }
      timer = setTimeout(async () => {
        try {
          const res     = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
          const players = await res.json();
          renderDropdown(dropdown, players, slot, card, input);
        } catch (e) { console.error(e); }
      }, 250);
    });

    // Re-open dropdown on focus if there's already a query typed
    input.addEventListener("focus", () => {
      const q = input.value.trim();
      if (q.length >= 2 && !dropdown.classList.contains("hidden")) return;
      if (q.length >= 2) {
        input.dispatchEvent(new Event("input"));
      }
    });

    // Clear field + reset slot when user clicks into it to re-search
    input.addEventListener("click", () => {
      input.select();
    });

    document.addEventListener("click", (e) => {
      if (!input.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.add("hidden");
      }
    });
  }

  function renderDropdown(el, players, slot, card, input) {
    if (!players.length) { el.classList.add("hidden"); return; }
    el.innerHTML = players.map(p => `
      <a href="#" data-id="${p.id}" data-name="${p.name}" data-team="${p.team || ""}">
        <span class="sr-name">${p.name}</span>
        ${p.team ? `<span class="sr-team">${p.team}</span>` : ""}
      </a>
    `).join("");
    el.classList.remove("hidden");

    el.querySelectorAll("a").forEach(a => {
      a.addEventListener("click", async (e) => {
        e.preventDefault();
        const id = parseInt(a.dataset.id);
        input.value = a.dataset.name;
        el.classList.add("hidden");
        await loadPlayer(id, slot, card);
      });
    });
  }

  async function loadPlayer(id, slot, cardEl) {
    cardEl.textContent = "Loading…";
    cardEl.classList.remove("empty");

    try {
      const res  = await fetch(`/api/player/${id}`);
      const data = await res.json();
      if (data.error) { cardEl.textContent = "Player not found."; return; }

      state[slot] = data;
      renderCard(cardEl, data);

      // Refresh compare table if both slots are filled
      if (state.a && state.b) renderCompareTable();
    } catch (err) {
      cardEl.textContent = "Error loading player.";
      console.error(err);
    }
  }

  function renderCard(el, data) {
    const s = data.stats;
    const r = data.rating;
    el.innerHTML = `
      <div style="text-align:center; padding:1rem;">
        <img src="${s.headshot_url}" style="height:120px;object-fit:contain;"
             onerror="this.src='/static/img/silhouette.svg'" />
        <div style="font-family:var(--font-head);font-weight:900;font-size:1.2rem;
                    text-transform:uppercase;margin-top:.5rem;">${s.name}</div>
        <div style="font-family:var(--font-mono);font-size:.7rem;color:var(--text-dim);">
          ${s.position} · ${s.team}
        </div>
        <div style="font-family:var(--font-head);font-size:3rem;font-weight:900;
                    color:var(--accent2);line-height:1;margin-top:.75rem;">${r}</div>
        <div style="font-family:var(--font-mono);font-size:.6rem;color:var(--text-dim);
                    letter-spacing:.12em;">OVR (NBA 2K26)</div>
      </div>
    `;
  }

  function renderCompareTable() {
    const wrap = document.getElementById("compare-table-wrap");
    const a    = state.a.stats;
    const b    = state.b.stats;
    const ra   = state.a.rating;
    const rb   = state.b.rating;

    const rows = [
      { label: "OVR Rating (2K26)", va: ra,                  vb: rb,                fmt: v => v,    higher: true },
      { label: "Points",            va: a.pts,                vb: b.pts,             fmt: fmtF,      higher: true },
      { label: "Rebounds",          va: a.reb,                vb: b.reb,             fmt: fmtF,      higher: true },
      { label: "Assists",           va: a.ast,                vb: b.ast,             fmt: fmtF,      higher: true },
      { label: "Steals",            va: a.stl,                vb: b.stl,             fmt: fmtF,      higher: true },
      { label: "Blocks",            va: a.blk,                vb: b.blk,             fmt: fmtF,      higher: true },
      { label: "Turnovers",         va: a.tov,                vb: b.tov,             fmt: fmtF,      higher: false },
      { label: "FG%",               va: a.fg_pct * 100,       vb: b.fg_pct * 100,    fmt: fmtP,      higher: true },
      { label: "3PT%",              va: a.fg3_pct * 100,      vb: b.fg3_pct * 100,   fmt: fmtP,      higher: true },
      { label: "FT%",               va: a.ft_pct * 100,       vb: b.ft_pct * 100,    fmt: fmtP,      higher: true },
      { label: "True Shooting %",   va: a.ts_pct * 100,       vb: b.ts_pct * 100,    fmt: fmtP,      higher: true },
      { label: "+/- Per Game",      va: a.plus_minus,         vb: b.plus_minus,      fmt: fmtPM,     higher: true },
      { label: "Minutes",           va: a.min,                vb: b.min,             fmt: fmtF,      higher: true },
      { label: "Games Played",      va: a.gp,                 vb: b.gp,             fmt: v => v,    higher: true },
    ];

    const trs = rows.map(row => {
      const aBetter = row.higher ? row.va > row.vb : row.va < row.vb;
      const bBetter = row.higher ? row.vb > row.va : row.vb < row.va;
      return `<tr>
        <td class="cat-col">${row.label}</td>
        <td class="${aBetter ? "better" : ""}">${row.fmt(row.va)}</td>
        <td class="${bBetter ? "better" : ""}">${row.fmt(row.vb)}</td>
      </tr>`;
    }).join("");

    wrap.innerHTML = `
      <div class="compare-table-outer">
        <table class="compare-table">
          <thead>
            <tr>
              <th class="cat-col">Stat</th>
              <th>${a.name}</th>
              <th>${b.name}</th>
            </tr>
          </thead>
          <tbody>${trs}</tbody>
        </table>
      </div>
    `;
    wrap.classList.remove("hidden");
  }

  function fmtF(v)  { return parseFloat(v).toFixed(1); }
  function fmtP(v)  { return parseFloat(v).toFixed(1) + "%"; }
  function fmtPM(v) { return (v > 0 ? "+" : "") + parseFloat(v).toFixed(1); }
})();
