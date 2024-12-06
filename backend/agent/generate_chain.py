from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def create_generate_chain(llm):
    """
    Creates a generate chain for answering code-related questions.

    Args:
        llm (LLM): The language model to use for generating responses.

    Returns:
        A callable function that takes a context and a question as input and returns a string response.
    """
    generate_template = """You are a knowledgeable assistant that generates answers to the question solely based on the documents provided in the context. Your goal is to use the provided context to answer the user's question clearly, and comprehensively.
    
    Context:
    Documents: {resources}
    
    Question:
    {prompt}
    
    Answer:  """

    generate_prompt = PromptTemplate(template=generate_template, input_variables=["prompt", "resources"])

    # Create the generate chain
    generate_chain = generate_prompt | llm | StrOutputParser()

    return generate_chain


# TODO: Create initial chain including the personalized summary as the starting context
# TODO: Build chains with context of previous chat invocations
