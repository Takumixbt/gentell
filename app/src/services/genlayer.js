import { studionet } from "genlayer-js/chains";

const CHAIN_ID_HEX = `0x${studionet.id.toString(16)}`;

export function hasInjectedWallet() {
  return typeof window !== "undefined" && !!window.ethereum;
}

export async function getConnectedAccount() {
  if (!hasInjectedWallet()) return null;
  const accounts = await window.ethereum.request({ method: "eth_accounts" });
  return accounts[0] ?? null;
}

async function addStudionetChain() {
  await window.ethereum.request({
    method: "wallet_addEthereumChain",
    params: [
      {
        chainId: CHAIN_ID_HEX,
        chainName: studionet.name,
        rpcUrls: [...studionet.rpcUrls.default.http],
        nativeCurrency: studionet.nativeCurrency,
        blockExplorerUrls: [studionet.blockExplorers.default.url],
      },
    ],
  });
}

export async function ensureCorrectChain() {
  const currentChainId = await window.ethereum.request({ method: "eth_chainId" });
  if (currentChainId === CHAIN_ID_HEX) return;

  try {
    await window.ethereum.request({
      method: "wallet_switchEthereumChain",
      params: [{ chainId: CHAIN_ID_HEX }],
    });
  } catch (switchError) {
    if (switchError?.code === 4001) {
      throw new Error(
        "Switching networks was rejected — GenTell needs the GenLayer Studio Network to submit transactions."
      );
    }
    // Any other failure (unrecognized chain, code 4902, or a wallet-specific
    // variant of that error) most likely means the chain isn't added yet.
    try {
      await addStudionetChain();
    } catch (addError) {
      if (addError?.code === 4001) {
        throw new Error(
          "Adding the GenLayer Studio Network was rejected — it's required to submit transactions."
        );
      }
      throw addError;
    }
  }
}

export async function requestWalletAccount() {
  if (!hasInjectedWallet()) {
    throw new Error("No wallet found — install MetaMask or another browser wallet to connect.");
  }
  const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
  if (!accounts.length) {
    throw new Error("Wallet connection was rejected.");
  }
  await ensureCorrectChain();
  return accounts[0];
}

export function onAccountsChanged(callback) {
  if (hasInjectedWallet()) window.ethereum.on("accountsChanged", callback);
}

export function offAccountsChanged(callback) {
  if (hasInjectedWallet()) window.ethereum.removeListener("accountsChanged", callback);
}

export function onChainChanged(callback) {
  if (hasInjectedWallet()) window.ethereum.on("chainChanged", callback);
}

export function offChainChanged(callback) {
  if (hasInjectedWallet()) window.ethereum.removeListener("chainChanged", callback);
}
