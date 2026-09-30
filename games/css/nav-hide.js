/* Hide the sticky header when scrolling down, show it when scrolling up. */
(function () {
  var header = document.querySelector('header.bg-white');
  if (!header) return;
  header.style.transition = 'transform 0.3s ease';
  var lastY = window.scrollY, ticking = false;
  function update() {
    var y = window.scrollY, h = header.offsetHeight;
    if (y > lastY && y > h) header.style.transform = 'translateY(-100%)';
    else if (y < lastY || y <= h) header.style.transform = '';
    lastY = y; ticking = false;
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(update); }
  }, { passive: true });
})();
