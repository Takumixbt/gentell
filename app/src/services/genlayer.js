export function hasInjectedWallet() {
  return typeof window !== "undefined" && !!window.ethereum;
}

export async function getConnectedAccount() {
  if (!hasInjectedWallet()) return null;
  const accounts = await window.ethereum.request({ method: "eth_accounts" });
  return accounts[0] ?? null;
}

export async function requestWalletAccount() {
  if (!hasInjectedWallet()) {
    throw new Error("No wallet found — install MetaMask or another browser wallet to connect.");
  }
  const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
  if (!accounts.length) {
    throw new Error("Wallet connection was rejected.");
  }
  return accounts[0];
}

export function onAccountsChanged(callback) {
  if (hasInjectedWallet()) window.ethereum.on("accountsChanged", callback);
}

export function offAccountsChanged(callback) {
  if (hasInjectedWallet()) window.ethereum.removeListener("accountsChanged", callback);
}
