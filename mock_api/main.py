import random

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="Mock ERP API")

class LineItem(BaseModel):
    description: str
    amount: float

class Invoice(BaseModel):
    id: str
    vendor: str
    currency: str
    line_items: list[LineItem]
    total_amount: float

class ApprovalResult(BaseModel):
    status: str
    reason: str = ""

@app.get("/api/invoices/pending", response_model=list[Invoice])
def get_pending_invoices():
    """Return a list of invoices. Includes a 'trap' where total != sum of line items."""
    return [
        Invoice(
            id="INV-001", vendor="TechCorp", currency="USD",
            line_items=[LineItem(description="Laptops", amount=5000.0)],
            total_amount=5000.0
        ),
        Invoice(
            id="INV-002", vendor="OfficeSupplies", currency="EUR",
            line_items=[LineItem(description="Desks", amount=12000.0)],
            total_amount=12000.0
        ),
        Invoice( # The Trap (AI Hallucination math error)
            id="INV-003", vendor="ScamCo", currency="USD",
            line_items=[LineItem(description="Services", amount=100.0)],
            total_amount=1000.0 
        )
    ]

@app.post("/api/invoices/{invoice_id}/approve", response_model=ApprovalResult)
def approve_invoice(invoice_id: str):
    """Approve an invoice. Randomly fails to simulate flaky infrastructure."""
    if random.random() < 0.2:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ERP Database Timeout"
        )
    return ApprovalResult(status="APPROVED")
