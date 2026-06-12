"""Generic logits adaptation hooks for token-level decoding.

Logit adapters are optional extension points for decoders that expose token logits.
They run after a model produces logits and before sampling chooses the next token.
When no adapters are supplied, logits are returned unchanged. Future modules,
including psychodynamic or parapraxis-style decoders, should plug into this
interface instead of modifying core generation logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence, TypeAlias

TensorLike: TypeAlias = Any


@dataclass(frozen=True)
class GenerationRuntimeState:
    """Static context available before a decoding run starts."""

    input_ids: Sequence[int] = ()
    prompt_text: str | None = None
    model_name: str | None = None
    tokenizer: Any | None = None
    sampling_config: Mapping[str, Any] | None = None
    metadata: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class DecodingState:
    """Per-step context passed to logit adapters during token decoding.

    ``prompt_text`` is the original prompt when available.
    ``generated_prefix_text`` is decoded from the current ``generated_ids`` when
    a tokenizer is available, so it evolves as generation proceeds.
    """

    step_index: int
    input_ids: Sequence[int]
    generated_ids: Sequence[int]
    prompt_text: str | None = None
    generated_prefix_text: str | None = None
    tokenizer: Any | None = None
    sampling_config: Mapping[str, Any] | None = None
    metadata: Mapping[str, Any] | None = None


class LogitAdapter(Protocol):
    """Protocol for optional logits processors used by decoding loops."""

    def prepare(self, runtime_state: GenerationRuntimeState) -> None:
        """Receive run-level context before token generation begins."""

    def adjust_logits(self, logits: TensorLike, decoding_state: DecodingState) -> TensorLike:
        """Return logits to use for sampling the next token."""


class NoOpLogitAdapter:
    """Logit adapter that intentionally preserves logits unchanged."""

    def prepare(self, runtime_state: GenerationRuntimeState) -> None:
        del runtime_state

    def adjust_logits(self, logits: TensorLike, decoding_state: DecodingState) -> TensorLike:
        del decoding_state
        return logits


def prepare_logit_adapters(
    logit_adapters: Sequence[LogitAdapter] | None,
    runtime_state: GenerationRuntimeState,
) -> None:
    """Prepare adapters in deterministic order when any are configured."""

    for adapter in logit_adapters or ():
        adapter.prepare(runtime_state)


def apply_logit_adapters(
    logits: TensorLike,
    decoding_state: DecodingState,
    logit_adapters: Sequence[LogitAdapter] | None = None,
) -> TensorLike:
    """Apply configured adapters after model logits and before sampling."""

    adjusted_logits = logits
    for adapter in logit_adapters or ():
        adjusted_logits = adapter.adjust_logits(adjusted_logits, decoding_state)
    return adjusted_logits
