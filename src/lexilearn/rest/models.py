from pydantic import BaseModel, Field
from typing import Any, List, Literal, TypeVar, Generic, Optional, Dict

T = TypeVar('T')

class SuccessResponse(BaseModel, Generic[T]):
    ok: bool = Field(default=True, frozen=True)
    data: T

class DetectWordsRequest(BaseModel):
    sentence: str
    level: Literal["beginner", "advanced"]
    exclude_keys: List[str] = []

class DetectedWord(BaseModel):
    type: Literal["verb", "noun", "adjective"]
    id: str

class DetectWordsData(BaseModel):
    detected: List[DetectedWord]

class RandomWordsRequest(BaseModel):
    level: Literal["beginner", "advanced"]
    exclude_keys: List[str] = []
    preferred_types: List[Literal["verb", "noun"]] = []

class RandomWordItem(BaseModel):
    type: Literal["verb", "noun"]
    id: str

class RandomWordData(BaseModel):
    item: RandomWordItem

class WordItem(BaseModel):
    type: Literal["verb", "noun"]
    id: str

class WordsData(BaseModel):
    items: List[WordItem]
    next_cursor: Optional[str] = None

class VerbDetails(BaseModel):
    infinitive: str
    present: Dict[str, str]
    present_perfect: List[str]
    singular_present_tense: List[str]
    simple_past: List[str]
    is_separable: bool
    is_regular: bool
    english_alternative: List[str]
    notes: List[str] = []

class CaseForms(BaseModel):
    nominative: str
    accusative: str
    dative: str
    genitive: str

class NounDetails(BaseModel):
    noun: str
    plural: str
    gender: Literal["der", "die", "das"]
    case_forms: CaseForms
    english_translation: str
    is_irregular: bool

# New models for LLM output
class VerbConjugations(BaseModel):
    present: Dict[str, str]
    simple_past: Dict[str, str]
    past_participle: str
    perfekt_aux: str

class VerbTrainingData(BaseModel):
    infinitive: str
    german_sentence: str
    english_translation: str
    conjugations: VerbConjugations
    is_separable: bool
    is_regular: bool
    notes: List[str] = []

class Prompt(BaseModel):
    id: str
    level: Literal["beginner", "advanced"]
    en: str
    de: str
    tags: List[str]

class PromptsData(BaseModel):
    prompts: List[Prompt]

class EvaluationItem(BaseModel):
    type: Literal["verb", "noun"]
    id: str

class EvaluationRequest(BaseModel):
    item: EvaluationItem
    prompt_id: str
    expected: str
    answer: str
    level: Literal["beginner", "advanced"]

class EvaluationIssue(BaseModel):
    type: str
    detail: str

class NormalizedEvaluation(BaseModel):
    answer: str
    expected: str

class EvaluationData(BaseModel):
    correct: bool
    why: str
    primary_fix: str
    issues: List[EvaluationIssue]
    normalized: NormalizedEvaluation

class PracticeQueueItem(BaseModel):
    type: Literal["verb", "noun"]
    id: str
    due_at: str
    stability: float
    interval_days: int
    lapses: int

class PracticeQueueData(BaseModel):
    queue: List[PracticeQueueItem]

class ConfidenceItem(BaseModel):
    type: Literal["verb", "noun"]
    id: str

class Telemetry(BaseModel):
    correct: bool

class ConfidenceRequest(BaseModel):
    item: ConfidenceItem
    confidence: Literal["Again", "Hard", "Good", "Easy"]
    level: Literal["beginner", "advanced"]
    telemetry: Telemetry

class Scheduled(BaseModel):
    due_at: str
    interval_days: int
    stability: float

class ConfidenceData(BaseModel):
    scheduled: Scheduled
    moved_to: str

class CompleteItem(BaseModel):
    type: Literal["verb", "noun"]
    id: str

class CompleteRequest(BaseModel):
    item: CompleteItem

class CompleteData(BaseModel):
    status: str

class ReviewAgainItem(BaseModel):
    type: Literal["verb", "noun"]
    id: str

class ReviewAgainRequest(BaseModel):
    item: ReviewAgainItem

class ReviewAgainData(BaseModel):
    status: str

class CompletedItem(BaseModel):
    type: Literal["verb", "noun"]
    id: str
    completed_at: str

class CompletedData(BaseModel):
    items: List[CompletedItem]

class IgnoreItem(BaseModel):
    type: Literal["verb", "noun"]
    id: str

class IgnoreRequest(BaseModel):
    item: IgnoreItem

class IgnoreData(BaseModel):
    status: str

class UnignoreItem(BaseModel):
    type: Literal["verb", "noun"]
    id: str

class UnignoreRequest(BaseModel):
    item: UnignoreItem

class UnignoreData(BaseModel):
    status: str

class Hint(BaseModel):
    label: str
    insert: str

class HintsData(BaseModel):
    hints: List[Hint]

class SettingsData(BaseModel):
    level: Literal["beginner", "advanced"]
    daily_goal: int
    style: str
    review_enabled: bool

class PatchSettingsRequest(BaseModel):
    level: Optional[Literal["beginner", "advanced"]] = None
    daily_goal: Optional[int] = None
    style: Optional[str] = None
    review_enabled: Optional[bool] = None

class TodayStats(BaseModel):
    learned: int
    practiced: int
    completed: int

class TotalStats(BaseModel):
    learned: int
    completed: int
    in_queue: int

class StatsData(BaseModel):
    today: TodayStats
    totals: TotalStats

class GrammarEntry(BaseModel):
    lemma: str
    label: str
    explanation: str


class SentenceAnalysisData(BaseModel):
    analysis_id: str
    sentence: str
    tokens: List[str]
    verbs: List[GrammarEntry]
    nouns: List[GrammarEntry]
    adjectives: List[GrammarEntry]
    notes: List[str]
    focus: List[str]
    created_at: str


class SentenceAnalyzeRequest(BaseModel):
    sentence: str
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    goals: List[str] = []


class AssignmentActivity(BaseModel):
    title: str
    summary: str
    instructions: str
    expected_output: str
    tips: List[str] = []
    iteration_prompt: Optional[str] = None


class AssignmentData(BaseModel):
    assignment_id: str
    sentence: str
    level: str
    goals: List[str]
    focus: Dict[str, List[str]]
    activities: List[AssignmentActivity]
    reflection: List[str] = []
    real_world_bridge: List[str] = []
    language_bank: List[Dict[str, str]] = []
    status: str
    iteration: int
    analysis_id: Optional[str] = None
    analysis_snapshot: Optional[Dict[str, Any]] = None
    created_at: str


class AssignmentCreateRequest(BaseModel):
    sentence: str
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    goals: List[str] = []
    analysis_id: Optional[str] = None


class AssignmentProgressRequest(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    iteration_feedback: Optional[str] = None


class ScenarioRequest(BaseModel):
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    theme: str
    recently_learned: List[str] = []


class ScenarioData(BaseModel):
    scenario_id: str
    level: str
    theme: str
    situation: str
    role_play: Dict[str, str]
    checklist: List[str]
    language_bank: List[Dict[str, str]]
    created_at: str
