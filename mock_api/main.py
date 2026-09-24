import random
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(
    title="ERP REST API",
    description="Corporate ERP System. Interactive Swagger documentation available at /docs",
    version="1.0.0"
)

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

VENDORS = ["TechCorp", "OfficeSupplies", "GlobalLogistics", "CloudServices", "ScamCo", "ConsultingGroup"]

def generate_invoices(count: int = 25):
    invoices = []
    for i in range(1, count + 1):
        vendor = random.choice(VENDORS)
        
        # Generate 1 to 4 line items
        num_items = random.randint(1, 4)
        line_items = []
        actual_sum = 0.0
        
        for j in range(num_items):
            # Amount between 100 and 6000
            amount = round(random.uniform(100.0, 6000.0), 2)
            line_items.append(LineItem(description=f"Item {j+1}", amount=amount))
            actual_sum += amount
            
        total_amount = round(actual_sum, 2)
        
        # 15% chance to corrupt the math (The Data Trap)
        if random.random() < 0.15:
            total_amount = round(total_amount + random.uniform(100.0, 5000.0), 2)
            
        invoices.append(Invoice(
            id=f"INV-{str(i).zfill(4)}",
            vendor=vendor,
            currency="USD",
            line_items=line_items,
            total_amount=total_amount
        ))
    return invoices

# Generate a static pool so it stays consistent per server restart
CACHED_INVOICES = generate_invoices(25)

@app.get("/api/invoices/pending", response_model=list[Invoice])
def get_pending_invoices():
    """Return a list of pending invoices. Includes random data corruption traps."""
    return CACHED_INVOICES

@app.post("/api/invoices/{invoice_id}/approve", response_model=ApprovalResult)
def approve_invoice(invoice_id: str):
    """Approve an invoice. Randomly fails (503) to simulate unstable legacy infrastructure."""
    if random.random() < 0.2:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ERP Database Timeout"
        )
    return ApprovalResult(status="APPROVED")
