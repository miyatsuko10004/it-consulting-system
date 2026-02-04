from typing import List, Optional
from pydantic import BaseModel
from datetime import date

class AllocationBase(BaseModel):
    start_date: date
    end_date: date
    effort_percent: int

class Allocation(AllocationBase):
    id: int
    class Config:
        from_attributes = True

class AssignmentCreate(BaseModel):
    employee_id: int
    allocations: List[AllocationBase]

class Assignment(BaseModel):
    id: int
    employee_id: int
    # Derived from allocations min/max if needed, or nullable
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    allocations: List[Allocation]
    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    name: str
    customer_id: int
    contract_amount: int
    start_date: date
    end_date: date

class Project(ProjectCreate):
    id: int
    status: str
    assignments: List[Assignment] = []
    class Config:
        from_attributes = True

class Billing(BaseModel):
    id: int
    project_id: int
    billing_date: date
    amount: int
    status: str
    class Config:
        from_attributes = True
