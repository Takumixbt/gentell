import { createClient } from "genlayer-js";
import { simulator } from "genlayer-js/chains";

function mapToObject(map) {
  return Array.from(map.entries()).reduce((obj, [key, value]) => {
    obj[key] = value;
    return obj;
  }, {});
}

class GenTell {
  contractAddress;
  client;

  constructor(contractAddress, account = null, studioUrl = null) {
    this.contractAddress = contractAddress;
    const config = {
      chain: simulator,
      ...(account ? { account } : {}),
      ...(studioUrl ? { endpoint: studioUrl } : {}),
    };
    this.client = createClient(config);
  }

  updateAccount(account) {
    this.client = createClient({ chain: simulator, account });
  }

  async getAllAssessments() {
    const assessments = await this.client.readContract({
      address: this.contractAddress,
      functionName: "get_all_assessments",
      args: [],
    });
    return Array.from(assessments.entries()).map(([tokenId, data]) => {
      const obj = mapToObject(data);
      return { ...obj, tokenId, riskScore: Number(obj.risk_score ?? 0) };
    });
  }

  async getAssessment(tokenId) {
    const data = await this.client.readContract({
      address: this.contractAddress,
      functionName: "get_assessment",
      args: [tokenId],
    });
    const obj = mapToObject(data);
    return { ...obj, riskScore: Number(obj.risk_score ?? 0) };
  }

  async assessToken(tokenId, sourceUrl) {
    const txHash = await this.client.writeContract({
      address: this.contractAddress,
      functionName: "assess_token",
      args: [tokenId, sourceUrl],
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
