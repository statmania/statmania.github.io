/* Stat Mania blog: dynamic sidebar widgets, post extras, tags page and author pages.
 *
 * All data comes from site-data.js (a script file, so it also works when a page is
 * opened straight from disk), which scripts/build_site_data.py rewrites on
 * every `quarto render` (even of a single post). Nothing here is baked into pages,
 * so a new or retagged post shows up everywhere on the next page load.
 * Loaded on every page by _site-include.html. Hand-written: edit freely.
 */
(function () {
  var me = document.currentScript;
  var base = (me && me.dataset.base) || '';
  var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                'August', 'September', 'October', 'November', 'December'];
  var small = window.matchMedia('(max-width: 991.98px)');

  // ---------- tiny helpers ----------
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function link(href, text, cls) {
    var a = el('a', cls, text);
    a.href = href;
    return a;
  }
  function tagHref(t) { return base + 'tags.html#tag=' + encodeURIComponent(t); }
  function ready(fn) {
    if (document.readyState === 'complete') fn();
    else window.addEventListener('load', fn);
  }
  function counter(list) {
    var c = {};
    list.forEach(function (x) { c[x] = (c[x] || 0) + 1; });
    return c;
  }
  function byCount(c) {
    return Object.keys(c).sort(function (a, b) { return c[b] - c[a] || a.localeCompare(b); });
  }

  // ---------- "On this page" for small screens (needs no data) ----------
  function mobileToc() {
    var toc = document.querySelector('#quarto-margin-sidebar #TOC');
    var main = document.getElementById('quarto-document-content');
    if (!toc || !main || !toc.querySelector('a[href^="#"]')) return;
    var box = el('details', 'sm-toc-mobile');
    var sum = el('summary', null, 'On this page');
    var nav = el('nav');
    nav.setAttribute('aria-label', 'On this page');
    var links = [];
    toc.querySelectorAll('a[href^="#"]').forEach(function (src) {
      var a = link(src.getAttribute('href'), src.textContent);
      a.addEventListener('click', function () { box.open = false; });
      nav.appendChild(a);
      links.push(a);
    });
    box.appendChild(sum);
    box.appendChild(nav);
    main.insertBefore(box, main.firstChild);
    var heads = links.map(function (a) { return document.getElementById(decodeURIComponent(a.hash.slice(1))); });
    function spy() {
      var cur = 0;
      heads.forEach(function (h, i) { if (h && h.getBoundingClientRect().top < 120) cur = i; });
      links.forEach(function (a, i) { a.classList.toggle('active', i === cur); });
      sum.textContent = 'On this page · ' + (links[cur] ? links[cur].textContent : '');
    }
    window.addEventListener('scroll', spy, {passive: true});
    spy();
  }

  // ---------- data ----------
  function prepare(data) {
    var posts = data.posts.slice().sort(function (a, b) { return a.date < b.date ? 1 : -1; });
    var authors = {}, byName = {};
    Object.keys(data.authors || {}).forEach(function (slug) {
      var a = data.authors[slug];
      a.slug = slug;
      a.posts = [];
      authors[slug] = a;
      [a.name].concat(a.aliases || []).forEach(function (n) { byName[n.toLowerCase()] = a; });
    });
    posts.forEach(function (p) {
      var a = byName[(p.author || '').toLowerCase()];
      if (a) a.posts.push(p);
    });
    return {posts: posts, authors: authors, byName: byName};
  }
  function postHref(p) { return base + p.href; }
  function postItem(p) {
    var li = el('li');
    li.appendChild(link(postHref(p), p.title));
    li.appendChild(el('span', 'sm-tp-date', p.date));
    if (p.desc) li.appendChild(el('p', null, p.desc));
    return li;
  }

  // ---------- sidebar: archive + tag cloud ----------
  function archive(posts) {
    var years = {};
    posts.forEach(function (p) {
      var y = +p.date.slice(0, 4), m = +p.date.slice(5, 7);
      ((years[y] = years[y] || {})[m] = years[y][m] || []).push(p);
    });
    var nav = el('nav', 'sm-widget sm-archive');
    nav.setAttribute('aria-label', 'Post archive');
    nav.appendChild(el('h3', 'sm-widget-title', 'Archive'));
    Object.keys(years).sort(function (a, b) { return b - a; }).forEach(function (y, i) {
      var n = 0;
      Object.keys(years[y]).forEach(function (m) { n += years[y][m].length; });
      var yd = el('details', 'sm-year');
      yd.open = i === 0;
      var ys = el('summary', null, y + ' ');
      ys.appendChild(el('span', 'sm-count', n));
      yd.appendChild(ys);
      Object.keys(years[y]).sort(function (a, b) { return b - a; }).forEach(function (m) {
        var items = years[y][m];
        var md = el('details', 'sm-month');
        var ms = el('summary', null, MONTHS[m - 1] + ' ');
        ms.appendChild(el('span', 'sm-count', items.length));
        md.appendChild(ms);
        var ul = el('ul');
        items.forEach(function (p) {
          var li = el('li');
          li.appendChild(link(postHref(p), p.title));
          ul.appendChild(li);
        });
        md.appendChild(ul);
        yd.appendChild(md);
      });
      nav.appendChild(yd);
    });
    return nav;
  }
  function chips(counts, active) {
    var keys = byCount(counts);
    var lo = counts[keys[keys.length - 1]], hi = counts[keys[0]];
    var frag = document.createDocumentFragment();
    keys.forEach(function (t) {
      var size = 0.78 + (hi > lo ? 0.5 * (counts[t] - lo) / (hi - lo) : 0);
      var a = link(tagHref(t), t + ' ', 'sm-tag');
      a.dataset.tag = t;
      a.style.fontSize = size.toFixed(2) + 'rem';
      a.appendChild(el('span', 'sm-count', counts[t]));
      if (t === active) a.classList.add('active');
      frag.appendChild(a);
    });
    return frag;
  }
  function tagCounts(posts) {
    var all = [];
    posts.forEach(function (p) { new Set(p.tags).forEach(function (t) { all.push(t); }); });
    return counter(all);
  }
  function cloud(posts) {
    var sec = el('section', 'sm-widget sm-tags');
    sec.setAttribute('aria-label', 'Tag cloud');
    sec.appendChild(el('h3', 'sm-widget-title', 'Tags'));
    var box = el('div', 'sm-tag-cloud');
    box.appendChild(chips(tagCounts(posts)));
    sec.appendChild(box);
    return sec;
  }
  function sidebarWidgets(D) {
    var side = document.getElementById('quarto-margin-sidebar');
    var main = document.getElementById('quarto-document-content');
    if (!side) return;
    var w = el('div');
    w.id = 'sm-widgets';
    w.appendChild(archive(D.posts));
    w.appendChild(cloud(D.posts));
    // Posts on small screens: Quarto hides the sidebar, so widgets go under the article.
    function place() {
      var bottom = small.matches && side.querySelector('#TOC') && main;
      w.classList.toggle('sm-widgets-bottom', !!bottom);
      (bottom ? main : side).appendChild(w);
    }
    place();
    if (small.addEventListener) small.addEventListener('change', place);
  }

  // ---------- post page extras ----------
  function related(D, me, k) {
    var feats = function (p) { return p.tags.concat(p.cats.map(function (c) { return 'cat:' + c; })); };
    var df = {}, n = D.posts.length;
    D.posts.forEach(function (p) { new Set(feats(p)).forEach(function (f) { df[f] = (df[f] || 0) + 1; }); });
    var mine = new Set(feats(me)), scored = [];
    D.posts.forEach(function (q) {
      if (q === me) return;
      var s = 0;
      new Set(feats(q)).forEach(function (f) {
        if (mine.has(f)) s += Math.log(n / df[f]) * (f.indexOf('cat:') === 0 ? 0.5 : 1);
      });
      if (s > 0) scored.push([s, q]);
    });
    scored.sort(function (a, b) { return b[0] - a[0] || (a[1].date < b[1].date ? 1 : -1); });
    return scored.slice(0, k).map(function (x) { return x[1]; });
  }
  function authorCard(a) {
    var card = el('aside', 'sm-author-card');
    if (a.image) {
      var img = el('img', 'sm-author-img');
      img.src = base + a.image;
      img.alt = '';
      card.appendChild(img);
    }
    var body = el('div');
    body.appendChild(el('div', 'sm-author-card-name', a.name));
    body.appendChild(el('p', null, a.tagline || a.bio));
    body.appendChild(link(base + 'authors/' + a.slug + '.html',
      'All ' + a.posts.length + ' posts by ' + a.name + ' →', 'sm-author-more'));
    card.appendChild(body);
    return card;
  }
  function authorLink(node, a) {
    var k = link(base + 'authors/' + a.slug + '.html', node.textContent.trim(), 'sm-author-link');
    // homepage cards sit inside one big <a>; navigate ourselves so the author link wins
    k.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); location.href = k.href; });
    node.textContent = '';
    node.appendChild(k);
  }
  function postExtras(D) {
    var main = document.getElementById('quarto-document-content');
    var file = location.pathname.split('/').pop();
    var me = D.posts.filter(function (p) { return p.href.split('/').pop() === file; })[0];
    if (!me || !main || !/\/posts\//.test(location.pathname)) return;

    // byline -> author page
    document.querySelectorAll('.quarto-title-meta-heading').forEach(function (h) {
      if (!/^authors?$/i.test(h.textContent.trim())) return;
      h.nextElementSibling.querySelectorAll('p').forEach(function (p) {
        var a = D.byName[p.textContent.trim().toLowerCase()];
        if (a) authorLink(p, a);
      });
    });
    // tags
    if (me.tags.length) {
      var row = el('div', 'sm-post-tags');
      row.appendChild(el('span', 'sm-post-tags-label', 'Tags'));
      me.tags.forEach(function (t) { row.appendChild(link(tagHref(t), t, 'sm-tag')); });
      main.appendChild(row);
    }
    // related posts
    var rel = related(D, me, 5);
    if (rel.length) {
      var box = el('section', 'sm-related');
      box.appendChild(el('h2', null, 'Related posts'));
      var ul = el('ul', 'sm-post-list');
      rel.forEach(function (p) { ul.appendChild(postItem(p)); });
      box.appendChild(ul);
      main.appendChild(box);
    }
    // author card
    var au = D.byName[(me.author || '').toLowerCase()];
    if (au) main.appendChild(authorCard(au));
  }
  function homepageBylines(D) {
    document.querySelectorAll('.listing-author').forEach(function (n) {
      var a = D.byName[n.textContent.trim().toLowerCase()];
      if (a) authorLink(n, a);
    });
  }

  // ---------- pager (shared by tags page and author pages) ----------
  function pager(nav, pages, page, onPage) {
    nav.textContent = '';
    nav.hidden = pages < 2;
    function btn(label, n, cur, off) {
      var b = el('button', 'sm-page' + (cur ? ' active' : ''), label);
      b.type = 'button';
      b.disabled = !!off;
      if (cur) b.setAttribute('aria-current', 'page');
      b.addEventListener('click', function () { onPage(n); });
      nav.appendChild(b);
    }
    btn('‹ Prev', page - 1, false, page === 1);
    for (var i = 1; i <= pages; i++) btn(String(i), i, i === page, false);
    btn('Next ›', page + 1, false, page === pages);
  }
  function hashParams() { return new URLSearchParams(location.hash.slice(1)); }

  // ---------- tags page ----------
  function tagsPage(D) {
    var root = document.getElementById('sm-tags-page');
    if (!root) return;
    var side = document.getElementById('sm-tags-side');
    var counts = tagCounts(D.posts), per = 10;
    var hint = el('p', 'sm-tags-hint', 'Pick a tag to see its posts.');
    var sec = el('section', 'sm-tag-section');
    var nav = el('nav', 'sm-pager');
    nav.setAttribute('aria-label', 'Pagination');
    root.append(hint, sec, nav);
    function render() {
      var h = hashParams(), tag = h.get('tag') || '';
      var list = tag ? D.posts.filter(function (p) { return p.tags.indexOf(tag) > -1; }) : [];
      if (side) {
        side.textContent = '';
        side.appendChild(el('h3', 'sm-widget-title', 'Tags'));
        var box = el('div', 'sm-tag-cloud');
        box.appendChild(chips(counts, tag));
        side.appendChild(box);
      }
      hint.hidden = list.length > 0;
      sec.hidden = !list.length;
      sec.textContent = '';
      nav.hidden = true;
      if (!list.length) return;
      var pages = Math.ceil(list.length / per);
      var page = Math.min(Math.max(+h.get('page') || 1, 1), pages);
      var title = el('h2', null, tag + ' ');
      title.appendChild(el('span', 'sm-count', list.length + (list.length === 1 ? ' post' : ' posts')));
      var ul = el('ul', 'sm-post-list');
      list.slice((page - 1) * per, page * per).forEach(function (p) { ul.appendChild(postItem(p)); });
      sec.append(title, ul);
      pager(nav, pages, page, function (n) {
        location.hash = 'tag=' + encodeURIComponent(tag) + (n > 1 ? '&page=' + n : '');
      });
    }
    window.addEventListener('hashchange', render);
    render();
  }

  // ---------- author page ----------
  function authorPage(D) {
    var root = document.getElementById('sm-author-root');
    if (!root) return;
    var a = D.authors[root.dataset.slug];
    if (!a) return;
    var posts = a.posts, per = 10;
    function opts(label, counts) {
      var s = el('select');
      s.appendChild(new Option(label, ''));
      byCount(counts).forEach(function (k) { s.appendChild(new Option(k + ' (' + counts[k] + ')', k)); });
      return s;
    }
    var allCats = [], allTags = [];
    posts.forEach(function (p) {
      new Set(p.cats).forEach(function (c) { allCats.push(c); });
      new Set(p.tags).forEach(function (t) { allTags.push(t); });
    });
    var selCat = opts('All categories', counter(allCats)), selTag = opts('All tags', counter(allTags));
    var bar = el('div', 'sm-filter-bar');
    var l1 = el('label', null, 'Category '), l2 = el('label', null, 'Tag ');
    l1.appendChild(selCat); l2.appendChild(selTag);
    var count = el('span', 'sm-filter-count');
    count.setAttribute('aria-live', 'polite');
    bar.append(l1, l2, count);
    var ul = el('ul', 'sm-post-list');
    var nav = el('nav', 'sm-pager');
    nav.setAttribute('aria-label', 'Pagination');
    root.append(bar, ul, nav);

    var st = {cat: '', tag: '', page: 1};
    function read() {
      var h = hashParams();
      selCat.value = h.get('cat') || ''; selTag.value = h.get('tag') || '';
      st.cat = selCat.value; st.tag = selTag.value; st.page = +h.get('page') || 1;
    }
    function write() {
      var h = new URLSearchParams();
      if (st.cat) h.set('cat', st.cat);
      if (st.tag) h.set('tag', st.tag);
      if (st.page > 1) h.set('page', st.page);
      history.replaceState(null, '', location.pathname + (h.toString() ? '#' + h : ''));
    }
    function render() {
      var hit = posts.filter(function (p) {
        return (!st.cat || p.cats.indexOf(st.cat) > -1) && (!st.tag || p.tags.indexOf(st.tag) > -1);
      });
      var pages = Math.max(1, Math.ceil(hit.length / per));
      st.page = Math.min(Math.max(st.page, 1), pages);
      ul.textContent = '';
      hit.slice((st.page - 1) * per, st.page * per).forEach(function (p) { ul.appendChild(postItem(p)); });
      count.textContent = hit.length + ' of ' + posts.length + ' posts';
      pager(nav, pages, st.page, function (n) {
        st.page = n; write(); render();
        root.scrollIntoView({behavior: 'smooth'});
      });
    }
    function change() { st.cat = selCat.value; st.tag = selTag.value; st.page = 1; write(); render(); }
    selCat.addEventListener('change', change);
    selTag.addEventListener('change', change);
    window.addEventListener('hashchange', function () { read(); render(); });
    read(); render();
  }

  // ---------- go ----------
  mobileToc();
  function start(raw) {
    var D = prepare(raw);
    tagsPage(D);
    authorPage(D);
    homepageBylines(D);
    ready(function () {
      // after load, so Quarto has already copied the TOC into its own structures
      postExtras(D);
      sidebarWidgets(D);
    });
  }
  if (window.SM_DATA) start(window.SM_DATA);
  else {
    var ds = document.createElement('script');
    ds.src = base + 'site-data.js';
    ds.onload = function () { start(window.SM_DATA); };
    ds.onerror = function () { console.warn('site.js: could not load site-data.js'); };
    document.head.appendChild(ds);
  }
})();
