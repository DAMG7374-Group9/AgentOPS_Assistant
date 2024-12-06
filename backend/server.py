# import os
# import pickle
# import sys
#
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from typing import List, Any, Union, Dict
# from backend.agent.vector_store import create_vector_store
# from backend.agent.grader import GraderUtils
# from backend.agent.graph import GraphState
# from backend.agent.generate_chain import create_generate_chain
# from backend.agent.nodes import GraphNodes
# from backend.agent.edges import EdgeGraph
# from langgraph.graph import END, StateGraph
# from fastapi import FastAPI
# from fastapi.responses import RedirectResponse
# from langchain_core.pydantic_v1 import BaseModel, Field
# from langchain_core.messages import HumanMessage, AIMessage
# from langchain_core.output_parsers import StrOutputParser
# from dotenv import load_dotenv, find_dotenv
#
# load_dotenv(find_dotenv())  # important line if cannot load api key
#
# ## Getting the api keys from the .env file
#
# os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
# os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')
#
#
# # embedding model
# embedding_model = OpenAIEmbeddings()
#
# # Load the crawled saved docs from the local file
# with open("crawled_docs/saved_docs.pkl", "rb") as f:
#     saved_docs = pickle.load(f)
#
# # convert doc list to text strings
# # doc_text = [doc.page_content for doc in saved_docs]
#
# # create vector store
# store = create_vector_store(saved_docs)
#
# # creating retriever
# retriever = store.as_retriever()
#
# ## LLM model
# llm = ChatOpenAI(model="gpt-4o", temperature=0)
#
# # Create the generate chain
# generate_chain = create_generate_chain(llm)
#
# ## get the grader instances
#
# # Create an instance of the GraderUtils class
# grader = GraderUtils(llm)
#
# # Get the retrieval grader
# retrieval_grader = grader.create_retrieval_grader()
#
# # Get the hallucination grader
# hallucination_grader = grader.create_hallucination_grader()
#
# # Get the code evaluator
# code_evaluator = grader.create_code_evaluator()
#
# # Get the question rewriter
# question_rewriter = grader.create_question_rewriter()
#
# ## Creating the WorkFlow
#
# # Initiating the Graph
# workflow = StateGraph(GraphState)
#
# # Create an instance of the GraphNodes class
# graph_nodes = GraphNodes(llm, retriever, retrieval_grader, hallucination_grader, code_evaluator, question_rewriter)
#
# # Create an instance of the EdgeGraph class
# edge_graph = EdgeGraph(hallucination_grader, code_evaluator)
#
# # Define the nodes
# workflow.add_node("retrieve", graph_nodes.retrieve)  # retrieve documents
# workflow.add_node("grade_documents", graph_nodes.grade_documents)  # grade documents
# workflow.add_node("generate", graph_nodes.generate)  # generate answers
# workflow.add_node("transform_query", graph_nodes.transform_query)  # transform_query
#
# # Build graph
# workflow.set_entry_point("retrieve")
# workflow.add_edge("retrieve", "grade_documents")
# workflow.add_conditional_edges(
#     "grade_documents",
#     edge_graph.decide_to_generate,
#     {
#         "transform_query": "transform_query",  # "transform_query": "transform_query",
#         "generate": "generate",
#     },
# )
# workflow.add_edge("transform_query", "retrieve")
# workflow.add_conditional_edges(
#     "generate",
#     edge_graph.grade_generation_v_documents_and_question,
#     {
#         "not supported": "generate",
#         "useful": END,
#         "not useful": "transform_query",  # "transform_query"
#     },
# )
#
# # Compile
# chain = workflow.compile()
#
# ## Create the FastAPI app
#
# app = FastAPI(
#     title="Speckle Server",
#     version="1.0",
#     description="An API server to answer questions regarding the Speckle Developer Docs"
#
# )
#
#
# @app.get("/")
# async def redirect_root_to_docs():
#     return RedirectResponse("/docs")
#
#
# class Input(BaseModel):
#     input: str
#
#
# class Output(BaseModel):
#     output: dict
#
#
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="localhost", port=8000)
