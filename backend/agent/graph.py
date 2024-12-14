from enum import StrEnum

from typing_extensions import TypedDict


class GraphStep(TypedDict):
    step_name: str


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        prompt: The prompt that was used to generate the response.
        generation: LLM generation
        resources: A list of resources that were used to generate the response.
        steps: A list of steps that were taken to generate the response.
    """
    prompt: str
    generation: str
    resources: list
    steps: list[str]
    perform_web_search: bool
    chat_session_id: int
    transcript: str


class Steps(StrEnum):
    VECTOR_STORE_RETRIEVAL: str = "vector_store_retrieval"
    VECTOR_STORE_EVALUATION: str = "vector_store_evaluation"
    PAPER_SEARCH_RETRIEVAL: str = "paper_search_retrieval"
    PAPER_SEARCH_EVALUATION: str = "paper_search_evaluation"
    WEB_SEARCH_RETRIEVAL: str = "web_search_retrieval"
    LLM_GENERATION: str = "llm_generation"
