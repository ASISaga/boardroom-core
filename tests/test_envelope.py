"""Envelope normalization tests (01, INV-3, INV-5)."""

from __future__ import annotations

import pytest

from boardroom_core import Envelope, agenda, business_event, make_envelope, user_message


def test_all_three_triggers_normalize_to_one_shape():
    envelopes = [
        make_envelope(source="agui", company_id="acme", payload=user_message("hi", "u1")),
        make_envelope(
            source="eventgrid",
            company_id="acme",
            payload=business_event("invoice.overdue", {"amount": 1200}),
            dedupe_id="eg-1",
        ),
        make_envelope(source="manual", company_id="acme", payload=agenda("Q3 review")),
    ]
    for envelope in envelopes:
        body = envelope.to_dict()
        assert body["schema"] == "boardroom.msg.v1"
        assert body["company_id"] == "acme"
        envelope.validate()


def test_eventgrid_dedupe_id_is_the_event_id():
    envelope = make_envelope(
        source="eventgrid",
        company_id="acme",
        payload=business_event("x", {}),
        dedupe_id="event-42",
    )
    assert envelope.dedupe_id == "event-42"


def test_dedupe_id_defaults_to_a_fresh_uuid_per_envelope():
    first = make_envelope(source="agui", company_id="acme", payload=agenda("a"))
    second = make_envelope(source="agui", company_id="acme", payload=agenda("a"))
    assert first.dedupe_id != second.dedupe_id


def test_empty_company_id_is_rejected():
    with pytest.raises(ValueError):
        make_envelope(source="agui", company_id="", payload=agenda("a"))


def test_max_rounds_is_capped_at_the_hard_cap():
    with pytest.raises(ValueError):
        make_envelope(source="agui", company_id="acme", payload=agenda("a"), max_rounds=6)


def test_round_trip_through_dict_preserves_every_field():
    original = make_envelope(
        source="agui",
        company_id="acme",
        payload=user_message("hello", "u1", actor_claim="jws"),
        stream=False,
        max_rounds=5,
        trace="00-abc-def-01",
    )
    restored = Envelope.from_dict(original.to_dict())
    assert restored == original


def test_actor_claim_is_carried_but_actor_is_audit_only():
    payload = user_message("hello", "u1", actor_claim="signed-jws")
    assert payload["actor"] == "u1"
    assert payload["actor_claim"] == "signed-jws"
