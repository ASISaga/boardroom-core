"""Schema contract tests — release gate 3 (08).

Envelope (01), Evt and Digest (14) are validated against their JSON Schemas.
"""

from __future__ import annotations

import pytest

from boardroom_core import (
    ALL_SCHEMAS,
    EVT_TYPES,
    MVP_ROSTER,
    SchemaError,
    validate_digest,
    validate_envelope,
    validate_evt,
    validate_resonance,
)
from boardroom_core.evt import (
    Evt,
    EvtStream,
    is_domain_veto,
    is_recordable_dissent,
    outside_roster_competence,
)


def _digest(**overrides):
    digest = {
        "decision": "Hold the price and extend the trial to 30 days.",
        "rationale": "Runway supports it; the market objection is about proof, not price.",
        "owners": ["cmo"],
        "follow_ups": [{"role": "cfo", "action": "Re-forecast runway", "due": "2026-08-31"}],
        "dissent": [],
        "resonance": [
            {
                "role": "cfo",
                "rationale": "Extends payback but does not threaten runway.",
                "score": 0.65,
                "confidence": "medium",
                "domain_relevance": 0.9,
            }
        ],
        "overridden_vetoes": [],
        "purpose_hash": "a" * 64,
        "prompt_hash": "b" * 64,
        "model_versions": {"founder": "v1", "cfo": "v1", "cmo": "v1"},
        "tokens": 4210,
        "duration_s": 38.2,
    }
    digest.update(overrides)
    return digest


def test_every_schema_declares_its_id():
    for schema_id, schema in ALL_SCHEMAS.items():
        assert schema["$id"] == schema_id


def test_envelope_round_trips():
    envelope = {
        "schema": "boardroom.msg.v1",
        "source": "agui",
        "company_id": "acme",
        "dedupe_id": "d1",
        "payload": {"kind": "user_message", "text": "hello", "actor": "u1"},
    }
    validate_envelope(envelope)


def test_envelope_rejects_unknown_source():
    with pytest.raises(SchemaError):
        validate_envelope(
            {
                "schema": "boardroom.msg.v1",
                "source": "smtp",
                "company_id": "acme",
                "dedupe_id": "d1",
                "payload": {"kind": "agenda", "text": "x"},
            }
        )


def test_envelope_rejects_additional_properties():
    with pytest.raises(SchemaError):
        validate_envelope(
            {
                "schema": "boardroom.msg.v1",
                "source": "agui",
                "company_id": "acme",
                "dedupe_id": "d1",
                "payload": {"kind": "agenda", "text": "x"},
                "isolation_key": "nope",
            }
        )


def test_envelope_caps_max_rounds_at_five():
    with pytest.raises(SchemaError):
        validate_envelope(
            {
                "schema": "boardroom.msg.v1",
                "source": "manual",
                "company_id": "acme",
                "dedupe_id": "d1",
                "payload": {"kind": "agenda", "text": "x"},
                "options": {"max_rounds": 6},
            }
        )


@pytest.mark.parametrize("evt_type", EVT_TYPES)
def test_every_declared_evt_type_validates(evt_type):
    validate_evt(Evt(turn_id="t", seq=0, type=evt_type, actor="founder").to_dict())


def test_evt_type_enum_is_closed_for_v1():
    with pytest.raises(SchemaError):
        validate_evt(Evt(turn_id="t", seq=0, type="turn_paused", actor="founder").to_dict())


def test_evt_seq_is_strictly_increasing_within_a_turn():
    stream = EvtStream("t1")
    seqs = [stream.emit("speaker_delta", "cfo", {"text": "x"}).seq for _ in range(5)]
    assert seqs == sorted(seqs) and len(set(seqs)) == 5


def test_digest_validates_with_nested_resonance():
    validate_digest(_digest())


def test_digest_requires_dissent_array_even_when_unanimous():
    digest = _digest()
    del digest["dissent"]
    with pytest.raises(SchemaError):
        validate_digest(digest)


def test_digest_rejects_out_of_range_resonance_score():
    with pytest.raises(SchemaError):
        validate_digest(
            _digest(
                resonance=[
                    {
                        "role": "cfo",
                        "rationale": "r",
                        "score": 1.4,
                        "confidence": "high",
                        "domain_relevance": 0.9,
                    }
                ]
            )
        )


def test_resonance_requires_rationale():
    with pytest.raises(SchemaError):
        validate_resonance(
            {"role": "cfo", "score": 0.5, "confidence": "low", "domain_relevance": 0.5}
        )


def test_domain_veto_thresholds_match_the_chair_obligation_table():
    veto = {"role": "cfo", "rationale": "r", "score": 0.1, "confidence": "high", "domain_relevance": 0.8}
    dissent = {"role": "cfo", "rationale": "r", "score": 0.3, "confidence": "high", "domain_relevance": 0.7}
    irrelevant = {"role": "cmo", "rationale": "r", "score": 0.1, "confidence": "low", "domain_relevance": 0.2}

    assert is_domain_veto(veto)
    assert not is_domain_veto(dissent)
    assert not is_domain_veto(irrelevant)  # low score but outside the domain
    assert is_recordable_dissent(dissent)
    assert outside_roster_competence([irrelevant])
    assert not outside_roster_competence([veto, irrelevant])


def test_mvp_roster_is_founder_cfo_cmo():
    assert MVP_ROSTER == ("founder", "cfo", "cmo")
