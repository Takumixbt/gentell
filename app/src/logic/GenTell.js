import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

function getInjectedProvider() {
  return typeof window !== "undefined" ? window.ethereum : undefined;
}

class GenTell {
  contractAddress;
  client;

  constructor(contractAddress, { address = null, studioUrl = null } = {}) {
    this.contractAddress = contractAddress;
    const config = {
      chain: studionet,
      ...(address ? { account: address, provider: getInjectedProvider() } : {}),
      ...(studioUrl ? { endpoint: studioUrl } : {}),
    };
    this.client = createClient(config);
  }

  updateAccount(address) {
    this.client = createClient({
      chain: studionet,
      account: address,
      provider: getInjectedProvider(),
    });
  }

  async getAllAssessments() {
    const assessments = await this.client.readContract({
      address: this.contractAddress,
      functionName: "get_all_assessments",
      args: [],
    });
    return Object.entries(assessments).map(([address, obj]) => ({
      ...obj,
      address,
      riskScore: Number(obj.risk_score ?? 0),
    }));
  }

  async getAssessment(contractAddress) {
    const obj = await this.client.readContract({
      address: this.contractAddress,
      functionName: "get_assessment",
      args: [contractAddress],
    });
    return { ...obj, riskScore: Number(obj.risk_score ?? 0) };
  }

  async assessToken(chainId, contractAddress) {
    const txHash = await this.client.writeContract({
      address: this.contractAddress,
      functionName: "assess_token",
      args: [chainId, contractAddress],
    });
    const receipt = await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: "FINALIZED",
      interval: 10000,
      retries: 30,
    });
    return receipt;
  }
}

export default GenTell;
