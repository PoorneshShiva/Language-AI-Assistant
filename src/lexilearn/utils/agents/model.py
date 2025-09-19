"""
Module for the configuration
"""
from typing import Literal  # , Optional
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from langchain_google_genai import ChatGoogleGenerativeAI

from lexilearn.config import config

load_dotenv()


class AgenticModels:
    """ Managing all models on Agentic system for all the use
    cases
    """

    def __init__(self,
                 model: Literal["ollama",
                                "hugging-face",
                                "google"] = "ollama",
                 model_name: Literal["llama3.1",
                                     "gemma3",
                                     "gemini-1.5-flash",
                                     "gemini-1.5-pro",
                                     "gemini-pro"] = "llama3.1",
                 model_id: Literal[
                         "HuggingFaceH4/zephyr-7b-beta"
                         ] = "HuggingFaceH4/zephyr-7b-beta",
                 ):
        """ Initiator of tools on agentic system """
        self.config = config
        self.logging = self.config.logging
        self.model_provider = model
        self.model_name = model_name
        self.model_id = model_id

        if self.model_provider == "google" and not self.model_name.startswith("gemini"):
            self.logging.warning(f"Model provider is Google, but model_name '{self.model_name}' doesn't look like a Gemini model. Defaulting to 'gemini-1.5-flash'.")
            self.model_name = "gemini-1.5-flash"

        if self.model_provider in ["ollama", "google"]:
            self.llm = self.get_by_name()
        else:
            self.llm = self.get_by_id()

    def get_by_name(
             self,
            #  model_name: Literal["llama3.1"] = "llama3.1"
             ):
        # ) -> Optional[langchain_ollama.chat_models]:
        """ Get the langhain model based on the
        model_name given

        Args:
            model_name: model name for the langchain

        Returns:
            langchain_ollama.chat_models
            None

        Examples:
            >>> get_model_by_name(model_name="llama.3.1")
        """
        llm_instance = None
        try:
            if self.model_provider == "ollama":
                llm_instance = ChatOllama(
                    model=self.model_name,
                    num_gpu=0,
                    num_thread=20,
                    temperature=0)
            elif self.model_provider == "google":
                llm_instance = ChatGoogleGenerativeAI(
                        model=self.model_name,
                        temperature=0,
                        max_retries=2)
        except Exception as oops:  # pylint: disable=W broad-expect
            msg = f"Failed to load model '{self.model_name}' for provider '{self.model_provider}': {oops}"
            self.logging.error(msg)

        if llm_instance is None and self.model_provider in ["ollama", "google"]:
             self.logging.error(f"LLM instance could not be created for provider '{self.model_provider}' with model name '{self.model_name}'. self.llm will be None.")

        return llm_instance

    def get_by_id(
                 self,
                 # model_id: Literal[
                 #         "HuggingFaceH4/zephyr-7b-beta"
                 #        ] = "HuggingFaceH4/zephyr-7b-beta",
                 task: Literal["text-generation"] = "text-generation"
                 ):
        # ) -> Optional[langchain_ollama.chat_models]:
        """ Get the langhain model based on the
        model_name given

        Args:
            model_name: model name for the langchain

        Returns:
            langchain_ollama.chat_models
            None

        Examples:
            >>> get_model_by_id(
                model_id="HuggingFaceH4/zephyr-7b-beta",
                task="text-generation")
        """
        llm_instance = None
        try:
            if self.model_provider == "hugging-face":
                llm_instance = HuggingFacePipeline.from_model_id(
                    model_id=self.model_id,
                    task=task,
                    pipeline_kwargs={
                        "max_new_tokens": 512,
                        "do_sample": False,
                        "repetition_penalty": 1.03,
                        })
                llm_instance = ChatHuggingFace(llm=llm_instance)
        except Exception as oops:  # pylint: disable=W broad-expect
            msg = f"Failed to load model by id '{self.model_id}' for provider '{self.model_provider}': {oops}"
            self.logging.error(msg)

        if llm_instance is None and self.model_provider == "hugging-face":
            self.logging.error(f"LLM instance could not be created for provider '{self.model_provider}' with model id '{self.model_id}'. self.llm will be None.")
            
        return llm_instance

llm_tools_user = AgenticModels(model="ollama", model_name="llama3.1").llm
llm_tools_user_sonnet = AgenticModels(model="ollama", model_name="llama3.1").llm