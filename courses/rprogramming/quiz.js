// Lightweight, self-contained quiz component for R course lessons.
// Two quiz types, both graded entirely client-side (no server, no R needed):
//   data-quiz="mcq"  — single-choice: radio inputs, data-answer holds the
//                       correct <input value>, matched case-insensitively.
//   data-quiz="fitb" — fill-in-the-blank exact answer: a text input inside
//                       .sm-quiz-blank, data-answer holds the exact string
//                       (e.g. an R function name), matched after trimming.
// Markup contract: a .sm-quiz-check button triggers grading, results render
// into .sm-quiz-feedback, and a correct answer adds .sm-quiz-correct to the
// container so the "Check Answer" button can be visually retired.
(function () {
  function normalize(s) {
    return (s || '').trim();
  }

  function setFeedback(quiz, ok, correctText) {
    var fb = quiz.querySelector('.sm-quiz-feedback');
    if (!fb) return;
    if (ok) {
      fb.innerHTML = '<i class="fa-solid fa-circle-check"></i> Correct!';
      fb.className = 'sm-quiz-feedback sm-quiz-feedback-ok';
      quiz.classList.add('sm-quiz-correct');
    } else {
      fb.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> Not quite — try again.' +
        (correctText ? '' : '');
      fb.className = 'sm-quiz-feedback sm-quiz-feedback-bad';
    }
  }

  function gradeMcq(quiz) {
    var answer = normalize(quiz.getAttribute('data-answer')).toLowerCase();
    var checked = quiz.querySelector('input[type="radio"]:checked');
    quiz.querySelectorAll('.sm-quiz-options label').forEach(function (l) {
      l.classList.remove('sm-quiz-picked');
    });
    if (!checked) {
      setFeedback(quiz, false);
      var fb = quiz.querySelector('.sm-quiz-feedback');
      if (fb) { fb.textContent = 'Pick an option first.'; fb.className = 'sm-quiz-feedback sm-quiz-feedback-bad'; }
      return;
    }
    checked.closest('label').classList.add('sm-quiz-picked');
    var ok = normalize(checked.value).toLowerCase() === answer;
    setFeedback(quiz, ok);
  }

  function gradeFitb(quiz) {
    var answer = normalize(quiz.getAttribute('data-answer'));
    var input = quiz.querySelector('.sm-quiz-blank');
    if (!input) return;
    var ok = normalize(input.value) === answer;
    input.classList.toggle('sm-quiz-blank-ok', ok);
    input.classList.toggle('sm-quiz-blank-bad', !ok);
    setFeedback(quiz, ok);
  }

  function wire(quiz) {
    var type = quiz.getAttribute('data-quiz');
    var btn = quiz.querySelector('.sm-quiz-check');
    if (!btn) return;
    btn.addEventListener('click', function () {
      if (type === 'mcq') gradeMcq(quiz);
      else if (type === 'fitb') gradeFitb(quiz);
    });
    var fitbInput = quiz.querySelector('.sm-quiz-blank');
    if (fitbInput) {
      fitbInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') { e.preventDefault(); gradeFitb(quiz); }
      });
    }
  }

  document.querySelectorAll('.sm-quiz[data-quiz]').forEach(wire);
})();
