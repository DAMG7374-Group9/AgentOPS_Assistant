
from backend.agent import agent_workflow

async def process_llm_query(
    article_id: str, prompt: str, model: str, user_id: int
):
    """Process a Q/A query and store the result"""
    response = agent_workflow.invoke({"prompt": prompt})

    print(response["steps"])

    # qa_history = QAHistory(
    #     id=uuid.uuid4().hex,
    #     a_id=article_id,
    #     question=prompt,
    #     answer=response.response,
    #     referenced_pages=json.dumps([src.model_dump() for src in response.sources]),
    #     user_id=user_id,
    #     model=model,
    # )
    #
    # with db_session() as session:
    #     session.add(qa_history)
    #     session.commit()

    tools_used = ["vector_search"]
    if response.get("perform_web_search", False):
        tools_used.append("web_search")

    return {
        "response": response["generation"],
        "tools_used": ", ".join(tools_used),
    }
