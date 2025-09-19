from fastapi import APIRouter
from lexilearn.rest.words import router as words_router
from lexilearn.rest.practice import router as practice_router
from lexilearn.rest.user import router as user_router
from lexilearn.rest.misc import router as misc_router
from lexilearn.rest.learn import router as learn_router

router = APIRouter(prefix="/v1")

router.include_router(words_router, prefix="/words", tags=["words"])
router.include_router(practice_router, prefix="/practice", tags=["practice"])
router.include_router(user_router, tags=["user"])
router.include_router(misc_router, tags=["misc"])
router.include_router(learn_router, prefix="/learn", tags=["learn"])
