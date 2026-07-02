<template>
  <canvas ref="canvasEl" class="fixed inset-0 w-full h-full" style="z-index: 0"></canvas>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const canvasEl = ref(null);
let rafId = 0;
let resizeHandler = null;

const GLYPHS = "·∘○◯◌●◉"; // · ∘ ○ ◯ ◌ ● ◉
const CELL_SIZE = 26;
const FRAME_INTERVAL_MS = 45;

onMounted(() => {
  const canvas = canvasEl.value;
  const ctx = canvas.getContext("2d");
  let t = 0;
  let lastFrame = 0;

  function resize() {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  resize();
  resizeHandler = resize;
  window.addEventListener("resize", resizeHandler);

  function draw(now) {
    rafId = requestAnimationFrame(draw);
    if (now - lastFrame < FRAME_INTERVAL_MS) return;
    lastFrame = now;

    const rect = canvas.getBoundingClientRect();
    ctx.clearRect(0, 0, rect.width, rect.height);
    ctx.font = "22px monospace";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    const cols = Math.floor(rect.width / CELL_SIZE);
    const rows = Math.floor(rect.height / CELL_SIZE);

    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        const x = (col + 0.5) * (rect.width / cols);
        const y = (row + 0.5) * (rect.height / rows);

        const n =
          (Math.sin(0.18 * col + 2.1 * t) * Math.cos(0.14 * row + t) +
            Math.sin((col + row) * 0.09 + 1.5 * t) +
            Math.cos(0.11 * col - 0.12 * row + 0.85 * t)) /
            3 +
          1;
        const s = n / 2;

        const idx = Math.min(GLYPHS.length - 1, Math.floor(s * GLYPHS.length));
        const alpha = 0.08 + 0.22 * s;
        ctx.fillStyle = `rgba(255,255,255,${alpha})`;
        ctx.fillText(GLYPHS[idx], x, y);
      }
    }

    t += 0.011;
  }

  rafId = requestAnimationFrame(draw);
});

onUnmounted(() => {
  cancelAnimationFrame(rafId);
  if (resizeHandler) window.removeEventListener("resize", resizeHandler);
});
</script>
