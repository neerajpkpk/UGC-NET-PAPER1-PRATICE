document.addEventListener('DOMContentLoaded', function () {
  const questionsScript = document.getElementById('questions-data');
  const questionCard = document.getElementById('question-card');
  const resultCard = document.getElementById('result-card');
  const progressFill = document.getElementById('progress-fill');
  const questionCounter = document.getElementById('question-counter');
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  const skipBtn = document.getElementById('skip-btn');

  if (!questionsScript || !questionCard || !progressFill || !questionCounter || !prevBtn || !nextBtn || !skipBtn) {
    return;
  }

  const questions = JSON.parse(questionsScript.textContent);
  const state = {
    currentIndex: 0,
    answers: {},
    finished: false,
  };

  const optionLetters = ['A', 'B', 'C', 'D'];

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (character) => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;',
    })[character]);
  }

  const safeQuestionTags = new Set([
    'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'sup', 'sub',
    'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td',
  ]);

  function createSafeQuestionContent(markup) {
    let sourceMarkup = String(markup);
    const escapedSafeTag = /&lt;\/?(?:p|br|strong|b|em|i|u|sup|sub|ul|ol|li|table|thead|tbody|tfoot|tr|th|td)(?:\s[^&]*?)?&gt;/i;
    if (escapedSafeTag.test(sourceMarkup)) {
      const decoder = document.createElement('textarea');
      decoder.innerHTML = sourceMarkup;
      sourceMarkup = decoder.value;
    }

    const parsed = new DOMParser().parseFromString(sourceMarkup, 'text/html');
    const fragment = document.createDocumentFragment();

    function copyNode(source, target) {
      if (source.nodeType === Node.TEXT_NODE) {
        target.appendChild(document.createTextNode(source.textContent));
        return;
      }
      if (source.nodeType !== Node.ELEMENT_NODE) {
        return;
      }

      const tagName = source.tagName.toLowerCase();
      if (['script', 'style', 'iframe', 'object', 'svg', 'math'].includes(tagName)) {
        return;
      }

      let childTarget = target;
      if (safeQuestionTags.has(tagName)) {
        if (tagName === 'table') {
          const wrapper = document.createElement('div');
          wrapper.className = 'question-table-wrap';
          target.appendChild(wrapper);
          childTarget = wrapper;
        }

        const safeElement = document.createElement(tagName);
        if (['th', 'td'].includes(tagName)) {
          ['colspan', 'rowspan'].forEach((attribute) => {
            const value = Number.parseInt(source.getAttribute(attribute), 10);
            if (Number.isInteger(value) && value > 0 && value <= 20) {
              safeElement.setAttribute(attribute, String(value));
            }
          });
        }
        childTarget.appendChild(safeElement);
        childTarget = safeElement;
      }

      Array.from(source.childNodes).forEach((child) => copyNode(child, childTarget));
    }

    Array.from(parsed.body.childNodes).forEach((child) => copyNode(child, fragment));
    return fragment;
  }

  function updateProgress() {
    if (!questions.length) {
      progressFill.style.width = '0%';
      questionCounter.textContent = 'Question 0 / 0';
      prevBtn.disabled = true;
      prevBtn.style.opacity = '0.6';
      nextBtn.disabled = true;
      nextBtn.textContent = 'Next';
      return;
    }

    const progress = ((state.currentIndex + 1) / questions.length) * 100;
    progressFill.style.width = `${progress}%`;
    questionCounter.textContent = `Question ${state.currentIndex + 1} / ${questions.length}`;
    prevBtn.disabled = state.currentIndex === 0;
    prevBtn.style.opacity = state.currentIndex === 0 ? '0.6' : '1';
    skipBtn.disabled = !questions.length;
    nextBtn.disabled = false;
    nextBtn.textContent = state.currentIndex === questions.length - 1 ? 'Finish Practice' : 'Next';
  }

  function renderResults() {
    const attempted = Object.keys(state.answers).length;
    let correct = 0;

    questions.forEach((question) => {
      if (state.answers[question.id] === question.correct_answer) {
        correct += 1;
      }
    });

    const wrong = attempted - correct;
    const accuracy = attempted > 0 ? Math.round((correct / attempted) * 100) : 0;

    resultCard.innerHTML = `
      <h2>Practice Completed</h2>
      <div class="result-grid">
        <div class="result-item"><span>Total Questions</span><strong>${questions.length}</strong></div>
        <div class="result-item"><span>Attempted</span><strong>${attempted}</strong></div>
        <div class="result-item"><span>Correct</span><strong>${correct}</strong></div>
        <div class="result-item"><span>Wrong</span><strong>${wrong}</strong></div>
        <div class="result-item"><span>Accuracy</span><strong>${accuracy}%</strong></div>
        <div class="result-item"><span>Score</span><strong>${correct}/${questions.length}</strong></div>
      </div>
      <div class="result-actions">
        <button id="retry-practice" class="primary-btn" type="button">Retry Practice</button>
        <a href="${window.location.pathname.split('/practice/')[0]}" class="secondary-btn">Back to Subject</a>
      </div>
    `;

    resultCard.classList.remove('hidden');
    questionCard.classList.add('hidden');
    prevBtn.classList.add('hidden');
    nextBtn.classList.add('hidden');

    const retryBtn = document.getElementById('retry-practice');
    if (retryBtn) {
      retryBtn.addEventListener('click', function () {
        state.currentIndex = 0;
        state.answers = {};
        state.finished = false;
        resultCard.classList.add('hidden');
        questionCard.classList.remove('hidden');
        prevBtn.classList.remove('hidden');
        nextBtn.classList.remove('hidden');
        renderQuestion();
      });
    }
  }

  function renderQuestion() {
    if (state.finished) {
      return;
    }

    if (!questions.length) {
      questionCard.innerHTML = `
        <div class="empty-state">
          <p>No questions are available for this practice yet. Add questions from the admin panel.</p>
        </div>
      `;
      resultCard.classList.add('hidden');
      prevBtn.disabled = true;
      skipBtn.disabled = true;
      nextBtn.disabled = true;
      updateProgress();
      return;
    }

    const currentQuestion = questions[state.currentIndex];
    if (!currentQuestion) {
      state.currentIndex = 0;
      renderQuestion();
      return;
    }

    const selectedOption = state.answers[currentQuestion.id];
    const reviewed = typeof selectedOption !== 'undefined';
    const examDateLabel = currentQuestion.exam_date ? escapeHtml(currentQuestion.exam_date) : '';

    let html = `
      <div class="question-meta">
        <span class="badge">${currentQuestion.question_type === 'PYQ' ? `PYQ${examDateLabel ? ` • ${examDateLabel}` : ''}${currentQuestion.pyq_year ? ` • ${currentQuestion.pyq_year}` : ''}${currentQuestion.shift ? ` • ${currentQuestion.shift} Shift` : ''}` : 'Practice'}</span>
        <span class="badge subtle">${currentQuestion.difficulty}</span>
      </div>
      <div class="question-content"></div>
      <div class="option-group">
    `;

    optionLetters.forEach((letter) => {
      const optionValue = currentQuestion[`option_${letter.toLowerCase()}`];
      const isSelected = selectedOption === letter;
      let classes = 'option-btn';

      if (reviewed) {
        if (letter === currentQuestion.correct_answer) {
          classes += ' correct';
        }
        if (isSelected && letter !== currentQuestion.correct_answer) {
          classes += ' incorrect';
        }
      } else if (isSelected) {
        classes += ' selected';
      }

      html += `
        <button type="button" class="${classes}" data-option="${letter}" ${reviewed ? 'disabled' : ''}>
          <span class="option-letter">${letter}</span>
          <span>${optionValue}</span>
        </button>
      `;
    });

    html += '</div>';

    if (reviewed) {
      const isCorrect = selectedOption === currentQuestion.correct_answer;
      html += `
        <div class="feedback ${isCorrect ? 'correct' : 'wrong'}">
          ${isCorrect ? '✓ Correct' : '✗ Wrong'}
        </div>
        <div class="explanation-panel">
          <h4>Explanation</h4>
          <div class="explanation-text"></div>
        </div>
      `;
    }

    questionCard.innerHTML = html;
    questionCard.querySelector('.question-content').appendChild(
      createSafeQuestionContent(currentQuestion.question_text)
    );
    const explanationText = questionCard.querySelector('.explanation-text');
    if (explanationText) {
      explanationText.appendChild(
        createSafeQuestionContent(currentQuestion.explanation || '')
      );
    }
    updateProgress();
  }

  prevBtn.addEventListener('click', function () {
    if (state.currentIndex > 0) {
      state.currentIndex -= 1;
      renderQuestion();
    }
  });

  function moveToNextQuestion() {
    if (state.currentIndex === questions.length - 1) {
      state.finished = true;
      renderResults();
      return;
    }

    state.currentIndex += 1;
    renderQuestion();
  }

  nextBtn.addEventListener('click', function () {
    const currentQuestion = questions[state.currentIndex];
    const hasAnswered = typeof state.answers[currentQuestion.id] !== 'undefined';

    if (hasAnswered) {
      moveToNextQuestion();
      return;
    }

    moveToNextQuestion();
  });

  skipBtn.addEventListener('click', function () {
    moveToNextQuestion();
  });

  questionCard.addEventListener('click', function (event) {
    const optionButton = event.target.closest('.option-btn');
    if (!optionButton) {
      return;
    }

    const currentQuestion = questions[state.currentIndex];
    if (typeof state.answers[currentQuestion.id] !== 'undefined') {
      return;
    }

    state.answers[currentQuestion.id] = optionButton.dataset.option;
    renderQuestion();
  });

  renderQuestion();
});
