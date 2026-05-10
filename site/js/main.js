(function () {
    var el = document.getElementById("footer-year");
    if (el) {
        el.textContent = String(new Date().getFullYear());
    }
})();
