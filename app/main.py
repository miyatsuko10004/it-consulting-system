from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db, engine, Base
from app.models import Project, Employee, Customer, ProjectStatus, ProjectAssignment

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Dashboard / Project List
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "projects": projects})

# Create Project Form
@app.get("/projects/new", response_class=HTMLResponse)
def new_project_form(request: Request, db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return templates.TemplateResponse("project_form.html", {"request": request, "customers": customers, "statuses": list(ProjectStatus)})

@app.post("/projects", response_class=HTMLResponse)
def create_project(
    request: Request,
    name: str = Form(...),
    customer_id: int = Form(...),
    status: str = Form(...),
    contract_amount: int = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    db: Session = Depends(get_db)
):
    new_proj = Project(
        name=name,
        customer_id=customer_id,
        status=status,
        contract_amount=contract_amount,
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        payment_terms="月末締め翌月末払い"
    )
    db.add(new_proj)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# Employee List (Resource Management)
@app.get("/employees", response_class=HTMLResponse)
def employee_list(request: Request, db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    return templates.TemplateResponse("employees.html", {"request": request, "employees": employees})
