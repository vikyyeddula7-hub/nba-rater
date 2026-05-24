// teams.js — team filter, sort, roster toggle

(function () {
  const grid   = document.getElementById('team-grid');
  const cards  = Array.from(grid ? grid.querySelectorAll('.team-card') : []);
  const count  = document.getElementById('team-count');

  // Filter
  document.querySelectorAll('.ftab[data-tfilter]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.ftab[data-tfilter]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const f = btn.dataset.tfilter;
      let visible = 0;
      cards.forEach(c => {
        const show = f === 'all' || c.dataset.tbadge === f;
        c.style.display = show ? '' : 'none';
        if (show) visible++;
      });
      if (count) count.textContent = `Showing ${visible} teams · Ranked by NBA 2K26 team OVR`;
    });
  });

  // Sort
  const sortSel = document.getElementById('team-sort');
  if (sortSel && grid) {
    sortSel.addEventListener('change', () => {
      const key = sortSel.value;
      const sorted = [...cards].sort((a, b) => {
        if (key === 'ovr')  return parseFloat(b.dataset.tovr) - parseFloat(a.dataset.tovr);
        if (key === 'name') return a.dataset.tname.localeCompare(b.dataset.tname);
        return 0;
      });
      sorted.forEach(c => grid.appendChild(c));
    });
  }
})();

function toggleRoster(btn) {
  const card = btn.closest('.team-card');
  const full = card.querySelector('.full-roster');
  const preview = card.querySelector('.roster-preview');
  if (full.classList.contains('hidden')) {
    full.classList.remove('hidden');
    preview.classList.add('hidden');
    btn.textContent = 'Hide Roster ▴';
  } else {
    full.classList.add('hidden');
    preview.classList.remove('hidden');
    btn.textContent = 'See Full Roster ▾';
  }
}
