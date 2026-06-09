"""Minimal token decoding utilities with optional logit-adapter support."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

from psychodynamic_agent.llm.logit_adapters import (
    DecodingState,
    GenerationRuntimeState,
    LogitAdapter,
    TensorLike,
    apply_logit_adapters,
    prepare_logit_adapters,
)


class TokenLogitModel(Protocol):
    """Model protocol for decoders that expose next-token logits."""

    def next_logits(self, input_ids: Sequence[int], generated_ids: Sequence[int]) -> TensorLike:
        """Return base logits for the next token."""


class TokenSampler(Protocol):
    """Sampler protocol that chooses a token from adjusted logits."""

    def sample(self, logits: TensorLike) -> int:
        """Select the next token from logits."""


@dataclass(frozen=True)
class GenerationConfig:
    """Configuration for token-level generation."""

    max_new_tokens: int
    eos_token_id: int | None = None
    sampling_config: Mapping[str, Any] | None = None
    logit_adapters: Sequence[LogitAdapter] | None = None
    metadata: Mapping[str, Any] | None = None


def generate_tokens(
    *,
    model: TokenLogitModel,
    sampler: TokenSampler,
    input_ids: Sequence[int],
    config: GenerationConfig,
    tokenizer: Any | None = None,
    prompt_text: str | None = None,
) -> list[int]:
    """Generate tokens, applying optional logit adapters before each sample.

    The behavior is unchanged when ``config.logit_adapters`` is ``None`` or empty:
    model logits are passed directly to the sampler.
    """

    generated_ids: list[int] = []
    runtime_state = GenerationRuntimeState(
        input_ids=input_ids,
        prompt_text=prompt_text,
        tokenizer=tokenizer,
        sampling_config=config.sampling_config,
        metadata=config.metadata,
    )
    prepare_logit_adapters(config.logit_adapters, runtime_state)

    for step_index in range(config.max_new_tokens):
        base_logits = model.next_logits(input_ids, generated_ids)
        decoding_state = DecodingState(
            step_index=step_index,
            input_ids=input_ids,
            generated_ids=tuple(generated_ids),
            prefix_text=prompt_text,
            tokenizer=tokenizer,
            sampling_config=config.sampling_config,
            metadata=config.metadata,
        )
        logits = apply_logit_adapters(base_logits, decoding_state, config.logit_adapters)
        next_token = sampler.sample(logits)
        generated_ids.append(next_token)
        if config.eos_token_id is not None and next_token == config.eos_token_id:
            break

    return generated_ids
