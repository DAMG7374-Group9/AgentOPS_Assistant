import logging

from langchain_community.retrievers import ArxivRetriever
from langchain_community.tools import TavilySearchResults
from langchain_core.language_models import BaseChatModel

from backend.agent.vector_store import Retriever
from backend.agent.generate_chain import create_generate_chain
from backend.agent.graph import Steps, GraphState
from backend.database.chat_sessions import create_chat_session
from backend.database.messages import create_message, MessageSenderEnum

logger = logging.getLogger(__name__)


class GraphNodes:
    def __init__(self, llm: BaseChatModel, retriever: Retriever, retrieval_grader, web_search_tool: TavilySearchResults,
                 paper_search_tool: ArxivRetriever | None):
        self.llm = llm
        self.retriever = retriever
        self.retrieval_grader = retrieval_grader
        self.web_search_tool = web_search_tool
        self.paper_search_tool = paper_search_tool

        self.generate_chain = create_generate_chain(llm)

    def vector_store_retrieve(self, state):
        """
        Retrieve documents

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, documents, that contains retrieved documents
        """
        print("---RETRIEVE---")
        prompt = state["prompt"]

        # Retrieval
        documents = self.retriever.sim_search(prompt)
        state["resources"] = documents
        state["steps"] = [Steps.VECTOR_STORE_RETRIEVAL.value]

        return state

    def generate(self, state):
        """
        Generate answer

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, generation, that contains LLM generation
        """
        print("---GENERATE---")
        prompt = state["prompt"]
        resources = state["resources"]

        # RAG generation
        generation = self.generate_chain.invoke({"resources": '\n\n'.join(f"{index + 1}. {item}" for index, item in enumerate(resources)), "prompt": prompt, "transcript": state["transcript"]})
        state["generation"] = generation
        state["steps"].append(Steps.LLM_GENERATION.value)

        tools_used = ["vector_search"]
        if state.get("perform_web_search", False):
            tools_used.append("web_search")

        # create_message(content=prompt, chat_session_id=state["chat_session_id"], references=[], sender=MessageSenderEnum.USER,
        #                tools_used=tools_used)
        # create_message(content=generation, chat_session_id=state["chat_session_id"], references=[r for r in resources],
        #                sender=MessageSenderEnum.SYSTEM, tools_used=tools_used)
        return state

    def _base_grade_documents(self, state: GraphState, previous_state: str):
        prompt = state["prompt"]
        resources = state["resources"]

        filtered_resources = []
        next_search = False

        for resource in resources:
            score = self.retrieval_grader.invoke({
                "prompt": prompt, "resources": resource
            })
            # print(f"{resource} || {score}")
            if score["score"].lower() == "yes":
                filtered_resources.append(resource)
            else:
                next_search = True
                continue

        if next_search:
            match previous_state:
                case "vector_store":
                    state["perform_paper_search"] = True
                    state["steps"].append(Steps.VECTOR_STORE_EVALUATION.value)
                case "paper_search":
                    state["perform_web_search"] = True
                    state["steps"].append(Steps.PAPER_SEARCH_EVALUATION.value)
        state["resources"] = filtered_resources

        return state

    def grade_vector_store_documents(self, state: GraphState):
        print("---GRADE VECTOR STORE DOCUMENTS---")
        return self._base_grade_documents(state, "vector_store")

    def grade_paper_search_documents(self, state: GraphState):
        return self._base_grade_documents(state, "paper_search")

    def web_search(self, state: GraphState):
        prompt = state["prompt"]
        web_results = self.web_search_tool.invoke({"query": prompt})
        state["resources"] = [
           result for result in web_results
        ]
        state["steps"].append(Steps.WEB_SEARCH_RETRIEVAL.value)
        return state

    def paper_search(self, state: GraphState):
        prompt = state["prompt"]
        arxiv_papers = self.paper_search_tool.invoke(prompt)
        state["resources"] = [
            paper.page_content for paper in arxiv_papers
        ]
        state["steps"].append(Steps.PAPER_SEARCH_RETRIEVAL.value)
        return state

    def transform_query(self, state):
        """
        Transform the query to produce a better question.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Updates question key with a re-phrased question
        """
        print("---TRANSFORM QUERY---")
        question = state["input"]
        documents = state["documents"]

        # Re-write question
        better_question = self.question_rewriter.invoke({"input": question})
        return {"documents": documents, "input": better_question}

    def route_question(self, state):
        """
        Route question to web search or RAG.

        Args:
            state (dict): The current graph state

        Returns:
            str: Next node to call
        """

        print("---ROUTE QUESTION---")
        question = state["question"]
        source = self.llm.invoke(
            [SystemMessage(content=router_system_prompt)] + [HumanMessage(content=f"{question}")]
        )
        if source.datasource == "web_search":
            print("---ROUTE QUESTION TO WEB SEARCH---")
            return "web_search"
        elif source.datasource == "vectorstore":
            print("---ROUTE QUESTION TO RAG---")
        return "vectorstore"
