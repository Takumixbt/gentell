<template>
  <div class="max-w-2xl w-full mx-auto text-center">
    <p class="text-sm tracking-[0.3em] text-white/80 uppercase mb-4">GenLayer Intelligent Contract</p>
    <h1 class="text-5xl md:text-7xl font-semibold tracking-tight mb-4">GenTell</h1>
    <p class="text-white/95 max-w-xl mx-auto text-lg mb-10">
      Consensus-verified rug-pull risk scores, powered by on-chain security data and AI validators.
    </p>

    <form @submit.prevent="submit" class="flex flex-col sm:flex-row gap-3 mb-3">
      <select
        v-model="chainId"
        class="bg-white/5 border border-white/15 rounded-full px-5 py-3 text-white focus:outline-none focus:border-white/50"
      >
        <option v-for="c in CHAINS" :key="c.id" :value="c.id" class="bg-black">
          {{ c.label }}
        </option>
      </select>
      <input
        v-model="contractAddress"
        type="text"
        placeholder="Token contract address (0x...)"
        class="flex-1 bg-white/5 border border-white/15 rounded-full px-5 py-3 text-white placeholder-white/55 focus:outline-none focus:border-white/50"
      />
      <button
        type="submit"
        :disabled="loading || !contractAddress"
        class="bg-white text-black font-medium rounded-full px-8 py-3 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-white/90 transition-colors"
      >
        {{ loading ? "Analyzing…" : "Analyze" }}
      </button>
    </form>
    <p v-if="loading" class="text-white/70 text-sm">
      Validators are pulling on-chain security data and reaching consensus — this can take a moment.
    </p>
    <p v-if="error" class="text-white/80 text-sm">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from "vue";

defineProps({
  loading: { type: Boolean, default: false },
  error: { type: String, default: "" },
});
const emit = defineEmits(["submit"]);

const CHAINS = [
  { id: "1", label: "Ethereum" },
  { id: "56", label: "BNB Chain" },
  { id: "137", label: "Polygon" },
  { id: "42161", label: "Arbitrum" },
  { id: "10", label: "Optimism" },
  { id: "8453", label: "Base" },
];

const chainId = ref(CHAINS[0].id);
const contractAddress = ref("");

function submit() {
  if (!contractAddress.value) return;
  emit("submit", { chainId: chainId.value, contractAddress: contractAddress.value.trim() });
}
</script>
