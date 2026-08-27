"""``boardroom_core`` — wire contracts shared by the Function app F (03) and
the Foundry orchestration container O (02).

Nothing in this package performs I/O; it is pure contract code so both sides
of the wire can depend on it without inheriting each other's runtime.
"""

from boardroom_core.envelope import (
    DEFAULT_MAX_ROUNDS,
    HARD_MAX_ROUNDS,
    Envelope,
    Options,
    agenda,
    business_event,
    make_envelope,
    user_message,
)
from boardroom_core.evt import (
    CHAIR_ROLE,
    CXO_ROLES,
    EVT_TYPES,
    MVP_ROSTER,
    POSITIONS,
    TERMINAL_EVT_TYPES,
    Evt,
    EvtStream,
    is_domain_veto,
    is_recordable_dissent,
    outside_roster_competence,
)
from boardroom_core.schemas import (
    ALL_SCHEMAS,
    CONNECTOR_SCHEMA,
    DIGEST_SCHEMA,
    ENVELOPE_SCHEMA,
    EVT_SCHEMA,
    RESONANCE_SCHEMA,
    SchemaError,
    validate,
    validate_connector,
    validate_digest,
    validate_envelope,
    validate_evt,
    validate_resonance,
)

__all__ = [
    "ALL_SCHEMAS",
    "CHAIR_ROLE",
    "CONNECTOR_SCHEMA",
    "CXO_ROLES",
    "DEFAULT_MAX_ROUNDS",
    "DIGEST_SCHEMA",
    "ENVELOPE_SCHEMA",
    "EVT_SCHEMA",
    "EVT_TYPES",
    "Envelope",
    "Evt",
    "EvtStream",
    "HARD_MAX_ROUNDS",
    "MVP_ROSTER",
    "Options",
    "POSITIONS",
    "RESONANCE_SCHEMA",
    "SchemaError",
    "TERMINAL_EVT_TYPES",
    "agenda",
    "business_event",
    "is_domain_veto",
    "is_recordable_dissent",
    "make_envelope",
    "outside_roster_competence",
    "user_message",
    "validate",
    "validate_connector",
    "validate_digest",
    "validate_envelope",
    "validate_evt",
    "validate_resonance",
]
