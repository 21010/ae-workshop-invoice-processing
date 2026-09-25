# Guided Automation Project: Invoice Processing

Welcome to the hands-on guided project! In this session, you will evolve from traditional RPA script writing to **Automation Engineering**.

## Prerequisite: Get Your Own Copy of this Repository

> Before you start writing code, you need your own copy of this project so you can save your work and earn your certificate!

[![Fork Repository](https://img.shields.io/badge/1._Click_Here_To_Fork_This_Repository-black?style=for-the-badge&logo=github)](https://github.com/21010/ae-workshop-invoice-processing/fork)

1. Click the **Fork** button above to create a copy in your personal GitHub account.
2. Navigate to *your* new repository.
3. Click the green **`<> Code`** button on your repository, switch to the **Codespaces** tab, and click **Create codespace on main**. *(Do not create a Codespace on the original repository!)*
4. When you finish the masterclass and push your code, GitHub Actions will automatically grade your work and award a certificate directly to your repository!

## The Business Request (From the Finance Team)

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
>
> 1. Sometimes the upstream vendor system glitches and the total amount on the invoice doesn't actually match the sum of the individual line items. We need the bot to calculate the math on the screen and make sure it adds up. If it doesn't add up, the bot should skip it so we don't corrupt our ledgers.
> 2. We are only allowed to auto-approve standard invoices. If an invoice is over $10,000, please don't let the bot click approve. Leave those for us to review manually.
>
> Oh, one last thing: the ERP system is really slow and sometimes the webpage crashes with a "503 Error". If that happens, the bot should just refresh the page and try again.
>
> Thanks!
> Sarah (Senior Financial Analyst)

---

### The Engineering Reality

Sarah described her problem using a specific, fragile technical solution (a UI-clicking, a macro). As Automation Engineers, we know that UI automation frequently breaks when a website updates. Instead of building a screen-scraping bot, we will solve her underlying business requirements by building a headless, robust, API-driven Python backend.

> **Caveat:** API-driven Python is strictly better *when an API exists*. For legacy mainframe green-screens, SAP GUI without BAPI, or vendor portals lacking REST endpoints, traditional RPA (UI automation) remains the correct architectural choice.\n\n### The Manual Process (As-Is)
*Here is how Sarah's team currently processes invoices manually:*

1. Open the Google Chrome browser and navigate to the internal ERP portal.
2. Type in the username and password to log in.
3. Click on the "Finance Dashboard" tab.
4. Click on "Pending Vendor Invoices" to load the grid.
5. For each invoice in the list:
   * Open the Windows Calculator app *(Note: This step is deliberately exaggerated for teaching purposes)*.
   * Add up every single line item on the screen manually.
   * Check if the calculator total matches the "Total Amount" on the screen (If it doesn't, skip it).
   * Check if the Total Amount is greater than $10,000 (If it is, skip it so the manager can review it). *(Note: A real AP control set would also include PO three-way match and vendor whitelisting)*
   * If the math is correct and it is under $10,000, click the green "Approve" button.
6. If the website crashes with a 503 error, hit F5 to refresh, log in again, and find where they left off.

---

## Engineering the Solution (Step-by-Step)

Sarah's manual process is slow, error-prone, and mind-numbing. We are not going to build the fragile screen-scraping macro she asked for. Instead, we are going to build an enterprise-grade, API-driven Python backend that operates invisibly and never breaks when the UI changes.

Your workspace is completely empty (except for this guide and a ERP API running silently in the background on `http://127.0.0.1:8080`). It is time to put on your Automation Engineer hat and build this solution from scratch.

### Process Analysis & Architecture Design

<details>
<summary><b>📚 Click here to learn more about: Business Analysis & Domain-Driven Design</b></summary>

> **1. Understand the Business Domain**
>
> Business stakeholders often request software by describing a specific technical solution (e.g., "Build a script to click these buttons"). As engineers, our job is to map the actual *Business Domain*. What are the real-world processes, events, and failure conditions?
>
> **2. Establish a Ubiquitous Language**
>
> The most critical rule of Domain-Driven Design (DDD) is establishing a "Ubiquitous Language" - a shared vocabulary between developers and business experts. If the business talks about "Invoices", "Line Items", and "Approval Thresholds", those exact terms must become the core components (models) in our code.
>
> **3. Define Bounded Contexts & Entities**
>
> We must isolate our specific area of responsibility (the Bounded Context). Inside this context, we define our Entities (objects with a distinct identity, like an Invoice) and Value Objects (attributes without an identity, like a Line Item amount).
>
> **4. Hexagonal Architecture (Ports and Adapters)**
>
> DDD separates the core business rules from the technical implementation. The mathematical validation of an Invoice does not care if the data came from a REST API or a database. By separating the "Domain" (business rules) from the "Infrastructure" (technical details like HTTP requests), we build software that can survive technological shifts.
> Ports and Adapters (also known as Hexagonal Architecture) is a pattern that isolates your core business logic (the hexagon) from outside concerns. A "Port" is the interface your application exposes (e.g., fetching an invoice), while an "Adapter" is the technical implementation that plugs into that port (e.g., a REST API client or a SQL database query). This decouples your core logic from external dependencies, making the system highly testable and resilient to technology changes.

</details>

---

Before writing code, we must translate Sarah's request into a strict DDD engineering plan:

#### Understand the Domain & Identify Risks

##### The Core Workflow

Acquire pending invoices, verify data integrity (math validation), apply business rules ($10,000 threshold), and execute the approval.

   ```mermaid
   flowchart TD
       A((Start)) --> B(Log into ERP Portal)
       B --> C(Navigate to Pending Invoices)
       C --> D{Invoices Remain?}
       D -- Yes --> E(Calculate Sum of Line Items)
       E --> F{Sum == Total?}
       F -- No --> G(Skip Invoice - Corrupted Data)
       F -- Yes --> H{Total < $10k?}
       H -- No --> I(Skip for Manual Review)
       H -- Yes --> J(Click Approve)
       G --> D
       I --> D
       J --> D
       D -- No --> K((End))
   ```

##### Risks

| ID | Type | Risk | Mitigation |
| :- | :--- | :--- | :--------- |
| R-01 | Domain Risk | The upstream system occasionally sends corrupted payloads where the math does not add up. | We will implement strict data validation at the absolute boundary of our application to reject bad payloads before they ever reach our core logic. |
| R-02 | Infrastructure Risk | The target ERP API is known to drop connections and throw 503 errors. | We will isolate all API calls and wrap them in an exponential backoff retry loop. |

#### Define the Ubiquitous Language & Entities

Based on Sarah's email, our Domain models must explicitly represent an `Invoice` (Entity) which contains multiple `LineItem`s (Value Objects).

In addition to the `Invoice` and `LineItem`, we also define `Vendor` and `Currency` as important attributes of the domain. It's crucial that our internal Python attributes (e.g., `total_amount`) exactly map to the business vocabulary, avoiding generic or misleading terms.

#### Map the Architecture Layers

We will not write a single, procedural script. Instead, we divide the responsibilities:

* **The Infrastructure Layer:** This layer is solely responsible for talking to the unstable external world. It handles the HTTP requests and the retry loops.
* **The Domain Layer:** This layer is strictly isolated from the network. It contains our `Invoice` models and the validation rules.
* **The Application Layer:** This is the orchestrator (or Use Case). It fetches data from the Infrastructure, passes it to the Domain for validation, applies the $10,000 threshold rule, and tells the Infrastructure to approve the valid invoices.

#### Design the Automated Workflow (To-Be)

Instead of opening Chrome and calculating math manually, our API-driven Python backend will execute the following architecture:

   ```mermaid
   flowchart LR
       Start((Process Triggered)) --> Fetch(Fetch Pending Invoices)
       Fetch --> Loop{Invoices Remain?}
       Loop -- Yes --> Validate{Is Math Valid?}
       Loop -- No --> End((Process Complete))
       Validate -- No --> Reject(Reject as Corrupted)
       Validate -- Yes --> CheckAmount{Amount > $10k?}
       CheckAmount -- Yes --> Manual(Flag for Manual Review)
       CheckAmount -- No --> Approve(Auto-Approve Invoice)
       Reject --> Next(Next Invoice)
       Manual --> Next
       Approve --> Next
       Next --> Loop
   ```

This flowchart accurately models the target state. We use this behavioral flow diagram rather than a static UML class diagram because our primary goal is to map the orchestration of the workflow and the business rules, rather than purely focusing on object inheritance.

### Project Initialization

<details>
<summary>
    <b>📚 Click here to learn more about: Reproducible Environments & The `uv` Package Manager</b>
</summary>

> **1. The Modern Standard (PEP 621)**
>
> In legacy Python, developers used `requirements.txt` and struggled with "it works on my machine" bugs. Modern Python engineering demands isolated, reproducible environments. The industry standard is now **PEP 621**, which centralizes all project configuration and dependencies into a single file called `pyproject.toml`.
>
> **2. Introducing `uv`**
>
> To manage these modern projects, we use `uv` - a fast package manager built in Rust by Astral. It replaces `pip`, `venv`, `poetry`, and `pip-tools` entirely.
>
> **Installation:**
>
> * *Windows:* `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
> * *macOS/Linux:* `curl -LsSf https://astral.sh/uv/install.sh | sh`
>
> **How it manages virtual environments?**
>
> When you run commands like `uv run`, it automatically and implicitly creates an isolated `.venv` folder. It resolves dependencies in milliseconds and uses a global cache so you never download the same package twice.
>
> **Security (Audit Feature)**
>
> `uv` has built-in malware checking to prevent supply chain attacks. You can enable it via environment variables: `export UV_MALWARE_CHECK=1` (Linux) or `$env:UV_MALWARE_CHECK="1"` (Windows).
>
> **3. Basic `uv` Commands**
>
> * `uv init` - Initializes a new project and creates the `pyproject.toml`.
> * `uv add <package>` - Installs a package and adds it to the production dependencies.
> * `uv add --dev <package>` - Installs a package only for local development/testing.
> * `uv run <command>` - Automatically executes a command *inside* the isolated virtual environment. You never have to manually run `source .venv/bin/activate` again!
>
> **4. Anatomy of `pyproject.toml`**
>
> Here is how a modern, best-practice configuration looks:
>
> * `[project]`: Defines the project metadata (name, version, python version requirement).
> * `dependencies`: An array of required production libraries (e.g., `requests`, `pydantic`). These are what gets shipped to the server.
> * `[dependency-groups]`: Defines the `dev` array for local tools (e.g., `pytest`, `ruff`). By cleanly separating dev tools, we ensure our production Docker containers remain small, fast, and secure.
> * `[build-system]`: Tells packaging tools how to build your project (e.g., using `hatchling` or `setuptools`). By centralizing this in `pyproject.toml`, Python standardizes project builds and eliminates the need for legacy `setup.py` scripts.
> * `[project.scripts]`: Allows you to define command-line entry points for your bot, making it executable from anywhere in the terminal.

</details>

---

With our architecture mapped out on the whiteboard, it is time to lay the technical foundation. In the past, you might have written a simple `requirements.txt` file or relied on proprietary RPA wrappers like `rcc` (Robocorp).

Today, you are going to initialize a strict, reproducible, and open-source environment using `uv`. We will explicitly define our production dependencies (what the bot needs to run) and our development dependencies (what we need to build it securely).

#### Update `uv`

   It is a best practice to ensure you are running the latest version of `uv`. Because `uv` is heavily optimized and frequently updated with new features and security patches, running `uv self update` ensures you have the most stable release before scaffolding a new project.

   ```bash
   uv self update
   ```

#### Initialize the project in the terminal

This command creates the core `pyproject.toml` file, which is the modern standard for Python configuration.

```bash
uv init --no-package --python 3.12
```

#### Add production dependencies

*Connecting to the Business Case:* We need `pydantic` to rigorously validate the math on Sarah's invoices (our Domain), `requests` to fetch the data (our Infrastructure), and `tenacity` to automatically handle the 503 network crashes she complained about.

```bash
uv add pydantic requests tenacity
```

#### Add development dependencies

*Why `--dev`?* Tools like `pytest` (for testing) and `ruff` (for formatting) are critical for building the bot locally, but they do not need to be shipped to the final production server. By explicitly keeping them separate, we ensure our production Docker container remains extremely small and secure.

```bash
uv add --dev pytest ruff bandit pyrefly pre-commit trufflehog
```

#### Analyze the Configuration

Open the newly generated `pyproject.toml` file in your editor. Notice how `uv` automatically tracked your dependencies and separated them into production vs. development arrays. This single file is now the source of truth for your bot's entire environment!

### Building Automated Security Guardrails

<details>
<summary><b>📚 Click here to learn more about : Shift-Left Security & Tooling</b></summary>

> **1. The Problem with Legacy Scripts**
>
> In legacy RPA and scripting teams, code is often copy-pasted, poorly formatted, and deployed without security reviews. If a developer accidentally hardcodes Sarah's ERP password into a script and uploads it to GitHub, the entire company could be compromised.
>
> **2. Shift-Left Security & Pre-commit Mechanics**
>
> Modern engineering relies on **Shift-Left Security**, catching errors and security flaws as early as possible in the development lifecycle (shifting "left" on the timeline). We enforce this using a framework called `pre-commit`.
>
> When you type `git commit`, Git pauses and hands control to `pre-commit`. It runs a gauntlet of automated scanners against your code. If any scanner fails, the commit is instantly blocked. This guarantees that vulnerable or sloppy code cannot enter your repository.
>
> **3. Preparing for CI/CD and AI Engineering**
>
> By enforcing these rules locally, you are preparing your codebase for Enterprise CI/CD pipelines (like GitHub Actions or Azure DevOps). Furthermore, clean, standardized, and fully-tested code is an absolute prerequisite for **AI Harness Engineering** (where autonomous AI agents write and refactor code on your behalf). AI models struggle with messy, unformatted spaghetti code, but thrive in strict environments.
>
> **4. The Industry Standard Toolchain**
>
> Our pre-commit pipeline executes in a specific "Fail-Fast" order using the best tools available in the Python ecosystem:
>
> * **Trufflehog:** A high-speed secrets scanner. It uses heuristics and regex to instantly block commits containing hardcoded API keys, passwords, or tokens.
> * **Ruff (`check --fix` and `format`):** Built in Rust, Ruff is 10-100x faster than legacy tools like `flake8` and `black`. It automatically fixes syntax errors, removes unused imports, and enforces strict, uniform code formatting.
> * **Bandit:** A static application security testing (SAST) tool designed to find common security issues in Python code (e.g., using `eval()` or weak cryptographic hashes).
> * **Pyrefly:** An advanced static analysis tool that detects "code smells" and suggests modern Python refactoring patterns.
> * **uv audit:** Scans your `uv.lock` file against vulnerability databases to ensure none of your installed dependencies have known security exploits (CVEs).
> * **Pytest:** The industry standard testing framework. Running unit tests as the final pre-commit hook ensures developers cannot push code that breaks core business logic.
>

</details>

---

Now that our environment is built, we need to protect it. We are going to set up automated guardrails so that nobody on your team can ever commit sloppy or insecure code.

#### Enforce the modern 'main' branch standard

When you ran `uv init` in Step 1, it automatically initialized a Git repository for you behind the scenes. However, older Git configurations often default to the legacy `master` branch. Let's rename it to the modern industry standard `main`.

```bash
git branch -M main
```

#### Set up the automated security gates

   Create a file named `.pre-commit-config.yaml` in the root directory.

   > **Connecting the tools:** Remember those `--dev` tools we installed in Step 1? We are now configuring Git to use them! Notice how we force Git to execute them locally via `uv run`. This guarantees that tools like `ruff` (for formatting) and `bandit` (for scanning Python vulnerabilities) run securely inside our isolated environment. We also add `trufflehog` to scan for accidentally hardcoded API keys or passwords.

   <details>
   <summary><b>💡 Click here to copy the pre-commit configuration</b></summary>

   ```yaml
   fail_fast: true
   repos:
     - repo: local
       hooks:
         - id: trufflehog
           name: trufflehog
           entry: uv run trufflehog --regex --entropy=False --repo_path . .
           language: system
           pass_filenames: false
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
           entry: uv run bandit -c pyproject.toml -r src/
           language: system
           types: [python]
           pass_filenames: false
         - id: pyrefly
           name: pyrefly
           entry: uv run pyrefly check
           language: system
           types: [python]
           pass_filenames: false
         - id: uv-audit
           name: uv audit
           entry: uv audit
           language: system
           pass_filenames: false
           always_run: true
         - id: pytest-unit
           name: pytest unit
           entry: uv run pytest -m unit
           language: system
           pass_filenames: false
           always_run: true
   ```

   </details>

#### Install the hooks into Git

Finally, we must tell Git to actually read the file we just created. Run the command below. From this moment on, your code will be automatically scanned every single time you try to commit!

```bash
uv run pre-commit install
```

### [to do: fix the problem ad re-add title to this section]

<details>
<summary><b>📚 Click here to learn more about: Domain-Driven Isolation & Test Strategies</b></summary>

> **1. Structuring Domain-Driven Design (DDD)**
>
> Based on our Step 0 design, we must physically construct the folders that enforce our architecture. We divide our code into:
>
> * **Domain (`src/domain`):** Pure Python business rules. It has absolutely zero dependencies on the outside world.
> * **Infrastructure (`src/infrastructure`):** The "adapter" layer that talks to the chaotic external world (network APIs, databases, UI).
> * **Application (`src/application`):** The Use-Case orchestrator that fetches data via the Infrastructure and passes it to the Domain.
>
> **2. The Magic of `__init__.py`**
>
> In Python, a folder is just a folder until you add an `__init__.py` file. This file tells Python, "Treat this directory as an importable module."
>
> Beyond just marking a directory, modern engineers use `__init__.py` to control the public API of their modules. For example, by putting `from .models import Invoice` inside `src/domain/__init__.py`, other files can simply run `from src.domain import Invoice` instead of digging into nested sub-files.
>
> **3. Testing Categories (The Testing Pyramid)**
>
> A robust automation project uses multiple layers of tests to ensure stability:
>
> * **Unit Tests (`tests/unit`):** Tests a single function or class in total isolation (e.g., verifying invoice math). These run in milliseconds and never touch a network or database.
> * **Integration Tests (`tests/integration`):** Tests how multiple internal components interact (e.g., the Application orchestrator calling the Infrastructure). This is where we heavily use **Mocking** (faking API responses) so tests remain fast without hitting real servers.
> * **System / End-to-End (E2E) Tests:** Tests the entire system from start to finish hitting the actual staging ERP system.
> * **Smoke Tests:** A very fast subset of critical tests run immediately after deployment to ensure the application starts up and didn't "catch fire".
> * **Regression Tests:** Tests specifically written to reproduce past bugs, ensuring that adding new features never breaks old fixes.
> * **User Acceptance Tests (UAT):** Tests that validate the software actually solves the business problem (often mapped directly to Sarah's original requirements).
>
> **4. Pytest Best Practices & `conftest.py`**
>
> * **Naming Conventions:** Pytest will only discover your tests if the file starts with `test_` (e.g., `test_invoice.py`) and the function starts with `test_` (e.g., `def test_math_validation():`).
> * **The `conftest.py` File:** If you have data (like a fake test invoice) that you need across multiple test files, you put it in a file named `conftest.py` as a "Fixture". Pytest automatically injects these fixtures into any test function that asks for them by name, keeping your code incredibly DRY (Don't Repeat Yourself).
>
>   *Example `conftest.py`:*
>
>   ```python
>   import pytest
> 
>   @pytest.fixture
>   def fake_invoice():
>       return {"id": "INV-100", "total": 500}
>   ```
>
>   *Example Test (`test_invoice.py`):*
>
>   ```python
>   def test_invoice_total(fake_invoice):
>       # Pytest automatically passes the dictionary here!
>       assert fake_invoice["total"] == 500
>   ```
>
> **5. Setting up VS Code for Pytest**
>
> To run tests natively inside the VS Code "Testing" sidebar, you can manually create a `.vscode/settings.json` file telling the editor to use Pytest instead of the default `unittest` framework:
>
> ```json
> {
>     "python.testing.pytestEnabled": true,
>     "python.testing.unittestEnabled": false,
>     "python.testing.pytestArgs": ["tests"]
> }
> ```
>

</details>

---

Now that our environment is locked down by Git and `pre-commit`, it is time to physically build the folders for our Domain-Driven Design and our Testing framework.

#### Scaffold the Architecture

*Why these folders?* We are creating boundaries.

* The core logic goes in `domain`,
* The HTTP requests go in `infrastructure`,
* The orchestrator goes in `application`.
* The tests are similarly segregated between `unit` and `integration`.

```powershell
New-Item -ItemType Directory -Force -Path src/domain, src/application, src/infrastructure, tests/unit, tests/integration
```

#### Initialize them as Python Modules

Create an empty `__init__.py` file inside each folder so Python can import them.

We will also add an empty `conftest.py` file to our tests folder, preparing it for shared testing fixtures later.

```powershell
New-Item -ItemType File -Force -Path src/domain/__init__.py, src/application/__init__.py, src/infrastructure/__init__.py, tests/__init__.py, tests/conftest.py
   ```

#### Configure Pytest Markers

We told our `pre-commit` hook to only run tests marked as `unit`.

We must register this custom label in our `pyproject.toml` so Pytest understands it. Open `pyproject.toml` and add this block to the bottom:

```toml
[tool.pytest.ini_options]
markers = [
    "unit: mark a test as a unit test.",
    "integration: mark a test as an integration test."
]
```

#### Verify the Final Structure

By the end of this workshop, your project tree will look exactly like this:

```text
/ project-root
┣ src/
┃ ┣ domain/               # Step 4: Core business logic and data validation (Pydantic)
┃ ┣ infrastructure/       # Step 5: External API clients and network resilience (Tenacity)
┃ ┗ application/          # Step 6: The orchestrator that glues Domain & Infrastructure together
┣ tests/
┃ ┣ conftest.py           # Shared mock data and fixtures for Pytest
┃ ┣ unit/                 # Fast tests for business logic (no network required)
┃ ┗ integration/          # Complex tests using Mock APIs to prove the orchestrator works
┣ .pre-commit-config.yaml # Step 2: Security and formatting guardrails
┗ pyproject.toml          # Step 1: Environment and dependency definitions
```

### Forging the Domain (Defending Against Corrupted Data)

<details>
<summary><b>📚 Click here to learn more about: Defensive Data Modeling & Pydantic</b></summary>

> **1. The Flaw of Generic Dictionaries**
>
> In legacy automation, developers often passed raw JSON data around using generic Python dictionaries (e.g., `invoice["total_amount"]`). This is dangerous. If the ERP system unexpectedly changes the API and sends a string `"100.00"` instead of a float `100.00`, your bot will crash deep inside the code during a math operation.
>
> **2. The Pydantic Way**
>
> Pydantic is the industry standard library for data validation. Instead of dictionaries, we define our Domain entities as strict Python classes using `BaseModel`.
>
> * **Automatic Type Casting:** If Pydantic expects a `float` but receives the string `"100.00"`, it will automatically convert it to a float. If it receives something uncastable (like `"UNKNOWN"`), it instantly throws a loud validation error *at the boundary* of the application, rather than failing silently later.
> * **IntelliSense:** Because they are strict classes, your IDE (VS Code) will auto-complete `invoice.total_amount` for you, eliminating spelling typos.
> * **Custom Validators:** You can write custom Python methods decorated with `@model_validator` to enforce complex business rules. There are two critical modes:
>   * `mode="before"`: Runs *before* Pydantic does its automatic type casting. The data you receive is a raw dictionary. Use this if you need to mutate or clean up the raw payload before parsing (e.g., stripping whitespace).
>   * `mode="after"`: Runs *after* Pydantic has validated all types. The data you receive is a fully instantiated Python object. **This is best for business logic.**
> * **Field Constraints & Aliases:** Using the `Field()` function, you can enforce strict constraints directly on attributes without writing custom methods (e.g., `Field(ge=0)` ensures a number is greater than or equal to zero). You can also use `alias` to map messy external API keys (like `empId`) to clean internal Python variables (like `employee_id`).
>
>   *Example: Defining a strict Domain Model with Fields and Validators*
>
>   ```python
>   from pydantic import BaseModel, model_validator, Field
> 
>   class Employee(BaseModel):
>       # Use alias for bad external keys, and gt=0 to enforce positive numbers
>       employee_id: int = Field(alias="empId", gt=0)
>       name: str
>       # Constraints: age must be between 18 and 65
>       age: int = Field(ge=18, le=65)
>       is_active: bool = Field(default=True)
>
>       @model_validator(mode="before")
>       @classmethod
>       def clean_raw_data(cls, data: dict):
>           # Runs first! We clean the raw dictionary before Pydantic sees it.
>           if "name" in data and isinstance(data["name"], str):
>               data["name"] = data["name"].strip().title()
>           return data
>   
>   # Instantiating the model with raw, messy external JSON data
>   raw_data = {"empId": "404", "name": "   sarah   ", "age": "25"}
>   sarah = Employee(**raw_data) 
>   
>   # The object is now perfectly clean and safe to use!
>   # sarah.employee_id -> 404 (int)
>   # sarah.name -> "Sarah" (str)
>   ```
>
> **3. Best Practices**
>
> * Never use raw dictionaries for business logic. Always parse external JSON directly into a Pydantic model immediately after downloading it.
> * Keep your models "pure". A Pydantic model should only validate data; it should never make database queries or API calls itself.
>
> **4. Preparation for AI Agents**
> Strict data modeling is the absolute prerequisite for building **AI Agents** or LLM harnesses. Large Language Models often hallucinate or generate slightly malformed JSON. By forcing the LLM's output through a strict Pydantic model, you guarantee that your underlying Python code never receives corrupted AI output. In fact, modern AI frameworks (like LangChain or OpenAI's SDK) rely on Pydantic natively to force the LLM to adhere to specific schemas!

</details>

---

Sarah's business requirement explicitly stated that the ERP math is sometimes corrupted. We cannot trust the incoming data. We are going to build an impenetrable wall in our `domain` layer that strictly validates every single invoice before the orchestrator is even allowed to look at it.

#### Create the Data Models (`src/domain/models.py`)

> *What are we doing?*
>
> * We are creating the strict definitions for `LineItem` and `Invoice`.
> * We are also writing a custom validator to explicitly perform the math check that Sarah requested.

**Challenge:** *Try to write the `LineItem` and `Invoice` Pydantic models yourself! Use the `@model_validator(mode="after")` decorator to sum the line items and raise a `ValueError` if the math is wrong.*

<details>
<summary><b>💡 Click here for hints</b></summary>

> **Hints:**
>
> * You will need to use the `@model_validator(mode="after")` decorator. This ensures Pydantic casts all the types first so you can safely iterate over `self.line_items`. 
> * You can sum the amounts using a generator expression like `sum(item.amount for item in self.line_items)`.
>

<details>
<summary><b>💡 Still stuck? Click here for a code scaffold</b></summary>

```python
from pydantic import BaseModel, model_validator

class LineItem(BaseModel):
    model_config = {"frozen": True}
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
        # TODO: Calculate the sum of all item amounts in self.line_items
        # TODO: Compare the sum to self.total_amount using math.isclose(..., abs_tol=0.01)
        # TODO: If they don't match, raise a ValueError
        return self
```

<details>
<summary><b>💡 Click here to show the full solution snippet</b></summary>

```python
import math
from pydantic import BaseModel, model_validator

class LineItem(BaseModel):
    model_config = {"frozen": True}
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
        if not math.isclose(calculated_total, self.total_amount, abs_tol=0.01):
            raise ValueError(f"Math Error! Total {self.total_amount} != Sum {calculated_total}")
        return self
```

</details>
</details>
</details>

#### Prove the Defense Works (`tests/unit/test_domain.py`)

> *What are we doing?*
>
> * We are practicing Test-Driven Development (TDD).
> * Before we connect to the real API, we write a lightning-fast unit test simulating a corrupted invoice to definitively prove that our Pydantic model will reject it.

**Challenge:** *Write a Pytest function labeled `@pytest.mark.unit`. Create an invoice with bad math and use `with pytest.raises(ValueError):` to prove your validation catches it!*

<details>
<summary><b>💡 Click here for hints</b></summary>

> **Hints:**
[to do: add hints]

<details>
<summary><b>💡 Click here to show the full solution snippet</b></summary>

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
</details>

#### Run the Defense Test

Execute the unit test to verify your math validator works perfectly.

```bash
uv run pytest -m unit
```

### Preparing the Infrastructure (Bridging the Unstable Outside World)

<details>
<summary><b>📚 Click here to learn more about: 12-Factor Apps, REST, and Network Resilience</b></summary>

> **1. The 12-Factor App: Backing Services & Config**
>
> In Domain-Driven Design, the Infrastructure layer is the absolute edge of your application. It is the only place allowed to talk to the chaotic outside world. The **12-Factor App** methodology states:
>
> * **Backing Services:** Treat databases and APIs as attached resources. If the ERP system goes down, your app should gracefully wait, retry or report, not crash.
> * **Config:** Credentials (like API keys) must be injected via Environment Variables, never hardcoded in the script.
>
> **2. REST API Basics & HTTP Status Codes**
>
> Modern systems communicate via REST (Representational State Transfer) using standard HTTP verbs:
>
> * `GET`: Retrieve data (e.g., fetch invoices). Must be **Idempotent** (running it 100 times doesn't change anything).
> * `POST`: Create data or trigger actions (e.g., approve an invoice). Not inherently idempotent.
> * `PUT`: Update or replace an entire existing resource (e.g., updating an invoice record). Idempotent.
> * `PATCH`: Partially update an existing resource. Not strictly idempotent.
> * `DELETE`: Remove a resource from the server.
>
> You must understand HTTP Status Codes to build resilient bots:
>
> * **200 OK / 201 Created:** Success!
> * **301 Moved Permanently / 302 Found:** The resource has been moved. Most Python clients (like `requests`) will follow these redirects automatically.
> * **400 Bad Request:** You sent bad data (e.g., malformed JSON).
> * **401 Unauthorized / 403 Forbidden:** Your API key is invalid or lacks permissions.
> * **404 Not Found:** The URL is wrong or the record doesn't exist.
> * **500 Internal Server Error:** The server crashed (a bug on their end).
> * **503 Service Unavailable:** The server is overloaded (Sarah's exact problem!).
>
> **3. Best Practices for REST in Python**
>
> * **Always Set Timeouts:** If the ERP system hangs forever, your bot will hang forever. Always use `requests.get(url, timeout=10)`.
> * **Raise for Status:** Always call `response.raise_for_status()` to instantly throw an exception if you get a 4XX or 5XX code.
>
>   *Example: A perfect REST request*
>
>   ```python
>   import requests
>   
>   headers = {"Authorization": "Bearer YOUR_ENV_VAR_TOKEN"}
>   response = requests.get("https://api.erp.com/invoices", headers=headers, timeout=10)
>   response.raise_for_status() # Throws HTTPError if not 200 OK
>   data = response.json()
>   ```
>
> **4. OpenAPI (Swagger)**
>
> How do you know what endpoints a REST API has?
>
> Modern APIs implement the **OpenAPI Specification** (often referred to as Swagger). This provides an interactive web page (usually hosted at `/docs` or `/swagger`) that acts as a living contract. You can use it to see exactly what URLs are available, what JSON payloads they require, and even test them directly in your browser.
>
> **5. Defeating 503 Errors with `tenacity`**
>
> When a 503 error happens, we shouldn't write custom `while` loops with `time.sleep()`. Instead, we use the `tenacity` library to automatically retry with **Exponential Backoff** (waiting 1s, then 2s, then 4s to avoid overwhelming the struggling server).
>
> *Example: Exponential Backoff*
>
> ```python
> from tenacity import retry, stop_after_attempt, wait_exponential
>
> @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
> def dangerous_network_call():
>     # If this raises an exception, Tenacity intercepts it and tries again!
>     pass
> ```

</details>

---

Sarah's primary complaint was that the ERP system randomly throws `503 Service Unavailable` errors during peak hours, causing her legacy macro to crash instantly. We are going to build an API client that uses exponential backoff to patiently wait out the crashes, and automatically casts the raw JSON into the bulletproof Pydantic models we built in Step 4.

#### Analyze the ERP API (Swagger)

**Challenge:** *The ERP system is running locally on port `8080`.*

If you are using **GitHub Codespaces**, open the **Ports** tab (next to your Terminal), find Port `8080`, and click the "Open in Browser" globe icon. Then, add `/docs` to the end of the URL in your browser.

Read the OpenAPI contract to discover the exact HTTP verbs and endpoints needed to fetch pending invoices and approve them!*

#### Create the API Client (`src/infrastructure/api_client.py`)

> *What are we doing?*
>
> * We are building the `APIClient`. We use `requests` to handle the HTTP protocol, ensuring we set a strict `timeout` on every call.
> * We then decorate our POST request with `@retry` to guarantee it survives Sarah's dreaded 503 errors.

**Challenge**: *Build the client using the endpoints you discovered in the Swagger UI. Automatically cast the JSON response into your Pydantic `Invoice` models!*

<details>
<summary><b>💡 Click here for hints</b></summary>

> **Hints:**
>
> * Use `requests.get()` to fetch the data (check the Swagger UI at `/docs` for the exact endpoint URL).
> * Remember that because of our strict Pydantic model, initializing `Invoice` might throw a `ValueError` if the math is corrupted! Wrap that line in a `try/except` block so you can log the error and `continue` to the next invoice.

<details>
<summary><b>💡 Still stuck? Click here for a code scaffold</b></summary>

```python
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from src.domain.models import Invoice

class APIClient:
    def fetch_pending_invoices(self) -> list[Invoice]:
        # TODO: Make a GET request to http://127.0.0.1:8080/api/invoices/pending
        # TODO: Set a timeout (e.g., 10 seconds)
        # TODO: Raise for status
        # TODO: Loop through the JSON response and parse each item into an Invoice model
        # TODO: Wrap the parsing in a try/except ValueError to catch and skip corrupted invoices!
        pass

    # TODO: Add the @retry decorator with exponential backoff (max 3 attempts)
    def approve_invoice(self, invoice_id: str) -> bool:
        # TODO: Make a POST request to http://127.0.0.1:8080/api/invoices/{invoice_id}/approve
        # TODO: Set a timeout
        # TODO: Raise for status
        pass
```

<details>
<summary><b>💡 Click here to show the full solution snippet</b></summary>

[to do: fix this and replace code beloe with the actual full solution snippet]
```python
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from src.domain.models import Invoice

class APIClient:
    def fetch_pending_invoices(self) -> list[Invoice]:
        # TODO: Make a GET request to http://127.0.0.1:8080/api/invoices/pending
        # TODO: Set a timeout (e.g., 10 seconds)
        # TODO: Raise for status
        # TODO: Loop through the JSON response and parse each item into an Invoice model
        # TODO: Wrap the parsing in a try/except ValueError to catch and skip corrupted invoices!
        pass

    # TODO: Add the @retry decorator with exponential backoff (max 3 attempts)
    def approve_invoice(self, invoice_id: str) -> bool:
        # TODO: Make a POST request to http://127.0.0.1:8080/api/invoices/{invoice_id}/approve
        # TODO: Set a timeout
        # TODO: Raise for status
        pass
```

</details>
</details>
</details>

#### Configure the ERP Mock Data (`tests/conftest.py`)

> *What are we doing?*
>
> * We are creating a reusable Pytest fixture containing the raw JSON dictionary that the ERP system normally returns. Any test can now access this fake data!

<details>
<summary><b>💡 Click here for hints</b></summary>

> **Hints:**
>
> * Use the `@pytest.fixture` decorator above a function named `mock_erp_json`.
> * Return a list containing a single dictionary representing an invoice payload (include fields like `id`, `vendor`, `currency`, `line_items`, and `total_amount`).

<details>
<summary><b>💡 Click here to show the full solution snippet</b></summary>

```python
import pytest

@pytest.fixture
def mock_erp_json():
    return [{
        "id": "INV-MOCK",
        "vendor": "TestVendor",
        "currency": "USD",
        "line_items": [{"description": "Service", "amount": 100}],
        "total_amount": 100
    }]
```

</details>
</details>

#### Prove the Infrastructure Works (`tests/unit/test_api_client.py`)

> *What are we doing?*
>
> * We write a Unit test. Notice how we inject `mock_erp_json` into the function, and use `@patch` to intercept `requests.get`. We tell the intercepted request to return our fake JSON instead of hitting the network!

**Challenge:** *Create a unit test labeled `@pytest.mark.unit`. Use `@patch` and your `mock_erp_json` fixture to assert that your client correctly parses the fake data into a Pydantic model.*

<details>
<summary><b>💡 Click here for hints</b></summary>

> **Hints:**
>
> * Use `@patch("src.infrastructure.api_client.requests.get")`.
> * Create a `Mock()` object, set its `.json.return_value` to `mock_erp_json`, and assign it to `mock_get.return_value`.

<details>
<summary><b>💡 Click here to show the solution snippet</b></summary>

```python
import pytest
from unittest.mock import patch, Mock
from src.infrastructure.api_client import APIClient

@pytest.mark.unit
# @patch intercepts the requests.get function BEFORE it runs.
# It prevents the network call and passes a fake "mock_get" object into our test function.
@patch("src.infrastructure.api_client.requests.get")
def test_fetch_pending_invoices(mock_get, mock_erp_json):
    # ARRANGE: Configure our fake network response
    
    # 1. Create a fake HTTP response object
    mock_response = Mock()
    
    # 2. When our code calls response.json(), return the fake dictionary from conftest.py
    mock_response.json.return_value = mock_erp_json
    
    # 3. Tell the intercepted requests.get to return our fake HTTP response
    mock_get.return_value = mock_response
    
    # ACT: Run the client. 
    # It thinks it is hitting the real network, but it is actually talking to our Mock!
    client = APIClient()
    invoices = client.fetch_pending_invoices()
    
    # ASSERT: Did the client successfully parse the fake JSON into Pydantic models?
    assert len(invoices) == 1
    assert invoices[0].id == "INV-MOCK"
    assert invoices[0].vendor == "TestVendor"
```

</details>
</details>

#### Run the Unit Test

Execute the test to verify your mocking logic works perfectly.

```bash
uv run pytest -m unit
```

#### Test API Resilience (`tests/unit/test_api_client.py`)

> *What are we doing?*
>
> * We are proving that if the ERP sends a corrupted invoice (e.g. bad math), our `APIClient` catches the `ValueError` from Pydantic and skips it instead of crashing.

<details>
<summary><b>💡 Click here for hints</b></summary>

> **Hints:**
>
> * Similar to the previous test, but return a list with two invoice dictionaries: one with correct math and one with corrupted math.
> * Assert that the client returns only a single valid invoice.

<details>
<summary><b>💡 Click here to show the solution snippet</b></summary>

```python
@pytest.mark.unit
@patch("src.infrastructure.api_client.requests.get")
def test_fetch_pending_invoices_skips_corrupted_invoice(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = [
        {"id": "GOOD-1", "vendor": "A", "currency": "USD",
        "line_items": [{"description": "X", "amount": 100}], "total_amount": 100},
        {"id": "BAD-1", "vendor": "A", "currency": "USD",
        "line_items": [{"description": "X", "amount": 100}], "total_amount": 9999},
    ]
    mock_get.return_value = mock_response
    invoices = APIClient().fetch_pending_invoices()
    assert [inv.id for inv in invoices] == ["GOOD-1"]
```

</details>
</details>

### The Orchestrator (SOLID Principles in Action)

<details>
<summary><b>📚 Click here to learn more about: SOLID Principles & Python Protocols</b></summary>

> **1. The SOLID Principles**
>
> SOLID is an acronym for five design principles that make software maintainable. In automation, two are absolutely critical:
>
> * **(S) Single Responsibility Principle:** A class should do one thing.
>   * *Bad:* A massive "Bot" script that fetches API data, calculates math, and updates an Excel report all in one 500-line file.
>   * *Good:* Our DDD structure! `models.py` strictly handles math. `api_client.py` strictly handles networking.
>
> * **(D) Dependency Inversion Principle:** High-level logic should not depend on low-level implementation details.
>   * *Bad (Tightly Coupled):*
>
>     ```python
>     # If the UK office forces us to use SAP next year, we have to rewrite this entire core class!
>     from infrastructure.api_client import FastAPIClient 
>     class Orchestrator:
>         def __init__(self):
>             self.client = FastAPIClient() # Hardcoded dependency!
>     ```
>
>   * *Good (Loosely Coupled):* The Orchestrator asks for "something" that can fetch invoices, injected via the `__init__` constructor.
> * **(L) Liskov Substitution & Interface Segregation:** While less critical for this specific orchestrator, the remaining principles ensure our interfaces remain small and interchangeable. A mock API client used in tests should be perfectly substitutable for the real `APIClient` without the Orchestrator knowing the difference.
>
> **2. Python Protocols (Duck Typing)**
>
> How do we enforce the "Good" example of (D) Dependency Inversion Principle in Python?
>
> We use `typing.Protocol`. A Protocol defines an interface without writing any implementation code. It relies on "Duck Typing" (if it walks like a duck and quacks like a duck, it is a duck).
>
> *When to use it:* When you want to decouple your orchestrator from specific technologies (like FastAPI, SAP, or a fake database for testing).
>
> *Example: Defining a Protocol*
>
> ```python
> from typing import Protocol
> 
> class InvoiceFetcher(Protocol):
>     # We don't care HOW you fetch it, just that you have this method signature.
>     def fetch(self) -> list: ...
>   
> class Orchestrator:
>     # We can pass ANY class in here (FastAPIClient, SAPClient), as long as it has a fetch() method!
>     def __init__(self, fetcher: InvoiceFetcher):
>         self.fetcher = fetcher
> ```

</details>

---

In Sarah's email, she hinted that if this tool is successful, management might deploy it globally. This means next year, the bot might have to talk to SAP or Oracle instead of this custom ERP. By using Dependency Inversion and a `Protocol`, we can build an orchestrator that will survive that future migration without changing a single line of core business logic!

#### Create the Application Orchestrator (`src/application/processor.py`)

> *What are we doing?*
>
> * We define an `InvoiceAPIClient(Protocol)` interface.
> * Then, we build the `InvoiceProcessor` orchestrator and inject the client via the `__init__` method.
> * Finally, the `run()` method applies Sarah's final business rule: only approve invoices strictly under the $10,000 threshold.

**Challenge:** *Create an `InvoiceProcessor`. Define an `InvoiceAPIClient(Protocol)` rather than importing the FastAPI client. Write a `run()` method that loops through the invoices and approves them.*

<details>
<summary><b>💡 Click here for hints</b></summary>

> **Hints:**
>
> * Call `self.api_client.fetch_pending_invoices()` to get the list, then loop through it.
> * Use an `if` statement to check if `total_amount > self.threshold`.
> * Remember that network calls can fail—wrap `self.api_client.approve_invoice(inv.id)` in a `try/except Exception` block so a transient error doesn't crash your entire batch!

<details>
<summary><b>💡 Still stuck? Click here for a code scaffold</b></summary>

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
        # TODO: Fetch pending invoices using self.api_client
        # TODO: Loop through the invoices
        # TODO: If the invoice total is > self.threshold, log a warning
        # TODO: Otherwise, try to approve the invoice
        # TODO: Wrap the approval in a try/except block so a failure doesn't crash the loop!
        pass
```

<details>
<summary><b>💡 Click here to show the full solution snippet</b></summary>

```python
import logging
from src.domain.models import Invoice
from typing import Protocol

logger = logging.get_logger()

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
            # BEST PRACTICE: Bind the ID to the logger so it attaches to all subsequent logs!
            # This makes tracking a single invoice through the system effortless in Azure/Datadog.
            log = logger.bind(invoice_id=inv.id)
            log.info("processing_invoice")

            if inv.total_amount > self.threshold:
                # BEST PRACTICE: Use Warning for expected business exceptions (needs human review)
                log.warning("manual_review_required", amount=inv.total_amount)
            else:
                self.api_client.approve_invoice(inv.id)
                log.info("invoice_approved")
```

</details>
</details>
</details>

### Integration Testing (No Network Required!)

<details>
<summary><b>📚 Click here to learn more about: CUPID Principles & Integration Testing</b></summary>

> **1. The CUPID Properties**
>
> While SOLID focuses on class design, **CUPID** focuses on joyful developer experiences.
>
> * **C**omposable: Code that plays well with others (our Orchestrator takes any API Client).
> * **U**nix Philosophy: Do one thing well.
> * **P**redictable: Tests should pass 100% of the time. (Networks are unpredictable, which is why we mock them).
> * **I**diomatic: Writing Pythonic code (like using `Protocol`).
> * **D**omain-based: Structuring folders by business domain.
>
> **2. The Testing Spectrum**
>
> To build a reliable bot, we discuss all three layers (though this workshop only builds Unit and Integration tests):
>
> * **Unit Tests (Step 4 & 5):** We tested our Pydantic math in total isolation. We tested our `APIClient` by mocking the `requests` library.
> * **Integration Tests (This Step):** Here, we test the **wiring** between our Application Orchestrator and our Domain models. Does the Orchestrator correctly apply the $10,000 threshold rule?
> * **End-to-End (E2E) Tests (Next Step):** Does the entire script actually work when we hit the real ERP system?
>
> **3. Fakes vs Mocks**
>
> In Step 5, we used a `Mock` to dynamically intercept a Python library (`requests`). In this step, we will build a `Fake`—a lightweight, working implementation of our `InvoiceAPIClient` Protocol that just stores data in a Python list instead of sending it over the internet. This is much cleaner and faster for orchestrator testing!

</details>

---

Sarah needs proof that the bot won't accidentally approve a $50,000 invoice. Because we engineered a clean DDD architecture, we can prove this instantly. We will build a Fake API client that feeds the Orchestrator a cheap invoice and an expensive invoice.

#### Create the Fake Client (`tests/conftest.py`)

> *What are we doing?*
>
> * In Step 3, we learned that `conftest.py` is the home for reusable test fixtures. We are building a `FakeAPIClient` that implements our Protocol, but returns memory invoices instead of hitting the network.
> * By making it a `@pytest.fixture`, any test in our project can instantly request it!

**Challenge:** *Open `tests/conftest.py`. Write a `FakeAPIClient` class with a `fetch_pending_invoices` method returning two fake invoices (one under $10,000, one over). Create a fixture function that returns an instance of it.*

<details>
<summary><b>💡 Click here for hints</b></summary>

> **Hints:**
>
> * Create an `Orchestrator` class that accepts `api_client` via its `__init__` method.
> * Write a `run()` method that fetches invoices, checks if the amount is > 10000, and calls `approve_invoice()` for valid ones.
> * Use `logging.info()` or `logging.warning()` to track the states.

<details>
<summary><b>💡 Click here to show the full solution snippet</b></summary>

```python
import pytest
from src.domain.models import Invoice, LineItem

class FakeAPIClient:
    def __init__(self):
        self.approved_invoices = []
        
    def fetch_pending_invoices(self):
        # We intentionally hardcode a cheap and an expensive invoice here
        # so we can test that the Orchestrator applies the $10,000 rule correctly!
        return [
            Invoice(id="CHEAP-1", vendor="A", currency="USD", line_items=[LineItem(description="X", amount=5)], total_amount=5),
            Invoice(id="EXPENSIVE-1", vendor="A", currency="USD", line_items=[LineItem(description="X", amount=20000)], total_amount=20000)
        ]

    def approve_invoice(self, invoice_id: str):
        self.approved_invoices.append(invoice_id)
        return True

@pytest.fixture
def fake_api():
    return FakeAPIClient()
```

</details>
</details>

#### Write the Integration Test (`tests/integration/test_processor.py`)

> *What are we doing?*
>
> * Notice how we just ask Pytest for the `fake_api` fixture in the function arguments! We inject it into the Orchestrator, run it, and check the fake's internal list to prove it only approved the cheap invoice.

**Challenge:** *Create an integration test. Inject the `fake_api` fixture. Run the `InvoiceProcessor` and assert that "CHEAP-1" is approved and "EXPENSIVE-1" is not!*

<details>
<summary><b>💡 Click here for hints</b></summary>

> **Hints:**
>
> * Write a test function using `@patch` to mock your `api_client`.
> * Create fake invoice instances to return when `fetch_pending_invoices` is called.
> * Assert that `approve_invoice` is called the expected number of times based on the invoice amounts.

<details>
<summary><b>💡 Click here to show the full solution snippet</b></summary>

```python
import pytest
from src.application.processor import InvoiceProcessor

@pytest.mark.integration
def test_processor_approves_under_threshold_only(fake_api):
    # Arrange: Inject the Fake infrastructure!
    processor = InvoiceProcessor(api_client=fake_api)
    
    # Act
    processor.run()
    
    # Assert
    assert "CHEAP-1" in fake_api.approved_invoices
    assert "EXPENSIVE-1" not in fake_api.approved_invoices
```

</details>
</details>

#### Run the Integration Test

Execute the test to verify your Orchestrator logic works perfectly.

```bash
uv run pytest -m integration
```

### The Entry Point (Running the Bot)

<details>
<summary><b>📚 Click here to learn more about: Lightweight Entry Points & Integration</b></summary>

> **1. The Purpose of a Lightweight Entry Point**
>
> In legacy RPA (like Robocorp), everything—network calls, business logic, math, and configuration—is often jammed into one massive `tasks.py` file.
>
> In our DDD architecture, `task.py` is incredibly "dumb" and lightweight. Its only job is to wire the separated layers together using **Dependency Injection** and hit "Go".
>
> **2. Seamless Integration (CI/CD, BPM, and Cloud)**
>
> Because our `task.py` is lightweight and our environment is managed by `uv`, we can execute this bot from absolutely anywhere:
>
> * **Terminal:** A developer can manually run it via `uv run task.py`.
> * **CI/CD Pipelines:** GitHub Actions, Jenkins, or Azure DevOps Pipelines can run it on a schedule.
> * **Data & Automation Orchestrators:** You can easily trigger this script from Apache Airflow, Prefect, or enterprise BPM Engines.
> * **Cloud Native Serverless:** You can wrap this execution command inside an Azure Function or trigger it via an Azure Logic App!
> * **Power Automate Desktop:** You can run it from PAD flow using `Run DOS command` action or custom action to execute `uv run task.py` and let this robust Python architecture do the heavy lifting without visual spaghetti!

</details>

---

The architecture is complete, and we are finally ready to process Sarah's real invoices against the live (mock) ERP system!

#### Create `task.py` in the root directory

> *What are we doing?*
>
> * We are creating the execution script.
> * We import our real infrastructure (`APIClient`), inject it into our Orchestrator (`InvoiceProcessor`), and run the process.

Notice how clean and readable this file is!

**Challenge:** *Create the main execution file. Import the real `APIClient` and the `InvoiceProcessor`. Instantiate the client, pass it into the processor, and call `run()`!*

<details>
<summary><b>💡 Click here for hints</b></summary>

> **Hints:**
>
> * Configure basic `logging` at the top of your file.
> * Instantiate your `APIClient` and pass it to the `Orchestrator`, then call the orchestrator's `run()` method inside a `main()` block.

<details>
<summary><b>💡 Click here to show the full solution snippet</b></summary>

```python
import logging
from src.infrastructure.api_client import APIClient
from src.application.processor import InvoiceProcessor

# Configure basic logging so we can see the output in the terminal
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def main():
    print("Starting Invoice Processing Bot...")

    # 1. Initialize the real Infrastructure client (Connecting to the outside world!)
    api_client = APIClient()

    # 2. Inject the real client into the Application Orchestrator (Dependency Injection)
    processor = InvoiceProcessor(api_client=api_client)

    # 3. Execute the core business logic flow
    processor.run()

    print("Processing Complete!")

# Standard Python idiom to ensure this only runs when executed directly
if __name__ == "__main__":
    main()
```

</details>
</details>

#### Execute your completed bot (End-to-End Test)

Run the process using `uv` to ensure it executes inside your isolated virtual environment. This proves the entire system works from end to end!

```bash
uv run task.py
```

### Observability & Enterprise Deployment

<details>
<summary><b>📚 Click here to learn more about: Structured Logs & Azure Architecture</b></summary>

> **1. The 12-Factor App on Logs**
>
> Legacy RPA frameworks generate static `log.html` or `stdout.log` files on the local hard drive. The **12-Factor App** principles state this is an anti-pattern. Servers and cloud containers are ephemeral; if the machine dies, your logs are permanently deleted.
>
> Instead, modern bots output **Event Streams** to the terminal (`stdout`), allowing log routers to transport them off-site.
>
> **2. Strings vs. Structured JSON**
>
> How should you write a log?
>
> * *Bad (Strings):* `logger.info(f"Invoice {inv_id} processed for {amount}")`. To search for this in Azure, you have to write horrible Regex queries.
> * *Good (Structured JSON):* `logger.info("invoice_processed", invoice_id=inv_id, amount=amount)`. This natively outputs a JSON dictionary. You can easily query: `SELECT * FROM logs WHERE amount > 5000`.
>
> **3. Contextual Binding (Tracing)**
>
> In `structlog`, you can `bind()` context to a logger. If you bind the `invoice_id` at the start of a `for` loop, every single log event fired inside that loop will automatically attach that `invoice_id` to its JSON payload. This creates a perfect audit trace for Azure Application Insights, Datadog, Splunk, or Elasticsearch!
>
> **4. Observability Best Practices**
>
> * **INFO:** Standard business events (e.g., `invoice_approved`).
> * **WARNING:** Expected edge cases that require human intervention (e.g., `manual_review_required`).
> * **ERROR:** Unexpected system crashes (e.g., `erp_database_timeout`).
>
> To separate issues, we should define Custom Domain Exceptions (e.g., `class MathValidationError(ValueError): pass`). This allows our orchestrator to catch `MathValidationError` (a business error we can log and skip) differently from a `requests.exceptions.ConnectionError` (a technical error where we should probably abort and alert IT).
>
> **5. Enterprise Deployment (Azure Architecture)**
>
> Because we followed DDD and 12-Factor principles, our code is 100% portable. Here is how you deploy it:
>
> * **On-Premises (Hybrid):** Run via PAD flow or Windows Task Scheduler. Use the `azure-monitor-opentelemetry` Python package to pipe your `structlog` stream through the corporate firewall into Azure Application Insights.
> * **Cloud Native (Azure Container Apps/AKS):** Package the bot in a `Dockerfile`. Azure automatically intercepts the JSON `stdout` stream from Step 9 with zero code changes!
> * **Serverless (Azure Functions):** Wrap `processor.run()` in a Time-Triggered Function.
>   * *Template Example:*
>
>     ```python
>     import azure.functions as func
>     from task import main
>     
>     app = func.FunctionApp()
>     @app.timer_trigger(schedule="0 */5 * * * *", arg_name="timer", run_on_startup=False)(schedule="0 */15 * * * *", arg_name="myTimer") # Run every 15 minutes
>     def erp_bot(myTimer: func.TimerRequest) -> None:
>         main()
>     ```
>
> * **Low-Code Orchestration (Azure Logic Apps):** If the ERP requires legacy XML SOAP authentication, let a Logic App handle the complex Auth visual flow, and have it trigger your Azure Function purely for the Pydantic math validation.

</details>

*Note: You might wonder why we initially used standard `logging` in Step 6 only to replace it now. Standard logging is universally understood, and we wanted to focus purely on Orchestration logic first. Now that our core logic works, we are upgrading to `structlog` to demonstrate enterprise observability best practices.*

---

Sarah loves the bot, but audit season is approaching. She needs a perfectly queryable audit trail showing exactly *why* every invoice was approved or rejected. The legacy `log.html` won't cut it. We are going to implement enterprise-grade Structured JSON logging.

#### Add the modern logging library

> *What are we doing?*
>
> * We are installing `structlog`, the industry standard for structured Python logging.

```bash
uv add structlog
```

#### Refactor your Orchestrator (`src/application/processor.py`)

> *What are we doing?*
>
> * We replace standard `logging` with `structlog`.
> * Inside the processing loop, we create a bound logger (`log = logger.bind(...)`). Now, every time we log `manual_review_required` or `invoice_approved`, the Invoice ID and Amount are captured in the JSON payload!
  
**Challenge:** *Replace the standard `logging` with `structlog`. Notice how we `bind()` variables like `invoice_id` to the logger so every log line automatically includes that context!*

<details>
<summary><b>💡 Click here for hints</b></summary>

> **Hints:**
>
> * Import `structlog`.
> * Remove the standard `logging` setup.
> * Initialize a logger with `log = structlog.get_logger()`.
> * Inside your loop, use `log.bind(invoice_id=inv.id, amount=inv.total_amount)` to create a context-aware logger that automatically includes these fields in every log message it emits.

<details>
<summary><b>💡 Click here to show the full solution snippet</b></summary>

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
            # BEST PRACTICE: Bind the ID to the logger so it attaches to all subsequent logs!
            # This makes tracking a single invoice through the system effortless in Azure/Datadog.
            log = logger.bind(invoice_id=inv.id)
            log.info("processing_invoice")

            if inv.total_amount > self.threshold:
                # BEST PRACTICE: Use Warning for expected business exceptions (needs human review)
                log.warning("manual_review_required", amount=inv.total_amount)
            else:
                self.api_client.approve_invoice(inv.id)
                log.info("invoice_approved")
```

</details>
</details>

#### Update your Entry Point (`task.py`)

> *What are we doing?*
>
> * We tell `structlog` to render all log events as JSON strings, and inject an ISO-8601 timestamp into every payload automatically.

**Challenge:** *Configure `structlog` to output as JSON with an ISO timestamp.*

<details>
<summary><b>💡 Click here for hints</b></summary>

> **Hints:**
>
> * Use `structlog.configure()` to set the processors.
> * You will need `structlog.processors.TimeStamper(fmt="iso")` to add the timestamp, and `structlog.processors.JSONRenderer()` to format the final output as a JSON string.

<details>
<summary><b>💡 Click here to show the full solution snippet</b></summary>

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

    # Wire everything up and run!
    api_client = FastAPIClient()
    processor = InvoiceProcessor(api_client=api_client)
    processor.run()

    logger.info("bot_finished")

if __name__ == "__main__":
    main()
```

</details>
</details>

#### Run the bot

Execute the bot. Look at your terminal! You will see machine-readable JSON logs that cloud dashboards (Azure, Datadog, Splunk) can natively parse and query.

```bash
uv run task.py
```

---

### 🏆 Achievement Unlocked: Automation Architect

**You absolutely nailed it.**

Congratulations! You didn't just write a script; you engineered a robust, decoupled, 12-factor cloud-native masterpiece. You took Sarah's fragile Excel macro, extracted the spaghetti logic, banished the random 503 network crashes using exponential backoff, and wrapped it all in an impenetrable fortress of Pydantic validation and unit tests.

The dark days of debugging `NameError: 'data' is undefined` in a 3,000-line `tasks.py` file at 2:00 AM are officially over.

By mastering Domain-Driven Design, SOLID principles, and structured JSON observability, you haven't just learned how to build modern Python automation solutions—you have future-proofed your career.

Here is the secret: **AI Agents** (like OpenAI Swarm, LangChain, or AutoGen) *hate* messy code. They need strict data contracts (Pydantic), isolated tools (Infrastructure), and clear orchestrator boundaries to function autonomously without destroying production.

By building this architecture today, you are now one massive step closer to the AI Era. You aren't just an RPA Developer anymore; you are an AI Systems Architect.

Go grab a cake or chicken leg. You've earned it. ☕🚀
