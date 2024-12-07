from sqlalchemy import Column, Integer, String, Date

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
    with db_session() as session:
        stmt = """
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
        results = session.execute(stmt, (employee_email, ))
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
