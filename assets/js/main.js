/* ═══════════════════════════════════════════════════════════
   Ruben Esteche — personal site interactions
   Vanilla JS, no dependencies.
   ═══════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ── Sticky nav ─────────────────────────────────────────── */
  const nav = document.getElementById("nav");
  const onScroll = () => nav.classList.toggle("is-scrolled", window.scrollY > 24);
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ── Mobile menu ────────────────────────────────────────── */
  const toggle = document.getElementById("nav-toggle");
  const links = document.getElementById("nav-links");
  toggle.addEventListener("click", () => {
    const open = links.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(open));
  });
  links.addEventListener("click", (e) => {
    if (e.target.tagName === "A") {
      links.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
    }
  });

  /* ── Active section highlight ───────────────────────────── */
  const sections = document.querySelectorAll("section[id]");
  const navAnchors = links.querySelectorAll('a[href^="#"]');
  const sectionObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        navAnchors.forEach((a) =>
          a.classList.toggle("is-active", a.getAttribute("href") === "#" + entry.target.id)
        );
      });
    },
    { rootMargin: "-40% 0px -55% 0px" }
  );
  sections.forEach((s) => sectionObserver.observe(s));

  /* ── Reveal on scroll ───────────────────────────────────── */
  const revealObserver = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          obs.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
  );
  document.querySelectorAll(".reveal").forEach((el) => revealObserver.observe(el));

  /* ── Typewriter ─────────────────────────────────────────── */
  const phrases = [
    "python -m rag.deploy --grounded --with-sources",
    'llm.invoke("turn this database into a conversation")',
    "kubectl rollout status deployment/inference-api",
    "ψ(x,t) → attention(Q,K,V)  # physics to transformers",
    "terraform apply  # infra as code, always",
  ];
  const target = document.getElementById("typewriter");
  if (target && !prefersReducedMotion) {
    let phraseIdx = 0, charIdx = 0, deleting = false;
    const tick = () => {
      const phrase = phrases[phraseIdx];
      target.textContent = phrase.slice(0, charIdx);
      let delay = deleting ? 24 : 55;
      if (!deleting && charIdx === phrase.length) {
        delay = 2400; deleting = true;
      } else if (deleting && charIdx === 0) {
        deleting = false;
        phraseIdx = (phraseIdx + 1) % phrases.length;
        delay = 450;
      } else {
        charIdx += deleting ? -1 : 1;
      }
      setTimeout(tick, delay);
    };
    tick();
  } else if (target) {
    target.textContent = phrases[0];
  }

  /* ── Animated stat counters ─────────────────────────────── */
  const counters = document.querySelectorAll(".stat__num[data-count]");
  const counterObserver = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const end = parseInt(el.dataset.count, 10);
        const duration = 1200;
        const start = performance.now();
        const step = (now) => {
          const p = Math.min((now - start) / duration, 1);
          el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3)));
          if (p < 1) requestAnimationFrame(step);
        };
        prefersReducedMotion ? (el.textContent = end) : requestAnimationFrame(step);
        obs.unobserve(el);
      });
    },
    { threshold: 0.6 }
  );
  counters.forEach((c) => counterObserver.observe(c));

  /* ── Live GitHub star counts (progressive enhancement) ──── */
  document.querySelectorAll(".project__stars[data-repo]").forEach((el) => {
    fetch("https://api.github.com/repos/" + el.dataset.repo)
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d && typeof d.stargazers_count === "number") {
          el.textContent = "★ " + d.stargazers_count;
        }
      })
      .catch(() => {}); // keep the static fallback on rate-limit/offline
  });

  /* ── Footer year ────────────────────────────────────────── */
  const year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();

  /* ── Neural network canvas ──────────────────────────────── */
  const canvas = document.getElementById("neural-canvas");
  if (!canvas || prefersReducedMotion) return;

  const ctx = canvas.getContext("2d");
  let nodes = [];
  let width, height, dpr;
  let mouse = { x: -9999, y: -9999 };

  const CONNECT_DIST = 150;
  const MOUSE_DIST = 200;

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    const rect = canvas.parentElement.getBoundingClientRect();
    width = rect.width;
    height = rect.height;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const count = Math.min(Math.floor((width * height) / 16000), 90);
    nodes = Array.from({ length: count }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.35,
      r: Math.random() * 1.6 + 0.8,
    }));
  }

  canvas.parentElement.addEventListener("pointermove", (e) => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
  });
  canvas.parentElement.addEventListener("pointerleave", () => {
    mouse.x = -9999; mouse.y = -9999;
  });

  function frame() {
    ctx.clearRect(0, 0, width, height);

    for (const n of nodes) {
      n.x += n.vx;
      n.y += n.vy;
      if (n.x < 0 || n.x > width) n.vx *= -1;
      if (n.y < 0 || n.y > height) n.vy *= -1;
    }

    // links between nearby nodes
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i], b = nodes[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        const dist = Math.hypot(dx, dy);
        if (dist < CONNECT_DIST) {
          const alpha = (1 - dist / CONNECT_DIST) * 0.35;
          ctx.strokeStyle = "rgba(103, 165, 220, " + alpha + ")";
          ctx.lineWidth = 0.7;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }
      // link to cursor — the "you are part of the network" touch
      const m = nodes[i];
      const mdist = Math.hypot(m.x - mouse.x, m.y - mouse.y);
      if (mdist < MOUSE_DIST) {
        const alpha = (1 - mdist / MOUSE_DIST) * 0.5;
        ctx.strokeStyle = "rgba(34, 211, 238, " + alpha + ")";
        ctx.lineWidth = 0.8;
        ctx.beginPath();
        ctx.moveTo(m.x, m.y);
        ctx.lineTo(mouse.x, mouse.y);
        ctx.stroke();
      }
    }

    for (const n of nodes) {
      ctx.fillStyle = "rgba(148, 197, 233, 0.75)";
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
      ctx.fill();
    }

    requestAnimationFrame(frame);
  }

  window.addEventListener("resize", resize);
  resize();
  requestAnimationFrame(frame);
})();
