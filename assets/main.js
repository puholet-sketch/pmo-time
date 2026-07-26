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

  if (window.mermaid) {
    mermaid.initialize({
      startOnLoad: true,
      theme: "base",
      themeVariables: {
        primaryColor: "#fff5f5",
        primaryTextColor: "#1a1a1a",
        primaryBorderColor: "#c00000",
        lineColor: "#8a0000",
        secondaryColor: "#f3f1ef",
        tertiaryColor: "#ffffff",
        noteBkgColor: "#faf9f8",
        noteTextColor: "#333333",
        noteBorderColor: "#e8e4e1",
        actorBkg: "#ffffff",
        actorBorder: "#c00000",
        actorTextColor: "#1a1a1a",
        signalColor: "#1a1a1a",
        labelBoxBkgColor: "#ffffff",
        labelBoxBorderColor: "#e8e4e1",
        labelTextColor: "#1a1a1a",
        altSectionBkgColor: "#faf9f8",
        sequenceNumberColor: "#ffffff",
      },
      flowchart: { curve: "basis", htmlLabels: true, padding: 16 },
      securityLevel: "strict",
    });
  }
})();
