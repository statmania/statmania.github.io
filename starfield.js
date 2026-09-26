// Starfield / constellation canvas background — the ONE shared copy, used by
// every section of the site (raw/ pages, games/, utility/, courses/ hub,
// blog/, slide/, question/, quiz/). Don't copy it into a section; point a
// <script> tag at it with the right relative path (e.g. ../starfield.js).
//
// It draws into every canvas matching any of:
//   canvas.sm-canvas   (games, utility, blog, quiz, question pages)
//   #sm-canvas         (raw/-rendered pages: homepage and hubs)
//   #sm-slide-canvas   (reveal.js slide decks)
// The canvas is fixed and viewport-sized (see the .sm-canvas / #sm-canvas
// rules in each section's CSS) so the animation spans the whole page.
// Also fills #sm-footer-year if present (homepage/hub footers).
(function () {
  function initCanvas(canvas) {
    if (!canvas || !canvas.getContext) return;
    var ctx = canvas.getContext('2d');
    var W, H, dpr;
    var particles = [];
    var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = window.innerWidth;
      H = window.innerHeight;
      canvas.width = W * dpr;
      canvas.height = H * dpr;
      canvas.style.width = W + 'px';
      canvas.style.height = H + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function init() {
      var count = Math.min(80, Math.floor((W || 1200) / 24));
      particles = [];
      for (var i = 0; i < count; i++) {
        particles.push({
          x: Math.random() * W,
          y: Math.random() * H,
          vx: (Math.random() - 0.5) * 0.25,
          vy: (Math.random() - 0.5) * 0.25,
          r: Math.random() * 1.6 + 0.6
        });
      }
    }

    function step() {
      ctx.clearRect(0, 0, W, H);
      var maxDist = 120;
      for (var i = 0; i < particles.length; i++) {
        var p = particles[i];
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > W) p.vx *= -1;
        if (p.y < 0 || p.y > H) p.vy *= -1;

        for (var j = i + 1; j < particles.length; j++) {
          var q = particles[j];
          var dx = p.x - q.x, dy = p.y - q.y;
          var dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < maxDist) {
            ctx.strokeStyle = 'rgba(0,229,255,' + (0.16 * (1 - dist / maxDist)) + ')';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(q.x, q.y);
            ctx.stroke();
          }
        }
      }
      for (var k = 0; k < particles.length; k++) {
        var pt = particles[k];
        ctx.beginPath();
        ctx.fillStyle = 'rgba(180,225,255,0.85)';
        ctx.arc(pt.x, pt.y, pt.r, 0, Math.PI * 2);
        ctx.fill();
      }
      if (!reduceMotion) requestAnimationFrame(step);
    }

    resize();
    init();
    step();
    window.addEventListener('resize', function () { resize(); init(); });
  }

  document.querySelectorAll('canvas.sm-canvas, #sm-canvas, #sm-slide-canvas').forEach(initCanvas);

  var year = document.getElementById('sm-footer-year');
  if (year) year.textContent = new Date().getFullYear();
})();
