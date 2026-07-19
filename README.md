# Quantum ZK infrastructure

## Status: experimental prompt adapter

This repository is **not ZK infrastructure, a prover, or a proof verifier**. It
preserves an early experiment that sends circuit source to a text model for
review. Model output can be incomplete or wrong and must not be treated as a
security audit.

The original prototype used a retired Anthropic chat interface and model name.
It has been replaced with a small provider boundary:

- offline dry-run mode is the default and makes no network requests;
- tests do not install the Anthropic SDK or require an API key;
- live mode is explicit and uses the Anthropic Messages API; and
- prompts clearly distinguish source review from cryptographic verification.

## Local dry run

Requires Python 3.10 or newer.

```sh
python claude_zk_integration.py
python -m unittest discover -s tests
```

The first command only reports the prompt size. It does not send source code
anywhere.

## Optional live mode

```sh
python -m pip install '.[live]'
export ANTHROPIC_API_KEY='...'
export ANTHROPIC_MODEL='a-model-available-to-your-account'
python claude_zk_integration.py --live --source 'fn main(x: Field) { assert(x != 0); }'
```

Do not submit private circuits, witness data, secrets, or customer data to a
hosted model. Model access and model selection remain the operator's
responsibility.

## Roadmap before production use

- Define a supported circuit language and structured review result.
- Add compiler-backed checks instead of relying on prose.
- Add threat models, data-retention controls, and provider-specific tests.
- Obtain independent cryptographic and application-security review.
