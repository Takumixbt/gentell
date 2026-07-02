# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from dataclasses import dataclass
from genlayer import *


@allow_storage
@dataclass
class RiskAssessment:
    token_id: str
    source_url: str
    risk_score: u256
    risk_level: str
    red_flags: str
    summary: str


class GenTell(gl.Contract):
    assessments: TreeMap[str, RiskAssessment]

    def __init__(self):
        pass

    def _assess_token(self, source_url: str, token_id: str) -> dict:
        def get_risk_assessment() -> str:
            web_data = gl.nondet.web.render(source_url, mode="text")

            task = f"""
You are a crypto security analyst. Analyze the following web page content
about a token ({token_id}) and assess its rug-pull / scam risk.

Look for red flags such as:
- Unlocked or absent liquidity
- Highly concentrated holder distribution (few wallets holding most of supply)
- Unverified or unaudited contract code
- Anonymous team with no social presence
- Mint / pause / blacklist functions giving the owner excessive control
- Abnormal trading patterns for a recently deployed token
- Missing or fake audit claims

Web content:
{web_data}

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
            result = gl.nondet.exec_prompt(task, response_format="json")
            return json.dumps(result, sort_keys=True)

        result_json = json.loads(
            gl.eq_principle.prompt_comparative(
                get_risk_assessment,
                "The results should agree on risk_score (within 10 points), "
                "risk_level, and the overall set of red flags identified. "
                "The summary field may be worded differently across validators "
                "as long as it conveys the same risk assessment.",
            )
        )
        return result_json

    @gl.public.write
    def assess_token(self, token_id: str, source_url: str) -> None:
        result = self._assess_token(source_url, token_id)

        self.assessments[token_id] = RiskAssessment(
            token_id=token_id,
            source_url=source_url,
            risk_score=u256(int(result["risk_score"])),
            risk_level=str(result["risk_level"]),
            red_flags=str(result["red_flags"]),
            summary=str(result["summary"]),
        )

    @gl.public.view
    def get_assessment(self, token_id: str) -> dict:
        if token_id not in self.assessments:
            raise Exception("No assessment found for this token")
        a = self.assessments[token_id]
        return {
            "token_id": a.token_id,
            "source_url": a.source_url,
            "risk_score": a.risk_score,
            "risk_level": a.risk_level,
            "red_flags": a.red_flags,
            "summary": a.summary,
        }

    @gl.public.view
    def get_all_assessments(self) -> dict:
        return {
            k: {
                "token_id": v.token_id,
                "source_url": v.source_url,
                "risk_score": v.risk_score,
                "risk_level": v.risk_level,
                "red_flags": v.red_flags,
                "summary": v.summary,
            }
            for k, v in self.assessments.items()
        }
