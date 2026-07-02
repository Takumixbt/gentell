<template>
  <div class="w-full max-w-4xl mx-auto">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-base uppercase tracking-widest text-white/70 font-medium">Recent Assessments</h2>
      <button @click="sortDesc = !sortDesc" class="text-sm text-white/60 hover:text-white transition-colors">
        Sort by risk {{ sortDesc ? "↓" : "↑" }}
      </button>
    </div>

    <div v-if="!assessments.length" class="text-white/50 text-sm border border-white/15 rounded-xl p-8 text-center bg-black/40">
      No tokens analyzed yet — be the first.
    </div>

    <div v-else class="border border-white/15 rounded-xl overflow-hidden divide-y divide-white/15 bg-black/40">
      <div
        v-for="a in sorted"
        :key="a.tokenId"
        class="flex items-center justify-between px-5 py-4 hover:bg-white/10 transition-colors cursor-pointer"
        @click="$emit('select', a)"
      >
        <div class="min-w-0 mr-4">
          <p class="font-medium text-white/95">{{ a.tokenId }}</p>
          <p class="text-white/55 text-sm truncate">{{ a.summary }}</p>
        </div>
        <div class="flex items-center gap-4 shrink-0">
          <span class="text-sm uppercase tracking-wider text-white/60">{{ a.risk_level }}</span>
          <span class="text-lg font-semibold w-10 text-right">{{ a.riskScore }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  assessments: { type: Array, default: () => [] },
});
defineEmits(["select"]);

const sortDesc = ref(true);
const sorted = computed(() =>
  [...props.assessments].sort((a, b) => (sortDesc.value ? b.riskScore - a.riskScore : a.riskScore - b.riskScore))
);
</script>
