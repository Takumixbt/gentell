# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from dataclasses import dataclass
from genlayer import *


@allow_storage
@dataclass
class RiskAssessment:
    contract_address: str
    chain_id: str
    token_symbol: str
    risk_score: u256
    risk_level: str
    red_flags: str
    summary: str


class GenTell(gl.Contract):
    assessments: TreeMap[str, RiskAssessment]

    def __init__(self):
        pass

    def _assess_token(self, chain_id: str, contract_address: str) -> dict:
        chain_id = str(chain_id)
        contract_address = str(contract_address)

        def get_risk_assessment() -> str:
            api_url = (
                f"https://api.gopluslabs.io/api/v1/token_security/{chain_id}"
                f"?contract_addresses={contract_address}"
            )
            response = gl.nondet.web.get(api_url)
            data = json.loads(response.body.decode("utf-8"))
            security = data.get("result", {}).get(contract_address.lower(), {})

            if not security:
                security = {"note": "No security data found for this contract address."}
            elif security.get("holders"):
                # Trim the holder list so the prompt stays a reasonable size.
                security = {**security, "holders": security["holders"][:5]}

            task = f"""
You are a crypto security analyst. Analyze the following structured token
security data (from GoPlus Security) for contract {contract_address} on
chain ID {chain_id}, and assess its rug-pull / scam risk.

Security data:
{json.dumps(security)}

Look for red flags such as:
- is_honeypot, is_blacklisted, transfer_pausable, selfdestruct
- is_mintable, hidden_owner, can_take_back_ownership, owner_change_balance
- slippage_modifiable, personal_slippage_modifiable, anti_whale_modifiable
- Low is_open_source, high owner_percent/creator_percent, concentrated top holders
- High buy_tax / sell_tax
- Missing or empty security data (no info found for this contract)

Respond in JSON:
{{
    "risk_score": int,   // 0-100, 0 = safe, 100 = extremely high risk
    "risk_level": str,   // one of: "low", "medium", "high", "critical"
    "red_flags": str,    // comma-separated red flags detected, or "none"
    "summary": str       // one sentence summary of the assessment
}}
It is mandatory that you respond only using the JSON format above,
nothing else. Don't include any other words or characters,
your output must be only JSON without any formatting prefix or suffix.
This result should be perfectly parsable by a JSON parser without errors.
        """
            llm_result = gl.nondet.exec_prompt(task, response_format="json")
            combined = {
                "risk_score": llm_result["risk_score"],
                "risk_level": llm_result["risk_level"],
                "red_flags": llm_result["red_flags"],
                "summary": llm_result["summary"],
                "token_symbol": security.get("token_symbol", ""),
            }
            return json.dumps(combined, sort_keys=True)

        result_json = json.loads(
            gl.eq_principle.prompt_comparative(
                get_risk_assessment,
                "The results should agree on risk_level (exact match) and "
                "risk_score (within 25 points of each other). They do not need "
                "to identify the exact same red flags, only a substantially "
                "overlapping set — differences in how strictly a validator "
                "weighs administrative permissions (e.g. owner/blacklist "
                "functions) on an otherwise well-established, widely-trusted "
                "token are expected and should still count as agreement, as "
                "long as the overall verdict (safe vs risky) matches. The "
                "summary field may be worded differently across validators.",
            )
        )
        return result_json

    @gl.public.write
    def assess_token(self, chain_id: str, contract_address: str) -> None:
        chain_id = str(chain_id)
        contract_address = str(contract_address)
        result = self._assess_token(chain_id, contract_address)

        key = contract_address.lower()
        self.assessments[key] = RiskAssessment(
            contract_address=contract_address,
            chain_id=chain_id,
            token_symbol=str(result.get("token_symbol", "")),
            risk_score=u256(int(result["risk_score"])),
            risk_level=str(result["risk_level"]),
            red_flags=str(result["red_flags"]),
            summary=str(result["summary"]),
        )

    @gl.public.view
    def get_assessment(self, contract_address: str) -> dict:
        key = str(contract_address).lower()
        if key not in self.assessments:
            raise Exception("No assessment found for this contract")
        a = self.assessments[key]
        return {
            "contract_address": a.contract_address,
            "chain_id": a.chain_id,
            "token_symbol": a.token_symbol,
            "risk_score": a.risk_score,
            "risk_level": a.risk_level,
            "red_flags": a.red_flags,
            "summary": a.summary,
        }

    @gl.public.view
    def get_all_assessments(self) -> dict:
        return {
            k: {
                "contract_address": v.contract_address,
                "chain_id": v.chain_id,
                "token_symbol": v.token_symbol,
                "risk_score": v.risk_score,
                "risk_level": v.risk_level,
                "red_flags": v.red_flags,
                "summary": v.summary,
            }
            for k, v in self.assessments.items()
        }
