import streamlit as st
import snowflake.connector
import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import time

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
        schema="MEETPRO_INSIGHTS"
    )
    return conn


# Fetch combined employee and project details
def get_employee_and_projects(email):
    conn = connect_to_snowflake()
    try:
        query = """
        SELECT
            E.EMPLOYEEID,
            E.EMPLOYEENAME,
            E.EMAIL,
            E.JOBLEVEL,
            E.ROLETYPE,
            E.DEPARTMENTID,
            E.CURRENTPROJECTID,
            E.SUPERVISORID,
            P.PROJECTID,
            P.PROJECTNAME,
            P.PROJECTDESCRIPTION,
            P.STARTDATE,
            P.ENDDATE,
            P.PROJECTSTATUS,
            P.PROJECTMANAGERID,
            P.JIRABOARDID
        FROM
            DB_AGENTOPS.MEETPRO_INSIGHTS.DIMEMPLOYEE E
        JOIN
            DB_AGENTOPS.MEETPRO_INSIGHTS.DIMPROJECT P
        ON
            E.EMPLOYEEID = P.EMPLOYEEID
        WHERE
            E.EMAIL = %s
        """
        cur = conn.cursor()
        cur.execute(query, (email,))
        results = cur.fetchall()

        if results:
            # Combine all rows into a single dictionary
            combined_data = {
                "EmployeeID": results[0][0],
                "EmployeeName": results[0][1],
                "Email": results[0][2],
                "JobLevel": results[0][3],
                "RoleType": results[0][4],
                "DepartmentID": results[0][5],
                "CurrentProjectID": results[0][6],
                "SupervisorID": results[0][7],
                "Projects": [
                    {
                        "ProjectID": row[8],
                        "ProjectName": row[9],
                        "ProjectDescription": row[10],
                        "StartDate": row[11],
                        "EndDate": row[12],
                        "ProjectStatus": row[13],
                        "ProjectManagerID": row[14],
                        "JiraBoardID": row[15]
                    }
                    for row in results
                ]
            }
            return combined_data
        else:
            return None
    finally:
        conn.close()


# Generate a personalized summary with LangChain
def generate_personalized_summary(data, transcript):
    template = """
        You are an advanced assistant designed to generate personalized summaries for employees based on their role, ongoing tasks, projects, and meeting discussions.
        Based on the designation refine the most important points that refine 80 percent essence of the conversation refined to the
        designation and what they will need as takeaways from the meeting.  It must be personally customized for the employee and include the other most important parts as well

    Employee Details:
    - Name: {EmployeeName}
    - Email: {Email}
    - Job Level: {JobLevel}
    - Role Type: {RoleType}
    - Department ID: {DepartmentID}
    - Supervisor ID: {SupervisorID}
    - Current Project ID: {CurrentProjectID}

    Assigned Projects:
    {ProjectDetails}

    Meeting Transcript:
    {Transcript}

    Output Guidelines
    - Format the summary with clear headings, bullet points, and concise language.
    - Prioritize details relevant to the employee's role, avoiding redundant or irrelevant information.
    - Include citations from the RAG for context or clarification.

    Example Output
    Employee Summary for [EmployeeName]
    Key Meeting Decisions:
    - Decision 1: [Brief summary].
    - Impact on [CurrentProjectName]: [Explain how this decision affects the employee’s tasks].
    - And so on

    Actionable Insights:
    - Task [TaskID]: Update priority to [High/Medium] and align with [Stakeholder/Team].
    - Skill Opportunity: Explore [new technology] for [specific task/project].
    - And so on

    Next Steps:
    1. [Action item 1 based on transcript].
    2. [Action item 2 based on tasks and RAG].
    3. And so on

    Use this structured approach for generating comprehensive, personalized summaries.

    Generate a summary tailored to the employee's role and responsibilities. Use note-taking format (headings, bullet points, and concise sentences) and limit the summary to 200 words.
    """
    project_details = "\n".join(
        f"- Project ID: {project['ProjectID']}, Name: {project['ProjectName']}, "
        f"Description: {project['ProjectDescription']}, Status: {project['ProjectStatus']}, "
        f"Start Date: {project['StartDate']}, End Date: {project['EndDate']}, "
        f"Manager ID: {project['ProjectManagerID']}, Jira Board ID: {project['JiraBoardID']}"
        for project in data["Projects"]
    ) if data["Projects"] else "No projects assigned."

    prompt = PromptTemplate(
        input_variables=["EmployeeName", "Email", "JobLevel", "RoleType", "DepartmentID", "SupervisorID",
                         "CurrentProjectID", "ProjectDetails", "Transcript"],
        template=template
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run({
        "EmployeeName": data["EmployeeName"],
        "Email": data["Email"],
        "JobLevel": data["JobLevel"],
        "RoleType": data["RoleType"],
        "DepartmentID": data["DepartmentID"],
        "SupervisorID": data["SupervisorID"],
        "CurrentProjectID": data["CurrentProjectID"],
        "ProjectDetails": project_details,
        "Transcript": transcript
    })

    return response.strip()


# Initialize chatbot
def initialize_chatbot(summary, employee_details):
    memory = ConversationBufferMemory()
    context = f"""
    Summary of Meeting:
    {summary}

    Employee Details:
    - Name: {employee_details['EmployeeName']}
    - Role Type: {employee_details['RoleType']}
    - Current Project: {employee_details['CurrentProjectID']}
    - Projects: {', '.join([project['ProjectName'] for project in employee_details['Projects']]) if employee_details['Projects'] else "No projects assigned."}
    """
    memory.chat_memory.add_ai_message(context)

    conversation = ConversationChain(
        llm=llm,
        memory=memory
    )
    return conversation





# Ensure session state initialization for chatbot input and chat history
# CHANGE START: Initialize `chat_input` and `chat_history`
if "chat_input" not in st.session_state:
    st.session_state["chat_input"] = ""

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


# Main Streamlit App
def main():
    st.set_page_config(page_title="MeetPRO Insights", layout="wide")
    st.title("💼 MeetPRO Insights: Employee Assistant")

    col1, col2 = st.columns([2, 3])

    # Left Column: Email Inputs and Summary
    with col1:
        email_input = st.text_area("📧 Enter Email IDs (comma-separated):", "")
        email_ids = [email.strip() for email in email_input.split(",") if email.strip()]

        if email_ids:
            selected_email = st.selectbox("👤 Select an Employee Email ID", email_ids)

            if st.button("📄 Generate Summary"):
                data = get_employee_and_projects(selected_email)
                if data:
                    # st.write("Fetched Data:", data)  # Debugging
                    try:
                        with open("transcript.txt", "r") as file:
                            transcript_content = file.read()
                    except FileNotFoundError:
                        st.error("🚨 Transcript file not found.")
                        return

                    # st.write("Transcript Content:", transcript_content)  # Debugging

                    try:
                        summary = generate_personalized_summary(data, transcript_content)
                        progress_bar = col1.progress(0)
                        for perc_completed in range(100):
                            time.sleep(0.05)
                            progress_bar.progress(perc_completed + 1)
                        st.session_state.summary = summary
                        st.session_state.employee_details = data

                        # st.write("Generated Summary:", summary)  # Debugging
                        # col1.success("Personalized summary generated successfully")
                    except Exception as e:
                        st.error(f"🚨 Error in LangChain: {str(e)}")
                        return

                    if "conversation" not in st.session_state:
                        st.session_state.conversation = initialize_chatbot(summary, data)
                else:
                    st.error("No data found for the provided email.")
        if "summary" in st.session_state:
            st.markdown(f"<div>{st.session_state.summary}</div>", unsafe_allow_html=True)
            col1.success("Personalized summary generated successfully")

    # Right Column: Chatbot
    with col2:
        st.subheader("🤖 Chatbot Assistant")

        if "conversation" in st.session_state:
            for message in st.session_state.get("chat_history", []):
                if message["role"] == "user":
                    st.markdown(f"**You:** {message['content']}")
                elif message["role"] == "assistant":
                    st.markdown(f"**Chatbot:** {message['content']}")

            def handle_chat_input():
                if st.session_state.chat_input:
                    st.session_state.chat_history.append({"role": "user", "content": st.session_state.chat_input})
                    response = st.session_state.conversation.run(st.session_state.chat_input)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.session_state.chat_input = ""

            st.text_input("Ask a question to the chatbot:", key="chat_input", on_change=handle_chat_input)


if __name__ == "__main__":
    main()

