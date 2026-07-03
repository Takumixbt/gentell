# GenTell

A [GenLayer](https://genlayer.com) intelligent contract that scores crypto tokens for rug-pull / scam risk.

Give it a token's Ticker or CA and it scrapes the page and asks an LLM to assess red flags — unlocked liquidity, concentrated holder distribution, unverified contracts, anonymous teams, mint/pause/blacklist backdoors, and more. The assessment is reconciled across validators on-chain via `gl.eq_principle.strict_eq`, so the result isn't just one model's opinion — it's a consensus result.

## How it works

The contract (`contracts/gentell.py`) exposes:

- `assess_token(token_id, source_url)` — fetches the page at `source_url`, runs the risk analysis prompt through the LLM, and stores a `RiskAssessment` (risk score 0-100, risk level, red flags, one-line summary) keyed by `token_id`.
- `get_assessment(token_id)` — returns the stored assessment for a token.
- `get_all_assessments()` — returns every assessment stored so far.

## Project layout

- `contracts/gentell.py` — the intelligent contract.
- `test/test_gentell.py` — direct-mode tests (web + LLM calls mocked, no Studio/Docker needed).
- `app/` — Vue 3 + Vite + Tailwind frontend. Dark hero UI with a token search, live-updating assessment feed, and wallet connect via `genlayer-js`. Falls back to a simulated "demo mode" when no contract address is configured, so the UI is explorable without a deployment.
- `deploy/deployScript.ts` — deploys the contract via `genlayer-js`.
- `config/`, `tools/` — GenLayer testing-suite config and helpers.

## Running the tests

```bash
python -m venv .venv
.venv\Scripts\activate      # or source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
pytest test/
```

These are direct-mode tests — they mock the web fetch and LLM call, so no GenLayer Studio or localnet is required.

> **Windows note:** `genlayer-testing-suite`'s direct-mode VM loader calls `os.unlink()` on a temp file immediately after `os.dup2`'ing it onto stdin. That's fine on POSIX but raises `PermissionError: WinError 32` on Windows since the file is still open. If you hit this, patch the `os.unlink` call in `gltest/direct/loader.py` (in your venv's site-packages) to swallow `OSError`.

## Deploying

Deploying and running end-to-end against a live GenLayer Studio/localnet requires Docker and an LLM provider configured via `genlayer init`. That step needs an interactive terminal (the provider-selection prompt won't run through a piped/non-TTY shell), so run it yourself:

```bash
genlayer init
genlayer up
```

Then deploy `contracts/gentell.py` through the Studio UI, or via `deploy/deployScript.ts`.

## Running the frontend

```bash
cd app
npm install
cp .env.example .env   # fill in VITE_CONTRACT_ADDRESS after deploying
npm run dev
```

Without `VITE_CONTRACT_ADDRESS` set, the app runs in demo mode with simulated results.

## License

MIT — see [LICENSE](LICENSE).
