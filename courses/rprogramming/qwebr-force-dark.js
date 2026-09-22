// quarto-webr's Monaco editors hardcode the 'vs-light' theme at creation
// and only switch to 'vs-dark' in response to a `quarto-dark` class
// appearing on <body> (see _extensions/coatless/webr/qwebr-theme-switch.js).
// That class is normally set by Quarto's light/dark theme TOGGLE, which
// this site doesn't use (single fixed dark theme), so it never fires and
// the code editor stays stuck with a white background. Force it instead:
// set the class once, then re-apply the theme switch for a few seconds
// to catch editors that mount asynchronously after webR loads.
(function () {
  document.body.classList.add('quarto-dark');

  var tries = 0;
  var timer = setInterval(function () {
    tries++;
    if (typeof updateMonacoEditorTheme === 'function') {
      updateMonacoEditorTheme();
    }
    if (tries >= 20) clearInterval(timer); // ~10s at 500ms
  }, 500);
})();
