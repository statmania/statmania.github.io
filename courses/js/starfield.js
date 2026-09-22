// Starfield / constellation canvas background for the games section hero.
// Shared copy of the animation used on the homepage (raw/index.qmd) so both
// look like the same site. Draws into every <canvas class="sm-canvas">.
(function () {
  function initCanvas(canvas) {
    if (!canvas || !canvas.getContext) return;
    var ctx = canvas.getContext('2d');
    var wrap = canvas.parentElement;
    var W, H, dpr;
    var particles = [];
    var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var count = Math.min(50, Math.floor((window.innerWidth || 1200) / 24));

    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = wrap.clientWidth;
      H = wrap.clientHeight;
      canvas.width = W * dpr;
      canvas.height = H * dpr;
      canvas.style.width = W + 'px';
      canvas.style.height = H + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function init() {
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

  document.querySelectorAll('canvas.sm-canvas').forEach(initCanvas);
})();
