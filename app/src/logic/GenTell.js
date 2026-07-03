import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

function getInjectedProvider() {
  return typeof window !== "undefined" ? window.ethereum : undefined;
}

function mapToObject(map) {
  return Array.from(map.entries()).reduce((obj, [key, value]) => {
    obj[key] = value;
    return obj;
  }, {});
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
    return Array.from(assessments.entries()).map(([address, data]) => {
      const obj = mapToObject(data);
      return { ...obj, address, riskScore: Number(obj.risk_score ?? 0) };
    });
  }

  async getAssessment(contractAddress) {
    const data = await this.client.readContract({
      address: this.contractAddress,
      functionName: "get_assessment",
      args: [contractAddress],
    });
    const obj = mapToObject(data);
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
