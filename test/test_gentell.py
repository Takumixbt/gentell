"""Direct-mode tests for the token risk oracle — web + LLM calls are mocked."""

import json

API_PATTERN = r".*api\.gopluslabs\.io.*"
LLM_PATTERN = r".*crypto security analyst.*"


def _setup_risk_mocks(
    vm,
    contract_address,
    security_data,
    risk_score,
    risk_level,
    red_flags,
    summary,
):
    body = json.dumps(
        {
            "code": 1,
            "message": "OK",
            "result": {contract_address.lower(): security_data},
        }
    )
    vm.mock_web(API_PATTERN, {"status": 200, "body": body})
    vm.mock_llm(
        LLM_PATTERN,
        json.dumps(
            {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "red_flags": red_flags,
                "summary": summary,
            }
        ),
    )


SAFE_ADDRESS = "0x0000000000000000000000000000000000000A"
SCAM_ADDRESS = "0x0000000000000000000000000000000000000B"


def test_assess_low_risk_token(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/gentell.py")
    direct_vm.sender = direct_alice

    _setup_risk_mocks(
        direct_vm,
        SAFE_ADDRESS,
        {
            "token_symbol": "SAFE",
            "is_honeypot": "0",
            "is_mintable": "0",
            "is_open_source": "1",
            "is_blacklisted": "0",
            "owner_percent": "0.001",
            "holder_count": "50000",
        },
        risk_score=5,
        risk_level="low",
        red_flags="none",
        summary="Token appears safe with open-source code and no owner control red flags.",
    )

    contract.assess_token("1", SAFE_ADDRESS)

    result = contract.get_assessment(SAFE_ADDRESS)
    assert result["risk_score"] == 5
    assert result["risk_level"] == "low"
    assert result["red_flags"] == "none"
    assert result["token_symbol"] == "SAFE"
    assert result["chain_id"] == "1"


def test_assess_high_risk_token(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/gentell.py")
    direct_vm.sender = direct_alice

    _setup_risk_mocks(
        direct_vm,
        SCAM_ADDRESS,
        {
            "token_symbol": "SCAM",
            "is_honeypot": "1",
            "hidden_owner": "1",
            "is_mintable": "1",
            "is_open_source": "0",
            "owner_percent": "0.80",
        },
        risk_score=95,
        risk_level="critical",
        red_flags="honeypot, hidden owner, mintable, unverified contract, concentrated ownership",
        summary="Extremely high risk of rug pull.",
    )

    contract.assess_token("56", SCAM_ADDRESS)

    result = contract.get_assessment(SCAM_ADDRESS)
    assert result["risk_score"] == 95
    assert result["risk_level"] == "critical"
    assert "honeypot" in result["red_flags"]
    assert result["token_symbol"] == "SCAM"


def test_get_assessment_not_found_fails(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/gentell.py")
    direct_vm.sender = direct_alice

    with direct_vm.expect_revert("No assessment found for this contract"):
        contract.get_assessment("0x000000000000000000000000000000000000FF")


def test_reassess_token_updates_existing(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/gentell.py")
    direct_vm.sender = direct_alice

    _setup_risk_mocks(
        direct_vm,
        SAFE_ADDRESS,
        {"token_symbol": "TOK", "is_honeypot": "0"},
        risk_score=10,
        risk_level="low",
        red_flags="none",
        summary="Looks fine.",
    )
    contract.assess_token("1", SAFE_ADDRESS)
    assert contract.get_assessment(SAFE_ADDRESS)["risk_score"] == 10

    direct_vm.clear_mocks()
    _setup_risk_mocks(
        direct_vm,
        SAFE_ADDRESS,
        {"token_symbol": "TOK", "is_honeypot": "1", "selfdestruct": "1"},
        risk_score=99,
        risk_level="critical",
        red_flags="honeypot, selfdestruct function",
        summary="Rug pull detected.",
    )
    contract.assess_token("1", SAFE_ADDRESS)
    assert contract.get_assessment(SAFE_ADDRESS)["risk_score"] == 99


def test_get_all_assessments(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/gentell.py")
    direct_vm.sender = direct_alice

    _setup_risk_mocks(
        direct_vm,
        SAFE_ADDRESS,
        {"token_symbol": "A", "is_honeypot": "0"},
        risk_score=5,
        risk_level="low",
        red_flags="none",
        summary="Safe.",
    )
    contract.assess_token("1", SAFE_ADDRESS)

    direct_vm.clear_mocks()
    _setup_risk_mocks(
        direct_vm,
        SCAM_ADDRESS,
        {"token_symbol": "B", "is_honeypot": "1"},
        risk_score=90,
        risk_level="critical",
        red_flags="honeypot",
        summary="Risky.",
    )
    contract.assess_token("1", SCAM_ADDRESS)

    all_assessments = contract.get_all_assessments()
    assert len(all_assessments) == 2
    assert all_assessments[SAFE_ADDRESS.lower()]["risk_score"] == 5
    assert all_assessments[SCAM_ADDRESS.lower()]["risk_score"] == 90
