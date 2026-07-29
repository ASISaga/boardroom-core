"""Evt stream frames (14) and the MVP roster (06).

The ``Evt`` ``type`` enum is CLOSED for ``boardroom.evt.v1``. Consumers MUST
treat an unrecognized type as informative-only (14 forward-compatibility rule):
log it, render a generic fallback or nothing, never error and never drop the
connection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final

from boardroom_core.schemas import validate_evt

#: MVP base roster (06) — fixed and not user-configurable at v1.
CHAIR_ROLE: Final = "founder"
CXO_ROLES: Final[tuple[str, ...]] = ("cfo", "cmo")
MVP_ROSTER: Final[tuple[str, ...]] = (CHAIR_ROLE, *CXO_ROLES)

#: Non-roster actor ids permitted on an Evt frame (14).
SYSTEM_ACTORS: Final[tuple[str, ...]] = ("system", "user")

EVT_TYPES: Final[tuple[str, ...]] = (
    "boardroom_hydrated",
    "turn_started",
    "speaker_started",
    "speaker_delta",
    "speaker_done",
    "position_stated",
    "resolution",
    "state_persisted",
    "state_conflict",
    "turn_complete",
    "turn_cancelled",
    "turn_failed",
)

#: Terminal frames — exactly one closes a turn (02 P6).
TERMINAL_EVT_TYPES: Final[tuple[str, ...]] = (
    "turn_complete",
    "turn_cancelled",
    "turn_failed",
)

#: POSITION values a CXO may state (06).
POSITIONS: Final[tuple[str, ...]] = ("support", "oppose", "amend", "defer")

#: Domain-veto thresholds (17 chair obligations).
VETO_SCORE_MAX: Final = 0.2
DISSENT_SCORE_MAX: Final = 0.4
DOMAIN_RELEVANCE_MIN: Final = 0.6


@dataclass
class Evt:
    """``boardroom.evt.v1`` frame. ``seq`` is strictly increasing within a turn."""

    turn_id: str
    seq: int
    type: str
    actor: str
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "boardroom.evt.v1",
            "turn_id": self.turn_id,
            "seq": self.seq,
            "type": self.type,
            "actor": self.actor,
            "data": self.data,
        }

    def validate(self) -> None:
        validate_evt(self.to_dict())


class EvtStream:
    """Sequence-number allocator for one turn (14: total order per turn by seq)."""

    def __init__(self, turn_id: str) -> None:
        self.turn_id = turn_id
        self._seq = 0

    def emit(self, type: str, actor: str, data: dict[str, Any] | None = None) -> Evt:
        evt = Evt(
            turn_id=self.turn_id,
            seq=self._seq,
            type=type,
            actor=actor,
            data=data or {},
        )
        self._seq += 1
        evt.validate()
        return evt


def is_domain_veto(resonance: dict[str, Any]) -> bool:
    """Domain veto (17): score below 0.2 with domain_relevance at or above 0.6."""
    return (
        resonance["score"] < VETO_SCORE_MAX
        and resonance["domain_relevance"] >= DOMAIN_RELEVANCE_MIN
    )


def is_recordable_dissent(resonance: dict[str, Any]) -> bool:
    """Must be recorded in ``Digest.dissent`` (17) whether or not the decision proceeds."""
    return (
        resonance["score"] < DISSENT_SCORE_MAX
        and resonance["domain_relevance"] >= DOMAIN_RELEVANCE_MIN
    )


def outside_roster_competence(resonances: list[dict[str, Any]]) -> bool:
    """Every role's ``domain_relevance`` below 0.6 (17): say so, do not manufacture judgment."""
    return bool(resonances) and all(
        r["domain_relevance"] < DOMAIN_RELEVANCE_MIN for r in resonances
    )
