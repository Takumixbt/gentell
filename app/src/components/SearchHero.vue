<template>
  <div class="max-w-2xl w-full mx-auto text-center">
    <p class="text-sm tracking-[0.3em] text-white/90 uppercase mb-4">GenLayer Intelligent Contract</p>
    <h1 class="text-5xl md:text-7xl font-semibold tracking-tight mb-4">GenTell</h1>
    <p class="text-white max-w-xl mx-auto text-lg mb-10">
      Consensus-verified rug-pull risk scores, powered by on-chain security data and AI validators.
    </p>

    <form @submit.prevent="submit" class="flex flex-col sm:flex-row gap-3 mb-3">
      <div ref="pickerRef" class="relative shrink-0">
        <button
          type="button"
          @click="pickerOpen = !pickerOpen"
          class="w-full sm:w-44 flex items-center justify-between gap-2 bg-white/5 border border-white/15 rounded-full pl-5 pr-4 py-3 text-white hover:border-white/40 transition-colors focus:outline-none focus:border-white/50"
        >
          <span class="flex items-center gap-2 truncate">
            <span class="w-2 h-2 rounded-full bg-white/80 shrink-0"></span>
            {{ selectedChain.label }}
          </span>
          <svg
            class="w-4 h-4 text-white/70 shrink-0 transition-transform"
            :class="{ 'rotate-180': pickerOpen }"
            viewBox="0 0 20 20"
            fill="none"
          >
            <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
          </svg>
        </button>

        <div
          v-if="pickerOpen"
          class="absolute z-20 mt-2 w-full sm:w-52 bg-black border border-white/15 rounded-2xl shadow-2xl shadow-black/50 overflow-hidden"
        >
          <button
            v-for="c in CHAINS"
            :key="c.id"
            type="button"
            @click="selectChain(c.id)"
            class="w-full flex items-center justify-between gap-2 px-4 py-2.5 text-sm text-left hover:bg-white/10 transition-colors"
            :class="c.id === chainId ? 'text-white' : 'text-white/85'"
          >
            {{ c.label }}
            <svg
              v-if="c.id === chainId"
              class="w-4 h-4 text-white shrink-0"
              viewBox="0 0 20 20"
              fill="none"
            >
              <path
                d="M4 10.5L8 14.5L16 6.5"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>
        </div>
      </div>

      <input
        v-model="contractAddress"
        type="text"
        placeholder="Token contract address (0x...)"
        class="flex-1 bg-white/5 border border-white/15 rounded-full px-5 py-3 text-white placeholder-white/60 focus:outline-none focus:border-white/50"
      />
      <button
        type="submit"
        :disabled="loading || !contractAddress"
        class="bg-white text-black font-medium rounded-full px-8 py-3 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-white/90 transition-colors"
      >
        {{ loading ? "Analyzing…" : "Analyze" }}
      </button>
    </form>
    <p v-if="loading" class="text-white/90 text-sm">
      Validators are pulling on-chain security data and reaching consensus — this can take a moment.
    </p>
    <p v-if="error" class="text-white text-sm">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";

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
const pickerOpen = ref(false);
const pickerRef = ref(null);

const selectedChain = computed(() => CHAINS.find((c) => c.id === chainId.value) ?? CHAINS[0]);

function selectChain(id) {
  chainId.value = id;
  pickerOpen.value = false;
}

function handleClickOutside(event) {
  if (pickerRef.value && !pickerRef.value.contains(event.target)) {
    pickerOpen.value = false;
  }
}

onMounted(() => document.addEventListener("click", handleClickOutside));
onUnmounted(() => document.removeEventListener("click", handleClickOutside));

function submit() {
  if (!contractAddress.value) return;
  emit("submit", { chainId: chainId.value, contractAddress: contractAddress.value.trim() });
}
</script>
