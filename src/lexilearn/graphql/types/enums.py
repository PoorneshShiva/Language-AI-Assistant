import strawberry
import enum

@strawberry.enum
class Level(enum.Enum):
    BEGINNER = "beginner"
    ADVANCED = "advanced"

@strawberry.enum
class ItemType(enum.Enum):
    VERB = "verb"
    NOUN = "noun"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    CONJUNCTION = "conjunction"

@strawberry.enum
class LearnStatus(enum.Enum):
    NEW = "new"
    QUEUED = "queued"
    LEARNING = "learning"
    COMPLETED = "completed"
    IGNORED = "ignored"

@strawberry.enum
class Confidence(enum.Enum):
    AGAIN = "Again"
    HARD = "Hard"
    GOOD = "Good"
    EASY = "Easy"

@strawberry.enum
class LearnStyle(enum.Enum):
    READING = "reading"
    VISUAL = "visual"
    MIXED = "mixed"
