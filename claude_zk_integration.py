"""Experimental, provider-neutral prompt adapter for reviewing ZK source code.

The default provider is deterministic and offline. Live Anthropic access is an
explicit opt-in so importing or testing this module never requires credentials.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Protocol


class TextProvider(Protocol):
    """Small boundary implemented by offline and hosted text providers."""

    def complete(self, prompt: str) -> str:
        """Return a response for ``prompt``."""


@dataclass(frozen=True)
class DryRunProvider:
    """Deterministic provider used for local development and tests."""

    def complete(self, prompt: str) -> str:
        return (
            "[dry-run] No request was sent. "
            f"Prepared a {len(prompt)}-character review prompt."
        )


class AnthropicProvider:
    """Optional adapter for the current Anthropic Messages API."""

    def __init__(self, *, api_key: str, model: str, max_tokens: int = 800):
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for live mode")
        if not model:
            raise ValueError("ANTHROPIC_MODEL is required for live mode")

        try:
            from anthropic import Anthropic
        except ImportError as error:
            raise RuntimeError(
                "Live mode requires the optional dependency: "
                "python -m pip install '.[live]'"
            ) from error

        self._client = Anthropic(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens

    def complete(self, prompt: str) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return "\n".join(
            block.text for block in response.content if hasattr(block, "text")
        )


@dataclass
class ZKReviewAssistant:
    """Build review prompts without claiming to verify a proof."""

    provider: TextProvider

    def analyze_source(self, source: str) -> str:
        if not source.strip():
            raise ValueError("source must not be empty")
        prompt = (
            "Review the following zero-knowledge circuit source. Identify likely "
            "constraint, privacy, and input-validation risks. Do not claim that "
            "the circuit or a proof is verified; recommend compiler tests and an "
            "independent cryptographic review.\n\n"
            f"{source}"
        )
        return self.provider.complete(prompt)

    def chat(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("prompt must not be empty")
        return self.provider.complete(prompt)


def build_provider(*, live: bool) -> TextProvider:
    if not live:
        return DryRunProvider()
    return AnthropicProvider(
        api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        model=os.getenv("ANTHROPIC_MODEL", ""),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="send the prompt through Anthropic (requires explicit credentials)",
    )
    parser.add_argument(
        "--source",
        default="fn main(x: Field) { assert(x != 0); }",
        help="circuit source to place in the review prompt",
    )
    args = parser.parse_args(argv)

    assistant = ZKReviewAssistant(build_provider(live=args.live))
    print(assistant.analyze_source(args.source))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
