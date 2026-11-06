(function () {
  var KEY = 'ox26-2-v1';

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; }
  }
  function save(s) {
    try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) { /* 저장이 막혀도 문제는 풀 수 있다 */ }
  }

  // 고정된 상단바 높이만큼 링크 이동 위치를 내린다.
  var stick = document.getElementById('stick');
  function setStick() {
    document.documentElement.style.setProperty('--sh', stick.offsetHeight + 'px');
  }
  setStick();
  window.addEventListener('resize', setStick);

  // 지금 사용 중인 인원: 브라우저마다 임의 번호로 30초마다 신호를 보내고, 70초 안에 신호를 보낸 수를 센다.
  (function online() {
    var URL_ = 'https://gwangsu-on-default-rtdb.firebaseio.com/years/2026/ox26Online';
    var LIVE = 70000, OLD = 600000, EVERY = 30000;
    var box = document.getElementById('online');
    var num = document.getElementById('onlineN');
    var todayBox = document.getElementById('today');
    var todayNum = document.getElementById('todayN');
    var VISITS = 'https://gwangsu-on-default-rtdb.firebaseio.com/years/2026/ox26Visits/';
    var counted = '';
    var id;
    try {
      id = localStorage.getItem('ox26-id');
      if (!id) { id = newId(); localStorage.setItem('ox26-id', id); }
    } catch (e) { id = newId(); }
    function newId() { return 'b' + Math.random().toString(36).slice(2, 12); }

    // 오늘 방문자: 한국 날짜별로 브라우저 번호를 한 번씩 남기고 그 수를 센다.
    function visits(now) {
      var day = new Date(now + 9 * 3600000).toISOString().slice(0, 10);
      var url = VISITS + day;
      var mark = counted === day ? Promise.resolve() :
        fetch(url + '/' + id + '.json', { method: 'PUT', body: 'true' }).then(function () { counted = day; });
      return mark.then(function () {
        return fetch(url + '.json?shallow=true');
      }).then(function (r) { return r.json(); }).then(function (all) {
        todayNum.textContent = Object.keys(all || {}).length;
        todayBox.hidden = false;
      });
    }

    function beat() {
      if (document.hidden) return;
      fetch(URL_ + '/' + id + '.json', { method: 'PUT', body: '{"ts":{".sv":"timestamp"}}' })
        .then(function (r) { return r.json(); })
        .then(function (me) {
          return fetch(URL_ + '.json').then(function (r) { return r.json(); }).then(function (all) {
            var n = 0;
            Object.keys(all || {}).forEach(function (k) {
              var age = me.ts - ((all[k] && all[k].ts) || 0);
              if (age < LIVE) n++;
              else if (age > OLD && Math.random() < 0.2) fetch(URL_ + '/' + k + '.json', { method: 'DELETE' });
            });
            num.textContent = n;
            box.hidden = false;
            return visits(me.ts);
          });
        })
        .catch(function () { box.hidden = true; });
    }
    beat();
    setInterval(beat, EVERY);
    document.addEventListener('visibilitychange', beat);
  })();

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
