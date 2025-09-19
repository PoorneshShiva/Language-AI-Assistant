from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional

from lexilearn.database import Database
from lexilearn.models.common import UserQuery
from lexilearn.rest.models import (
    SuccessResponse,
    SentenceAnalyzeRequest,
    SentenceAnalysisData,
    GrammarEntry,
    AssignmentCreateRequest,
    AssignmentData,
    AssignmentActivity,
    AssignmentProgressRequest,
    ScenarioRequest,
    ScenarioData,
)
from lexilearn.utils.agents.course_builder import CourseBuilder


router = APIRouter()


def _iso(value) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _make_entries(items: List[dict], label: str) -> List[GrammarEntry]:
    entries: List[GrammarEntry] = []
    for item in items or []:
        lemma = item.get("infinitive") or item.get("noun") or item.get("adjective") or item.get("lemma") or item.get("word")
        if not lemma:
            continue
        explanation_bits: List[str] = []
        if item.get("english_alternative"):
            explanation_bits.append(f"EN: {', '.join(item['english_alternative'])}")
        if item.get("notes"):
            notes = item["notes"] if isinstance(item["notes"], list) else [item["notes"]]
            explanation_bits.extend(notes)
        if item.get("case_forms"):
            cases = item["case_forms"]
            explanation_bits.append(
                ", ".join(f"{case}:{form}" for case, form in cases.items())
            )
        if item.get("present") and isinstance(item["present"], dict):
            explanation_bits.append(
                " / ".join(f"{k}:{v}" for k, v in item["present"].items())
            )
        entries.append(
            GrammarEntry(
                lemma=lemma,
                label=label,
                explanation="; ".join(explanation_bits) or ""
            )
        )
    return entries


@router.post("/analyze", response_model=SuccessResponse[SentenceAnalysisData])
async def analyze_sentence(payload: SentenceAnalyzeRequest, request: Request):
    db: Database = request.state.db
    agent_main = request.state.agent_main
    user_id = "test_user"

    agent = agent_main.build_german_graph()
    result = agent.invoke(UserQuery(query=payload.sentence))

    verbs = getattr(result, "verbs_info", []) or []
    nouns = getattr(result, "nouns_info", []) or []
    adjectives = getattr(result, "adjectives_info", []) or []

    tokens = payload.sentence.replace("\n", " ").split()
    notes: List[str] = []
    if verbs:
        notes.append("Überprüfe Tempus & Verbklassen in den Beispielen.")
    if nouns:
        notes.append("Achte auf Artikel und Fälle der Nomen.")
    if adjectives:
        notes.append("Vergleiche die Adjektivendungen und Steigerungsformen.")

    focus = payload.goals or []
    if verbs:
        focus.append("Verbkonjugation")
    if nouns:
        focus.append("Kasus der Nomen")
    if adjectives:
        focus.append("Adjektivendungen")

    analysis_payload = {
        "verbs": verbs,
        "nouns": nouns,
        "adjectives": adjectives,
        "notes": notes,
    }

    analysis_id = db.save_sentence_analysis(
        user_id=user_id,
        sentence=payload.sentence,
        analysis=analysis_payload,
        focus=focus,
    )

    created_at = datetime.utcnow()
    data = SentenceAnalysisData(
        analysis_id=analysis_id,
        sentence=payload.sentence,
        tokens=tokens,
        verbs=_make_entries(verbs, "Verb"),
        nouns=_make_entries(nouns, "Nomen"),
        adjectives=_make_entries(adjectives, "Adjektiv"),
        notes=notes,
        focus=focus,
        created_at=_iso(created_at),
    )
    return SuccessResponse(data=data)


@router.get("/analyze/history", response_model=SuccessResponse[List[SentenceAnalysisData]])
async def list_sentence_history(request: Request, limit: int = 10):
    db: Database = request.state.db
    user_id = "test_user"
    summaries = db.list_sentence_analyses(user_id, limit=limit)
    items: List[SentenceAnalysisData] = []
    for summary in summaries:
        doc = db.get_sentence_analysis(summary["analysis_id"])
        if not doc:
            continue
        analysis = doc.get("analysis", {})
        items.append(
            SentenceAnalysisData(
                analysis_id=doc["analysis_id"],
                sentence=doc.get("sentence", ""),
                tokens=doc.get("sentence", "").split(),
                verbs=_make_entries(analysis.get("verbs", []), "Verb"),
                nouns=_make_entries(analysis.get("nouns", []), "Nomen"),
                adjectives=_make_entries(analysis.get("adjectives", []), "Adjektiv"),
                notes=analysis.get("notes", []),
                focus=doc.get("focus", []),
                created_at=_iso(doc.get("created_at")),
            )
        )
    return SuccessResponse(data=items)


@router.post("/assignments", response_model=SuccessResponse[AssignmentData])
async def create_assignment(payload: AssignmentCreateRequest, request: Request):
    db: Database = request.state.db
    user_id = "test_user"
    analysis_snapshot = None
    if payload.analysis_id:
        snapshot = db.get_sentence_analysis(payload.analysis_id)
        if not snapshot:
            raise HTTPException(status_code=404, detail="Analysis not found")
        analysis_snapshot = snapshot["analysis"]
    else:
        analysis_snapshot = {}

    builder = CourseBuilder()
    raw_assignment = builder.generate_assignment(
        sentence=payload.sentence,
        level=payload.level,
        goals=payload.goals,
        analysis=analysis_snapshot or {},
    )

    assignment_id = db.create_assignment(
        {
            "user_id": user_id,
            "sentence": payload.sentence,
            "level": payload.level,
            "goals": payload.goals,
            "focus": raw_assignment.get("focus", {}),
            "activities": raw_assignment.get("activities", []),
            "reflection": raw_assignment.get("reflection", []),
            "real_world_bridge": raw_assignment.get("real_world_bridge", []),
            "language_bank": raw_assignment.get("language_bank", []),
            "status": "active",
            "iteration": 1,
            "analysis_id": payload.analysis_id,
            "analysis_snapshot": analysis_snapshot,
        }
    )

    doc = db.get_assignment(assignment_id)
    if not doc:
        raise HTTPException(status_code=500, detail="Assignment could not be created")

    data = AssignmentData(
        assignment_id=doc["assignment_id"],
        sentence=doc["sentence"],
        level=doc["level"],
        goals=doc.get("goals", []),
        focus=doc.get("focus", {}),
        activities=[AssignmentActivity(**activity) for activity in doc.get("activities", [])],
        reflection=doc.get("reflection", []),
        real_world_bridge=doc.get("real_world_bridge", []),
        language_bank=doc.get("language_bank", []),
        status=doc.get("status", "active"),
        iteration=doc.get("iteration", 1),
        analysis_id=doc.get("analysis_id"),
        analysis_snapshot=doc.get("analysis_snapshot"),
        created_at=_iso(doc.get("created_at")),
    )
    return SuccessResponse(data=data)


@router.get("/assignments", response_model=SuccessResponse[List[AssignmentData]])
async def list_assignments(request: Request, status: Optional[str] = None):
    db: Database = request.state.db
    user_id = "test_user"
    docs = db.list_assignments(user_id, status=status)
    items: List[AssignmentData] = []
    for doc in docs:
        items.append(
            AssignmentData(
                assignment_id=doc["assignment_id"],
                sentence=doc["sentence"],
                level=doc["level"],
                goals=doc.get("goals", []),
                focus=doc.get("focus", {}),
                activities=[AssignmentActivity(**activity) for activity in doc.get("activities", [])],
                reflection=doc.get("reflection", []),
                real_world_bridge=doc.get("real_world_bridge", []),
                language_bank=doc.get("language_bank", []),
                status=doc.get("status", "active"),
                iteration=doc.get("iteration", 1),
                analysis_id=doc.get("analysis_id"),
                analysis_snapshot=doc.get("analysis_snapshot"),
                created_at=_iso(doc.get("created_at")),
            )
        )
    return SuccessResponse(data=items)


@router.patch("/assignments/{assignment_id}", response_model=SuccessResponse[AssignmentData])
async def update_assignment(assignment_id: str, payload: AssignmentProgressRequest, request: Request):
    db: Database = request.state.db
    assignment = db.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    updates = {}
    if payload.status:
        updates["status"] = payload.status
    if payload.iteration_feedback:
        db.append_assignment_history(
            assignment_id,
            {
                "kind": "feedback",
                "payload": payload.iteration_feedback,
            },
        )
    if payload.notes:
        db.append_assignment_history(
            assignment_id,
            {
                "kind": "note",
                "payload": payload.notes,
            },
        )

    if payload.iteration_feedback:
        builder = CourseBuilder()
        variant = builder.generate_assignment(
            sentence=assignment.get("sentence"),
            level=assignment.get("level"),
            goals=assignment.get("goals", []),
            analysis=assignment.get("analysis_snapshot") or {},
        )
        updates.update(
            {
                "activities": variant.get("activities", assignment.get("activities", [])),
                "focus": variant.get("focus", assignment.get("focus", {})),
                "reflection": variant.get("reflection", assignment.get("reflection", [])),
                "real_world_bridge": variant.get("real_world_bridge", assignment.get("real_world_bridge", [])),
                "language_bank": variant.get("language_bank", assignment.get("language_bank", [])),
                "iteration": assignment.get("iteration", 1) + 1,
            }
        )

    if updates:
        assignment = db.update_assignment(assignment_id, updates)
    else:
        assignment = db.get_assignment(assignment_id)

    data = AssignmentData(
        assignment_id=assignment["assignment_id"],
        sentence=assignment["sentence"],
        level=assignment["level"],
        goals=assignment.get("goals", []),
        focus=assignment.get("focus", {}),
        activities=[AssignmentActivity(**activity) for activity in assignment.get("activities", [])],
        reflection=assignment.get("reflection", []),
        real_world_bridge=assignment.get("real_world_bridge", []),
        language_bank=assignment.get("language_bank", []),
        status=assignment.get("status", "active"),
        iteration=assignment.get("iteration", 1),
        analysis_id=assignment.get("analysis_id"),
        analysis_snapshot=assignment.get("analysis_snapshot"),
        created_at=_iso(assignment.get("created_at")),
    )
    return SuccessResponse(data=data)


@router.post("/scenarios", response_model=SuccessResponse[ScenarioData])
async def create_scenario(payload: ScenarioRequest, request: Request):
    db: Database = request.state.db
    builder = CourseBuilder()
    raw = builder.generate_real_life_prompt(
        level=payload.level,
        theme=payload.theme,
        recently_learned=payload.recently_learned,
    )
    scenario_id = db.add_real_life_scenario(
        {
            "user_id": "test_user",
            "level": payload.level,
            "theme": raw.get("theme", payload.theme),
            "situation": raw.get("situation", ""),
            "role_play": raw.get("role_play", {}),
            "checklist": raw.get("checklist", []),
            "language_bank": raw.get("language_bank", []),
        }
    )
    doc = next((sc for sc in db.list_real_life_scenarios("test_user", limit=50) if sc["scenario_id"] == scenario_id), None)
    if not doc:
        raise HTTPException(status_code=500, detail="Scenario was not persisted")
    data = ScenarioData(
        scenario_id=doc["scenario_id"],
        level=doc.get("level", payload.level),
        theme=doc.get("theme", payload.theme),
        situation=doc.get("situation", ""),
        role_play=doc.get("role_play", {}),
        checklist=doc.get("checklist", []),
        language_bank=doc.get("language_bank", []),
        created_at=_iso(doc.get("created_at", datetime.utcnow())),
    )
    return SuccessResponse(data=data)


@router.get("/scenarios", response_model=SuccessResponse[List[ScenarioData]])
async def list_scenarios(request: Request, limit: int = 10):
    db: Database = request.state.db
    docs = db.list_real_life_scenarios("test_user", limit=limit)
    items = [
        ScenarioData(
            scenario_id=doc["scenario_id"],
            level=doc.get("level", "beginner"),
            theme=doc.get("theme", ""),
            situation=doc.get("situation", ""),
            role_play=doc.get("role_play", {}),
            checklist=doc.get("checklist", []),
            language_bank=doc.get("language_bank", []),
            created_at=_iso(doc.get("created_at")),
        )
        for doc in docs
    ]
    return SuccessResponse(data=items)
