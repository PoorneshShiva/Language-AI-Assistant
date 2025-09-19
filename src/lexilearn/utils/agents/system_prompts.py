"""Module for generating system prompts for language model interactions.

This module defines the SysPrompts class, which is responsible for creating
tailored system messages and associated output parsers for various NLP tasks
related to German grammar, such as part-of-speech tagging, translation, and
fetching detailed grammatical information for different word types.
"""
from typing import Optional, Tuple, Literal # Consolidate typing imports

from pydantic._internal._model_construction import ModelMetaclass
from langchain.output_parsers import PydanticOutputParser
from langchain_core.messages import SystemMessage
from langchain.output_parsers import YamlOutputParser 
from langchain_core.output_parsers import JsonOutputParser


class SysPrompts:
    """Manages the generation of system prompts for various NLP tasks related to German grammar.

    This class centralizes the logic for creating tailored system messages and 
    associated output parsers (if a Pydantic format is provided) for tasks such as
    part-of-speech tagging, translation, and fetching grammatical details for
    different word types (verbs, adjectives, nouns, etc.).
    """

    def __init__(self):
        """Initializes the SysPrompts class. 
        
        Currently, no specific initialization is performed within this method.
        """
        pass

    def get_pos_query(self,
                     pydantic_format: Optional[ModelMetaclass] = None
                     ) -> Tuple[Optional[PydanticOutputParser], SystemMessage]:
        """Generates a system prompt and an optional parser for part-of-speech (POS) tagging.

        The prompt instructs an LLM to extract parts of speech from a given query,
        adhering to specific requirements like not inferring words and returning JSON.

        Args:
            pydantic_format: An optional Pydantic model class (ModelMetaclass) that defines 
                             the desired output structure. If provided, a PydanticOutputParser
                             is created and its format instructions are appended to the prompt.

        Returns:
            A tuple containing:
                - An instance of PydanticOutputParser if `pydantic_format` was provided, else None.
                - A SystemMessage object containing the configured prompt for POS tagging.
        """
        pos_query_text = """You are a precise and reliable linguistic parser.
        
        Your task is to extract specific parts of speech from a given query (1 or 2 sentences)
        . Only return words **explicitly present** in the input text, and do not infer or hallucinate any words.
        
        **Requirements:**
        - Do not include any word that is not in the input.
        - If a category is not found, return an empty list.
        - Do not return explanations or extra text—only the structured data in JSON format.
        - Treat proper nouns as nouns.
        - Use lowercase for all words in the output lists.
        
        """
        pos_parser: Optional[PydanticOutputParser] = None
        if pydantic_format:
            pos_parser = PydanticOutputParser(pydantic_object=pydantic_format)
            pos_query_format_instructions = pos_parser.get_format_instructions()
            pos_query_text += f"\nInstructions:\n{pos_query_format_instructions}"
        
        pos_system_message = SystemMessage(content=pos_query_text)
        return (pos_parser, pos_system_message)

    def get_translation_query(self,
                              src_lang: str = Literal["German"],
                              dest_lang: str = Literal["English"],
                              pydantic_format: Optional[ModelMetaclass] = None
                              ) -> Tuple[Optional[PydanticOutputParser], SystemMessage]:
        """Generates a system prompt and an optional parser for translation.

        The prompt instructs an LLM to translate text from a source language to a
        destination language, focusing on accuracy and naturalness.

        Args:
            src_lang: The source language for translation (default: "German").
            dest_lang: The destination language for translation (default: "English").
            pydantic_format: An optional Pydantic model class for the output structure.

        Returns:
            A tuple containing:
                - A PydanticOutputParser if `pydantic_format` was provided, else None.
                - A SystemMessage for the translation task.
        """
        translation_query_text = f"""You are a precise and professional {src_lang}-to-{dest_lang} translator.
        
        Your task is to translate a given sentence or short paragraph from {src_lang} to natural, fluent {dest_lang}. The output should:
        
        - Preserve the original meaning exactly.
        - Avoid adding or removing any information.
        - Use correct {dest_lang} grammar and idiomatic expressions where appropriate.
        - Be limited to only what was present in the {src_lang} input—do not explain or interpret.
        """
        translation_parser: Optional[PydanticOutputParser] = None # Explicit type hint
        if pydantic_format:
            translation_parser = PydanticOutputParser(pydantic_object=pydantic_format)
            translation_query_format_instructions = translation_parser.get_format_instructions()
            translation_query_text += f"\nInstructions:\n{translation_query_format_instructions}" # Added newline
            
        translation_system_message = SystemMessage(content=translation_query_text)
        return (translation_parser, translation_system_message)

    def get_verb_conjugations_query(self,
                              pydantic_format: Optional[ModelMetaclass] = None
                              ) -> Tuple[Optional[PydanticOutputParser], SystemMessage]:
        """Generates a system prompt and parser for German verb conjugation details.

        The prompt asks for a structured morphological breakdown of a German verb,
        including tenses and forms, with specific formatting instructions.

        Args:
            pydantic_format: Optional Pydantic model for the output structure.

        Returns:
            A tuple (PydanticOutputParser or None, SystemMessage).
        """
        verb_conj_query_text = f"""You are a professional German language grammar assistant.
        For the given German verb, provide a structured morphological breakdown covering
        commonly used tenses and forms. Your response should be clear, concise, and learner-friendly.

        Instructions:
        - Do not provide any explanation — just the required words.
        - Provide the informtaion in german
        - Do not hallucinate or invent forms.
        - Just Give True or False for Regular and Seperable Verb 
        - Do not include markdown formatting or any extra text — return only valid JSON.
        - Return booleans as true/false (not in lists).
        - The infinitive must be a single string, not a list.
        - Set "is_regular" to False if the verb has a vowel change in the stem between 
          infinitive and any of its conjugated forms (especially simple past or present).

        - Set "is_separable" to True if the verb begins with a separable prefix,
          such as: ab-, an-, auf-, aus-, bei-, ein-, mit-, nach-, vor-, weg-, zu-,
          and forms like aufstehen become steht ... auf in use.
        
        Give the following informations:
        
        1. Provide th Infinitive of the verb in German, Just one in str
        2. Provide the singular present tense could be multiple in German
        3. Provide Do not include markdown formatting or any extra text — return only valid JSON.the simple past (Präteritum) could be multiple in German
        4. Give the Present Perfect (Perfekt) could be multiple in German
        5. Give the english translate for the given verb
        6. Is it a regular verb answer it in bool
        7. Is it a seperable verb answer it in bool
        
        Example:
        verb: spiele
        1. spielen
        2. [spielt]
        3. [spielte]
        4. [hat gespielt]
        5. [play]
        6. True
        7. False
        
        """

        verb_parser: Optional[PydanticOutputParser] = None # Explicit type hint
        if pydantic_format:
            verb_parser = PydanticOutputParser(pydantic_object=pydantic_format)
            verb_query_format_instructions = verb_parser.get_format_instructions()
            verb_conj_query_text += f"\nInstructions:\n{verb_query_format_instructions}" # Added newline
            
        verb_conj_system_message = SystemMessage(content=verb_conj_query_text)
        print(verb_conj_system_message)
        return (verb_parser, verb_conj_system_message)

    def get_adjectives_query(self,
                       pydantic_format: Optional[ModelMetaclass] = None
                       ) -> Tuple[Optional[PydanticOutputParser], SystemMessage]:
        """Generates a system prompt and parser for German adjective details.

        The prompt asks for a structured breakdown of an adjective, including
        comparative and superlative forms, with specific JSON formatting.

        Args:
            pydantic_format: Optional Pydantic model for the output structure.

        Returns:
            A tuple (PydanticOutputParser or None, SystemMessage).
        """
        adj_query_text = """
        You are a professional German language grammar assistant.
        For the given German adjective, provide a structured morphological breakdown that includes its comparative and superlative forms.
        
        Instructions:
        - Do not provide any explanation — just the required words.
        - Provide the information in German.
        - Do not hallucinate or invent forms.
        - Only include adjectives that are regular and comparable.
        - Do not include markdown formatting or any extra text — return only valid JSON.
        - Return booleans as true/false (not in lists).
        - The positive, comparative, and superlative forms must be single strings (not in lists).
        - The English translation must be a single string.
        
        Provide the following information:
        
        1. The positive form (base form) of the adjective as a string
        2. The comparative form as a string
        3. The superlative form as a string (e.g. "am schönsten / der/die/das schönste")
        4. The English translation as a string
        5. Is it a regular adjective (true/false)
        6. Is it comparable (true/false)
        
        Example:
        
        Input: schön
        
        Output:
        {
          "adjective": "schön",
          "comparative": "schöner",
          "superlative": "am schönsten / der/die/das schönste",
          "english_translation": "beautiful",
          "is_regular": true,
          "is_comparable": true
        }
        """
        adj_parser: Optional[PydanticOutputParser] = None # Explicit type hint
        if pydantic_format:
            adj_parser = PydanticOutputParser(pydantic_object=pydantic_format)
            adj_query_format_instructions = adj_parser.get_format_instructions()
            adj_query_text += f"\nInstructions:\n{adj_query_format_instructions}" # Added newline
            
        adj_system_message = SystemMessage(content=adj_query_text)
        return (adj_parser, adj_system_message)

    def get_noun_query(self,
                       pydantic_format: Optional[ModelMetaclass] = None
                       ) -> Tuple[Optional[PydanticOutputParser], SystemMessage]:
        """Generates a system prompt and parser for German noun details.

        The prompt requests a structured JSON object for a noun, including singular,
        plural, gender, case forms, and translation, with strict formatting.

        Args:
            pydantic_format: Optional Pydantic model for the output structure.

        Returns:
            A tuple (PydanticOutputParser or None, SystemMessage).
        """
        noun_query_text = """You are a professional German language grammar assistant.

        For the given German noun, return a **structured JSON object** describing its grammatical features.
        
        Instructions:
        - Do not include markdown formatting or any extra text — return only **valid JSON**.
        - Do not include numbered keys like "1. Singular" or "2. Plural" — only use the exact field names provided.
        - Booleans must be returned as `true` or `false`, not strings.
        - Case forms must be a nested JSON object with keys: "nominative", "accusative", "dative", "genitive"
        - The output must be a valid JSON object directly compatible with a Pydantic model.

        Provide the noun details in the following format:
        
        Noun: Haus
        1. Singular: Haus
        2. Plural: Häuser
        3. Gender: das
        4. Case forms: {"nominative": "Haus", "accusative": "Haus", "dative": "Haus", "genitive": "Hauses"}
        5. English: house
        6. Is irregular: True
        """
        noun_parser: Optional[PydanticOutputParser] = None # Explicit type hint
        noun_system_message = None
        if pydantic_format:
            noun_parser = PydanticOutputParser(pydantic_object=pydantic_format)
            noun_query_format_instructions = noun_parser.get_format_instructions()
            noun_query_text += f"\nInstructions:\n{noun_query_format_instructions}" # Added newline
            
            noun_system_message = SystemMessage(content=noun_query_text)
            return (noun_parser, noun_system_message)
        
        noun_system_message = SystemMessage(content=noun_query_text)
        return (None, noun_system_message)

    def get_adverb_query(self,
                       pydantic_format: Optional[ModelMetaclass] = None
                       ) -> Tuple[Optional[PydanticOutputParser], SystemMessage]:
        """Generates a system prompt and parser for German adverb details.

        The prompt requests a structured JSON object for an adverb, including its type
        (temporal, local, etc.) and comparability, with strict formatting.

        Args:
            pydantic_format: Optional Pydantic model for the output structure.

        Returns:
            A tuple (PydanticOutputParser or None, SystemMessage).
        """
        adverb_query_text = """You are a professional German language grammar assistant.

        For the given German adverb, return a structured JSON object describing its grammatical features.
        
        Instructions:
        - Do not include markdown formatting or any extra text — return only valid JSON.
        - Only use the exact field names provided below — no additional or numbered keys.
        - Booleans must be returned as true or false, not strings.
        - The value of adverb_type must be one of: "temporal", "local", "modal", "causal", "manner", or "degree". If the type is unclear, set it to null.
        
        The output must be a valid JSON object directly compatible with the following structure:
            
            {
              "adverb": "string",                        // The German adverb
              "english_translation": "string",           // English translation of the adverb
              "adverb_type": "temporal" | "local" | "modal" | "causal" | "manner" | "degree" | null,
              "is_comparable": true | false              // Whether the adverb is comparable
            }
             
        """
        adverb_parser: Optional[PydanticOutputParser] = None # Explicit type hint
        adverb_system_message = None
        if pydantic_format:
            adverb_parser = PydanticOutputParser(pydantic_object=pydantic_format)
            adverb_query_format_instructions = adverb_parser.get_format_instructions()
            adverb_query_text += f"\nInstructions:\n{adverb_query_format_instructions}" # Added newline
            
            adverb_system_message = SystemMessage(content=adverb_query_text)
            return (adverb_parser, adverb_system_message)
        
        adverb_system_message = SystemMessage(content=adverb_query_text)
        return (None, adverb_system_message)
        
    def get_preposition_query(self,
                       pydantic_format: Optional[ModelMetaclass] = None
                       ) -> Tuple[Optional[PydanticOutputParser], SystemMessage]:
        """Generates a system prompt and parser for German preposition details.

        The prompt requests a structured JSON for a preposition, including case governed
        and type, with strict formatting rules.

        Args:
            pydantic_format: Optional Pydantic model for the output structure.

        Returns:
            A tuple (PydanticOutputParser or None, SystemMessage).
        """
        preposition_query_text = """
        You are a professional German language grammar assistant.

        For the given German preposition, return a structured JSON object describing its grammatical features.
        
        Instructions:
         - Do not include markdown formatting or any extra text — return only valid JSON.
         - Only use the exact field names provided — do not add numbering or additional labels.
         - Booleans must be returned as true or false, not strings.
         - The field case_governed must be one of: "accusative", "dative", "genitive", or "mixed" depending on the preposition's use.
         - The output must be a valid JSON object directly compatible with a Pydantic model.
         - Return the case_governed as accusative, dative, genitive or mixed
         - Return the preposition_type as local, temporal, modal or causal

        """
        preposition_parser: Optional[PydanticOutputParser] = None # Explicit type hint
        preposition_system_message = None
        if pydantic_format:
            preposition_parser = PydanticOutputParser(pydantic_object=pydantic_format)
            preposition_query_format_instructions = preposition_parser.get_format_instructions()
            preposition_query_text += f"\nInstructions:\n{preposition_query_format_instructions}" # Added newline
            
            preposition_system_message = SystemMessage(content=preposition_query_text)
            return (preposition_parser, preposition_system_message)
        
        preposition_system_message = SystemMessage(content=preposition_query_text)
        return (None, preposition_system_message)
        
    def get_conjunction_query(self,
                       pydantic_format: Optional[ModelMetaclass] = None
                       ) -> Tuple[Optional[PydanticOutputParser], SystemMessage]:
        """Generates a system prompt and parser for German conjunction details.

        The prompt requests a structured JSON for a conjunction, including its type
        (coordinating, subordinating, correlative), with strict formatting.

        Args:
            pydantic_format: Optional Pydantic model for the output structure.

        Returns:
            A tuple (PydanticOutputParser or None, SystemMessage).
        """
        conjunction_query_text = """You are a professional German language grammar assistant.

        For the given German conjunction, return a structured JSON object describing its grammatical features.
        
        Instructions:
        - Do not include markdown formatting or any extra text — return only valid JSON.
        - Only use the exact field names provided — do not add numbering or additional labels.
        - The field conjunction_type must be one of: "coordinating", "subordinating", or "correlative".
        - The output must be a valid JSON object directly compatible with a Pydantic model.
        - the value of conjunction_type must be correlative, coordinating or subordinating
    
        """
        conjunction_parser: Optional[PydanticOutputParser] = None # Explicit type hint
        conjunction_system_message = None
        if pydantic_format:
            conjunction_parser = PydanticOutputParser(pydantic_object=pydantic_format)
            conjunction_query_format_instructions = conjunction_parser.get_format_instructions()
            conjunction_query_text += f"\nInstructions:\n{conjunction_query_format_instructions}" # Added newline
            
            conjunction_system_message = SystemMessage(content=conjunction_query_text)
            return (conjunction_parser, conjunction_system_message)
        
        conjunction_system_message = SystemMessage(content=conjunction_query_text)
        return (None, conjunction_system_message)
