<template>
  <div class="text-sm">
    <button
      v-if="!address"
      @click="$emit('connect')"
      class="border border-white/30 hover:border-white text-white px-4 py-2 rounded-full transition-colors"
    >
      Connect
    </button>
    <div v-else class="flex items-center gap-3">
      <span class="text-white/75">
        <Address :address="address" />
      </span>
      <button @click="$emit('disconnect')" class="text-white/55 hover:text-white transition-colors">
        Disconnect
      </button>
    </div>
  </div>
</template>

<script setup>
import Address from "./Address.vue";

defineProps({
  address: { type: String, default: null },
});
defineEmits(["connect", "disconnect"]);
</script>
