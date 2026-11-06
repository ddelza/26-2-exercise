(function () {
  var KEY = 'ox26-2-v1';

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; }
  }
  function save(s) {
    try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) { /* 저장이 막혀도 문제는 풀 수 있다 */ }
  }

  // 개념 페이지: 문제에서 왔으면 돌아가는 단추를 보여 준다.
  var back = document.getElementById('back');
  if (back) {
    var m = /[?&]from=(q\d{3})/.exec(location.search);
    if (m) {
      back.href = 'ox.html#' + m[1];
      back.textContent = Number(m[1].slice(1)) + '번 문제로 돌아가기';
      back.hidden = false;
    }
    return;
  }

  var qs = Array.prototype.slice.call(document.querySelectorAll('.q'));
  if (!qs.length) return;
  var state = load();
  var filter = 'all';
  var showAll = false;

  function mark(q) {
    var v = state[q.id];
    var ans = q.dataset.a;
    var sol = q.querySelector('.sol');
    var btns = q.querySelectorAll('.btns button');
    q.classList.remove('right', 'wrong');
    btns.forEach(function (b) {
      b.classList.toggle('sel', b.dataset.v === v);
      b.disabled = !!v;
    });
    var res = q.querySelector('.res');
    if (v) {
      q.classList.add(v === ans ? 'right' : 'wrong');
      res.textContent = (v === ans ? '맞았습니다.' : '틀렸습니다.') + ' 정답은 ' + ans + '입니다.';
    } else {
      res.textContent = '정답은 ' + ans + '입니다.';
    }
    sol.hidden = !(v || showAll);
    q.querySelector('.again').hidden = !v;
  }

  function summary() {
    var done = 0, right = 0, per = {};
    qs.forEach(function (q) {
      var u = q.dataset.unit;
      per[u] = per[u] || { n: 0, d: 0 };
      per[u].n++;
      var v = state[q.id];
      if (v) { done++; per[u].d++; if (v === q.dataset.a) right++; }
    });
    document.getElementById('done').textContent = done;
    document.getElementById('right').textContent = right;
    document.getElementById('meter').style.width = (done / qs.length * 100) + '%';
    document.querySelectorAll('[data-prog]').forEach(function (el) {
      var p = per[el.dataset.prog];
      el.textContent = p.d ? p.d + '/' + p.n + '문제' : p.n + '문제';
    });
  }

  function applyFilter() {
    var shown = 0;
    qs.forEach(function (q) {
      var v = state[q.id];
      var ok = filter === 'all' || (filter === 'todo' && !v) || (filter === 'wrong' && v && v !== q.dataset.a);
      q.classList.toggle('off', !ok);
      if (ok) shown++;
    });
    document.querySelectorAll('.unit').forEach(function (u) {
      u.classList.toggle('none', !u.querySelector('.q:not(.off)'));
    });
    document.getElementById('empty').hidden = shown > 0;
  }

  qs.forEach(function (q) {
    q.querySelectorAll('.btns button').forEach(function (b) {
      b.addEventListener('click', function () {
        state[q.id] = b.dataset.v;
        save(state);
        mark(q);
        summary();
      });
    });
    q.querySelector('.again').addEventListener('click', function () {
      delete state[q.id];
      save(state);
      mark(q);
      summary();
      q.querySelector('.btns button').focus();
    });
    mark(q);
  });

  document.querySelectorAll('[data-f]').forEach(function (b) {
    b.addEventListener('click', function () {
      filter = b.dataset.f;
      document.querySelectorAll('[data-f]').forEach(function (o) {
        o.setAttribute('aria-pressed', String(o === b));
      });
      applyFilter();
    });
  });

  var sa = document.getElementById('showall');
  sa.addEventListener('click', function () {
    showAll = !showAll;
    sa.setAttribute('aria-pressed', String(showAll));
    qs.forEach(mark);
  });

  document.getElementById('reset').addEventListener('click', function () {
    if (!confirm('푼 기록을 모두 지울까요?')) return;
    state = {};
    save(state);
    qs.forEach(mark);
    summary();
    applyFilter();
  });

  summary();
})();
