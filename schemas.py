"""Wire contracts shared by F (03) and O (02).

Every schema in this module is transcribed verbatim from the normative spec
files and is the single source of truth for both sides of the wire:

- ``ENVELOPE_SCHEMA``  — ``boardroom.msg.v1``       (01-architecture.md)
- ``EVT_SCHEMA``       — ``boardroom.evt.v1``       (14-agent-schemas.md)
- ``DIGEST_SCHEMA``    — ``boardroom.digest.v1``    (14-agent-schemas.md)
- ``RESONANCE_SCHEMA`` — ``boardroom.resonance.v1`` (16-purpose-and-resonance.md)
- ``CONNECTOR_SCHEMA`` — ``boardroom.connector.v1`` (15-company-data-access.md)

Schemas are versioned by their ``$id`` (00-INDEX rule A4): a breaking change
bumps the version and both versions are accepted for one release.
"""

from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ENVELOPE_SCHEMA_ID = "boardroom.msg.v1"
EVT_SCHEMA_ID = "boardroom.evt.v1"
DIGEST_SCHEMA_ID = "boardroom.digest.v1"
RESONANCE_SCHEMA_ID = "boardroom.resonance.v1"
CONNECTOR_SCHEMA_ID = "boardroom.connector.v1"

#: Envelope — the only inbound shape O accepts (01).
ENVELOPE_SCHEMA: dict[str, Any] = {
    "$id": ENVELOPE_SCHEMA_ID,
    "type": "object",
    "additionalProperties": False,
    "required": ["schema", "source", "company_id", "dedupe_id", "payload"],
    "properties": {
        "schema": {"const": ENVELOPE_SCHEMA_ID},
        "source": {"enum": ["agui", "eventgrid", "manual"]},
        "company_id": {"type": "string", "minLength": 1},
        "dedupe_id": {
            "type": "string",
            "description": "EventGrid event id for source=eventgrid; else uuid4",
        },
        "payload": {
            "oneOf": [
                {"$ref": "#/$defs/UserMsg"},
                {"$ref": "#/$defs/BizEvent"},
                {"$ref": "#/$defs/Agenda"},
            ]
        },
        "options": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "stream": {"type": "boolean", "default": True},
                "max_rounds": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5,
                    "default": 3,
                },
            },
        },
        "trace": {"type": "string", "description": "W3C traceparent"},
    },
    "$defs": {
        "UserMsg": {
            "type": "object",
            "required": ["kind", "text", "actor"],
            "properties": {
                "kind": {"const": "user_message"},
                "text": {"type": "string"},
                "actor": {
                    "type": "string",
                    "description": "CIAM user id, audit only; NOT a trust boundary",
                },
                "actor_claim": {
                    "type": "string",
                    "description": (
                        "F-signed JWS {uid,roles,exp}; the actual authorization "
                        "input for grant_role/revoke_role (05)"
                    ),
                },
            },
        },
        "BizEvent": {
            "type": "object",
            "required": ["kind", "event_type", "data"],
            "properties": {
                "kind": {"const": "business_event"},
                "event_type": {"type": "string"},
                "data": {"type": "object"},
            },
        },
        "Agenda": {
            "type": "object",
            "required": ["kind", "text"],
            "properties": {
                "kind": {"const": "agenda"},
                "text": {"type": "string"},
            },
        },
    },
}

#: Evt — outbound stream frame (14). The ``type`` enum is CLOSED for v1.
EVT_SCHEMA: dict[str, Any] = {
    "$id": EVT_SCHEMA_ID,
    "type": "object",
    "additionalProperties": False,
    "required": ["schema", "turn_id", "seq", "type", "actor"],
    "properties": {
        "schema": {"const": EVT_SCHEMA_ID},
        "turn_id": {"type": "string"},
        "seq": {
            "type": "integer",
            "minimum": 0,
            "description": "strictly increasing within a turn",
        },
        "type": {
            "enum": [
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
            ]
        },
        "actor": {
            "type": "string",
            "description": "'founder' | 'system' | 'user' | a role id from the roster",
        },
        "data": {"type": "object"},
    },
}

#: Resonance judgment (16). Rationale is produced BEFORE the score.
RESONANCE_SCHEMA: dict[str, Any] = {
    "$id": RESONANCE_SCHEMA_ID,
    "type": "object",
    "additionalProperties": False,
    "required": ["role", "rationale", "score", "confidence", "domain_relevance"],
    "properties": {
        "role": {"type": "string"},
        "rationale": {
            "type": "string",
            "description": (
                "MUST be produced BEFORE the score; the reasoning is the primary "
                "artifact, the score is its summary"
            ),
        },
        "score": {"type": "number", "minimum": 0, "maximum": 1},
        "confidence": {"enum": ["low", "medium", "high"]},
        "domain_relevance": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "how much this proposal falls within this CXO's domain at all",
        },
    },
}

#: Digest (14) — persisted as turn rows; unit of audit, hydration context,
#: timeline and chargeback.
DIGEST_SCHEMA: dict[str, Any] = {
    "$id": DIGEST_SCHEMA_ID,
    "type": "object",
    "additionalProperties": False,
    "required": [
        "decision",
        "rationale",
        "owners",
        "follow_ups",
        "dissent",
        "resonance",
        "purpose_hash",
        "prompt_hash",
        "model_versions",
        "tokens",
        "duration_s",
    ],
    "properties": {
        "decision": {"type": "string"},
        "rationale": {"type": "string"},
        "owners": {"type": "array", "items": {"type": "string"}},
        "follow_ups": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["role", "action", "due"],
                "properties": {
                    "role": {"type": "string"},
                    "action": {"type": "string"},
                    "due": {"type": "string", "format": "date"},
                },
            },
        },
        "dissent": {
            "type": "array",
            "description": (
                "every unresolved oppose/amend POSITION at close; empty array "
                "means genuine unanimity, never omission (06)"
            ),
            "items": {
                "type": "object",
                "required": ["role", "position", "objection"],
                "properties": {
                    "role": {"type": "string"},
                    "position": {"enum": ["oppose", "amend"]},
                    "objection": {"type": "string"},
                },
            },
        },
        "resonance": {
            "type": "array",
            "description": (
                "every participating role's resonance judgment (16). Present even "
                "when unanimous — the evidence the decision was reasoned over"
            ),
            "items": {"$ref": RESONANCE_SCHEMA_ID},
        },
        "overridden_vetoes": {
            "type": "array",
            "description": (
                "domain vetoes (16) the Founder chose to override, each with the "
                "chair's recorded rationale; empty array is the normal case, "
                "omission is never permitted"
            ),
            "items": {
                "type": "object",
                "required": ["role", "override_rationale"],
                "properties": {
                    "role": {"type": "string"},
                    "override_rationale": {"type": "string"},
                },
            },
        },
        "purpose_hash": {
            "type": "string",
            "description": (
                "sha256 of company purpose + derived role purposes in force at "
                "close (16); a score is uninterpretable without it"
            ),
        },
        "prompt_hash": {"type": "string", "description": "sha256 of the prompt set used"},
        "model_versions": {
            "type": "object",
            "description": (
                "role id -> model deployment version that produced that role's "
                "contribution and score (16)"
            ),
            "additionalProperties": {"type": "string"},
        },
        "tokens": {"type": "integer"},
        "duration_s": {"type": "number"},
    },
}

#: Per-company MCP connector inventory entry (15).
CONNECTOR_SCHEMA: dict[str, Any] = {
    "$id": CONNECTOR_SCHEMA_ID,
    "type": "object",
    "additionalProperties": False,
    "required": ["connector_id", "kind", "mcp_url", "roles", "access"],
    "properties": {
        "connector_id": {"type": "string"},
        "kind": {
            "type": "string",
            "description": "free-form label, e.g. accounting|crm|code|analytics|ticketing|hris",
        },
        "mcp_url": {"type": "string", "format": "uri"},
        "roles": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "roster role ids permitted to use this connector; Founder is "
                "implicitly included for read"
            ),
        },
        "access": {"enum": ["read", "read_write"], "default": "read"},
        "enabled": {"type": "boolean", "default": True},
    },
}

ALL_SCHEMAS: dict[str, dict[str, Any]] = {
    ENVELOPE_SCHEMA_ID: ENVELOPE_SCHEMA,
    EVT_SCHEMA_ID: EVT_SCHEMA,
    DIGEST_SCHEMA_ID: DIGEST_SCHEMA,
    RESONANCE_SCHEMA_ID: RESONANCE_SCHEMA,
    CONNECTOR_SCHEMA_ID: CONNECTOR_SCHEMA,
}

_REGISTRY = Registry().with_resources(
    (schema_id, Resource.from_contents(schema, default_specification=DRAFT202012))
    for schema_id, schema in ALL_SCHEMAS.items()
)


class SchemaError(ValueError):
    """A payload did not satisfy its declared wire schema."""

    def __init__(self, schema_id: str, message: str) -> None:
        super().__init__(f"{schema_id}: {message}")
        self.schema_id = schema_id


def _validator(schema_id: str) -> Draft202012Validator:
    return Draft202012Validator(ALL_SCHEMAS[schema_id], registry=_REGISTRY)


def validate(schema_id: str, instance: Any) -> None:
    """Raise :class:`SchemaError` if ``instance`` violates ``schema_id``."""
    errors = sorted(_validator(schema_id).iter_errors(instance), key=lambda e: list(e.path))
    if errors:
        raise SchemaError(schema_id, errors[0].message)


def validate_envelope(instance: Any) -> None:
    validate(ENVELOPE_SCHEMA_ID, instance)


def validate_evt(instance: Any) -> None:
    validate(EVT_SCHEMA_ID, instance)


def validate_digest(instance: Any) -> None:
    validate(DIGEST_SCHEMA_ID, instance)


def validate_resonance(instance: Any) -> None:
    validate(RESONANCE_SCHEMA_ID, instance)


def validate_connector(instance: Any) -> None:
    validate(CONNECTOR_SCHEMA_ID, instance)
