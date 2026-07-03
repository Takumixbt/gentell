<template>
  <div class="w-full max-w-xl mx-auto border border-white/20 rounded-2xl p-8 bg-black/70 backdrop-blur-sm">
    <div class="flex items-center justify-between mb-6">
      <div>
        <p class="text-sm tracking-[0.25em] text-white uppercase">
          {{ assessment.token_symbol || "Unknown token" }}
        </p>
        <a
          :href="explorerUrl"
          target="_blank"
          rel="noopener"
          class="text-sm text-white/90 hover:text-white underline"
        >
          {{ shortAddress }}
        </a>
      </div>
      <span class="text-sm uppercase tracking-widest border rounded-full px-3 py-1" :class="levelClasses">
        {{ assessment.risk_level }}
      </span>
    </div>

    <div class="mb-6">
      <div class="flex items-end justify-between mb-2">
        <span class="text-5xl font-semibold">{{ assessment.riskScore }}</span>
        <span class="text-white/90 text-sm mb-1">/ 100 risk</span>
      </div>
      <div class="w-full h-2 bg-white/15 rounded-full overflow-hidden">
        <div
          class="h-full bg-white transition-all duration-700"
          :style="{ width: assessment.riskScore + '%' }"
        ></div>
      </div>
    </div>

    <p class="text-white mb-6 leading-relaxed">{{ assessment.summary }}</p>

    <div v-if="flagsList.length">
      <p class="text-sm uppercase tracking-widest text-white/90 mb-2">Red flags</p>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="flag in flagsList"
          :key="flag"
          class="text-sm border border-white/25 rounded-full px-3 py-1 text-white"
        >
          {{ flag }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  assessment: { type: Object, required: true },
});

const EXPLORERS = {
  1: "https://etherscan.io/address/",
  56: "https://bscscan.com/address/",
  137: "https://polygonscan.com/address/",
  42161: "https://arbiscan.io/address/",
  10: "https://optimistic.etherscan.io/address/",
  8453: "https://basescan.org/address/",
};

const flagsList = computed(() => {
  const raw = props.assessment.red_flags || "";
  if (!raw || raw.toLowerCase() === "none") return [];
  return raw
    .split(",")
    .map((f) => f.trim())
    .filter(Boolean);
});

const shortAddress = computed(() => {
  const addr = props.assessment.contract_address || props.assessment.address || "";
  return addr.length > 10 ? `${addr.slice(0, 6)}…${addr.slice(-4)}` : addr;
});

const explorerUrl = computed(() => {
  const base = EXPLORERS[props.assessment.chain_id] || EXPLORERS[1];
  return base + (props.assessment.contract_address || props.assessment.address || "");
});

const levelClasses = computed(() => {
  const level = (props.assessment.risk_level || "").toLowerCase();
  if (level === "critical") return "bg-white text-black border-white";
  if (level === "high") return "text-white border-white/70";
  if (level === "medium") return "text-white border-white/45";
  return "text-white/90 border-white/30";
});
</script>
