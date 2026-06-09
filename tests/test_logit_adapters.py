from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from psychodynamic_agent.llm.decoding import GenerationConfig, generate_tokens
from psychodynamic_agent.llm.logit_adapters import (
    DecodingState,
    GenerationRuntimeState,
    NoOpLogitAdapter,
    apply_logit_adapters,
)


@dataclass
class FakeModel:
    logits_by_step: list[list[float]]
    calls: list[tuple[tuple[int, ...], tuple[int, ...]]] = field(default_factory=list)

    def next_logits(self, input_ids: Sequence[int], generated_ids: Sequence[int]) -> list[float]:
        self.calls.append((tuple(input_ids), tuple(generated_ids)))
        return list(self.logits_by_step[len(generated_ids)])


@dataclass
class ArgmaxSampler:
    seen_logits: list[list[float]] = field(default_factory=list)

    def sample(self, logits: list[float]) -> int:
        self.seen_logits.append(list(logits))
        return max(range(len(logits)), key=lambda idx: logits[idx])


class BiasTokenAdapter:
    def __init__(self, token_id: int, bias: float):
        self.token_id = token_id
        self.bias = bias
        self.prepared = False

    def prepare(self, runtime_state: GenerationRuntimeState) -> None:
        del runtime_state
        self.prepared = True

    def adjust_logits(self, logits: list[float], decoding_state: DecodingState) -> list[float]:
        del decoding_state
        adjusted = list(logits)
        adjusted[self.token_id] += self.bias
        return adjusted


class AddConstantAdapter:
    def __init__(self, amount: float, calls: list[str], name: str):
        self.amount = amount
        self.calls = calls
        self.name = name

    def prepare(self, runtime_state: GenerationRuntimeState) -> None:
        del runtime_state

    def adjust_logits(self, logits: list[float], decoding_state: DecodingState) -> list[float]:
        del decoding_state
        self.calls.append(self.name)
        return [value + self.amount for value in logits]


class MultiplyAdapter:
    def __init__(self, factor: float, calls: list[str], name: str):
        self.factor = factor
        self.calls = calls
        self.name = name

    def prepare(self, runtime_state: GenerationRuntimeState) -> None:
        del runtime_state

    def adjust_logits(self, logits: list[float], decoding_state: DecodingState) -> list[float]:
        del decoding_state
        self.calls.append(self.name)
        return [value * self.factor for value in logits]


def test_generation_works_with_no_adapters() -> None:
    model = FakeModel(logits_by_step=[[0.1, 0.9], [1.0, 0.0]])
    sampler = ArgmaxSampler()

    generated = generate_tokens(
        model=model,
        sampler=sampler,
        input_ids=[42],
        config=GenerationConfig(max_new_tokens=2),
    )

    assert generated == [1, 0]
    assert sampler.seen_logits == [[0.1, 0.9], [1.0, 0.0]]
    assert model.calls == [((42,), ()), ((42,), (1,))]


def test_no_op_adapter_does_not_change_logits() -> None:
    logits = [0.2, 0.5, 0.3]
    state = DecodingState(step_index=0, input_ids=[1], generated_ids=[])

    adjusted = apply_logit_adapters(logits, state, [NoOpLogitAdapter()])

    assert adjusted == logits
    assert adjusted is logits


def test_biasing_adapter_modifies_logits_before_sampling() -> None:
    adapter = BiasTokenAdapter(token_id=0, bias=2.0)
    model = FakeModel(logits_by_step=[[0.0, 1.0]])
    sampler = ArgmaxSampler()

    generated = generate_tokens(
        model=model,
        sampler=sampler,
        input_ids=[7],
        config=GenerationConfig(max_new_tokens=1, logit_adapters=[adapter]),
    )

    assert adapter.prepared is True
    assert sampler.seen_logits == [[2.0, 1.0]]
    assert generated == [0]


def test_multiple_adapters_apply_in_supplied_order() -> None:
    calls: list[str] = []
    state = DecodingState(step_index=0, input_ids=[], generated_ids=[])

    adjusted = apply_logit_adapters(
        [1.0],
        state,
        [AddConstantAdapter(1.0, calls, "add"), MultiplyAdapter(3.0, calls, "multiply")],
    )

    assert calls == ["add", "multiply"]
    assert adjusted == [6.0]
