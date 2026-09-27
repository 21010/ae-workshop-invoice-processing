# Automate Invoice Processing - Guided Project

Welcome to the hands-on guided project! 

In this session, you will evolve from traditional RPA script writing to **Automation Engineering**. You won't be building a screen-scraping bot that mimics human clicks. Instead, you'll learn to architect an enterprise-grade, headless Python backend. 

By the end of this journey, you will have built a resilient, API-driven solution that validates data mathematically, survives network crashes autonomously, and protects itself from insecure code—delivering a bulletproof solution that the Finance team can truly depend on.

## Prerequisite: Get Your Own Copy of this Repository

<p style="padding: 0.5em 2em; background: #ffd3d3;">⚠️ Before you start writing code, you need your own copy of this project so you can save your work!</p>

1. Click the **Fork This Repository** button below to create a copy in your personal GitHub account.

    <a target="_blank" rel="noopener noreferrer" href="https://github.com/21010/ae-workshop-invoice-processing/fork" style="padding: 0.2em 0.5em; background: #e6eaef; border-radius: .375em; color: #111;" onMouseOver="this.style.background='#D4D6D9'" onMouseOut="this.style.background='#e6eaef'">
        <svg data-component="Octicon" aria-hidden="true" focusable="false" class="octicon octicon-repo-forked" viewBox="0 0 16 16" width="16" height="16" fill="currentColor" display="inline-block" overflow="visible" style="vertical-align:text-bottom"><path d="M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z"></path></svg>
        <b>Fork</b>
    </a>

2. Navigate to *your* new repository.
3. Click the green <span style="background:#1f883d; color: #fff; padding: 0.3em 0.5em; border-radius: .375em; text-wrap:nowrap;">< >  Code ▾</span> button **on your repository**
4. Switch to the **Codespaces** tab, and click <span style="background:#1f883d; color: #fff; padding: 0.3em 0.5em; border-radius: .375em; text-wrap:nowrap;">Create codespace on main</span>. 
:warning: Do not create a Codespace on the original repository!

You are all set! Now you can safely commit your progress!

## 1. The Business Request

*You have just received the following email from Sarah in the Finance Department:*

<div style="background:#f1f1f1; padding: 1em 2em; border-radius: 0.375em;">
    <span><b>From:&nbsp;&nbsp;&nbsp;&nbsp;</b> Sarah Jones [sarah.jones@corp.com]
    <br/><b>Subject:</b> Request for a new Excel Macro / Power Automate script for Invoices approval process</span>
    <hr/>
    <span>
        <p>Hi Automation Team,</p>
        <p>We are drowning in vendor invoices and we really need a bot to help us. Right now, my team spends hours clicking through the ERP portal to approve these.</p>
        <p>Can you build a Power Automate Desktop script or maybe an Excel macro that logs into the ERP screen, looks at the list of pending invoices, and clicks "Approve" for each one?</p>
        <p>There are two things the bot needs to check before clicking approve:
            <ul>
                <li>Sometimes the upstream vendor system glitches and the total amount on the invoice doesn't actually match the sum of the individual line items. We need the bot to calculate the math on the screen and make sure it adds up. If it doesn't add up, the bot should skip it so we don't corrupt our ledgers.</li>
                <li>We are only allowed to auto-approve standard invoices. If an invoice is over $10,000, please don't let the bot click approve. Leave those for us to review manually.</li>
            </ul>
        </p>
        <p>Oh, one last thing: the ERP system is really slow and sometimes the webpage crashes with a "503 Error". If that happens, the bot should just refresh the page and try again.</p>
        <p>Thanks!<br/>Sarah (Senior Financial Analyst)</p>
    </span>
</div>

---

### 1.1. The Engineering Reality

Sarah described her problem using a specific, fragile technical solution (a UI-clicking, a macro). As Automation Engineers, we know that UI automation frequently breaks when a website updates. Instead of building a screen-scraping bot, we will solve her underlying business requirements by building a headless, robust, API-driven Python backend.

<p style="background:#eee; padding: .5em 1em; border-radius: .375em;"><b>ℹ️ Caveat</b><br/>
<i>API-driven Python is strictly better *when an API exists*. For legacy mainframe green-screens, SAP GUI without BAPI, or vendor portals lacking REST endpoints, traditional RPA (UI automation) remains the correct architectural choice.</i>
</p>

### 1.2. The Manual Process (As-Is)

*Here is how Sarah's team currently processes invoices manually:*

1. Open the Google Chrome browser and navigate to the ERP portal.
2. Type in the username and password to log in.
3. Click on the `Finance Dashboard` tab.
4. Click on `Pending Vendor Invoices` to load the grid.
5. Click `Export` and select Excel spreadsheet as a format. Save the document on your computer. *Do not close the browser*
6. Open the downloaded Excel spreadsheet.
7. For each invoice in the spreadsheet:
   * Add an Excel formula (`=SUM(...)`) to calculate the sum of all line items for that invoice.
   * Compare the calculated sum to the "Total Amount" listed (if it doesn't match, highlight it in red and skip it).
   * Check if the Total Amount is greater than $10,000 (if it is, skip it so the manager can review it). *(Note: A real AP control set would also include PO three-way match and vendor whitelisting)*
8. Switch back to the open Google Chrome browser.
9. For each valid invoice identified in the spreadsheet (correct math and under $10,000), locate it in the portal grid and click the green "Approve" button.
10. If the website crashes with a 503 error, hit F5 to refresh, log in again, and find where they left off.

---

## 2. Engineering the Solution

Sarah's manual process is slow, error-prone, and mind-numbing. No suprise she wants to automate it! 

However, before we rush into writing code or building the screen-scraping macro she asked for, a true Automation Engineer takes a step back. We must first rigorously analyze the core business problem she is trying to solve, ignoring the specific technical solution she suggested. Only after we have mapped out the logic, the rules, and the failure points will we begin architecting a resilient, enterprise-grade solution from scratch.

Let's put on our Automation Engineer hats and start breaking this down.

<p style="background:#eee; padding: .5em 1em; border-radius: .375em;"><b>ℹ️ ERP API Access</b><br/>
<i>Your workspace is completely empty (except for this guide and a ERP API running in the background on <code>http://127.0.0.1:8080</code>) in your Codespace environment.</i></p>

### 2.1. Process Analysis & Architecture Design

<details>
<summary style="cursor: pointer;"><b>📚 Click here to learn more about: Business Analysis & Domain-Driven Design</b></summary>

#### Business Analysis & Domain-Driven Design (DDD)

##### Understand the Business Domain & Subdomains

Business stakeholders often request software by describing a specific technical solution (e.g., "Build a script to click these buttons"). 

As engineers, our job is to map the actual *Business Domain*. What are the real-world processes, events, and failure conditions? We often break a large domain into *Subdomains* (Core, Supporting, and Generic) to focus our efforts on what truly provides business value.

##### Establish a Ubiquitous Language

An important rule of Domain-Driven Design (DDD) is establishing a "Ubiquitous Language" - a shared, strict vocabulary used consistently by both developers and domain experts.

If the business talks about `Invoices`, `Line Items`, and `Approval Thresholds`, those exact terms must become the core classes and variables in our code. No translating terms between business and engineering.

##### Define Bounded Contexts

A Bounded Context is a strict boundary within which a particular domain model is defined and applicable. 

The concept of an "Invoice" might mean something completely different to the Accounting team compared to the Shipping team. The Bounded Context ensures our Ubiquitous Language remains unambiguous within our specific area of responsibility.

##### Entities and Value Objects

Inside our Bounded Context, we model the world using two primary building blocks:

* **Entities**: Objects with a distinct, persistent identity that thread through time (e.g., an `Invoice` with a unique ID).
* **Value Objects**: Immutable attributes defined only by their properties, without an identity (e.g., a `MonetaryAmount` or a `LineItem` where if two have the same values, they are entirely interchangeable).

##### Aggregates and Aggregate Roots

* **Aggregates**: A cluster of domain objects (Entities and Value Objects) that are treated as a single unit for data changes. They guarantee the consistency of changes. 
* **Aggregate Root**: The only Entity within the Aggregate that outside objects are allowed to hold references to. For example, you wouldn't modify an `Invoice Line Item` directly; you would ask the `Invoice` (the Aggregate Root) to add or remove it, ensuring the `Total Amount` stays perfectly in sync.

##### Repositories and Domain Services

* **Repositories**: Abstractions that handle the retrieval and storage of Aggregates. To the domain logic, a Repository looks like an in-memory collection of objects, completely hiding whether the data actually lives in a SQL database, a REST API, or a flat file.
* **Domain Services**: Stateless operations or business rules that don't naturally fit inside a single Entity or Value Object (e.g., an `InvoiceApprovalService` that orchestrates rules across multiple aggregates).

##### Hexagonal Architecture (Ports and Adapters)

DDD separates the core business rules from the technical implementation. 

The mathematical validation of an Invoice does not care if the data came from a REST API or a database. 

By separating the `Domain` (business rules) from the `Infrastructure` (technical details like HTTP requests), we build software that can survive technological shifts.

Ports and Adapters (also known as Hexagonal Architecture) is a pattern that isolates your core business logic (the hexagon) from outside concerns. 

A "Port" is the interface your application exposes (e.g., fetching an invoice), while an "Adapter" is the technical implementation that plugs into that port (e.g., a REST API client or a SQL database query). 

This decouples your core logic from external dependencies, making the system highly testable and resilient to technology changes.

</details>

---

Before writing code, we must translate Sarah's request into a strict DDD engineering plan. Let's start!

#### Understand the Domain & Identify Risks

<div style="background: #eee; padding: .5em 1em; border: 1px solid #ccc">
    <b> 📋 What are we doing?</b>
    <ul>
        <li>In this section, we break down Sarah's email to map out the actual business reality.</li>
        <li>We will formalize the core workflow she described into a visual flowchart, define a shared vocabulary (the Ubiquitous Language), establish the business entities, and identify the critical failure points (risks) that our software must mitigate.</li>
    </ul>
</div>

##### The Core Workflow (As-Is)

To understand what we are replacing, we first need to visualize Sarah's **As-Is (Current State)** process. 
This is the manual, screen-clicking workflow her team currently suffers through every day. It explicitly highlights the logic her team follows to process invoices, serving as the blueprint for our backend automation.

Acquire pending invoices, verify data integrity (math validation), apply business rules ($10,000 threshold), and execute the approval.

   ```mermaid
   flowchart LR
       A((Start)) --> B(Log into ERP Portal)
       B --> C(Navigate to Pending Invoices)
       C --> D(Export to Excel)
       D --> E{Invoices Remain?}
       E -- Yes --> F(Calculate Sum of Line Items)
       F --> G{Sum == Total?}
       G -- No --> H(Highlight Red - Skip)
       G -- Yes --> I{Total < $10k?}
       I -- No --> J(Skip for Manual Review)
       I -- Yes --> K(Locate in Portal & Approve)
       H --> E
       J --> E
       K --> E
       E -- No --> L((End))
   ```

[todo: should we document5 this in /docs? add instructions for the student]

##### Risks

In Domain-Driven Design, we categorize risks to figure out *where* our code should handle them. Our categorization is a practical extension of DDD principles:

| Risk Category | Description |
| :------------ | :---------- |
| **Domain Risks** | Relate to the core business logic, such as Sarah mentioning the upstream vendor system glitching and sending corrupt invoice math. These must be caught by our core validation rules inside the Domain Entities. |
| **Infrastructure Risks** | Deal with the chaotic outside world, like the ERP portal crashing with 503 errors. These must be handled at the absolute boundary of our application (the Infrastructure Adapters) using resilient network strategies like retries. |
| **Application Risks** (Orchestration Risks) | Relate to the workflow failing mid-process, such as a server restarting while processing an invoice. These are handled in the Application Services layer using transactions, idempotency, or queues. |

[todo: add short narrative on what risks we noticed in our project]

| ID     | Type | Risk | Mitigation |
| :----- | :--- | :--- | :--------- |
| RD01 | Domain Risk | The upstream system occasionally sends corrupted payloads where the math does not add up. | We will implement strict data validation at the absolute boundary of our application to reject bad payloads before they ever reach our core logic. |
| RI01 | Infrastructure Risk | The target ERP API is known to drop connections and throw 503 errors. | We will isolate all API calls and wrap them in an exponential backoff retry loop. |

[todo: should we document this in /docs? add instructions for the student]

#### Define the Ubiquitous Language

Based on Sarah's email, our Domain models must explicitly represent an `Invoice` (Entity) which contains multiple `LineItem`s (Value Objects).

In addition to the `Invoice` and `LineItem`, we also define `Vendor` and `Currency` as important attributes of the domain. It's crucial that our internal Python attributes (e.g., `total_amount`) exactly map to the business vocabulary, avoiding generic or misleading terms.

Additionally, the `Approval Threshold` is a critical part of the Ubiquitous Language. It is not just a random `10000` integer hardcoded in a script; it is a formal Domain concept that dictates whether an invoice is eligible for Auto-Approval or requires Manual Review. We will model this explicitly.

[todo: add a narrative and a table to summarize our ubiquitous language for this project]

[todo: should we document5 this in /docs? add instructions for the student]

#### Map the Architecture Layers

To ensure our solution is robust and can survive technology shifts, we map our components using the **Ports and Adapters** (Hexagonal) architecture. We separate the pure business rules (the Domain) from the technical implementation details (the Infrastructure). 

If Sarah's Finance team decides to switch from this specific ERP system to SAP next year, our Domain rules (e.g., the $10,000 threshold and math validation) won't need to change at all. We will only need to swap out the Infrastructure adapter.

| Layer | Description |
| :---- | :---------- |
| **Infrastructure** | This layer is solely responsible for talking to the unstable external world. It handles the HTTP requests and the retry loops. In our project, this will be an API Client that uses `requests` and `tenacity` to securely interact with the ERP Portal's REST API, protecting the rest of the application from 503 errors and network timeouts. |
| **Domain** | This layer is strictly isolated from the network. It contains our `Invoice` models and the validation rules. |
| **Application** | This is the orchestrator (or Use Case). It fetches data from the Infrastructure, passes it to the Domain for validation, applies the $10,000 threshold rule, and tells the Infrastructure to approve the valid invoices. |

[todo: should we document5 this in /docs? add instructions for the student]

#### Design the Automated Workflow (To-Be)

Now that we have separated our concerns into distinct architectural layers and established our Ubiquitous Language, we can design the **To-Be** workflow. 

Notice how this new diagram maps directly to our layered architecture: fetching invoices happens in the Infrastructure, validating math and applying thresholds happens in the Domain, and the Application orchestrator coordinates the flow. 

Instead of opening Chrome and calculating math, our API-driven Python backend will invisibly and reliably execute the following flow:

[todo: try to optimize this mermaid flow below; should we use some standard uml diagrams instead of a basic flowchart?]

   ```mermaid
   flowchart LR
       subgraph Application [Application Layer - Orchestrator]
           Start((Process Triggered))
           Loop{Invoices Remain?}
           Next(Next Invoice)
           End((Process Complete))
       end
       
       subgraph Infrastructure [Infrastructure Layer - Adapters]
           Fetch(Fetch Pending Invoices via API)
           Approve(Auto-Approve via API)
       end
       
       subgraph Domain [Domain Layer - Core Rules]
           Validate{Is Math Valid?}
           CheckAmount{Amount < $10k?}
           Reject(Reject as Corrupted)
           Manual(Flag for Manual Review)
       end

       Start --> Fetch
       Fetch --> Loop
       Loop -- Yes --> Validate
       Loop -- No --> End
       Validate -- No --> Reject
       Validate -- Yes --> CheckAmount
       CheckAmount -- No --> Manual
       CheckAmount -- Yes --> Approve
       Reject --> Next
       Manual --> Next
       Approve --> Next
       Next --> Loop
   ```

[todo: should we document5 this in /docs? add instructions for the student]

### Project Initialization

<details>
<summary style="cursor: pointer;"><b>📚 Click here to learn more about: Reproducible Environments & The `uv` Package Manager</b></summary>

#### Reproducible Environment & The `uv` Package Manager

##### The Modern Standard (PEP 621)

In legacy Python, developers used `requirements.txt` and struggled with "it works on my machine" bugs. 

Modern Python engineering demands isolated, reproducible environments. The industry standard is now **PEP 621**, which centralizes all project configuration and dependencies into a single file called `pyproject.toml`.

##### Introducing `uv`

To manage these modern projects, we use `uv` - a fast package manager built in Rust by Astral. It replaces `pip`, `venv`, `poetry`, and `pip-tools` entirely.

###### Installation

* *Windows:* `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
* *macOS/Linux:* `curl -LsSf https://astral.sh/uv/install.sh | sh`

###### How it manages virtual environments?

When you run commands like `uv run`, it automatically and implicitly creates an isolated `.venv` folder. It resolves dependencies in milliseconds and uses a global cache so you never download the same package twice.

###### Security (Audit Feature)

`uv` has built-in malware checking to prevent supply chain attacks. You can enable it via environment variables: `export UV_MALWARE_CHECK=1` (Linux) or `$env:UV_MALWARE_CHECK="1"` (Windows).

##### Basic `uv` Commands

* `uv init` - Initializes a new project and creates the `pyproject.toml`.
* `uv add <package>` - Installs a package and adds it to the production dependencies.
* `uv add --dev <package>` - Installs a package only for local development/testing.
* `uv run <command>` - Automatically executes a command *inside* the isolated virtual environment. You never have to manually run `source .venv/bin/activate` again!

[todo: add command to remove package, uv sync, uv lock, uv audit]

##### Anatomy of `pyproject.toml`

Here is how a modern, best-practice configuration looks:

* `[project]`: Defines the project metadata (name, version, python version requirement).
* `dependencies`: An array of required production libraries (e.g., `requests`, `pydantic`). These are what gets shipped to the server.
* `[dependency-groups]`: Defines the `dev` array for local tools (e.g., `pytest`, `ruff`). By cleanly separating dev tools, we ensure our production Docker containers remain small, fast, and secure.
* `[build-system]`: Tells packaging tools how to build your project (e.g., using `hatchling` or `setuptools`). By centralizing this in `pyproject.toml`, Python standardizes project builds and eliminates the need for legacy `setup.py` scripts.
* `[project.scripts]`: Allows you to define command-line entry points for your bot, making it executable from anywhere in the terminal.

</details>

---

[todo: add What are we doing? section to summarize the chapter using the structure:

<div style="background: #eee; padding: .5em 1em; border: 1px solid #ccc">
    <b> 📋 What are we doing?</b>
    <ul>
        <li></li>
        <li></li>
    </ul>
</div>
]

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
<summary style="cursor: pointer;"><b>📚 Click here to learn more about : Shift-Left Security & Tooling</b></summary>

#### Shift-Left Security & Tooling

In legacy RPA and scripting teams, code is often copy-pasted, poorly formatted, and deployed without security reviews. If a developer accidentally hardcodes Sarah's ERP password into a script and uploads it to GitHub, the entire company could be compromised.

Modern engineering relies on **Shift-Left Security**, catching errors and security flaws as early as possible in the development lifecycle (shifting "left" on the timeline). We enforce this using a framework called `pre-commit`.

When you type `git commit`, Git pauses and hands control to `pre-commit`. It runs a gauntlet of automated scanners against your code. If any scanner fails, the commit is instantly blocked. This guarantees that vulnerable or sloppy code cannot enter your repository.

By enforcing these rules locally, you are preparing your codebase for Enterprise CI/CD pipelines (like GitHub Actions or Azure DevOps). Furthermore, clean, standardized, and fully-tested code is an absolute prerequisite for **AI Harness Engineering** (where autonomous AI agents write and refactor code on your behalf). AI models struggle with messy, unformatted spaghetti code, but thrive in strict environments.

Our pre-commit pipeline executes in a specific "Fail-Fast" order using the best tools available in the Python ecosystem:

* **Trufflehog:** A high-speed secrets scanner. It uses heuristics and regex to instantly block commits containing hardcoded API keys, passwords, or tokens.
* **Ruff (`check --fix` and `format`):** Built in Rust, Ruff is 10-100x faster than legacy tools like `flake8` and `black`. It automatically fixes syntax errors, removes unused imports, and enforces strict, uniform code formatting.
* **Bandit:** A static application security testing (SAST) tool designed to find common security issues in Python code (e.g., using `eval()` or weak cryptographic hashes).
* **Pyrefly:** An advanced static analysis tool that detects "code smells" and suggests modern Python refactoring patterns.
* **uv audit:** Scans your `uv.lock` file against vulnerability databases to ensure none of your installed dependencies have known security exploits (CVEs).
* **Pytest:** The industry standard testing framework. Running unit tests as the final pre-commit hook ensures developers cannot push code that breaks core business logic.

[todo: verify and update this section to follow the best practices of configuring pre-commit pipeline: order, tools; analyze our existing pre-commit configuration; remember to keep pyrefly instead of mypy or pyright]

</details>

---

[todo: add What are we doing? section to summarize the chapter using the structure:

<div style="background: #eee; padding: .5em 1em; border: 1px solid #ccc">
    <b> 📋 What are we doing?</b>
    <ul>
        <li></li>
        <li></li>
    </ul>
</div>
]

Now that our environment is built, we need to protect it. We are going to set up automated guardrails so that nobody on your team can ever commit sloppy or insecure code.

#### Enforce the modern 'main' branch standard

When you ran `uv init` in Step 1, it automatically initialized a Git repository for you behind the scenes. However, older Git configurations often default to the legacy `master` branch. Let's rename it to the modern industry standard `main`.

```bash
git branch -M main
```

[todo: shouldn't we initial commit the project to store what we already done? add the instruction for the studnet to commit; explain best practices how to prepare commits that aligns with modern tools like gitlint]

#### Set up the automated security gates

Create a file named `.pre-commit-config.yaml` in the root directory.

**Connecting the tools** 

We are now configuring Git to execute a powerful pipeline of automated security and formatting gates.
We leverage official pre-commit hooks (like the standalone `trufflehog` v3 hook) and force Git to execute our locally installed `--dev` tools (like `uv audit` and `pytest-unit`) via `uv run`.
This guarantees that formatting tools (`ruff`) and static analyzers (`bandit`, `pyrefly`) run flawlessly inside our isolated environment. We've also included `gitlint` to keep our commit messages clean!

[todo: update this section to reflect changes; use our existing pre-commit-config.yaml file as a template]

<details>
<summary style="cursor: pointer;"><b>💡 Click here to copy the pre-commit configuration</b></summary>

```yaml
fail_fast: true
repos:
  - repo: https://github.com/trufflesecurity/trufflehog
    rev: v3.88.10
    hooks:
      - id: trufflehog

  - repo: local
    hooks:
      - id: uv-audit
        name: uv audit
        entry: uv audit
        language: system
        pass_filenames: false
        always_run: true

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: check-added-large-files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [ --fix ]
      - id: ruff-format

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.8
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
        additional_dependencies: ["bandit[toml]"]

  - repo: local
    hooks:
      - id: pyrefly
        name: pyrefly
        entry: uv run pyrefly
        language: system
        types: [python]
        require_serial: true

      - id: pytest-unit
        name: pytest unit
        entry: uv run pytest -m unit
        language: system
        pass_filenames: false
        always_run: true

  - repo: https://github.com/jorisroovers/gitlint
    rev: v0.19.1
    hooks:
      - id: gitlint
```

</details>

#### Install the hooks into Git

Finally, we must tell Git to actually read the file we just created. Run the command below. From this moment on, your code will be automatically scanned every single time you try to commit!

```bash
uv run pre-commit install
```

[todo: shouldn't the student run pre-commit to check how it works? note that the first time it will take longer and explain why]

### Architecting the Foundation (DDD & Testing)

<details>
<summary style="cursor: pointer;"><b>📚 Click here to learn more about: Domain-Driven Isolation & Test Strategies</b></summary>

#### Domain-Driven Isolation & Test Strategies

[todo: add short introductory to the topic here]

##### Structuring Domain-Driven Design (DDD)

Based on our design, we must physically construct the folders that enforce our architecture. We divide our code into:

* **Domain (`src/domain`):** Pure Python business rules. It has absolutely zero dependencies on the outside world.
* **Infrastructure (`src/infrastructure`):** The "adapter" layer that talks to the chaotic external world (network APIs, databases, UI).
* **Application (`src/application`):** The Use-Case orchestrator that fetches data via the Infrastructure and passes it to the Domain.

##### The Magic of `__init__.py`

In Python, a folder is just a folder until you add an `__init__.py` file. This file tells Python, "Treat this directory as an importable module."

Beyond just marking a directory, modern engineers use `__init__.py` to control the public API of their modules. For example, by putting `from .models import Invoice` inside `src/domain/__init__.py`, other files can simply run `from src.domain import Invoice` instead of digging into nested sub-files.

##### Testing Categories (The Testing Pyramid)

A robust automation project uses multiple layers of tests to ensure stability:

| Test Type | Description | When to use? |
| :-------- | :---------- | :----------- |
| Unit (`tests/unit`) | Tests a single function or class in total isolation (e.g., verifying invoice math). These run in milliseconds and never touch a network or database. | [todo: fill in] |
| Integration (`tests/integration`) | Tests how multiple internal components interact (e.g., the Application orchestrator calling the Infrastructure). This is where we heavily use **Mocking** (faking API responses) so tests remain fast without hitting real servers. | [todo: fill in] |
| System / End-to-End (`tests/e2e`) | Tests the entire system from start to finish hitting the actual staging ERP system. | [todo: fill in] |
| Smoke (`tests/smoke`) | A very fast subset of critical tests run immediately after deployment to ensure the application starts up and didn't "catch fire". | [todo: fill in] |
| Regression (`tests/regression`) | Tests specifically written to reproduce past bugs, ensuring that adding new features never breaks old fixes. | [todo: fill in] |
| User Acceptance Tests (UAT) | Tests that validate the software actually solves the business problem. | [todo: fill in] |

[todo: verify if this section follow best pracices and standards; update if something is missing or the description is incorrect/incomplete]

##### Pytest Best Practices & `conftest.py`

* **Naming Conventions:** Pytest will only discover your tests if the file starts with `test_` (e.g., `test_invoice.py`) and the function starts with `test_` (e.g., `def test_math_validation():`).
* **The `conftest.py` File:** If you have data (like a fake test invoice) that you need across multiple test files, you put it in a file named `conftest.py` as a "Fixture". Pytest automatically injects these fixtures into any test function that asks for them by name, keeping your code incredibly DRY (Don't Repeat Yourself).

*Example `conftest.py`:*

```python
import pytest


@pytest.fixture
def fake_invoice():
    return {"id": "INV-100", "total": 500}
```

*Example Test (`test_invoice.py`):*

```python
    def test_invoice_total(fake_invoice):
        # Pytest automatically passes the dictionary here!
        assert fake_invoice["total"] == 500
```

##### Setting up VS Code for Pytest

To run tests natively inside the VS Code "Testing" sidebar, you can manually create a `.vscode/settings.json` file telling the editor to use Pytest instead of the default `unittest` framework:

```json
    {
        "python.testing.pytestEnabled": true,
        "python.testing.unittestEnabled": false,
        "python.testing.pytestArgs": ["tests"]
    }
```

[todo: analyze our existing config in .vscode/settings.json and add other values in settings.json required by vs code to detect the environment properly]


</details>

---

[todo: add What are we doing? section to summarize the chapter using the structure:

<div style="background: #eee; padding: .5em 1em; border: 1px solid #ccc">
    <b> 📋 What are we doing?</b>
    <ul>
        <li></li>
        <li></li>
    </ul>
</div>
]

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

We told our `pre-commit` hook to only run tests marked as `unit`. We must register this custom label in our `pyproject.toml` so Pytest understands it. 

Open `pyproject.toml` and add this block to the bottom:

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
<summary style="cursor: pointer;"><b>📚 Click here to learn more about: Defensive Data Modeling & Pydantic</b></summary>

#### Defensive Data Modeling & Pydantic

##### The Flaw of Generic Dictionaries

In legacy automation, developers often passed raw JSON data around using generic Python dictionaries (e.g., `invoice["total_amount"]`). This is dangerous. If the ERP system unexpectedly changes the API and sends a string `"100.00"` instead of a float `100.00`, your bot will crash deep inside the code during a math operation.

##### The Pydantic Way

Pydantic is the industry standard library for data validation. Instead of dictionaries, we define our Domain entities as strict Python classes using `BaseModel`.

* **Automatic Type Casting:** If Pydantic expects a `float` but receives the string `"100.00"`, it will automatically convert it to a float. If it receives something uncastable (like `"UNKNOWN"`), it instantly throws a loud validation error *at the boundary* of the application, rather than failing silently later.
* **IntelliSense:** Because they are strict classes, your IDE (VS Code) will auto-complete `invoice.total_amount` for you, eliminating spelling typos.
* **Custom Validators:** You can write custom Python methods decorated with `@model_validator` to enforce complex business rules. There are two critical modes:
    * `mode="before"`: Runs *before* Pydantic does its automatic type casting. The data you receive is a raw dictionary. Use this if you need to mutate or clean up the raw payload before parsing (e.g., stripping whitespace).
    * `mode="after"`: Runs *after* Pydantic has validated all types. The data you receive is a fully instantiated Python object. **This is best for business logic.**
* **Field Constraints & Aliases:** Using the `Field()` function, you can enforce strict constraints directly on attributes without writing custom methods (e.g., `Field(ge=0)` ensures a number is greater than or equal to zero). You can also use `alias` to map messy external API keys (like `empId`) to clean internal Python variables (like `employee_id`).

*Example: Defining a strict Domain Model with Fields and Validators*

```python
from pydantic import BaseModel, model_validator, Field


class Employee(BaseModel):
    # Use alias for bad external keys, and gt=0 to enforce positive numbers
    employee_id: int = Field(alias="empId", gt=0)
    name: str
    # Constraints: age must be between 18 and 65
    age: int = Field(ge=18, le=65)
    is_active: bool = Field(default=True)

    @model_validator(mode="before")
    @classmethod
    def clean_raw_data(cls, data: dict):
        # Runs first! We clean the raw dictionary before Pydantic sees it.
        if "name" in data and isinstance(data["name"], str):
            data["name"] = data["name"].strip().title()
        return data


# Instantiating the model with raw, messy external JSON data
raw_data = {"empId": "404", "name": "   sarah   ", "age": "25"}
sarah = Employee(**raw_data)

# The object is now perfectly clean and safe to use!
# sarah.employee_id -> 404 (int)
# sarah.name -> "Sarah" (str)
```

##### Best Practices

* Never use raw dictionaries for business logic. Always parse external JSON directly into a Pydantic model immediately after downloading it.
* Keep your models "pure". A Pydantic model should only validate data; it should never make database queries or API calls itself.

[todo: verify if we list all best practicies of working with data and pydantic (what about pydantic way?)]

##### Preparation for AI Agents

Strict data modeling is the absolute prerequisite for building **AI Agents** or LLM harnesses. Large Language Models often hallucinate or generate slightly malformed JSON. By forcing the LLM's output through a strict Pydantic model, you guarantee that your underlying Python code never receives corrupted AI output. In fact, modern AI frameworks (like LangChain or OpenAI's SDK) rely on Pydantic natively to force the LLM to adhere to specific schemas!

</details>

---

[todo: add What are we doing? section to summarize the chapter using the structure:

<div style="background: #eee; padding: .5em 1em; border: 1px solid #ccc">
    <b> 📋 What are we doing?</b>
    <ul>
        <li></li>
        <li></li>
    </ul>
</div>
]

Sarah's business requirement explicitly stated that the ERP math is sometimes corrupted. We cannot trust the incoming data. We are going to build an impenetrable wall in our `domain` layer that strictly validates every single invoice before the orchestrator is even allowed to look at it.

#### Create the Data Models (`src/domain/models.py`)

[todo: refine the description to explain what we need to do and why, before we challenge the students and ask them to prepare models with validation.]

First we need to create the strict definitions for `LineItem` and `Invoice`.
We are also writing a custom validator to explicitly perform the math check that Sarah requested.

<div style="background:#f0ffc0; padding: .5em 1em; 0 1em;">
    <b>🧩 CHALLENGE</b>
    <ol>
        <li>Try to write the <code>LineItem</code> and <code>Invoice</code> Pydantic models yourself!</li>
        <li>Use the <code>@model_validator(mode="after")</code> decorator to sum the line items and raise a <code>ValueError</code> if the math is wrong.</li>
    </ol>
</div>

<details>
<summary style="cursor: pointer;"><b>💡 Click here for hints</b></summary>

**Hints:**

* You will need to use the `@model_validator(mode="after")` decorator. This ensures Pydantic casts all the types first so you can safely iterate over `self.line_items`. 
* You can sum the amounts using a generator expression like `sum(item.amount for item in self.line_items)`.

<details>
<summary style="cursor: pointer;"><b>💡 Still stuck? Click here for a code scaffold</b></summary>

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
<summary style="cursor: pointer;"><b>💡 Click here to show the full solution snippet</b></summary>

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

[todo: refine the description to explay what must be done and why before we challenge the studnets to rite the code]

We are practicing Test-Driven Development (TDD).
Before we connect to the real API, we write a lightning-fast unit test simulating a corrupted invoice to definitively prove that our Pydantic model will reject it.

<div style="background:#f0ffc0; padding: .5em 1em; 0 1em;">
    <b>🧩 CHALLENGE</b>
    <ol>
        <li>Write a Pytest function labeled <code>@pytest.mark.unit</code>.</li>
        <li>Create an invoice with bad math and use <code>with pytest.raises(ValueError):</code> to prove your validation catches it!</li>
    </ol>
</div>

<details>
<summary style="cursor: pointer;"><b>💡 Click here for hints</b></summary>

**Hints:**

* Use the `Invoice` class you just created.
* Pass in invalid `total_amount` data intentionally.
* Wrap the object creation inside a `with pytest.raises(ValueError):` context manager.

<details>
<summary style="cursor: pointer;"><b>💡 Click here to show the solution snippet</b></summary>

```python
import pytest
from src.domain.models import Invoice, LineItem

@pytest.mark.unit
def test_bad_math_is_rejected():
    with pytest.raises(ValueError):
        # TODO: initialize `Invoive` with corrupted data - total_amount != sum of amount in line_items
```

<details>
    <summary style="cursor: pointer;"><b>💡 Click here to show the full solution snippet</b></summary>

    ```python
    import pytest
    from src.domain.models import Invoice, LineItem


    @pytest.mark.unit
    def test_bad_math_is_rejected():
        with pytest.raises(ValueError):
            Invoice(
                id="1",
                vendor="A",
                currency="USD",
                line_items=[LineItem(description="Item", amount=50)],
                total_amount=9000,  # Data Corruption!
            )
    ```

</details>
</details>
</details>

#### Run the Defense Test

Execute the unit test to verify your math validator works perfectly.

```bash
uv run pytest -m unit
```

### Preparing the Infrastructure (Bridging the Unstable Outside World)

<details>
<summary style="cursor: pointer;"><b>📚 Click here to learn more about: 12-Factor Apps, REST, and Network Resilience</b></summary>

#### 12-Factor Apps, REST API, and Network Resilience

##### The 12-Factor App: Backing Services & Config

In Domain-Driven Design, the Infrastructure layer is the absolute edge of your application. It is the only place allowed to talk to the chaotic outside world. The **12-Factor App** methodology states:

* **Backing Services:** Treat databases and APIs as attached resources. If the ERP system goes down, your app should gracefully wait, retry or report, not crash.
* **Config:** Credentials (like API keys) must be injected via Environment Variables or get as a Secrets from the credential vault, never hardcoded in the script.

##### REST API Basics & HTTP Status Codes

Modern systems communicate via REST (Representational State Transfer) using standard HTTP verbs:

| Verb | Description |
| :--- | :---------- |
| `GET` | Retrieve data (e.g., fetch invoices). Must be **Idempotent** (running it 100 times doesn't change anything). |
| `POST` | Create data or trigger actions (e.g., approve an invoice). Not inherently idempotent. |
| `PUT` | Update or replace an entire existing resource (e.g., updating an invoice record). Idempotent. |
| `PATCH` | Partially update an existing resource. Not strictly idempotent. |
| `DELETE` | Remove a resource from the server. |

You must understand HTTP Status Codes to build resilient bots:

| Code | Status |
| :--- | :----- |
| `200 OK` / `201 Created` | Success! |
| `301 Moved Permanently` / `302 Found` | The resource has been moved. Most Python clients (like `requests`) will follow these redirects automatically. |
| `400 Bad Request` | You sent bad data (e.g., malformed JSON). |
| `401 Unauthorized` / `403 Forbidden` | Your API key is invalid or lacks permissions. |
| `404 Not Found` | The URL is wrong or the record doesn't exist. |
| `500 Internal Server Error` | The server crashed (a bug on their end). |
| `503 Service Unavailable` | The server is overloaded (Sarah's exact problem!). |

##### Best Practices for REST API in Python

* **Always Set Timeouts:** If the ERP system hangs forever, your bot will hang forever. Always use `requests.get(url, timeout=10)`.
* **Raise for Status:** Always call `response.raise_for_status()` to instantly throw an exception if you get a 4XX or 5XX code.

[todo: analyze if we list all best practices for working with REST API]

*Example: A perfect REST request*

```python
import requests

headers = {"Authorization": "Bearer YOUR_ENV_VAR_TOKEN"}
response = requests.get("https://api.erp.com/invoices", headers=headers, timeout=10)
response.raise_for_status()  # Throws HTTPError if not 200 OK
data = response.json()
```

##### OpenAPI (Swagger)

How do you know what endpoints a REST API has?

Modern APIs implement the **OpenAPI Specification** (often referred to as Swagger). This provides an interactive web page (usually hosted at `/docs` or `/swagger`) that acts as a living contract. You can use it to see exactly what URLs are available, what JSON payloads they require, and even test them directly in your browser.

##### Defeating 503 Errors with `tenacity`

When a 503 error happens, we shouldn't write custom `while` loops with `time.sleep()`. Instead, we use the `tenacity` library to automatically retry with **Exponential Backoff** (waiting 1s, then 2s, then 4s to avoid overwhelming the struggling server).

*Example: Exponential Backoff*

```python
from tenacity import retry, stop_after_attempt, wait_exponential


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def dangerous_network_call():
    # If this raises an exception, Tenacity intercepts it and tries again!
    ...
```

</details>

---

[todo: add What are we doing? section to summarize the chapter using the structure:

<div style="background: #eee; padding: .5em 1em; border: 1px solid #ccc">
    <b> 📋 What are we doing?</b>
    <ul>
        <li></li>
        <li></li>
    </ul>
</div>
]

Sarah's primary complaint was that the ERP system randomly throws `503 Service Unavailable` errors during peak hours, causing her legacy macro to crash instantly. We are going to build an API client that uses exponential backoff to patiently wait out the crashes, and automatically casts the raw JSON into the bulletproof Pydantic models we built in Step 4.

#### Analyze the ERP API (Swagger)

[todo: add description what must be done and why before we will challenge the students and ask to analyze the API documentation.]

<div style="background:#f0ffc0; padding: .5em 1em; 0 1em;">
    <b>🧩 CHALLENGE</b>
    <ol>
        <li>The ERP system is running locally on port <code>8080</code>. If you are using <b>GitHub Codespaces</b>, open the <b>Ports</b> tab (next to your Terminal), find Port <code>8080</code>, and click the <code>Open in Browser</code> globe icon. Then, add </code>/docs</code> to the end of the URL in your browser.</li>
        <li>Read the OpenAPI contract to discover the exact HTTP verbs and endpoints needed to fetch pending invoices and approve them!</li>
    </ol>
</div>

[todo: should we add hints here?]

#### Create the API Client (`src/infrastructure/api_client.py`)

[todo: refine the description to explain what must be done and why before the challenge]

We are building the `APIClient`. We use `requests` to handle the HTTP protocol, ensuring we set a strict `timeout` on every call.
We then decorate our POST request with `@retry` to guarantee it survives Sarah's dreaded 503 errors.

<div style="background:#f0ffc0; padding: .5em 1em; 0 1em;">
    <b>🧩 CHALLENGE</b>
    <ol>
        <li>Build the client using the endpoints you discovered in the Swagger UI.</li>
        <li>Automatically cast the JSON response into your Pydantic <code>Invoice</code> models!</li>
    </ol>
</div>

<details>
<summary style="cursor: pointer;"><b>💡 Click here for hints</b></summary>

**Hints:**

* Use `requests.get()` to fetch the data (check the Swagger UI at `/docs` for the exact endpoint URL).
* Remember that because of our strict Pydantic model, initializing `Invoice` might throw a `ValueError` if the math is corrupted! Wrap that line in a `try/except` block so you can log the error and `continue` to the next invoice.

<details>
<summary style="cursor: pointer;"><b>💡 Still stuck? Click here for a code scaffold</b></summary>

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
    <summary style="cursor: pointer;"><b>💡 Click here to show the full solution snippet</b></summary>

    ```python
    import requests
    from tenacity import retry, stop_after_attempt, wait_exponential
    from src.domain.models import Invoice


    class FastAPIClient:
        def fetch_pending_invoices(self) -> list[Invoice]:
            response = requests.get("http://127.0.0.1:8080/api/invoices/pending", timeout=10)
            response.raise_for_status()

            valid_invoices = []
            for item in response.json():
                try:
                    valid_invoices.append(Invoice(**item))
                except ValueError as e:
                    # Log or print the error and skip this corrupted invoice
                    print(f"Skipping corrupted invoice: {e}")
                    continue

            return valid_invoices

        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
        def approve_invoice(self, invoice_id: str) -> bool:
            response = requests.post(f"http://127.0.0.1:8080/api/invoices/{invoice_id}/approve", timeout=10)
            response.raise_for_status()
            return True
    ```

</details>
</details>
</details>

#### Configure the ERP Mock Data (`tests/conftest.py`)

[todo: refine the description to explain what must be done and why before we challenge the students to write the code]

We are creating a reusable Pytest fixture containing the raw JSON dictionary that the ERP system normally returns. Any test can now access this fake data!

[todo: restore the challenge description here]

<details>
<summary style="cursor: pointer;"><b>💡 Click here for hints</b></summary>

**Hints:**

* Use the `@pytest.fixture` decorator above a function named `mock_erp_json`.
* Return a list containing a single dictionary representing an invoice payload (include fields like `id`, `vendor`, `currency`, `line_items`, and `total_amount`).

<details>
    <summary style="cursor: pointer;"><b>💡 Click here to show the full solution snippet</b></summary>

    ```python
    import pytest


    @pytest.fixture
    def mock_erp_json():
        return [
            {
                "id": "INV-MOCK",
                "vendor": "TestVendor",
                "currency": "USD",
                "line_items": [{"description": "Service", "amount": 100}],
                "total_amount": 100,
            }
        ]
    ```

</details>
</details>

#### Prove the Infrastructure Works (`tests/unit/test_api_client.py`)

[todo: refine the description to explain what must be done and why before we challenge the students to write the code]

We write a Unit test. Notice how we inject `mock_erp_json` into the function, and use `@patch` to intercept `requests.get`. We tell the intercepted request to return our fake JSON instead of hitting the network!

<div style="background:#f0ffc0; padding: .5em 1em; 0 1em;">
    <b>🧩 CHALLENGE</b>
    <ol>
        <li>Create a unit test labeled <code>@pytest.mark.unit</code>.</li>
        <li>Use <code>@patch</code> and your <code>mock_erp_json</code> fixture to assert that your client correctly parses the fake data into a Pydantic model.</li>
    </ol>
</div>

<details>
<summary style="cursor: pointer;"><b>💡 Click here for hints</b></summary>

**Hints:**

* Use `@patch("src.infrastructure.api_client.requests.get")`.
* Create a `Mock()` object, set its `.json.return_value` to `mock_erp_json`, and assign it to `mock_get.return_value`.

<details>
<summary style="cursor: pointer;"><b>💡 Click here to show the solution snippet</b></summary>

```python
[todo: prepare a solution scalfold]
```

<details>
<summary style="cursor: pointer;"><b>💡 Click here to show the full solution snippet</b></summary>

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
</details>

#### Run the Unit Test

Execute the test to verify your mocking logic works perfectly.

```bash
uv run pytest -m unit
```

#### Test API Resilience (`tests/unit/test_api_client.py`)

[todo: refine the description to explain what must be done and why before we challenge the studnet to write the code]

We are proving that if the ERP sends a corrupted invoice (e.g. bad math), our `APIClient` catches the `ValueError` from Pydantic and skips it instead of crashing.

[todo: restore the challenge]

<details>
<summary style="cursor: pointer;"><b>💡 Click here for hints</b></summary>

**Hints:**

* Similar to the previous test, but return a list with two invoice dictionaries: one with correct math and one with corrupted math.
* Assert that the client returns only a single valid invoice.

<details>
<summary style="cursor: pointer;"><b>💡 Click here to show the solution snippet</b></summary>

```python
[todo: prepare the solution scalfold]
```
<details>
<summary style="cursor: pointer;"><b>💡 Click here to show the full solution snippet</b></summary>

```python
@pytest.mark.unit
@patch("src.infrastructure.api_client.requests.get")
def test_fetch_pending_invoices_skips_corrupted_invoice(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = [
        {"id": "GOOD-1", "vendor": "A", "currency": "USD", "line_items": [{"description": "X", "amount": 100}], "total_amount": 100},
        {"id": "BAD-1", "vendor": "A", "currency": "USD", "line_items": [{"description": "X", "amount": 100}], "total_amount": 9999},
    ]
    mock_get.return_value = mock_response
    invoices = APIClient().fetch_pending_invoices()
    assert [inv.id for inv in invoices] == ["GOOD-1"]
```

</details>
</details>
</details>

### The Orchestrator (SOLID Principles in Action)

<details>
<summary style="cursor: pointer;"><b>📚 Click here to learn more about: SOLID Principles & Python Protocols</b></summary>

#### SOLID Principles

SOLID is an acronym for five design principles that make software maintainable. In automation, two are absolutely critical:

* **(S) Single Responsibility Principle:** A class should do one thing.
    * *Bad:* A massive "Bot" script that fetches API data, calculates math, and updates an Excel report all in one 500-line file.

        ```python
        [todo: add bad example]
        ```

    * *Good:* Our DDD structure! `models.py` strictly handles math. `api_client.py` strictly handles networking.

        ```python
        [todo: add good example]
        ```

* (O) Open/Closed [todo: fill in]

* (L) Liskov Substitution & Interface Segregation: While less critical for this specific orchestrator, the remaining principles ensure our interfaces remain small and interchangeable. A mock API client used in tests should be perfectly substitutable for the real `APIClient` without the Orchestrator knowing the difference.

* (I) [todo: fill in]

* **(D) Dependency Inversion Principle:** High-level logic should not depend on low-level implementation details.
    * *Bad (Tightly Coupled):*

        ```python
        # If the UK office forces us to use SAP next year, we have to rewrite this entire core class!
        from infrastructure.api_client import FastAPIClient


        class Orchestrator:
            def __init__(self):
                self.client = FastAPIClient()  # Hardcoded dependency!
         ```

    * *Good (Loosely Coupled):* The Orchestrator asks for "something" that can fetch invoices, injected via the `__init__` constructor.

        ```python
        [todo: add a good example here]
        ```

#### Python Protocols (Duck Typing)

How do we enforce the "Good" example of (D) Dependency Inversion Principle in Python?

We use `typing.Protocol`. A Protocol defines an interface without writing any implementation code. It relies on "Duck Typing" (if it walks like a duck and quacks like a duck, it is a duck).

*When to use it:* When you want to decouple your orchestrator from specific technologies (like FastAPI, SAP, or a fake database for testing).

*Example: Defining a Protocol*

```python
from typing import Protocol


class InvoiceFetcher(Protocol):
    # We don't care HOW you fetch it, just that you have this method signature.
    def fetch(self) -> list: ...

    class Orchestrator:
        # We can pass ANY class in here (FastAPIClient, SAPClient), as long as it has a fetch() method!
        def __init__(self, fetcher: InvoiceFetcher):
            self.fetcher = fetcher
```

</details>

---

[todo: add What are we doing? section to summarize the chapter using the structure:

<div style="background: #eee; padding: .5em 1em; border: 1px solid #ccc">
    <b> 📋 What are we doing?</b>
    <ul>
        <li></li>
        <li></li>
    </ul>
</div>
]

In Sarah's email, she hinted that if this tool is successful, management might deploy it globally. This means next year, the bot might have to talk to SAP or Oracle instead of this custom ERP. By using Dependency Inversion and a `Protocol`, we can build an orchestrator that will survive that future migration without changing a single line of core business logic!

#### Create the Application Orchestrator (`src/application/processor.py`)

[todo: refine the description to explain what must be done and why before we challenge the students to write a code.]

* We define an `InvoiceAPIClient(Protocol)` interface.
* Then, we build the `InvoiceProcessor` orchestrator and inject the client via the `__init__` method.
* Finally, the `run()` method applies Sarah's final business rule: only approve invoices strictly under the $10,000 threshold.

<div style="background:#f0ffc0; padding: .5em 1em; 0 1em;">
    <b>🧩 CHALLENGE</b>
    <ol>
        <li>Create an <code>InvoiceProcessor</code>. Define an <code>InvoiceAPIClient(Protocol)</code> rather than importing the FastAPI client.</li>
        <li>Write a <code>run()</code> method that loops through the invoices and approves them.</li>
    </ol>
</div>

<details>
<summary style="cursor: pointer;"><b>💡 Click here for hints</b></summary>

**Hints:**

* Call `self.api_client.fetch_pending_invoices()` to get the list, then loop through it.
* Use an `if` statement to check if `total_amount > self.threshold`.
* Remember that network calls can fail—wrap `self.api_client.approve_invoice(inv.id)` in a `try/except Exception` block so a transient error doesn't crash your entire batch!

<details>
<summary style="cursor: pointer;"><b>💡 Still stuck? Click here for a code scaffold</b></summary>

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
<summary style="cursor: pointer;"><b>💡 Click here to show the full solution snippet</b></summary>

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
<summary style="cursor: pointer;"><b>📚 Click here to learn more about: CUPID Principles & Integration Testing</b></summary>

#### CUPID Principles

While SOLID focuses on class design, **CUPID** focuses on joyful developer experiences.

* **C**omposable: Code that plays well with others (our Orchestrator takes any API Client).
* **U**nix Philosophy: Do one thing well.
* **P**redictable: Tests should pass 100% of the time. (Networks are unpredictable, which is why we mock them).
* **I**diomatic: Writing Pythonic code (like using `Protocol`).
* **D**omain-based: Structuring folders by business domain.

[todo: analyze if we can/should add good/bad examples to each principle]

#### Integration Testing

To build a reliable bot, we discuss all three layers (though this workshop only builds Unit and Integration tests):

* **Unit Tests (Step 4 & 5):** We tested our Pydantic math in total isolation. We tested our `APIClient` by mocking the `requests` library.
* **Integration Tests (This Step):** Here, we test the **wiring** between our Application Orchestrator and our Domain models. Does the Orchestrator correctly apply the $10,000 threshold rule?
* **End-to-End (E2E) Tests (Next Step):** Does the entire script actually work when we hit the real ERP system?

#### Fakes vs Mocks

In Step 5, we used a `Mock` to dynamically intercept a Python library (`requests`). In this step, we will build a `Fake`—a lightweight, working implementation of our `InvoiceAPIClient` Protocol that just stores data in a Python list instead of sending it over the internet. This is much cleaner and faster for orchestrator testing!

[todo: refine this section to focus on Integration testing and how they link to CUPID]

</details>

---

[todo: add What are we doing? section to summarize the chapter using the structure:

<div style="background: #eee; padding: .5em 1em; border: 1px solid #ccc">
    <b> 📋 What are we doing?</b>
    <ul>
        <li></li>
        <li></li>
    </ul>
</div>
]

Sarah needs proof that the bot won't accidentally approve a $50,000 invoice. Because we engineered a clean DDD architecture, we can prove this instantly. We will build a Fake API client that feeds the Orchestrator a cheap invoice and an expensive invoice.

#### Create the Fake Client (`tests/conftest.py`)

[todo: refine the description below to explain what must be done and why before we challenge the students to write a code.]

In Step 3, we learned that `conftest.py` is the home for reusable test fixtures. We are building a `FakeAPIClient` that implements our Protocol, but returns memory invoices instead of hitting the network.
By making it a `@pytest.fixture`, any test in our project can instantly request it!

<div style="background:#f0ffc0; padding: .5em 1em; 0 1em;">
    <b>🧩 CHALLENGE</b>
    <ol>
        <li>Open <code>tests/conftest.py</code>. Write a <code>FakeAPIClient</code> class with a <code>fetch_pending_invoices</code> method returning two fake invoices (one under $10,000, one over).</li>
        <li>Create a fixture function that returns an instance of it.</li>
    </ol>
</div>

<details>
<summary style="cursor: pointer;"><b>💡 Click here for hints</b></summary>

**Hints:**

* Create an `Orchestrator` class that accepts `api_client` via its `__init__` method.
* Write a `run()` method that fetches invoices, checks if the amount is > 10000, and calls `approve_invoice()` for valid ones.
* Use `logging.info()` or `logging.warning()` to track the states.

<details>
<summary style="cursor: pointer;"><b>💡 Click here to show the solution snippet</b></summary>

```python
import pytest
from src.domain.models import Invoice, LineItem


class FakeAPIClient:
def __init__(self):
    self.approved_invoices = []

def fetch_pending_invoices(self):
    # TODO: hoardoce a cheap and an expensive invoice here so we can test that the Orchestrator applies the business rule correctly!

def approve_invoice(self, invoice_id: str):
    # TODO: implement the fuction that append the ivoce_id to the self.approved_invoices and returns True


@pytest.fixture
def fake_api():
# TODO: return an instance of newly created FakeAPIClient
```

<details>
<summary style="cursor: pointer;"><b>💡 Click here to show the full solution snippet</b></summary>

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
            Invoice(id="EXPENSIVE-1", vendor="A", currency="USD", line_items=[LineItem(description="X", amount=20000)], total_amount=20000),
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
</details>

#### Write the Integration Test (`tests/integration/test_processor.py`)

[todo: refine the description to explain what must be done and why before we challenge the students to write the code.]

Notice how we just ask Pytest for the `fake_api` fixture in the function arguments! We inject it into the Orchestrator, run it, and check the fake's internal list to prove it only approved the cheap invoice.

<div style="background:#f0ffc0; padding: .5em 1em; 0 1em;">
    <b>🧩 CHALLENGE</b>
    <ol>
        <li>Create an integration test. Inject the <code>fake_api</code> fixture.</li>
        <li>Run the <code>InvoiceProcessor</code> and assert that "CHEAP-1" is approved and "EXPENSIVE-1" is not!</li>
    </ol>
</div>

<details>
<summary style="cursor: pointer;"><b>💡 Click here for hints</b></summary>

**Hints:**

* Write a test function using `@patch` to mock your `api_client`.
* Create fake invoice instances to return when `fetch_pending_invoices` is called.
* Assert that `approve_invoice` is called the expected number of times based on the invoice amounts.

<details>
<summary style="cursor: pointer;"><b>💡 Click here to show the solution snippet</b></summary>

```python
import pytest
from src.application.processor import InvoiceProcessor


@pytest.mark.integration
def test_processor_approves_under_threshold_only(fake_api):
# Arrange: Inject the Fake infrastructure!
# TODO: initiate a new instance of InvoiceProcessor passing our fake_api 

# Act
# TODO: simple! just use .run() method on the processor

# Assert
# TODO: assert "cheap" invoice is in approved_invoices
# TODO: assert "expensive" invoice is not in approved_invoices
```
<details>
<summary style="cursor: pointer;"><b>💡 Click here to show the full solution snippet</b></summary>

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
</details>

#### Run the Integration Test

Execute the test to verify your Orchestrator logic works perfectly.

```bash
uv run pytest -m integration
```

### The Entry Point (Running the Bot)

<details>
<summary style="cursor: pointer;"><b>📚 Click here to learn more about: Lightweight Entry Points & Integration</b></summary>

#### Lighweight Entry Points

In legacy RPA (like Robocorp), everything—network calls, business logic, math, and configuration—is often jammed into one massive `tasks.py` file.

In our DDD architecture, `task.py` is incredibly "dumb" and lightweight. Its only job is to wire the separated layers together using **Dependency Injection** and hit "Go".

#### Integration

Because our `task.py` is lightweight and our environment is managed by `uv`, we can execute this bot from absolutely anywhere:

* **Terminal:** A developer can manually run it via `uv run task.py`.
* **CI/CD Pipelines:** GitHub Actions, Jenkins, or Azure DevOps Pipelines can run it on a schedule.
* **Data & Automation Orchestrators:** You can easily trigger this script from Apache Airflow, Prefect, or enterprise BPM Engines.
* **Cloud Native Serverless:** You can wrap this execution command inside an Azure Function or trigger it via an Azure Logic App!
* **Power Automate Desktop:** You can run it from PAD flow using `Run DOS command` action or custom action to execute `uv run task.py` and let this robust Python architecture do the heavy lifting without visual spaghetti!

[todo: analyze this section; should we teach about something else here? any best practices? industry standards? enrich if needed]

</details>

---

[todo: add What are we doing? section to summarize the chapter using the structure:

<div style="background: #eee; padding: .5em 1em; border: 1px solid #ccc">
    <b> 📋 What are we doing?</b>
    <ul>
        <li></li>
        <li></li>
    </ul>
</div>
]

The architecture is complete, and we are finally ready to process Sarah's real invoices against the live (mock) ERP system!

#### Create `task.py` in the root directory

[todo: refine the description to explain what must be done and why before we challenge the students to write the code.]

* We are creating the execution script.
* We import our real infrastructure (`APIClient`), inject it into our Orchestrator (`InvoiceProcessor`), and run the process.

Notice how clean and readable this file is!

<div style="background:#f0ffc0; padding: .5em 1em; 0 1em;">
    <b>🧩 CHALLENGE</b>
    <ol>
        <li>Create the main execution file named <code>task.py</code>.</li>
        <li>Import the real <code>APIClient</code> and the <code>InvoiceProcessor</code>.</li>
        <li>Instantiate the client, pass it into the processor, and call <code>run()</code>.</li>
    </ol>
</div>

<details>
<summary style="cursor: pointer;"><b>💡 Click here for hints</b></summary>

**Hints:**

* Configure basic `logging` at the top of your file.
* Instantiate your `APIClient` and pass it to the `Orchestrator`, then call the orchestrator's `run()` method inside a `main()` block.

<details>
<summary style="cursor: pointer;"><b>💡 Click here to show the solution snippet</b></summary>

```python
import logging
from src.infrastructure.api_client import APIClient
from src.application.processor import InvoiceProcessor

# Configure basic logging so we can see the output in the terminal
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main():
print("Starting Invoice Processing Bot...")

# 1. Initialize the real Infrastructure client (Connecting to the outside world!)
# TODO: initiate the APIClient

# 2. Inject the real client into the Application Orchestrator (Dependency Injection)
# TODO: initiate the InvoiceProcessor injecting the real api client

# 3. Execute the core business logic flow
# TODO: .run() the business flow

print("Processing Complete!")


# Standard Python idiom to ensure this only runs when executed directly
if __name__ == "__main__":
main()
```

<details>
<summary style="cursor: pointer;"><b>💡 Click here to show the full solution snippet</b></summary>

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
</details>

#### Execute your completed bot (End-to-End Test)

Run the process using `uv` to ensure it executes inside your isolated virtual environment. This proves the entire system works from end to end!

```bash
uv run task.py
```

### Observability & Enterprise Deployment

<details>
<summary style="cursor: pointer;"><b>📚 Click here to learn more about: Structured Logs & Azure Architecture</b></summary>

#### Structured Logs

##### The 12-Factor App on Logs

Legacy RPA frameworks generate static `log.html` or `stdout.log` files on the local hard drive. The **12-Factor App** principles state this is an anti-pattern. Servers and cloud containers are ephemeral; if the machine dies, your logs are permanently deleted.

Instead, modern bots output **Event Streams** to the terminal (`stdout`), allowing log routers to transport them off-site.

##### Strings vs. Structured JSON

How should you write a log?

* *Bad (Strings):*

    ```python
    import logging

    logger = logging.get_logger()

    logger.info(f"Invoice {inv_id} processed for {amount}")
    ```

    To search for this in Azure, you have to write horrible Regex queries.
* *Good (Structured JSON):* 

    ```python
    import structlog

    logger = structlog.get_logger()

    logger.info("invoice_processed", invoice_id=inv_id, amount=amount)
    ```
    
    This natively outputs a JSON dictionary. You can easily query: `SELECT * FROM logs WHERE amount > 5000`.

##### Contextual Binding (Tracing)

In `structlog`, you can `bind()` context to a logger. If you bind the `invoice_id` at the start of a `for` loop, every single log event fired inside that loop will automatically attach that `invoice_id` to its JSON payload. This creates a perfect audit trace for Azure Application Insights, Datadog, Splunk, or Elasticsearch!

```python
[todo: add practical example]
```

##### Observability Best Practices

* **INFO:** Standard business events (e.g., `invoice_approved`).
* **WARNING:** Expected edge cases that require human intervention (e.g., `manual_review_required`).
* **ERROR:** Unexpected system crashes (e.g., `erp_database_timeout`).

To separate issues, we should define Custom Domain Exceptions (e.g., `class MathValidationError(ValueError): pass`). This allows our orchestrator to catch `MathValidationError` (a business error we can log and skip) differently from a `requests.exceptions.ConnectionError` (a technical error where we should probably abort and alert IT).

[todo: add practical examples in python]

##### Enterprise Deployment (Azure Architecture)

Because we followed DDD and 12-Factor principles, our code is 100% portable. Here is how you deploy it:

* **On-Premises (Hybrid):** Run via PAD flow or Windows Task Scheduler. Use the `azure-monitor-opentelemetry` Python package to pipe your `structlog` stream through the corporate firewall into Azure Application Insights.
* **Cloud Native (Azure Container Apps/AKS):** Package the bot in a `Dockerfile`. Azure automatically intercepts the JSON `stdout` stream from Step 9 with zero code changes!
* **Serverless (Azure Functions):** Wrap `processor.run()` in a Time-Triggered Function.
  * *Template Example:*

    ```python
    import azure.functions as func
    from task import main

    app = func.FunctionApp()


    @app.timer_trigger(schedule="0 */5 * * * *", arg_name="timer", run_on_startup=False)(
        schedule="0 */15 * * * *", arg_name="myTimer"
    )  # Run every 15 minutes
    def erp_bot(myTimer: func.TimerRequest) -> None:
        main()
    ```

* **Low-Code Orchestration (Azure Logic Apps):** If the ERP requires legacy XML SOAP authentication, let a Logic App handle the complex Auth visual flow, and have it trigger your Azure Function purely for the Pydantic math validation.

</details>

---

> Note: You might wonder why we initially used standard `logging` in Step 6 only to replace it now. Standard logging is universally understood, and we wanted to focus purely on Orchestration logic first. Now that our core logic works, we are upgrading to `structlog` to demonstrate enterprise observability best practices.

---

[todo: add What are we doing? section to summarize the chapter using the structure:

<div style="background: #eee; padding: .5em 1em; border: 1px solid #ccc">
    <b> 📋 What are we doing?</b>
    <ul>
        <li></li>
        <li></li>
    </ul>
</div>
]

Sarah loves the bot, but audit season is approaching. She needs a perfectly queryable audit trail showing exactly *why* every invoice was approved or rejected. The legacy `log.html` won't cut it. We are going to implement enterprise-grade Structured JSON logging.

#### Add the modern logging library

[todo: refine the description to explain what must be done and why]

We are installing `structlog`, the industry standard for structured Python logging.

First let's add `structlog` to our dependencies using `uv`.

```bash
uv add structlog
```

#### Refactor your Orchestrator (`src/application/processor.py`)

[todo: refine the description below to explain what must be done and why before we challenge the students to write the code.]

We replace standard `logging` with `structlog`.
Inside the processing loop, we create a bound logger (`log = logger.bind(...)`). Now, every time we log `manual_review_required` or `invoice_approved`, the Invoice ID and Amount are captured in the JSON payload!

<div style="background:#f0ffc0; padding: .5em 1em; 0 1em;">
    <b>🧩 CHALLENGE</b>
    <ol>
        <li>Replace the standard <code>logging</code> with <code>structlog</code>.</li>
        <li><code>bind()</code> variables like <code>invoice_id</code> to the logger so every log line automatically includes that context!</li>
    </ol>
</div>

<details>
<summary style="cursor: pointer;"><b>💡 Click here for hints</b></summary>

**Hints:**

* Import `structlog`.
* Remove the standard `logging` setup.
* Initialize a logger with `log = structlog.get_logger()`.
* Inside your loop, use `log.bind(invoice_id=inv.id, amount=inv.total_amount)` to create a context-aware logger that automatically includes these fields in every log message it emits.

<details>
<summary style="cursor: pointer;"><b>💡 Click here to show the solution snippet</b></summary>

```python
# TODO: import `tructlog` (replace `logging`
from src.domain.models import Invoice
from typing import Protocol

# TODO: initialize logger


class InvoiceAPIClient(Protocol):
def fetch_pending_invoices(self) -> list[Invoice]: ...
def approve_invoice(self, invoice_id: str) -> bool: ...


class InvoiceProcessor:
def __init__(self, api_client: InvoiceAPIClient):
    self.api_client = api_client
    self.threshold = 10000.0

def run(self):
    invoices = self.api_client.fetch_pending_invoices()
    # TODO: add a new INFO log; pass count attribute that contains number of invoices

    for inv in invoices:
        # BEST PRACTICE: Bind the ID to the logger so it attaches to all subsequent logs!
        # This makes tracking a single invoice through the system effortless in Azure/Datadog.
        # TODO: bind invoice_id=inv.id to the logger

        log.info("processing_invoice")

        if inv.total_amount > self.threshold:
            # BEST PRACTICE: Use Warning for expected business exceptions (needs human review)
            # TODO: add warnaing "manual_review_required" and pass amount attribute that equals total_amount of the invoice
            
        else:
            self.api_client.approve_invoice(inv.id)
            log.info("invoice_approved")
```

<details>
<summary style="cursor: pointer;"><b>💡 Click here to show the full solution snippet</b></summary>

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
</details>

#### Update your Entry Point (`task.py`)

[todo: refactor the description below to explain what must be done before we challenge the students to write the code.]

We tell `structlog` to render all log events as JSON strings, and inject an ISO-8601 timestamp into every payload automatically.

<div style="background:#f0ffc0; padding: .5em 1em; 0 1em;">
    <b>🧩 CHALLENGE</b>
    <ol>
        <li>Configure <code>structlog</code> to output as JSON with an ISO timestamp.</li>
    </ol>
</div>

[todo: refine the challenge description to instruct the user about the objective in a more accurate way]

<details>
<summary style="cursor: pointer;"><b>💡 Click here for hints</b></summary>

**Hints:**

* Use `structlog.configure()` to set the processors.
* You will need `structlog.processors.TimeStamper(fmt="iso")` to add the timestamp, and `structlog.processors.JSONRenderer()` to format the final output as a JSON string.

<details>
<summary style="cursor: pointer;"><b>💡 Click here to show the solution snippet</b></summary>

```python
import structlog
from src.infrastructure.api_client import FastAPIClient
from src.application.processor import InvoiceProcessor


def main():
# Configure the 12-Factor JSON log stream
# TODO: configure structlog to use TimeStamper(fmt="iso") and JSONRenderer

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

<details>
<summary style="cursor: pointer;"><b>💡 Click here to show the full solution snippet</b></summary>

```python
import structlog
from src.infrastructure.api_client import FastAPIClient
from src.application.processor import InvoiceProcessor


def main():
    # Configure the 12-Factor JSON log stream
    structlog.configure(processors=[structlog.processors.TimeStamper(fmt="iso"), structlog.processors.JSONRenderer()])

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
</details>

#### Run the bot

Execute the bot. Look at your terminal! You will see machine-readable JSON logs that cloud dashboards (Azure, Datadog, Splunk) can natively parse and query.

```bash
uv run task.py
```

---

### 🏆🏆🏆 CONGRATULATIONS!!! 🏆🏆🏆

**You absolutely nailed it.**

Congratulations! You didn't just write a script; you engineered a robust, decoupled, 12-factor cloud-native masterpiece. You took Sarah's fragile Excel macro, extracted the spaghetti logic, banished the random 503 network crashes using exponential backoff, and wrapped it all in an impenetrable fortress of Pydantic validation and unit tests.

The dark days of debugging `NameError: 'data' is undefined` in a 3,000-line `tasks.py` file at 2:00 AM are officially over.

By mastering Domain-Driven Design, SOLID principles, and structured JSON observability, you haven't just learned how to build modern Python automation solutions—you have future-proofed your career.

Here is the secret: **AI Agents** (like OpenAI Swarm, LangChain, or AutoGen) *hate* messy code. They need strict data contracts (Pydantic), isolated tools (Infrastructure), and clear orchestrator boundaries to function autonomously without destroying production.

By building this architecture today, you are now one massive step closer to the AI Era. You aren't just an RPA Developer anymore; you are an AI Systems Architect.

Go grab a cake or chicken leg. You've earned it. ☕🚀
