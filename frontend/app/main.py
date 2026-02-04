from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

RESOURCE_SERVICE_URL = "http://resource-service:8000"
PROJECT_SERVICE_URL = "http://project-service:8000"

@app.get("/employees", response_class=HTMLResponse)
async def employee_list(request: Request, q: str = None):
    async with httpx.AsyncClient() as client:
        # Call Resource Service
        params = {"skill": q} if q else {}
        # Resource Service's list API currently filters by exact skill match via query param
        # We might need to enhance Resource Service for full text search later, 
        # but for now let's use the endpoint we made.
        # Note: Previous TDD implemented /employees/?skill=...
        # We should map 'q' to 'skill' for compatibility or update Resource Service.
        
        # Let's assume we fetch all and filter in BFF for now if the API doesn't support rich search yet,
        # OR just pass the skill param if provided.
        resp = await client.get(f"{RESOURCE_SERVICE_URL}/employees/", params=params)
        employees = resp.json() if resp.status_code == 200 else []
        
        # Fetch Allocations from Project Service
        # Determine query range (e.g. next 6 months)
        from datetime import date, timedelta
        today = date.today()
        start_month = today.strftime("%Y-%m")
        # approx 6 months
        end_date = today + timedelta(days=180) 
        end_month = end_date.strftime("%Y-%m")
        
        alloc_resp = await client.get(f"{PROJECT_SERVICE_URL}/allocations", params={"start_month": start_month, "end_month": end_month})
        allocations = alloc_resp.json() if alloc_resp.status_code == 200 else []

        # Aggregate allocations by employee_id and month
        # Structure: {emp_id: { "2026-02": 50, "2026-03": 100 }}
        heatmap_map = {}
        for alloc in allocations:
            # We need employee_id. Allocation -> Assignment -> EmployeeID
            # Wait, Allocation model in Project Service doesn't explicitly return employee_id flatly?
            # Schema needs to include assignment details or we fetch assignment map.
            pass 
        
        # To simplify, let's update Project Service schema to include assignment.employee_id in Allocation list,
        # OR fetch assignments and map them.
        # Let's fetch assignments too.
        assign_resp = await client.get(f"{PROJECT_SERVICE_URL}/assignments") # Need this endpoint
        assignments = assign_resp.json() if assign_resp.status_code == 200 else []
        assign_map = {a['id']: a['employee_id'] for a in assignments}
        
        for alloc in allocations:
            emp_id = assign_map.get(alloc['assignment_id'])
            if not emp_id: continue
            
            if emp_id not in heatmap_map: heatmap_map[emp_id] = {}
            current_val = heatmap_map[emp_id].get(alloc['month'], 0)
            heatmap_map[emp_id][alloc['month']] = current_val + alloc['effort_percent']

        # Generate Headers
        month_headers = []
        curr = today.replace(day=1)
        for _ in range(6):
            month_headers.append(curr.strftime("%Y-%m"))
            # Next month logic
            if curr.month == 12:
                curr = curr.replace(year=curr.year+1, month=1)
            else:
                curr = curr.replace(month=curr.month+1)

        # Attach heatmap to employees
        for emp in employees:
            emp_map = heatmap_map.get(emp['id'], {})
            emp['heatmap'] = []
            for m in month_headers:
                percent = emp_map.get(m, 0)
                emp['heatmap'].append({"label": m, "percent": percent})

    return templates.TemplateResponse("employees.html", {
        "request": request, 
        "employees": employees,
        "month_headers": month_headers
    })
