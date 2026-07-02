<template>
  <div class="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
    <div v-for="step in steps" :key="step.title">
      <p class="text-white/40 text-5xl font-semibold mb-3">{{ step.n }}</p>
      <h3 class="text-lg font-medium mb-2 text-white/95">{{ step.title }}</h3>
      <p class="text-white/85 text-sm leading-relaxed">{{ step.desc }}</p>
    </div>
  </div>
</template>

<script setup>
const steps = [
  {
    n: "01",
    title: "Fetch",
    desc: "The contract pulls live on-chain security data for the address — liquidity, holders, mint/owner controls, taxes.",
  },
  {
    n: "02",
    title: "AI judges",
    desc: "An LLM analyzes the security data for rug-pull red flags and produces a risk score, level, and summary.",
  },
  {
    n: "03",
    title: "Validators agree",
    desc: "Independent GenLayer validators repeat the process and reach consensus — no single party controls the verdict.",
  },
];
</script>
