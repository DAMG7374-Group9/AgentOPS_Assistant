from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from backend.agent.edges import GraphEdges
from backend.agent.generate_chain import create_generate_chain
from backend.agent.grader import GraderUtils
from backend.agent.graph import GraphState
from backend.agent.nodes import GraphNodes
from backend.agent.vector_store import get_pinecone_vector_store, Retriever
from backend.config import settings
from backend.utils import get_tavily_web_search_tool, get_arxiv_search_tool


def compile_graph():

    # Vector Store
    vector_store = get_pinecone_vector_store()
    # retriever = vector_store.as_retriever(
    #     search_type="similarity",
    #     search_args={"k": 4}
    # )
    retriever = Retriever(vector_store=vector_store)

    # LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=settings.OPENAI_API_KEY)

    # Evaluation - Grader
    grader = GraderUtils(llm=llm)
    retrieval_grader = grader.create_retrieval_grader()

    # Tools
    web_search_tool = get_tavily_web_search_tool()
    # paper_search_tool = get_arxiv_search_tool()

    graph_nodes = GraphNodes(
        llm=llm, retriever=retriever, retrieval_grader=retrieval_grader, web_search_tool=web_search_tool,
        paper_search_tool=None
    )
    graph_edges = GraphEdges(None, None)

    # Build workflow
    workflow = StateGraph(GraphState)

    workflow.add_node("vector_search", graph_nodes.vector_store_retrieve)
    workflow.add_node("vector_search_evaluate", graph_nodes.grade_vector_store_documents)

    workflow.add_node("web_search", graph_nodes.web_search)
    workflow.add_node("generate", graph_nodes.generate)

    workflow.set_entry_point("vector_search")
    workflow.add_edge("vector_search", "vector_search_evaluate")


    workflow.add_conditional_edges(
        "vector_search_evaluate",
        graph_edges.vector_search_decide_to_generate,
        {
            "relevant": "generate",
            "irrelevant": "web_search"
        }
    )
    # workflow.add_edge("paper_search", "paper_search_evaluate")
    # workflow.add_conditional_edges(
    #     "paper_search_evaluate",
    #     graph_edges.paper_search_decide_to_generate,
    #     {
    #         "relevant": "generate",
    #         "irrelevant": "web_search"
    #     }
    # )
    workflow.add_edge("web_search", "generate")
    workflow.add_edge("generate", END)
    return workflow.compile()


agent_workflow = compile_graph()
