(() => {
  const toggle = document.querySelector(".nav-toggle");
  const mobile = document.querySelector("#mobile-nav");
  if (toggle && mobile) {
    toggle.addEventListener("click", () => {
      const open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      mobile.hidden = open;
    });
    mobile.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        toggle.setAttribute("aria-expanded", "false");
        mobile.hidden = true;
      });
    });
  }
})();
