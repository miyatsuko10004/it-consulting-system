from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
from datetime import date, timedelta

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

RESOURCE_SERVICE_URL = "http://resource-service:8000"
PROJECT_SERVICE_URL = "http://project-service:8000"

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    # In microservices, we might need a dedicated Customer Service or fetch from Project Service
    # Assuming Project Service handles projects and basic customer info for now
    # We need an endpoint in Project Service to list projects
    # Let's mock the data fetching or assume we add list endpoint to Project Service
    # Ideally: GET PROJECT_SERVICE_URL/projects
    
    # Check if Project Service has list endpoint. We added POST /projects/ but maybe not GET list in TDD step?
    # Let's assume we need to add it or it exists.
    # Quick fix: Add GET /projects to Project Service.
    
    async with httpx.AsyncClient() as client:
        # Try to fetch projects. If fail, show empty list.
        try:
            resp = await client.get(f"{PROJECT_SERVICE_URL}/projects/") # Need to ensure this exists
            projects = resp.json() if resp.status_code == 200 else []
        except:
            projects = []
            
    return templates.TemplateResponse("dashboard.html", {"request": request, "projects": projects})

from calendar import monthrange

# ... imports ...

@app.get("/employees", response_class=HTMLResponse)
async def employee_list(request: Request, q: str = None):
    async with httpx.AsyncClient() as client:
        params = {"skill": q} if q else {}
        resp = await client.get(f"{RESOURCE_SERVICE_URL}/employees/", params=params)
        employees = resp.json() if resp.status_code == 200 else []
        
        today = date.today()
        # approx 6 months end
        end_date = today + timedelta(days=180) 
        
        try:
            # Fetch daily allocations
            alloc_resp = await client.get(f"{PROJECT_SERVICE_URL}/allocations", params={"start_date": today.isoformat(), "end_date": str(end_date)})
            allocations = alloc_resp.json() if alloc_resp.status_code == 200 else []
            
            assign_resp = await client.get(f"{PROJECT_SERVICE_URL}/assignments")
            assignments = assign_resp.json() if assign_resp.status_code == 200 else []
            assign_map = {a['id']: a['employee_id'] for a in assignments}
            
            # Heatmap Aggregation (Daily to Monthly Average)
            heatmap_map = {} # {emp_id: { "2026-04": 75, ... }}
            
            # Helper to generate month keys for the next 6 months
            target_months = []
            curr = today.replace(day=1)
            for _ in range(6):
                _, last_day = monthrange(curr.year, curr.month)
                target_months.append({
                    "key": curr.strftime("%Y-%m"),
                    "year": curr.year,
                    "month": curr.month,
                    "days": last_day,
                    "start": curr,
                    "end": curr.replace(day=last_day)
                })
                if curr.month == 12:
                    curr = curr.replace(year=curr.year+1, month=1)
                else:
                    curr = curr.replace(month=curr.month+1)

            for alloc in allocations:
                emp_id = assign_map.get(alloc['assignment_id'])
                if not emp_id: continue
                if emp_id not in heatmap_map: heatmap_map[emp_id] = {}
                
                alloc_start = date.fromisoformat(alloc['start_date'])
                alloc_end = date.fromisoformat(alloc['end_date'])
                
                for tm in target_months:
                    # Calculate overlap days
                    overlap_start = max(alloc_start, tm["start"])
                    overlap_end = min(alloc_end, tm["end"])
                    
                    if overlap_start <= overlap_end:
                        overlap_days = (overlap_end - overlap_start).days + 1
                        monthly_contribution = (overlap_days / tm["days"]) * alloc['effort_percent']
                        
                        heatmap_map[emp_id][tm["key"]] = heatmap_map[emp_id].get(tm["key"], 0) + monthly_contribution
                        
        except Exception as e:
            print(f"Error calculating heatmap: {e}")
            heatmap_map = {}
            target_months = [] # Fallback

        month_headers = [m["key"] for m in target_months] if target_months else []

        for emp in employees:
            emp_map = heatmap_map.get(emp['id'], {})
            emp['heatmap'] = []
            for m in month_headers:
                percent = round(emp_map.get(m, 0)) # Round to nearest integer
                emp['heatmap'].append({"label": m, "percent": percent})

    return templates.TemplateResponse("employees.html", {
        "request": request, 
        "employees": employees,
        "month_headers": month_headers
    })

@app.get("/projects/new", response_class=HTMLResponse)
async def new_project_form(request: Request):
    # Mock customers for now
    customers = [{"id": 1, "name": "株式会社A"}, {"id": 2, "name": "株式会社B"}]
    statuses = [{"value": "Lead"}, {"value": "Contracted"}, {"value": "Completed"}]
    return templates.TemplateResponse("project_form.html", {"request": request, "customers": customers, "statuses": statuses})

@app.post("/projects", response_class=HTMLResponse)
async def create_project(
    request: Request,
    name: str = Form(...),
    customer_id: int = Form(...),
    status: str = Form(...),
    contract_amount: int = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...)
):
    payload = {
        "name": name,
        "customer_id": customer_id,
        "status": status,
        "contract_amount": contract_amount,
        "start_date": start_date,
        "end_date": end_date
    }
    async with httpx.AsyncClient() as client:
        await client.post(f"{PROJECT_SERVICE_URL}/projects/", json=payload)
    return RedirectResponse(url="/", status_code=303)

@app.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_detail(request: Request, project_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{PROJECT_SERVICE_URL}/projects/{project_id}")
        if resp.status_code != 200:
            return RedirectResponse(url="/")
        project = resp.json()
        
        # Add mock customer name since Project Service only stores ID
        project["customer"] = {"name": "株式会社A", "industry": "IT"} # Mock
        
        # Calculate summary (Simplified logic for BFF, or fetch from Project Service if it computes)
        # Project Service currently doesn't return summary in GET /projects/{id} unless we implemented it.
        # We implemented it in Monolith but maybe not fully in Microservice Project Service GET?
        # Let's assume Project Service GET returns basic info and we need to fetch assignments to calculate.
        # OR Project Service GET should return summary.
        
        # For now, let's pass a dummy summary to avoid template errors
        summary = {"revenue": project["contract_amount"], "cost": 0, "profit": 0, "margin_percent": 0, "breakdown": []}
        
    return templates.TemplateResponse("project_detail.html", {
        "request": request, 
        "project": project, 
        "summary": summary
    })

@app.get("/projects/{project_id}/edit", response_class=HTMLResponse)
async def edit_project_form(request: Request, project_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{PROJECT_SERVICE_URL}/projects/{project_id}")
        if resp.status_code != 200:
            return RedirectResponse(url="/")
        project = resp.json()
        
    customers = [{"id": 1, "name": "株式会社A"}, {"id": 2, "name": "株式会社B"}]
    statuses = [{"value": "Lead"}, {"value": "Contracted"}, {"value": "Completed"}]
    return templates.TemplateResponse("project_edit.html", {
        "request": request,
        "project": project,
        "customers": customers,
        "statuses": statuses
    })

@app.post("/projects/{project_id}/edit", response_class=HTMLResponse)
async def update_project(
    request: Request,
    project_id: int,
    name: str = Form(...),
    customer_id: int = Form(...),
    status: str = Form(...),
    contract_amount: int = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...)
):
    payload = {
        "name": name,
        "customer_id": customer_id,
        "status": status,
        "contract_amount": contract_amount,
        "start_date": start_date,
        "end_date": end_date
    }
    async with httpx.AsyncClient() as client:
        await client.put(f"{PROJECT_SERVICE_URL}/projects/{project_id}", json=payload)
        
    return RedirectResponse(url="/", status_code=303)

@app.get("/billings", response_class=HTMLResponse)
async def billing_list(request: Request):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{PROJECT_SERVICE_URL}/billings")
        billings = resp.json() if resp.status_code == 200 else []
        
        # We need project names. In a real app, join or fetch.
        # Here we mock or fetch projects to map.
        proj_resp = await client.get(f"{PROJECT_SERVICE_URL}/projects/")
        projects = proj_resp.json() if proj_resp.status_code == 200 else []
        proj_map = {p['id']: p['name'] for p in projects}
        
        for b in billings:
            b['project_name'] = proj_map.get(b['project_id'], 'Unknown Project')
            
    return templates.TemplateResponse("billings.html", {"request": request, "billings": billings})
