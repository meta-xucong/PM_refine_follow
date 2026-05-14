from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CandidateReview:
    account_address: str
    agent_verdict: str
    confidence: float
    copy_style: str
    human_review_priority: int
    main_reason: str
    risk_summary: str
    recommended_followup: str
    positive_evidence: list[str] = field(default_factory=list)
    negative_evidence: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    safety_overrides: list[str] = field(default_factory=list)
    needs_human_confirmation: bool = False
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class FeedbackEvent:
    account_address: str
    feedback_type: str
    source: str
    note: str | None = None
    source_ref: str | None = None
    created_at: str | None = None


@dataclass(slots=True)
class DailyPlan:
    date: str
    summary: str
    scan_plan: list[dict[str, Any]]
    recheck_accounts: list[dict[str, Any]]
    temporary_thresholds: dict[str, Any]
    requires_human_approval: bool
    risks: list[str]
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OutcomeReview:
    account_address: str
    horizon_days: int
    outcome_verdict: str
    confidence: float
    summary: str
    what_changed: list[str]
    false_positive_reason: str | None
    lessons: list[str]
    raw: dict[str, Any] = field(default_factory=dict)

