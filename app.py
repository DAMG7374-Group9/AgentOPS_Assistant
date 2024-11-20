import streamlit as st
import snowflake.connector
import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize the LLM with LangChain
llm = ChatOpenAI(
    openai_api_key=openai_api_key,
    model="gpt-4",
    temperature=0.7,
    max_tokens=500
)

# Snowflake connection
def connect_to_snowflake():
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse="MY_WAREHOUSE",
        database="DB_AGENTOPS_CORE",
        schema="DBT_CORE_SCHEMA"
    )
    return conn

# Fetch combined employee and task details
def get_employee_and_tasks(email):
    conn = connect_to_snowflake()
    try:
        query = """
        SELECT 
            emp.EmployeeID,
            emp.EmployeeName,
            emp.EmailID,
            emp.ProjectID,
            emp.RoleInProject,
            emp.DateAssigned,
            emp.DateCompleted,
            emp.ContributionScore,
            task.TaskID,
            task.TaskDescription,
            task.TaskStatus,
            task.TaskPriority,
            task.EstimatedCompletionTime,
            task.ActualCompletionTime
        FROM FactEmployeeProject emp
        LEFT JOIN FactProjectTasks task
        ON emp.EmployeeID = task.AssignedToEmployeeID
        WHERE emp.EmailID = %s
        """
        cur = conn.cursor()
        cur.execute(query, (email,))
        results = cur.fetchall()

        if results:
            # Combine all rows into a single dictionary
            combined_data = {
                "EmployeeID": results[0][0],
                "EmployeeName": results[0][1],
                "EmailID": results[0][2],
                "ProjectID": results[0][3],
                "RoleInProject": results[0][4],
                "DateAssigned": str(results[0][5]),
                "DateCompleted": str(results[0][6]),
                "ContributionScore": results[0][7],
                "Tasks": [
                    {
                        "TaskID": row[8],
                        "TaskDescription": row[9],
                        "TaskStatus": row[10],
                        "TaskPriority": row[11],
                        "EstimatedCompletionTime": row[12],
                        "ActualCompletionTime": row[13]
                    }
                    for row in results if row[8] is not None
                ]
            }
            return combined_data
        else:
            return None
    finally:
        conn.close()

# Generate a personalized summary with LangChain
def generate_personalized_summary(data, transcript):
    # Define a LangChain prompt template
    template = """
        Based on the designation refine the most important points that refine 80 percent essence of the conversation refined to the 
        designation and what they will need as takeaways from the meeting.  It must be personally customized for the employee and include the other most important parts as well

    Employee Details:
    - Name: {EmployeeName}
    - Email: {EmailID}
    - Role in Project: {RoleInProject}
    - Contribution Score: {ContributionScore}
    - Project ID: {ProjectID}
    - Dates: Assigned ({DateAssigned}) - Completed ({DateCompleted})

    Assigned Tasks:
    {TaskDetails}

    Meeting Transcript:
    {Transcript}

    Generate a summary tailored to the employee's role and responsibilities. Use note-taking format (headings, bullet points, and concise sentences) and limit the summary to 200 words.
    """

    # Format tasks into a readable string
    task_details = "\n".join(
        f"- Task ID: {task['TaskID']}, Description: {task['TaskDescription']}, "
        f"Status: {task['TaskStatus']}, Priority: {task['TaskPriority']}, "
        f"Estimated Time: {task['EstimatedCompletionTime']} hours, "
        f"Actual Time: {task['ActualCompletionTime']} hours"
        for task in data["Tasks"]
    ) if data["Tasks"] else "No tasks assigned."

    # Create a LangChain PromptTemplate
    prompt = PromptTemplate(
        input_variables=["EmployeeName", "EmailID", "RoleInProject", "ContributionScore", "ProjectID", "DateAssigned", "DateCompleted", "TaskDetails", "Transcript"],
        template=template
    )

    # Create an LLM chain
    chain = LLMChain(llm=llm, prompt=prompt)

    # Run the chain with input values
    response = chain.run({
        "EmployeeName": data["EmployeeName"],
        "EmailID": data["EmailID"],
        "RoleInProject": data["RoleInProject"],
        "ContributionScore": data["ContributionScore"],
        "ProjectID": data["ProjectID"],
        "DateAssigned": data["DateAssigned"],
        "DateCompleted": data["DateCompleted"],
        "TaskDetails": task_details,
        "Transcript": transcript
    })

    return response.strip()

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Chatbot Initialization with Memory
def initialize_chatbot(summary, employee_details):
    memory = ConversationBufferMemory()

    # Context for chatbot initialization
    context = f"""
    Summary of Meeting:
    {summary}

    Employee Details:
    - Name: {employee_details['EmployeeName']}
    - Role in Project: {employee_details['RoleInProject']}
    - Contribution Score: {employee_details['ContributionScore']}
    - Tasks: {', '.join([task['TaskDescription'] for task in employee_details['Tasks']]) if employee_details['Tasks'] else "No tasks assigned."}
    """

    # Preload the memory with the context
    memory.chat_memory.add_ai_message(context)

    # Create ConversationChain with memory
    conversation = ConversationChain(
        llm=llm,
        memory=memory
    )

    return conversation


# Streamlit App with Continuous Chat and "Generate Response" Button
def main():
    # Streamlit UI Configuration
    st.set_page_config(
        page_title="Employee AgentOPS",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("💼 Employee AgentOPS Assistant")

    # Step 1: Input email IDs
    email_input = st.text_area("📧 Enter Email IDs (comma-separated):", "")
    email_ids = [email.strip() for email in email_input.split(",") if email.strip()]

    if email_ids:
        # Step 2: Dropdown to select an email ID
        selected_email = st.selectbox("👤 Select an Employee Email ID", email_ids)

        if st.button("📄 Generate Summary"):
            # Step 3: Fetch combined employee and task details
            data = get_employee_and_tasks(selected_email)
            if data:
                # Read the meeting transcript
                try:
                    with open("transcript.txt", "r") as file:
                        transcript_content = file.read()
                except FileNotFoundError:
                    st.error("🚨 Meeting transcript file not found. Please ensure 'transcript.txt' is in the same directory.")
                    return

                # Generate personalized summary
                summary = generate_personalized_summary(data, transcript_content)

                # Store the summary in session state
                st.session_state.summary = summary
                st.session_state.employee_details = data

                # Initialize chatbot in session state
                if "conversation" not in st.session_state:
                    st.session_state.conversation = initialize_chatbot(summary, data)

                # Initialize conversation history
                if "chat_history" not in st.session_state:
                    st.session_state.chat_history = []

    # Display the summary if it exists
    if "summary" in st.session_state:
        st.subheader("📋 Personalized Summary")
        st.markdown(f"<div class='summary-box'>{st.session_state.summary}</div>", unsafe_allow_html=True)

    # Chatbot interaction
    if "conversation" in st.session_state:
        st.subheader("🤖 Chatbot Assistant")

        # Display conversation history
        for entry in st.session_state.chat_history:
            st.markdown(f"**You:** {entry['user']}")
            st.markdown(f"**Chatbot:** {entry['bot']}")

        # Use a temporary variable to manage input
        user_input = st.text_input("Ask a question to the chatbot:", key="chat_input")

        if st.button("Generate Response"):
            if user_input:
                # Access the persisted conversation from session state
                conversation = st.session_state.conversation

                # Generate chatbot response
                response = conversation.run(input=user_input)

                # Append the interaction to chat history
                st.session_state.chat_history.append({"user": user_input, "bot": response})

                # Clear the input box by resetting the session state variable
                st.session_state["chat_input"] = ""
                st.experimental_rerun()  # Force rerun to clear input box



        else:
            st.warning("⚠️ No data found for the selected email ID.")
    else:
        st.info("ℹ️ Please enter email IDs to proceed.")

if __name__ == "__main__":
    main()
