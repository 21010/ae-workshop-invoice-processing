[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/21010/ae-worshop/tree/main)

# Guided Automation Project: Invoice Processing

Welcome to the hands-on guided project! In this session, you will evolve from traditional RPA script writing to **Automation Engineering**.

## 1. The Business Request (From the Finance Team)

*You have just received the following email from Sarah in the Finance Department:*

> **Subject:** Request for a new Excel Macro / Power Automate script for Invoices
> 
> Hi Automation Team,
> 
> We are drowning in vendor invoices and we really need a bot to help us. Right now, my team spends hours clicking through the ERP portal to approve these. 
> 
> Can you build a Power Automate Desktop script or maybe an Excel macro that logs into the ERP screen, looks at the list of pending invoices, and clicks "Approve" for each one? 
> 
> There are two things the bot needs to check before clicking approve:
> 1. Sometimes the upstream vendor system glitches and the total amount on the invoice doesn't actually match the sum of the individual line items. We need the bot to calculate the math on the screen and make sure it adds up. If it doesn't add up, the bot should skip it so we don't corrupt our ledgers.
> 2. We are only allowed to auto-approve standard invoices. If an invoice is over $10,000, please don't let the bot click approve. Leave those for us to review manually.
> 
> Oh, one last thing: the ERP system is really slow and sometimes the webpage crashes with a "503 Error". If that happens, the bot should just refresh the page and try again.
> 
> Thanks!
> Sarah (Senior Financial Analyst)

---

### The Engineering Reality

Sarah described her problem using a specific, fragile technical solution (a UI-clicking macro). As Automation Engineers, we know that UI automation frequently breaks when a website updates. Instead of building a screen-scraping bot, we will solve her underlying business requirements by building a headless, robust, API-driven Python backend.

### The Manual Process (As-Is)
*Here is how Sarah's team currently processes invoices manually:*

1. Open the Google Chrome browser and navigate to the internal ERP portal.
2. Type in the username and password to log in.
3. Click on the "Finance Dashboard" tab.
4. Click on "Pending Vendor Invoices" to load the grid.
5. For each invoice in the list:
   * Open the Windows Calculator app.
   * Add up every single line item on the screen manually.
   * Check if the calculator total matches the "Total Amount" on the screen (If it doesn't, skip it).
   * Check if the Total Amount is greater than $10,000 (If it is, skip it so the manager can review it).
   * If the math is correct and it is under $10,000, click the green "Approve" button.
6. If the website crashes with a 503 error, hit F5 to refresh, log in again, and find where they left off.

---

## 2. Engineering the Solution (Step-by-Step)

Sarah's manual process is slow, error-prone, and mind-numbing. We are not going to build the fragile screen-scraping macro she asked for. Instead, we are going to build an enterprise-grade, API-driven Python backend that operates invisibly and never breaks when the UI changes.

Your workspace is completely empty (except for this guide and a ERP API running silently in the background on `http://127.0.0.1:8080`). It is time to put on your Automation Engineer hat and build this solution from scratch.

### Step 0: Process Analysis & Architecture Design

<details>
<summary><b>📚 Theory: Business Analysis & Domain-Driven Design (Learn More)</b></summary>

> **1. Understand the Business Domain**
> Business stakeholders often request software by describing a specific technical solution (e.g., "Build a script to click these buttons"). As engineers, our job is to map the actual *Business Domain*. What are the real-world processes, events, and failure conditions?
> 
> **2. Establish a Ubiquitous Language**
> The most critical rule of Domain-Driven Design (DDD) is establishing a "Ubiquitous Language" - a shared vocabulary between developers and business experts. If the business talks about "Invoices", "Line Items", and "Approval Thresholds", those exact terms must become the core components (models) in our code.
> 
> **3. Define Bounded Contexts & Entities**
> We must isolate our specific area of responsibility (the Bounded Context). Inside this context, we define our Entities (objects with a distinct identity, like an Invoice) and Value Objects (attributes without an identity, like a Line Item amount). 
> 
> **4. Hexagonal Architecture (Ports and Adapters)**
> DDD separates the core business rules from the technical implementation. The mathematical validation of an Invoice does not care if the data came from a REST API or a database. By cleanly separating the "Domain" (business rules) from the "Infrastructure" (technical details like HTTP requests), we build software that can survive technological shifts.

</details>

**🔨 Implementation Steps:**

Before writing code, we must translate Sarah's request into a strict DDD engineering plan:

1. **Understand the Domain & Identify Risks:**
   * *The Core Workflow:* Acquire pending invoices, verify data integrity (math validation), apply business rules ($10,000 threshold), and execute the approval.
   * *Domain Risks:* The upstream system occasionally sends corrupted payloads where the math does not add up. *Mitigation:* We will implement strict data validation at the absolute boundary of our application to reject bad payloads before they ever reach our core logic.
   * *Infrastructure Risks:* The target ERP API is known to drop connections and throw 503 errors. *Mitigation:* We will isolate all API calls and wrap them in an exponential backoff retry loop.

2. **Define the Ubiquitous Language & Entities:**
   Based on Sarah's email, our Domain models must explicitly represent an `Invoice` (Entity) which contains multiple `LineItem`s (Value Objects).

3. **Map the Architecture Layers:**
   We will not write a single, procedural script. Instead, we divide the responsibilities:
   * **The Infrastructure Layer:** This layer is solely responsible for talking to the unstable external world. It handles the HTTP requests and the retry loops.
   * **The Domain Layer:** This layer is strictly isolated from the network. It contains our `Invoice` models and the validation rules. 
   * **The Application Layer:** This is the orchestrator (or Use Case). It fetches data from the Infrastructure, passes it to the Domain for validation, applies the $10,000 threshold rule, and tells the Infrastructure to approve the valid invoices.

4. **Design the Automated Workflow (To-Be)**
   Instead of opening Chrome and calculating math manually, our API-driven Python backend will execute the following architecture:

   ```mermaid
   flowchart LR
       Start((Trigger: task.py)) --> Fetch(Infrastructure: GET /api/invoices)
       Fetch --> Loop{Application: More Invoices?}
       Loop -- Yes --> Validate{Domain: Pydantic Validation}
       Loop -- No --> End((End: Complete))
       Validate -- Math Error --> Reject(Application: Log Error & Skip)
       Validate -- Valid --> CheckAmount{Application: Is Total > $10,000?}
       CheckAmount -- Yes --> Manual(Application: Log Warning & Skip)
       CheckAmount -- No --> Approve(Infrastructure: POST /api/approve)
       Reject --> Next(Next Invoice)
       Manual --> Next
       Approve --> Next
       Next --> Loop
   ```

### Step 1: Project Initialization

<details>
<summary><b>📚 Theory: Reproducible Environments & The `uv` Package Manager (Learn More)</b></summary>

> **1. The Modern Standard (PEP 621)**
>
> In legacy Python, developers used `requirements.txt` and struggled with "it works on my machine" bugs. Modern Python engineering demands isolated, reproducible environments. The industry standard is now **PEP 621**, which centralizes all project configuration and dependencies into a single file called `pyproject.toml`.
> 
> **2. Introducing `uv`**
> To manage these modern projects, we use `uv` - an fast package manager built in Rust by Astral. It replaces `pip`, `venv`, `poetry`, and `pip-tools` entirely.
> 
> * **Installation:** 
>   * *Windows:* `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
>   * *macOS/Linux:* `curl -LsSf https://astral.sh/uv/install.sh | sh`
> * **How it manages virtual environments:** When you run commands like `uv run`, it automatically and implicitly creates an isolated `.venv` folder. It resolves dependencies in milliseconds and uses a global cache so you never download the same package twice.
> * **Security (Audit Feature):** `uv` has built-in malware checking to prevent supply chain attacks. You can enable it via environment variables: `export UV_PREVIEW_FEATURES=malware-check` (Linux) or `$env:UV_PREVIEW_FEATURES="malware-check"` (Windows).
> 
> **3. Basic `uv` Commands**
> 
> * `uv init` - Initializes a new project and creates the `pyproject.toml`.
> * `uv add <package>` - Installs a package and adds it to the production dependencies.
> * `uv add --dev <package>` - Installs a package only for local development/testing.
> * `uv run <command>` - Automatically executes a command *inside* the isolated virtual environment. You never have to manually run `source .venv/bin/activate` again!
> 
> **4. Anatomy of `pyproject.toml`**
> Here is how a modern, best-practice configuration looks:
> 
> * `[project]`: Defines the project metadata (name, version, python version requirement).
> * `dependencies`: An array of required production libraries (e.g., `requests`, `pydantic`). These are what gets shipped to the server.
> * `[dependency-groups]`: Defines the `dev` array for local tools (e.g., `pytest`, `ruff`). By cleanly separating dev tools, we ensure our production Docker containers remain small, fast, and secure.

</details>

**🔨 Implementation Steps:**

1. **Initialize the project in the terminal:**
   
   ```bash
   uv init
   ```
2. **Add production dependencies:**
   *Why these?* We need `pydantic` because it is the modern industry standard for validating JSON data structures. We need `requests` to talk to the HTTP API, and `tenacity` to handle retry loops when the API crashes.
   
   ```bash
   uv add pydantic requests tenacity
   ```
3. **Add development dependencies:**
   *Why `--dev`?* Tools like `pytest` (for testing) and `ruff` (for formatting) are critical for building the bot, but they don't need to be packaged into the final production server. Keeping them separate makes our bot faster and more secure.
   
   ```bash
   uv add --dev pytest ruff bandit pyrefly pre-commit
   ```
4. **Analyze the Configuration:**
   Open the newly generated `pyproject.toml` file. Notice how `uv` automatically tracked your dependencies. This file is the single source of truth for your bot's environment!

### Step 2: Code Quality & Pre-commit

<details>
<summary><b>📚 Theory: Shift-Left Security (Learn More)</b></summary>

> We want to automatically format our code and catch security issues before they are ever committed to Git. This guarantees that bad or vulnerable code never enters the repository.

</details>

**🔨 Implementation Steps:**

1. **Initialize Git and enforce the 'main' branch standard:**
   
   ```bash
   git init
   git branch -M main
   ```

2. **Setup pre-commit using our local tools:**
   Create a file named `.pre-commit-config.yaml` in the root directory. *Notice how we configure the hooks to execute locally via `uv run` to guarantee they use our exact environment versions.*
   
   <details>
   <summary><b>💡 Click here to copy the pre-commit configuration</b></summary>
   
   ```yaml
   repos:
     - repo: local
       hooks:
         - id: ruff
           name: ruff
           entry: uv run ruff check --fix
           language: system
           types: [python]
           require_serial: true
         - id: ruff-format
           name: ruff-format
           entry: uv run ruff format
           language: system
           types: [python]
         - id: bandit
           name: bandit
           entry: uv run bandit -c pyproject.toml -r .
           language: system
           types: [python]
         - id: pyrefly
           name: pyrefly
           entry: uv run pyrefly
           language: system
           types: [python]
     - repo: https://github.com/trufflesecurity/trufflehog
       rev: v3.73.0
       hooks:
         - id: trufflehog
   ```
   
   </details>

3. **Install the hooks:** `uv run pre-commit install`

### Step 3: Project Structure (DDD)

<details>
<summary><b>📚 Theory: Domain-Driven Isolation (Learn More)</b></summary>

> Based on our Step 0 design, we must construct the architecture that isolates our core business rules (Domain) from the unpredictable outside world (unstable APIs). This guarantees our code remains clean and testable.

</details>

**🔨 Implementation Steps:**

1. **Create the directories (Windows PowerShell):**
   
   ```powershell
   New-Item -ItemType Directory -Force -Path src/domain, src/application, src/infrastructure, tests/unit, tests/integration
   ```

2. **Make them Python packages:**
   Create an empty `__init__.py` file inside each folder. 
   *Why?* Without this file, Python sees a normal folder, not a module. By adding `__init__.py`, Python can import code across files. (Smart trick: You can also use this file to explicitly expose public classes, so imports look like `from src.domain import Invoice` instead of digging deep into sub-files!).
   
   ```powershell
   New-Item -ItemType File -Force -Path src/domain/__init__.py, src/application/__init__.py, src/infrastructure/__init__.py, tests/__init__.py
   ```

3. **Verify the Architecture Structure:**
   By the end of this workshop, your project tree will look exactly like this:
   
   ```text
   📦 project-root
   ┣ 📂 src/
   ┃ ┣ 📂 domain/         # Step 4: Core business logic and data validation (Pydantic)
   ┃ ┃ ┗ 📜 __init__.py
   ┃ ┣ 📂 infrastructure/ # Step 5: External API clients and network resilience (Tenacity)
   ┃ ┃ ┗ 📜 __init__.py
   ┃ ┗ 📂 application/    # Step 6: The orchestrator that glues Domain & Infrastructure together
   ┃   ┗ 📜 __init__.py
   ┣ 📂 tests/
   ┃ ┣ 📂 unit/           # Fast tests for business logic (no network required)
   ┃ ┃ ┗ 📜 __init__.py
   ┃ ┗ 📂 integration/    # Complex tests using Mock APIs to prove the orchestrator works
   ┃   ┗ 📜 __init__.py
   ┣ 📜 .pre-commit-config.yaml # Step 2: Security and formatting guardrails
   ┗ 📜 pyproject.toml          # Step 1: Environment and dependency definitions
   ```

### Step 4: Building the Domain (Data Validation)

<details>
<summary><b>📚 Theory: Defensive Data Modeling (Learn More)</b></summary>

> Data modeling is arguably the most important step in automation. Generic dictionaries allow corrupted data to infiltrate the system. By defining the shape of an Invoice using `pydantic`, any bad payloads from the upstream system will be caught and destroyed immediately at the boundary.

</details>

**🔨 Implementation Steps:**

1. **Create `src/domain/models.py`:**
   *Challenge: Try to write the `LineItem` and `Invoice` Pydantic models yourself! Use the `@model_validator(mode="after")` decorator to sum the line items and raise a `ValueError` if the math is wrong.*
   
   <details>
   <summary><b>💡 Click here to show the solution snippet</b></summary>
   
   ```python
   from pydantic import BaseModel, model_validator
   
   class LineItem(BaseModel):
       description: str
       amount: float
   
   class Invoice(BaseModel):
       id: str
       vendor: str
       currency: str
       line_items: list[LineItem]
       total_amount: float
   
       @model_validator(mode="after")
       def check_math(self):
           calculated_total = sum(item.amount for item in self.line_items)
           if calculated_total != self.total_amount:
               raise ValueError(f"Math Error! Total {self.total_amount} != Sum {calculated_total}")
           return self
   ```
   
   </details>

2. **Write Unit Tests (`tests/unit/test_domain.py`):**
   *Challenge: Write a Pytest function labeled `@pytest.mark.unit`. Create an invoice with bad math and use `with pytest.raises(ValueError):` to prove your validation catches it!*
   
   <details>
   <summary><b>💡 Click here to show the solution snippet</b></summary>
   
   ```python
   import pytest
   from src.domain.models import Invoice, LineItem
   
   @pytest.mark.unit
   def test_bad_math_is_rejected():
       with pytest.raises(ValueError):
           Invoice(
               id="1", vendor="A", currency="USD",
               line_items=[LineItem(description="Item", amount=50)],
               total_amount=9000  # Data Corruption!
           )
   ```
   
   </details>

3. **Run the test:** `uv run pytest -m unit`

### Step 5: Infrastructure (The Unstable External Services)

<details>
<summary><b>📚 Theory: 12-Factor Backing Services & Resilience (Learn More)</b></summary>

> In Domain-Driven Design, the Infrastructure layer is the absolute edge of your application. It is the only place allowed to talk to the unpredictable outside world (APIs, databases, file systems). 
> 
> In Step 0, we identified that the target ERP system is unstable (throws 503 errors). The 12-Factor App methodology states we must treat backing services robustly. Instead of writing custom retry loops, we will use the `tenacity` library to automatically handle network drops using exponential backoff.

</details>

**🔨 Implementation Steps:**

1. **Create `src/infrastructure/api_client.py`:**
   *Challenge: Create a `FastAPIClient` class. Write a GET method to fetch `http://127.0.0.1:8080/api/invoices/pending`. Notice how it immediately converts the raw JSON into the `Invoice` Pydantic model you built in Step 4! Then, write a POST method to approve an invoice, decorated with `@retry` from `tenacity`.*
   
   <details>
   <summary><b>💡 Click here to show the solution snippet</b></summary>
   
   ```python
   import requests
   from tenacity import retry, stop_after_attempt, wait_exponential
   from src.domain.models import Invoice
   
   class FastAPIClient:
       def fetch_pending_invoices(self) -> list[Invoice]:
           response = requests.get("http://127.0.0.1:8080/api/invoices/pending")
           response.raise_for_status()
           return [Invoice(**item) for item in response.json()]
   
       @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
       def approve_invoice(self, invoice_id: str) -> bool:
           response = requests.post(f"http://127.0.0.1:8080/api/invoices/{invoice_id}/approve")
           response.raise_for_status()
           return True
   ```
   
   </details>

### Step 6: Application Layer (The Orchestrator)

<details>
<summary><b>📚 Theory: SOLID Dependency Inversion (Learn More)</b></summary>

> The Application Layer is the "Conductor" of the orchestra. It doesn't know *how* to validate math (the Domain does that), and it doesn't know *how* to make HTTP requests (the Infrastructure does that). It simply orchestrates the flow and applies high-level business rules (like our $10,000 threshold limit).
> 
> The 'D' in SOLID stands for **Dependency Inversion**. If our orchestrator imports the `FastAPIClient` directly, they become tightly coupled. If we ever migrate to SAP or Salesforce, the orchestrator breaks. Instead, we define a `Protocol` (an interface). The orchestrator only knows it needs *something* that can fetch and approve invoices.

</details>

**🔨 Implementation Steps:**

1. **Create `src/application/processor.py`:**
   *Challenge: Create an `InvoiceProcessor`. Define an `InvoiceAPIClient(Protocol)` rather than hardcoding the FastAPI client. Write a `run()` method that loops through the invoices and only approves them if they are under $10,000.*
   
   <details>
   <summary><b>💡 Click here to show the solution snippet</b></summary>
   
   ```python
   import logging
   from src.domain.models import Invoice
   from typing import Protocol
   
   logger = logging.getLogger(__name__)
   
   # SOLID: Dependency Inversion. We don't care HOW the API works, just that it has these methods.
   class InvoiceAPIClient(Protocol):
       def fetch_pending_invoices(self) -> list[Invoice]: ...
       def approve_invoice(self, invoice_id: str) -> bool: ...
   
   class InvoiceProcessor:
       def __init__(self, api_client: InvoiceAPIClient):
           self.api_client = api_client
           self.threshold = 10000.0
   
       def run(self):
           invoices = self.api_client.fetch_pending_invoices()
           for inv in invoices:
               if inv.total_amount > self.threshold:
                   logger.warning(f"Manual Review required for {inv.id}")
               else:
                   self.api_client.approve_invoice(inv.id)
                   logger.info(f"Approved {inv.id}")
   ```
   
   </details>

### Step 7: Integration Testing (No Network Required!)

<details>
<summary><b>📚 Theory: CUPID Testability & Mocking (Learn More)</b></summary>

> Testing automation bots is difficult because they usually require logging into live UI systems. Because we engineered a clean DDD architecture with Dependency Inversion, we have achieved **Testability** (CUPID principles). We can test our entire business logic without ever touching the network!
> 
> Because our `InvoiceProcessor` in Step 6 only requires an object matching the `InvoiceAPIClient(Protocol)`, we can pass it a fake "Mock" client that stores data in memory instead of making real HTTP requests. 

</details>

**🔨 Implementation Steps:**

1. **Create `tests/integration/test_processor.py`:**
   *Challenge: Write a `MockAPIClient` class that returns fake memory invoices instead of hitting the network. Pass it into the `InvoiceProcessor` and assert that an invoice over $10,000 is NOT approved!*
   
   <details>
   <summary><b>💡 Click here to show the solution snippet</b></summary>
   
   ```python
   import pytest
   from src.application.processor import InvoiceProcessor
   from src.domain.models import Invoice, LineItem
   
   # A fake API client for testing!
   class MockAPIClient:
       def __init__(self):
           self.approved_invoices = []
   
       def fetch_pending_invoices(self):
           return [
               Invoice(id="CHEAP-1", vendor="A", currency="USD", line_items=[LineItem(description="X", amount=5)], total_amount=5),
               Invoice(id="EXPENSIVE-1", vendor="A", currency="USD", line_items=[LineItem(description="X", amount=20000)], total_amount=20000)
           ]
   
       def approve_invoice(self, invoice_id: str):
           self.approved_invoices.append(invoice_id)
           return True
   
   @pytest.mark.integration
   def test_processor_approves_under_threshold_only():
       client = MockAPIClient()
       processor = InvoiceProcessor(client)
       processor.run()
   
       # It should approve CHEAP-1, but block EXPENSIVE-1
       assert "CHEAP-1" in client.approved_invoices
       assert "EXPENSIVE-1" not in client.approved_invoices
   ```
   
   </details>

2. **Run the integration test:** 
   Execute `uv run pytest -m integration` in your terminal. 
   *(Note: If Pytest throws a yellow warning about "unknown markers", try creating a `pytest.ini` file in the root directory to officially register them!)*

### Step 8: The Entry Point (Running the Bot)

<details>
<summary><b>📚 Theory: Dependency Injection (Learn More)</b></summary>

> We have built our architecture, but we need a lightweight trigger to actually start the process. In traditional scripts, everything is jammed into one massive file. In our DDD architecture, the entry point simply wires the layers together using **Dependency Injection** and hits "Go".

</details>

**🔨 Implementation Steps:**

1. **Create `task.py` in the root directory:**
   *Challenge: Create the main execution file. Import the real `FastAPIClient` and the `InvoiceProcessor`. Instantiate the client, pass it into the processor, and call `run()`!*
   
   <details>
   <summary><b>💡 Click here to show the solution snippet</b></summary>
   
   ```python
   import logging
   from src.infrastructure.api_client import FastAPIClient
   from src.application.processor import InvoiceProcessor
   
   # Configure logging so we can see the output in the terminal
   logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
   
   def main():
       print("Starting Invoice Processing Bot...")
   
       # 1. Initialize the real Infrastructure client
       api_client = FastAPIClient()
   
       # 2. Inject it into the Application orchestrator (Dependency Injection)
       processor = InvoiceProcessor(api_client)
   
       # 3. Execute the business logic
       processor.run()
   
       print("Processing Complete!")
   
   if __name__ == "__main__":
       main()
   ```
   
   </details>

2. **Execute your completed bot:** 
   Run the process using `uv` to ensure it executes inside your isolated environment:
   
   ```bash
   uv run task.py
   ```

### Step 9: Observability (Replacing the Legacy log.html)

<details>
<summary><b>📚 Theory: 12-Factor Telemetry Streams (Learn More)</b></summary>

> Legacy RPA frameworks generate static `log.html` or `stdout.log` files on the local hard drive. The **12-Factor App** principles state this is an anti-pattern in the cloud because containers are ephemeral (they get deleted when finished). 
> 
> Instead, modern applications output **Structured JSON Logs** to the terminal stream. Log routers (like Datadog, Splunk, or Promtail) capture this stream automatically.

</details>

**🔨 Implementation Steps:**

1. **Add the modern logging library:**
   
   ```bash
   uv add structlog
   ```

2. **Update your Orchestrator (`src/application/processor.py`):**
   *Challenge: Replace the standard `logging` with `structlog`. Notice how we `bind()` variables like `invoice_id` to the logger so every log line automatically includes that context in the JSON payload!*
   
   <details>
   <summary><b>💡 Click here to show the solution snippet</b></summary>
   
   ```python
   import structlog
   from src.domain.models import Invoice
   from typing import Protocol
   
   logger = structlog.get_logger()
   
   class InvoiceAPIClient(Protocol):
       def fetch_pending_invoices(self) -> list[Invoice]: ...
       def approve_invoice(self, invoice_id: str) -> bool: ...
   
   class InvoiceProcessor:
       def __init__(self, api_client: InvoiceAPIClient):
           self.api_client = api_client
           self.threshold = 10000.0
   
       def run(self):
           invoices = self.api_client.fetch_pending_invoices()
           logger.info("fetched_invoices", count=len(invoices))
   
           for inv in invoices:
               # Bind the ID to the logger so it attaches to all subsequent logs!
               log = logger.bind(invoice_id=inv.id)
               log.info("processing_invoice")
   
               if inv.total_amount > self.threshold:
                   log.warning("manual_review_required", amount=inv.total_amount)
               else:
                   self.api_client.approve_invoice(inv.id)
                   log.info("invoice_approved")
   ```
   
   </details>

3. **Update your Entry Point (`task.py`):**
   *Challenge: Configure `structlog` to output as JSON with an ISO timestamp.*
   
   <details>
   <summary><b>💡 Click here to show the solution snippet</b></summary>
   
   ```python
   import structlog
   from src.infrastructure.api_client import FastAPIClient
   from src.application.processor import InvoiceProcessor
   
   def main():
       # Configure the 12-Factor JSON log stream
       structlog.configure(
           processors=[
               structlog.processors.TimeStamper(fmt="iso"),
               structlog.processors.JSONRenderer()
           ]
       )
   
       logger = structlog.get_logger()
       logger.info("bot_starting")
   
       api_client = FastAPIClient()
       processor = InvoiceProcessor(api_client)
       processor.run()
   
       logger.info("bot_finished")
   
   if __name__ == "__main__":
       main()
   ```
   
   </details>

4. **Run the bot:**
   Execute `uv run task.py`. Look at the terminal! You will see machine-readable JSON logs that cloud dashboards can query.

### Step 10: Enterprise Deployment (Azure Architecture)

Now that your bot is engineered, how do you deploy it to production? Because we followed the **12-Factor App** principles, this Python codebase is 100% portable. Here are the 4 standard ways to deploy this in a Microsoft Azure ecosystem:

**1. On-Premises Server (Hybrid Cloud)**

* **How:** If the ERP system is locked behind a strict corporate firewall, run the bot on a local Windows Server using Task Scheduler (`uv run task.py`).
* **Telemetry:** Install the `azure-monitor-opentelemetry` package and add `configure_azure_monitor()` to your `task.py`. The bot will stream its structured JSON logs out of your private network directly into **Azure Application Insights**.

**2. Azure Container Apps or AKS (Cloud Native)**

* **How:** Package the repository into a Docker container and deploy it to Azure Container Apps as a background job.
* **Telemetry:** The Azure infrastructure automatically captures the JSON `stdout` terminal stream we built in Step 9. You get Application Insights integration with **zero code changes**.

**3. Azure Functions (Serverless)**

* **How:** Wrap the `processor.run()` logic inside a Time-Triggered Azure Function (e.g., scheduled to run every 15 minutes). 
* **Pros:** You only pay for the exact milliseconds the bot is processing invoices. If there are no invoices, it costs $0.
* **Cons:** Serverless functions have execution time limits (usually 10 minutes). If your bot needs to process 10,000 invoices in a single run, you would need to use Azure Durable Functions.

**4. Azure Logic Apps (Low-Code Orchestration)**

* **How:** Sometimes the upstream ERP system requires complex, legacy XML SOAP authentication. Let a Logic App handle the complex trigger and authentication steps. The Logic App can fetch the data and then trigger your Python bot (hosted in an Azure Function) just to execute the heavy Pydantic math validation. 

**Conclusion:** The automation project is complete.
