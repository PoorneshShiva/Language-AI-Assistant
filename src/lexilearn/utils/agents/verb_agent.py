from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from lexilearn.utils.agents.model import llm_tools_user
from lexilearn.rest.models import VerbTrainingData, VerbConjugations

def generate_verb_training_data(infinitive: str, level: str) -> VerbTrainingData:
    parser = JsonOutputParser(pydantic_object=VerbTrainingData)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful German language tutor. Generate a German sentence using the given verb, its English translation, and the verb's full conjugations in present tense, simple past, and past participle. Also, provide if the verb is separable or regular, and any relevant notes. The output should be a JSON object matching the VerbTrainingData schema."),
        ("human", "Generate training data for the verb: {infinitive} at {level} level."),
    ])

    chain = prompt | llm_tools_user | parser

    response = chain.invoke({"infinitive": infinitive, "level": level})
    return response
