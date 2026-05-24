// home.js — filter, sort, theme toggle

(function () {
  // ── Theme toggle ──────────────────────────────────────────────────────────
  const toggleBtn = document.getElementById('theme-toggle');
  const saved = localStorage.getItem('theme') || 'dark';
  if (saved === 'light') document.body.classList.add('light');
  if (toggleBtn) {
    toggleBtn.textContent = document.body.classList.contains('light') ? '🌙' : '☀️';
    toggleBtn.addEventListener('click', () => {
      document.body.classList.toggle('light');
      const isLight = document.body.classList.contains('light');
      localStorage.setItem('theme', isLight ? 'light' : 'dark');
      toggleBtn.textContent = isLight ? '🌙' : '☀️';
    });
  }

  // ── Filter tabs ───────────────────────────────────────────────────────────
  const grid    = document.getElementById('player-grid');
  const cards   = Array.from(grid ? grid.querySelectorAll('.player-card') : []);
  const counter = document.getElementById('grid-count');

  document.querySelectorAll('.ftab').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.ftab').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const f = btn.dataset.filter;
      let visible = 0;
      cards.forEach(c => {
        const show = f === 'all' || c.dataset.badge === f;
        c.style.display = show ? '' : 'none';
        if (show) visible++;
      });
      if (counter) counter.textContent = `Showing ${visible} players · Ranked by NBA 2K26 OVR`;
    });
  });

  // ── Sort ──────────────────────────────────────────────────────────────────
  const sortSel = document.getElementById('sort-select');
  if (sortSel && grid) {
    sortSel.addEventListener('change', () => {
      const key = sortSel.value;
      const sorted = [...cards].sort((a, b) =>
        parseFloat(b.dataset[key]) - parseFloat(a.dataset[key])
      );
      sorted.forEach((c, i) => {
        const rankEl = c.querySelector('.card-rank');
        if (rankEl) rankEl.textContent = `#${i + 1}`;
        grid.appendChild(c);
      });
    });
  }
})();
