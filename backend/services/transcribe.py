# TODO: Add transcription record and return ID
from functools import lru_cache

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import tempfile
from pathlib import Path
import whisper
import boto3
import os
from dotenv import load_dotenv
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from backend.config import settings
from backend.database.employees import get_employee_details
from backend.database.users import get_email_by_user_id


# Load Whisper model for transcription
@lru_cache(maxsize=1)
def get_whisper_model():
    return whisper.load_model("base")


# Function to upload files to S3
def upload_file_to_s3(file_path, s3_key):
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

        s3_client.upload_file(file_path, settings.AWS_S3_BUCKET, s3_key)
        return ""
    except Exception as e:
        raise Exception(f"Failed to upload file to S3: {e}")


def generate_personalized_summary(transcription_path: str, user_id: int):
    user_email = get_email_by_user_id(user_id)[0]
    data = get_employee_details(employee_email=user_email)

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
    # Initialize the LLM with LangChain
    llm = ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        model="gpt-4",
        temperature=0.7,
    )

    with open(transcription_path, "r") as f:
        transcript = f.read()

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
