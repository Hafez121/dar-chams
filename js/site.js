/* ==========================================================================
   Dar Chams — site behaviour
   Vanilla JS, no dependencies. Everything degrades: with JavaScript off the
   pages are complete, in English, with a plain navigation and a WhatsApp link.
   ========================================================================== */
(function () {
  "use strict";

  var STR = window.DC_STRINGS || { en: {}, ar: {} };
  var html = document.documentElement;
  var lang = html.dataset.lang === "ar" ? "ar" : "en";     // the single source of truth
  var originals = new WeakMap();                            // element -> English text
  var originalAttrs = new WeakMap();                        // element -> {attr: English value}

  function t(key) {
    var d = STR[lang] || {};
    return Object.prototype.hasOwnProperty.call(d, key) ? d[key] : null;
  }

  /* ------------------------------------------------------------ translate */
  function applyText() {
    var nodes = document.querySelectorAll("[data-i18n]");
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      if (!originals.has(el)) originals.set(el, el.textContent);
      var v = t(el.dataset.i18n);
      el.textContent = v !== null ? v : originals.get(el);
    }
  }

  function applyAttrs() {
    var nodes = document.querySelectorAll("[data-i18n-attr]");
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      var store = originalAttrs.get(el);
      if (!store) { store = {}; originalAttrs.set(el, store); }
      var pairs = el.dataset.i18nAttr.split(";");
      for (var j = 0; j < pairs.length; j++) {
        var bits = pairs[j].split(":");
        if (bits.length !== 2) continue;
        var attr = bits[0].trim(), key = bits[1].trim();
        if (!(attr in store)) store[attr] = el.getAttribute(attr) || "";
        var v = t(key);
        el.setAttribute(attr, v !== null ? v : store[attr]);
      }
    }
  }

  var originalTitle = document.title;
  var descTag = document.querySelector('meta[name="description"]');
  var originalDesc = descTag ? descTag.getAttribute("content") : "";

  function applyMeta() {
    var page = document.body.dataset.page || "home";
    var title = t("meta.title." + page);
    var desc = t("meta.desc." + page);
    document.title = title !== null ? title : originalTitle;
    if (descTag) descTag.setAttribute("content", desc !== null ? desc : originalDesc);
  }

  /* The language travels in the URL (?lang=ar), never in localStorage. */
  function syncLinks() {
    var links = document.querySelectorAll("a[href]");
    for (var i = 0; i < links.length; i++) {
      var a = links[i];
      var href = a.getAttribute("href");
      if (!href || /^(https?:|mailto:|tel:|#)/i.test(href)) continue;
      var hash = "", base = href;
      var h = href.indexOf("#");
      if (h > -1) { hash = href.slice(h); base = href.slice(0, h); }
      base = base.split("?")[0];
      a.setAttribute("href", base + (lang === "ar" ? "?lang=ar" : "") + hash);
    }
  }

  function syncUrl() {
    if (!window.history || !history.replaceState) return;
    var url = location.pathname + (lang === "ar" ? "?lang=ar" : "") + location.hash;
    history.replaceState(null, "", url);
  }

  function render() {
    html.lang = lang;
    html.dir = lang === "ar" ? "rtl" : "ltr";
    html.dataset.lang = lang;
    applyText();
    applyAttrs();
    applyMeta();
    syncLinks();
    syncWhatsAppFab();
    var toggle = document.getElementById("langToggle");
    if (toggle) {
      toggle.textContent = lang === "ar" ? "English" : "العربية";
      toggle.setAttribute("lang", lang === "ar" ? "en" : "ar");
      toggle.setAttribute("aria-label", lang === "ar"
        ? "تحويل الموقع إلى الإنكليزية"
        : "Switch the site to Arabic");
    }
  }

  function setLang(next) {
    lang = next === "ar" ? "ar" : "en";
    render();
    syncUrl();
  }

  /* ------------------------------------------------------- WhatsApp basics */
  /* DEMO NUMBER — +961 71 555 019 is fictional and used only for this concept
     demo. Replace WA_NUMBER (and every tel: link) with the real one. */
  var WA_NUMBER = "96171555019";

  function waUrl(text) {
    return "https://wa.me/" + WA_NUMBER + "?text=" + encodeURIComponent(text);
  }

  function syncWhatsAppFab() {
    var fab = document.querySelector("[data-wa-fab]");
    if (!fab) return;
    fab.setAttribute("href", waUrl(t("wa.opening") || "Hello Dar Chams — I'd like to ask about a stay."));
  }

  /* ------------------------------------------------------------ navigation */
  function initNav() {
    var toggle = document.getElementById("navToggle");
    var nav = document.getElementById("siteNav");
    if (!toggle || !nav) return;

    var isOpen = false;

    function focusables() {
      return nav.querySelectorAll("a[href], button:not([disabled])");
    }

    function open() {
      isOpen = true;
      nav.classList.add("is-open");
      toggle.setAttribute("aria-expanded", "true");
      document.body.classList.add("nav-open");
      var f = focusables();
      if (f.length) f[0].focus();
      document.addEventListener("keydown", onKeydown);
    }

    function close(returnFocus) {
      isOpen = false;
      nav.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
      document.body.classList.remove("nav-open");
      document.removeEventListener("keydown", onKeydown);
      if (returnFocus) toggle.focus();
    }

    function onKeydown(e) {
      if (e.key === "Escape") { close(true); return; }
      if (e.key !== "Tab") return;
      var f = focusables();
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }

    toggle.addEventListener("click", function () { isOpen ? close(true) : open(); });

    nav.addEventListener("click", function (e) {
      if (e.target.closest("a") && isOpen) close(false);
    });

    var wide = window.matchMedia("(min-width: 820px)");
    function onChange() { if (wide.matches && isOpen) close(false); }
    wide.addEventListener ? wide.addEventListener("change", onChange) : wide.addListener(onChange);
  }

  function markCurrent() {
    var here = location.pathname.split("/").pop() || "index.html";
    var links = document.querySelectorAll(".site-nav__list a");
    for (var i = 0; i < links.length; i++) {
      if (links[i].getAttribute("href").split("?")[0].split("#")[0] === here) {
        links[i].setAttribute("aria-current", "page");
      }
    }
  }

  /* ---------------------------------------------------------------- reveal */
  function initReveal() {
    if (!html.classList.contains("js-reveal") || !("IntersectionObserver" in window)) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.04 });
    var items = document.querySelectorAll(".reveal");
    for (var i = 0; i < items.length; i++) io.observe(items[i]);
  }

  /* ------------------------------------------------------------------ form */
  var MONTHS = {
    en: ["January", "February", "March", "April", "May", "June",
         "July", "August", "September", "October", "November", "December"],
    ar: ["كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران",
         "تموز", "آب", "أيلول", "تشرين الأول", "تشرين الثاني", "كانون الأول"]
  };

  function prettyDate(value) {
    var p = value.split("-");
    if (p.length !== 3) return value;
    var m = parseInt(p[1], 10) - 1;
    return parseInt(p[2], 10) + " " + (MONTHS[lang] || MONTHS.en)[m] + " " + p[0];
  }

  function todayISO() {
    var d = new Date();
    var m = String(d.getMonth() + 1).padStart(2, "0");
    var day = String(d.getDate()).padStart(2, "0");
    return d.getFullYear() + "-" + m + "-" + day;
  }

  function initForm() {
    var form = document.getElementById("enquiryForm");
    if (!form) return;

    var status = document.getElementById("formStatus");
    var fields = ["name", "checkin", "checkout", "guests", "room"];

    // stop people picking yesterday
    var today = todayISO();
    form.checkin.min = today;
    form.checkout.min = today;
    form.checkin.addEventListener("change", function () {
      if (form.checkin.value) form.checkout.min = form.checkin.value;
    });

    function showError(name, key) {
      var input = form.elements[name];
      var box = document.getElementById("err-" + name);
      input.setAttribute("aria-invalid", "true");
      if (box) {
        box.textContent = t("form.err." + key) || (STR.en["form.err." + key] || "Please check this field.");
        box.classList.add("is-shown");
      }
    }

    function clearError(name) {
      var input = form.elements[name];
      var box = document.getElementById("err-" + name);
      input.removeAttribute("aria-invalid");
      if (box) { box.textContent = ""; box.classList.remove("is-shown"); }
    }

    fields.forEach(function (name) {
      form.elements[name].addEventListener("input", function () { clearError(name); });
      form.elements[name].addEventListener("change", function () { clearError(name); });
    });

    function validate() {
      var bad = [];
      fields.forEach(clearError);

      var name = form.name.value.trim();
      if (name.length < 2) { showError("name", "name"); bad.push("name"); }

      var ci = form.checkin.value, co = form.checkout.value;
      if (!ci) { showError("checkin", "checkin"); bad.push("checkin"); }
      else if (ci < today) { showError("checkin", "past"); bad.push("checkin"); }

      if (!co) { showError("checkout", "checkout"); bad.push("checkout"); }
      else if (ci && co <= ci) { showError("checkout", "order"); bad.push("checkout"); }

      var g = parseInt(form.guests.value, 10);
      if (!form.guests.value || isNaN(g) || g < 1 || g > 6) { showError("guests", "guests"); bad.push("guests"); }

      if (!form.room.value) { showError("room", "room"); bad.push("room"); }

      return bad;
    }

    function compose() {
      var roomSelect = form.room;
      // "Garden Room — $95" reads better in a message as just "Garden Room"
      var roomLabel = roomSelect.options[roomSelect.selectedIndex].textContent.split("—")[0].trim();
      var parts = [
        t("wa.hello") || STR.en["wa.hello"],
        (t("wa.name") || STR.en["wa.name"]) + " " + form.name.value.trim() + ".",
        (t("wa.checkin") || STR.en["wa.checkin"]) + " " + prettyDate(form.checkin.value) + ".",
        (t("wa.checkout") || STR.en["wa.checkout"]) + " " + prettyDate(form.checkout.value) + ".",
        (t("wa.guests") || STR.en["wa.guests"]) + " " + form.guests.value + ".",
        (t("wa.room") || STR.en["wa.room"]) + " " + roomLabel + "."
      ];
      var note = form.message.value.trim();
      if (note) parts.push((t("wa.note") || STR.en["wa.note"]) + " " + note.replace(/\s+/g, " "));
      return parts.join(" ");
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();                       // nothing is ever POSTed anywhere
      status.textContent = "";
      var bad = validate();
      if (bad.length) {
        status.textContent = t("form.status.fix") || STR.en["form.status.fix"];
        form.elements[bad[0]].focus();
        return;
      }
      var url = waUrl(compose());
      status.textContent = t("form.status.opening") || STR.en["form.status.opening"];
      var win = window.open(url, "_blank", "noopener");
      var fallback = document.getElementById("waFallback");
      if (fallback) {
        fallback.setAttribute("href", url);
        if (!win) fallback.hidden = false;      // pop-up blocked: give them the link
      }
    });
  }

  /* ------------------------------------------------------------------ boot */
  var toggle = document.getElementById("langToggle");
  if (toggle) {
    toggle.addEventListener("click", function () { setLang(lang === "ar" ? "en" : "ar"); });
  }

  render();
  markCurrent();
  initNav();
  initReveal();
  initForm();

  var yr = document.getElementById("year");
  if (yr) yr.textContent = String(new Date().getFullYear());
})();
