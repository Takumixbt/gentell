<template>
  <div class="relative min-h-screen bg-black text-white overflow-x-hidden">
    <FlowField />

    <div class="relative z-10 flex flex-col">
      <!-- Top bar -->
      <header class="flex items-center justify-between px-6 lg:px-12 py-6">
        <span class="text-base tracking-widest uppercase text-white/95 font-medium">GenTell</span>
        <WalletBadge :address="userAddress" @connect="connectAccount" @disconnect="disconnectAccount" />
      </header>

      <!-- Hero + search -->
      <section class="flex flex-col items-center justify-center px-6 py-20 md:py-28">
        <SearchHero :loading="loading" :error="error" @submit="handleAnalyze" />
        <p v-if="isDemo" class="text-white/90 text-sm mt-6">
          Demo mode — no contract deployed yet, showing simulated results.
        </p>
      </section>

      <!-- Result -->
      <section v-if="currentResult" class="px-6 pb-20">
        <ResultPanel :assessment="currentResult" />
      </section>

      <!-- Recent assessments -->
      <section class="px-6 pb-24">
        <AssessmentsFeed :assessments="assessments" @select="showAssessment" />
      </section>

      <!-- How it works -->
      <section class="px-6 pb-28">
        <HowItWorks />
      </section>

      <footer class="px-6 py-8 text-center text-white/85 text-sm border-t border-white/10">
        Built on GenLayer — intelligent contracts with native web + AI access.
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import {
  hasInjectedWallet,
  getConnectedAccount,
  requestWalletAccount,
  onAccountsChanged,
  offAccountsChanged,
} from "./services/genlayer";
import GenTell from "./logic/GenTell";
import FlowField from "./components/FlowField.vue";
import WalletBadge from "./components/WalletBadge.vue";
import SearchHero from "./components/SearchHero.vue";
import ResultPanel from "./components/ResultPanel.vue";
import AssessmentsFeed from "./components/AssessmentsFeed.vue";
import HowItWorks from "./components/HowItWorks.vue";

const contractAddress = import.meta.env.VITE_CONTRACT_ADDRESS;
const studioUrl = import.meta.env.VITE_STUDIO_URL;
const isDemo = computed(() => !contractAddress);

const oracle = isDemo.value ? null : new GenTell(contractAddress, { studioUrl });

const userAddress = ref(null);

const assessments = ref([]);
const currentResult = ref(null);
const loading = ref(false);
const error = ref("");

const DEMO_FLAGS = [
  "unlocked liquidity",
  "concentrated holders",
  "anonymous team",
  "unverified contract",
  "no audit",
  "mint function enabled",
];

function randomDemoAssessment(chainId, contractAddress) {
  const score = Math.floor(Math.random() * 100);
  const level = score < 25 ? "low" : score < 50 ? "medium" : score < 80 ? "high" : "critical";
  const flagCount = level === "low" ? 0 : level === "medium" ? 1 : level === "high" ? 2 : 3;
  const flags = [...DEMO_FLAGS].sort(() => Math.random() - 0.5).slice(0, flagCount);
  return {
    contract_address: contractAddress,
    chain_id: chainId,
    token_symbol: "DEMO",
    riskScore: score,
    risk_level: level,
    red_flags: flags.length ? flags.join(", ") : "none",
    summary:
      level === "low"
        ? "No major red flags detected — contract looks clean and ownership is not concentrated."
        : level === "critical"
          ? "Multiple severe red flags detected — high probability of rug pull."
          : "Some concerning signals found — proceed with caution.",
    address: contractAddress,
  };
}

const connectAccount = async () => {
  error.value = "";
  try {
    const address = await requestWalletAccount();
    userAddress.value = address;
    if (oracle) oracle.updateAccount(address);
  } catch (e) {
    error.value = e?.message ?? "Could not connect wallet.";
  }
};

const disconnectAccount = () => {
  userAddress.value = null;
};

function handleAccountsChanged(accounts) {
  userAddress.value = accounts[0] ?? null;
  if (oracle && userAddress.value) oracle.updateAccount(userAddress.value);
}

const loadAssessments = async () => {
  if (isDemo.value) return;
  assessments.value = await oracle.getAllAssessments();
};

const showAssessment = (assessment) => {
  currentResult.value = assessment;
};

const handleAnalyze = async ({ chainId, contractAddress }) => {
  loading.value = true;
  error.value = "";
  try {
    if (isDemo.value) {
      await new Promise((resolve) => setTimeout(resolve, 1200));
      const result = randomDemoAssessment(chainId, contractAddress);
      currentResult.value = result;
      assessments.value = [
        result,
        ...assessments.value.filter((a) => a.address !== contractAddress),
      ];
    } else {
      if (!userAddress.value) {
        const address = await requestWalletAccount();
        userAddress.value = address;
        oracle.updateAccount(address);
      }
      await oracle.assessToken(chainId, contractAddress);
      const result = await oracle.getAssessment(contractAddress);
      currentResult.value = result;
      await loadAssessments();
    }
  } catch (e) {
    error.value = e?.message ?? "Something went wrong analyzing this token.";
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await loadAssessments();
  if (hasInjectedWallet()) {
    const existing = await getConnectedAccount();
    if (existing) {
      userAddress.value = existing;
      if (oracle) oracle.updateAccount(existing);
    }
    onAccountsChanged(handleAccountsChanged);
  }
});

onUnmounted(() => {
  offAccountsChanged(handleAccountsChanged);
});
</script>
