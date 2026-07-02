<template>
  <div class="max-w-2xl w-full mx-auto text-center">
    <p class="text-sm tracking-[0.3em] text-white/60 uppercase mb-4">GenLayer Intelligent Contract</p>
    <h1 class="text-5xl md:text-7xl font-semibold tracking-tight mb-4">GenTell</h1>
    <p class="text-white/80 max-w-xl mx-auto text-lg mb-10">
      Consensus-verified rug-pull risk scores, powered by web-reading AI validators.
    </p>

    <form @submit.prevent="submit" class="flex flex-col sm:flex-row gap-3 mb-3">
      <input
        v-model="tokenId"
        type="text"
        placeholder="Token symbol or address"
        class="flex-1 bg-white/5 border border-white/15 rounded-full px-5 py-3 text-white placeholder-white/45 focus:outline-none focus:border-white/50"
      />
      <input
        v-model="sourceUrl"
        type="text"
        placeholder="Info page URL (e.g. dexscreener.com/...)"
        class="flex-[1.4] bg-white/5 border border-white/15 rounded-full px-5 py-3 text-white placeholder-white/45 focus:outline-none focus:border-white/50"
      />
      <button
        type="submit"
        :disabled="loading || !tokenId || !sourceUrl"
        class="bg-white text-black font-medium rounded-full px-8 py-3 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-white/90 transition-colors"
      >
        {{ loading ? "Analyzing…" : "Analyze" }}
      </button>
    </form>
    <p v-if="loading" class="text-white/60 text-sm">
      Validators are scraping and reaching consensus — this can take a moment.
    </p>
    <p v-if="error" class="text-white/70 text-sm">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from "vue";

defineProps({
  loading: { type: Boolean, default: false },
  error: { type: String, default: "" },
});
const emit = defineEmits(["submit"]);

const tokenId = ref("");
const sourceUrl = ref("");

function submit() {
  if (!tokenId.value || !sourceUrl.value) return;
  emit("submit", { tokenId: tokenId.value, sourceUrl: sourceUrl.value });
}
</script>
