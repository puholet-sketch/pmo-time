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

  if (!window.mermaid) return;

  mermaid.initialize({
    startOnLoad: false,
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
    // false → SVG шириной по содержимому, иначе растягивается на 100% и «уезжает» влево
    flowchart: { curve: "basis", htmlLabels: true, padding: 20, useMaxWidth: false },
    securityLevel: "strict",
  });

  function fitAndCenter(svg) {
    try {
      const bbox = svg.getBBox();
      if (!bbox.width || !bbox.height) return;

      const pad = 8;
      const x = Math.min(0, bbox.x) - pad;
      const y = Math.min(0, bbox.y) - pad;
      const w = bbox.width + pad * 2 + Math.max(0, bbox.x);
      const h = bbox.height + pad * 2 + Math.max(0, bbox.y);

      svg.setAttribute("viewBox", `${x} ${y} ${w} ${h}`);
      svg.setAttribute("width", String(Math.ceil(w)));
      svg.setAttribute("height", String(Math.ceil(h)));
      svg.removeAttribute("style");
      svg.style.display = "block";
      svg.style.maxWidth = "100%";
      svg.style.height = "auto";
      svg.style.margin = "0 auto";
    } catch {
      svg.style.display = "block";
      svg.style.margin = "0 auto";
      svg.style.maxWidth = "100%";
    }
  }

  function centerAll() {
    document.querySelectorAll(".mermaid-wrap svg").forEach(fitAndCenter);
  }

  mermaid
    .run({ querySelector: ".mermaid" })
    .then(() => {
      // htmlLabels рисуются чуть позже — второй проход после layout
      requestAnimationFrame(() => {
        centerAll();
        requestAnimationFrame(centerAll);
      });
    })
    .catch(centerAll);
})();
