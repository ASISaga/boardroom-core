"""Envelope construction and normalization (01, INV-3, INV-5).

Every trigger — agui, eventgrid, manual — normalizes to an Envelope here and
enters the single ``invoke_boardroom`` path. There is no trigger-specific
invocation path anywhere in this repository.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Literal

from boardroom_core.schemas import validate_envelope

Source = Literal["agui", "eventgrid", "manual"]

DEFAULT_MAX_ROUNDS = 3
HARD_MAX_ROUNDS = 5


@dataclass(frozen=True)
class Options:
    """Envelope options (01). ``max_rounds`` is capped at 5 by schema (02 Q)."""

    stream: bool = True
    max_rounds: int = DEFAULT_MAX_ROUNDS

    def to_dict(self) -> dict[str, Any]:
        return {"stream": self.stream, "max_rounds": self.max_rounds}


@dataclass(frozen=True)
class Envelope:
    """``boardroom.msg.v1`` — the only inbound shape O accepts."""

    company_id: str
    source: Source
    payload: dict[str, Any]
    dedupe_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    options: Options = field(default_factory=Options)
    trace: str | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "schema": "boardroom.msg.v1",
            "source": self.source,
            "company_id": self.company_id,
            "dedupe_id": self.dedupe_id,
            "payload": self.payload,
            "options": self.options.to_dict(),
        }
        if self.trace is not None:
            out["trace"] = self.trace
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Envelope":
        validate_envelope(data)
        opts = data.get("options") or {}
        return cls(
            company_id=data["company_id"],
            source=data["source"],
            payload=data["payload"],
            dedupe_id=data["dedupe_id"],
            options=Options(
                stream=opts.get("stream", True),
                max_rounds=opts.get("max_rounds", DEFAULT_MAX_ROUNDS),
            ),
            trace=data.get("trace"),
        )

    def validate(self) -> None:
        validate_envelope(self.to_dict())


def user_message(text: str, actor: str, actor_claim: str | None = None) -> dict[str, Any]:
    """Build a ``UserMsg`` payload (01)."""
    payload: dict[str, Any] = {"kind": "user_message", "text": text, "actor": actor}
    if actor_claim is not None:
        payload["actor_claim"] = actor_claim
    return payload


def business_event(event_type: str, data: dict[str, Any]) -> dict[str, Any]:
    """Build a ``BizEvent`` payload (01). Event text is data, never instruction (06)."""
    return {"kind": "business_event", "event_type": event_type, "data": data}


def agenda(text: str) -> dict[str, Any]:
    """Build an ``Agenda`` payload (01)."""
    return {"kind": "agenda", "text": text}


def make_envelope(
    *,
    source: Source,
    company_id: str,
    payload: dict[str, Any],
    dedupe_id: str | None = None,
    stream: bool = True,
    max_rounds: int = DEFAULT_MAX_ROUNDS,
    trace: str | None = None,
) -> Envelope:
    """Normalize any trigger into an Envelope (INV-3).

    ``company_id`` MUST already have been derived from authenticated
    server-side context by the caller (INV-5); this function does not and
    cannot make an untrusted identifier trustworthy.
    """
    if not company_id:
        raise ValueError("company_id is required and MUST be server-derived (INV-5)")
    if not 1 <= max_rounds <= HARD_MAX_ROUNDS:
        raise ValueError(f"max_rounds must be within 1..{HARD_MAX_ROUNDS} (02 section Q)")
    env = Envelope(
        company_id=company_id,
        source=source,
        payload=payload,
        dedupe_id=dedupe_id or str(uuid.uuid4()),
        options=Options(stream=stream, max_rounds=max_rounds),
        trace=trace,
    )
    env.validate()
    return env
