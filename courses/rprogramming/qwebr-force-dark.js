// quarto-webr's Monaco editors hardcode the 'vs-light' theme at creation
// and only switch to 'vs-dark' via updateMonacoEditorTheme() (see
// _extensions/coatless/webr/qwebr-theme-switch.js), which itself only
// runs in response to a `quarto-dark` class appearing on <body> — a class
// Quarto's light/dark theme TOGGLE sets, which this site doesn't use
// (single fixed dark theme).
//
// Don't set that class ourselves: Quarto's own dark-mode CSS reacts to it
// too (e.g. `body.quarto-dark .light-content { display: none; }`, which
// hid the navbar logo the first time this was tried, since no dark-mode
// logo variant is configured). Instead, bypass the class-driven helper
// entirely and set each Monaco instance's theme directly, polling for a
// few seconds to catch editors that mount asynchronously after webR loads.
(function () {
  var tries = 0;
  var timer = setInterval(function () {
    tries++;
    (window.qwebrEditorInstances || []).forEach(function (editor) {
      if (editor && typeof editor.updateOptions === 'function') {
        editor.updateOptions({ theme: 'vs-dark' });
      }
    });
    if (tries >= 20) clearInterval(timer); // ~10s at 500ms
  }, 500);
})();
