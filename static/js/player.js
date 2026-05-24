// player.js — animated OVR counter + theme toggle

(function () {
  // Theme toggle
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

  // Animated OVR counter
  const hero   = document.getElementById('ovr-hero');
  const counter = document.getElementById('ovr-counter');
  if (!hero || !counter) return;

  const target  = parseInt(hero.dataset.target, 10);
  const duration = 900; // ms
  const start    = performance.now();
  const startVal = Math.max(0, target - 30);

  function tick(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    // ease-out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(startVal + (target - startVal) * eased);
    counter.textContent = current;
    if (progress < 1) requestAnimationFrame(tick);
  }

  // Start when element is in view
  const obs = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting) {
      requestAnimationFrame(tick);
      obs.disconnect();
    }
  }, { threshold: 0.3 });
  obs.observe(hero);
})();
