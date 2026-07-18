// Calculator Euphoria — shared site behavior (theme toggle, mobile nav, FAQ accordions, homepage search/filter)

// Registry of every calculator, used for the homepage hero search.
// Keep in sync with the cards rendered in index.html.
var CALCULATORS = [
  { name: "Percentage Calculator", url: "/calculators/percentage-calculator.html", category: "Math" },
  { name: "Scientific Calculator", url: "/calculators/scientific-calculator.html", category: "Math" },
  { name: "GPA Calculator", url: "/calculators/gpa-calculator.html", category: "Math" },
  { name: "Fraction Calculator", url: "/calculators/fraction-calculator.html", category: "Math" },
  { name: "Mortgage Calculator", url: "/calculators/mortgage-calculator.html", category: "Finance" },
  { name: "Loan Calculator", url: "/calculators/loan-calculator.html", category: "Finance" },
  { name: "Compound Interest Calculator", url: "/calculators/compound-interest-calculator.html", category: "Finance" },
  { name: "Tip Calculator", url: "/calculators/tip-calculator.html", category: "Finance" },
  { name: "Discount Calculator", url: "/calculators/discount-calculator.html", category: "Finance" },
  { name: "Sales Tax Calculator", url: "/calculators/sales-tax-calculator.html", category: "Finance" },
  { name: "Simple Interest Calculator", url: "/calculators/simple-interest-calculator.html", category: "Finance" },
  { name: "BMI Calculator", url: "/calculators/bmi-calculator.html", category: "Health" },
  { name: "Calorie Calculator", url: "/calculators/calorie-calculator.html", category: "Health" },
  { name: "Sleep Calculator", url: "/calculators/sleep-calculator.html", category: "Health" },
  { name: "Age Calculator", url: "/calculators/age-calculator.html", category: "Everyday" },
  { name: "Unit Converter", url: "/calculators/unit-converter.html", category: "Everyday" },
  { name: "Date Calculator", url: "/calculators/date-calculator.html", category: "Everyday" },
  { name: "Aspect Ratio Calculator", url: "/calculators/aspect-ratio-calculator.html", category: "Everyday" }
];

(function () {
  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    initThemeToggle();
    initMobileNav();
    initFaqAccordions();
    initHeroSearch();
    initCategoryPills();
  });

  function initThemeToggle() {
    var btn = document.querySelector("[data-theme-toggle]");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var current = document.documentElement.getAttribute("data-theme");
      var prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
      var isDark = current ? current === "dark" : prefersDark;
      var next = isDark ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
    });
  }

  function initMobileNav() {
    var toggle = document.querySelector("[data-nav-toggle]");
    var nav = document.querySelector(".site-header nav");
    if (!toggle || !nav) return;
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("mobile-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  function initFaqAccordions() {
    var questions = document.querySelectorAll(".faq-q");
    questions.forEach(function (q) {
      q.addEventListener("click", function () {
        var item = q.closest(".faq-item");
        if (!item) return;
        var wasOpen = item.classList.contains("open");
        item.parentElement.querySelectorAll(".faq-item.open").forEach(function (openItem) {
          if (openItem !== item) openItem.classList.remove("open");
        });
        item.classList.toggle("open", !wasOpen);
      });
    });
  }

  function initHeroSearch() {
    var input = document.querySelector("[data-hero-search]");
    var results = document.querySelector("[data-search-results]");
    if (!input || !results) return;

    function render(query) {
      var q = query.trim().toLowerCase();
      if (!q) {
        results.classList.remove("show");
        results.innerHTML = "";
        return;
      }
      var matches = CALCULATORS.filter(function (c) {
        return c.name.toLowerCase().indexOf(q) !== -1 || c.category.toLowerCase().indexOf(q) !== -1;
      }).slice(0, 7);

      if (matches.length === 0) {
        results.innerHTML = '<div class="search-empty">No calculators match "' + escapeHtml(query) + '"</div>';
      } else {
        results.innerHTML = matches.map(function (c) {
          return '<a href="' + c.url + '">' + escapeHtml(c.name) + '<span class="cat-tag">' + escapeHtml(c.category) + "</span></a>";
        }).join("");
      }
      results.classList.add("show");
    }

    input.addEventListener("input", function () { render(input.value); });
    input.addEventListener("focus", function () { if (input.value) render(input.value); });
    document.addEventListener("click", function (e) {
      if (!results.contains(e.target) && e.target !== input) {
        results.classList.remove("show");
      }
    });
  }

  function initCategoryPills() {
    var pills = document.querySelectorAll("[data-filter]");
    var cards = document.querySelectorAll("[data-category]");
    if (!pills.length || !cards.length) return;
    pills.forEach(function (pill) {
      pill.addEventListener("click", function () {
        pills.forEach(function (p) { p.classList.remove("active"); });
        pill.classList.add("active");
        var filter = pill.getAttribute("data-filter");
        cards.forEach(function (card) {
          var show = filter === "all" || card.getAttribute("data-category") === filter;
          card.style.display = show ? "" : "none";
        });
      });
    });
  }

  function escapeHtml(str) {
    var div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }
})();
