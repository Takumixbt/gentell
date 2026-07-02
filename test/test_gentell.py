"""Direct-mode tests for the token risk oracle — web + LLM calls are mocked."""

import json


def _setup_risk_mocks(vm, page_body, risk_score, risk_level, red_flags, summary):
    vm.mock_web(r".*dexscreener\.com.*", {"status": 200, "body": page_body})
    vm.mock_llm(
        r".*crypto security analyst.*",
        json.dumps(
            {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "red_flags": red_flags,
                "summary": summary,
            }
        ),
    )


def test_assess_low_risk_token(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/gentell.py")
    direct_vm.sender = direct_alice

    _setup_risk_mocks(
        direct_vm,
        "Liquidity locked for 1 year. Contract verified. Team doxxed. Audit by CertiK.",
        risk_score=5,
        risk_level="low",
        red_flags="none",
        summary="Token appears safe with locked liquidity and a verified audit.",
    )

    contract.assess_token("SAFE", "https://dexscreener.com/eth/safe")

    result = contract.get_assessment("SAFE")
    assert result["risk_score"] == 5
    assert result["risk_level"] == "low"
    assert result["red_flags"] == "none"
    assert result["source_url"] == "https://dexscreener.com/eth/safe"


def test_assess_high_risk_token(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/gentell.py")
    direct_vm.sender = direct_alice

    _setup_risk_mocks(
        direct_vm,
        "Liquidity unlocked. Top wallet holds 80% of supply. No socials found.",
        risk_score=95,
        risk_level="critical",
        red_flags="unlocked liquidity, concentrated holders, anonymous team",
        summary="Extremely high risk of rug pull.",
    )

    contract.assess_token("SCAM", "https://dexscreener.com/eth/scam")

    result = contract.get_assessment("SCAM")
    assert result["risk_score"] == 95
    assert result["risk_level"] == "critical"
    assert "unlocked liquidity" in result["red_flags"]


def test_get_assessment_not_found_fails(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/gentell.py")
    direct_vm.sender = direct_alice

    with direct_vm.expect_revert("No assessment found for this token"):
        contract.get_assessment("UNKNOWN")


def test_reassess_token_updates_existing(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/gentell.py")
    direct_vm.sender = direct_alice

    _setup_risk_mocks(
        direct_vm,
        "Liquidity locked.",
        risk_score=10,
        risk_level="low",
        red_flags="none",
        summary="Looks fine.",
    )
    contract.assess_token("TOK", "https://dexscreener.com/eth/tok")
    assert contract.get_assessment("TOK")["risk_score"] == 10

    direct_vm.clear_mocks()
    _setup_risk_mocks(
        direct_vm,
        "Liquidity was removed overnight.",
        risk_score=99,
        risk_level="critical",
        red_flags="liquidity removed",
        summary="Rug pull detected.",
    )
    contract.assess_token("TOK", "https://dexscreener.com/eth/tok")
    assert contract.get_assessment("TOK")["risk_score"] == 99


def test_get_all_assessments(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/gentell.py")
    direct_vm.sender = direct_alice

    _setup_risk_mocks(
        direct_vm,
        "Safe token.",
        risk_score=5,
        risk_level="low",
        red_flags="none",
        summary="Safe.",
    )
    contract.assess_token("A", "https://dexscreener.com/eth/a")

    direct_vm.clear_mocks()
    _setup_risk_mocks(
        direct_vm,
        "Risky token.",
        risk_score=90,
        risk_level="critical",
        red_flags="unlocked liquidity",
        summary="Risky.",
    )
    contract.assess_token("B", "https://dexscreener.com/eth/b")

    all_assessments = contract.get_all_assessments()
    assert len(all_assessments) == 2
    assert all_assessments["A"]["risk_score"] == 5
    assert all_assessments["B"]["risk_score"] == 90
