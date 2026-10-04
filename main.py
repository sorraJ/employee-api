import sqlite3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from database import connection, cursor


class Employee(BaseModel):
    id: int
    name: str
    department: str
    position: str


app = FastAPI()


@app.get("/employees")
def get_employees():
    cursor.execute("SELECT * FROM employees")
    employees_from_db = cursor.fetchall()

    employees_list = []

    for employee in employees_from_db:
        employee_dict = {
            "id": employee[0],
            "name": employee[1],
            "department": employee[2],
            "position": employee[3]
        }

        employees_list.append(employee_dict)

    return employees_list


@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    cursor.execute(
        "SELECT * FROM employees WHERE id = ?",
        (employee_id,)
    )

    employee = cursor.fetchone()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    employee_dict = {
        "id": employee[0],
        "name": employee[1],
        "department": employee[2],
        "position": employee[3]
    }

    return employee_dict


@app.post("/employees")
def create_employee(employee: Employee):
    try:
        cursor.execute("""
        INSERT INTO employees (id, name, department, position)
        VALUES (?, ?, ?, ?)
        """, (
            employee.id,
            employee.name,
            employee.department,
            employee.position
        ))

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Employee already exists"
        )

    connection.commit()

    return employee


@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    cursor.execute(
        "SELECT * FROM employees WHERE id = ?",
        (employee_id,)
    )

    employee = cursor.fetchone()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    cursor.execute(
        "DELETE FROM employees WHERE id = ?",
        (employee_id,)
    )

    connection.commit()

    employee_dict = {
        "id": employee[0],
        "name": employee[1],
        "department": employee[2],
        "position": employee[3]
    }

    return employee_dict


@app.put("/employees/{employee_id}")
def put_employee(employee_id: int, employee: Employee):
    cursor.execute(
        "SELECT * FROM employees WHERE id = ?",
        (employee_id,)
    )

    existing_employee = cursor.fetchone()

    if existing_employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    cursor.execute("""
        UPDATE employees
        SET name = ?, department = ?, position = ?
        WHERE id = ?
    """, (
        employee.name,
        employee.department,
        employee.position,
        employee_id
    ))

    connection.commit()

    employee_dict = {
        "id": employee_id,
        "name": employee.name,
        "department": employee.department,
        "position": employee.position
    }

    return employee_dict