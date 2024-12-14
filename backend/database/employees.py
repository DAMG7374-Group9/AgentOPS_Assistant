import snowflake
from sqlalchemy import Column, Integer, String, Date, text

from backend.config import settings
from backend.database import Base, db_session


class FactEmployeeProject(Base):
    __tablename__ = 'FACTEMPLOYEEPROJECT'
    __table_args__ = {'schema': 'DB_AGENTOPS_CORE.DBT_CORE_SCHEMA'}

    ASSIGNMENTID = Column(Integer, primary_key=True, autoincrement=False)
    EMPLOYEEID = Column(Integer, nullable=False)
    EMPLOYEENAME = Column(String(100))
    EMAILID = Column(String(150))
    PROJECTID = Column(Integer, nullable=False)
    ROLEINPROJECT = Column(String(100))
    DATEASSIGNED = Column(Date)
    DATECOMPLETED = Column(Date)
    CONTRIBUTIONSCORE = Column(Integer)


def get_employee_details(employee_email: str):
    conn = snowflake.connector.connect(
        user=settings.SNOWFLAKE_DB_USER,
        password=settings.SNOWFLAKE_DB_PASSWORD,
        account=settings.SNOWFLAKE_DB_ACCOUNT,
        warehouse="MY_WAREHOUSE",
        database="DB_AGENTOPS_CORE",
        schema="MEETPRO_INSIGHTS"
    )
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
        cur.execute(query, (employee_email,))
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
