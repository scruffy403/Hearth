# Hearth Purse — (V2 of Bank Visualization prototype) Specification

**Author:** John Soto  
**Status:** Draft  
**Date:** June 2026  
**Project:** `hearth` (monorepo)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [The Hearth Ecosystem](#2-the-hearth-ecosystem)
3. [Goals and Non-Goals](#3-goals-and-non-goals)
4. [System Architecture](#4-system-architecture)
5. [Data Architecture](#5-data-architecture)
6. [Backend — FastAPI](#6-backend--fastapi)
7. [Frontend — React](#7-frontend--react)
8. [Infrastructure and Deployment](#8-infrastructure-and-deployment)
9. [Testing Strategy](#9-testing-strategy)
10. [Documentation](#10-documentation)
11. [Phased Build Plan](#11-phased-build-plan)
12. [Future Considerations](#12-future-considerations)
13. [Naming and Design Philosophy](#13-naming-and-design-philosophy)

---

## 1. Project Overview

A personal household finance dashboard for two users (John and Naomi), replacing the v1 Streamlit prototype. v2 is a properly separated full-stack application:

- **FastAPI backend** handling all data ingestion, ML categorization, forecasting, and persistence
- **React frontend** providing interactive dashboard views
- **YNAB as the primary data source**, replacing manual CSV downloads
- **Deployed on a self-hosted VPS** (Hetzner), accessible to both users over HTTPS

The v1 Streamlit app remains functional as the public portfolio demo. v2 is the private production tool.

### Key improvements over v1

| Concern | v1 | v2 |
|---|---|---|
| Data ingestion | Manual CSV download + upload | Automated YNAB API sync |
| Architecture | Monolithic Streamlit app | Separated FastAPI backend + React frontend |
| Persistence | JSON files | PostgreSQL |
| Training data | CSV-derived, limited history | YNAB approved transactions, 4+ years |
| Deployment | Streamlit Community Cloud | Hetzner VPS, Docker Compose |
| Testing | Ad hoc | TDD, pytest + Vitest |
| Documentation | ARCHITECTURE.md | Auto-generated + MkDocs |

---

## 2. The Hearth Ecosystem

Hearth Purse is the first module of a broader personal home management ecosystem
called **Hearth**. This section documents that larger vision so that architectural
decisions made now can accommodate it without requiring structural rework later.

### Vision

Hearth is a suite of small, well-made tools for home life — built gradually, for
personal and family use, each solving a real problem. The guiding principle is that
running a household involves a surprising amount of invisible cognitive load: tracking
money, planning meals, remembering what's in the fridge, keeping on top of events
before they creep up. Hearth modules aim to reduce that overhead quietly and reliably,
without the noise and monetisation incentives of commercial alternatives.

Each module is self-contained but shares infrastructure, design language, and
eventually a common entry point.

### Planned and possible modules

| Module | Name | Purpose | Status |
|---|---|---|---|
| Finance dashboard | **Hearth Purse** | Household budget, cashflow, ML categorisation | v2 in progress |
| Grocery / pantry | **Hearth Larder** | Track what's in stock, reduce waste, shopping lists | Concept |
| Meal planning | **Hearth Table** | Weekly meal plans, recipe linking, Larder integration | Concept |
| Calendar intelligence | **Hearth Almanac** | Surfaces upcoming events with actionable reminders | Concept |
| Home entry point | **Hearth Home** | Landing page linking all modules, family photo display | Future frontend phase |

Names follow the same aesthetic as Hearth Purse — domestic, slightly archaic,
warm rather than techy. A larder is where food is stored; a table is where the
family eats; an almanac tracks time and seasons. The naming should feel like it
belongs in a home, not a product catalogue.

### Monorepo structure for the ecosystem

All modules live in a single repository. This avoids the coordination overhead of
multiple repos while the project is built and maintained by one person. If any module
ever grew to the point of needing independent deployment pipelines or separate teams,
extracting it into its own repo is straightforward — monorepo to multi-repo is a
well-understood migration; multi-repo to monorepo is painful.

```
hearth/                          # Repository root
├── purse/                       # Finance dashboard (this project)
│   ├── backend/                 # FastAPI
│   └── frontend/                # React
├── larder/                      # Future: grocery/pantry tracking
│   ├── backend/
│   └── frontend/
├── almanac/                     # Future: calendar/reminder intelligence
│   ├── backend/
│   └── frontend/
├── shared/                      # Shared across modules
│   ├── design-tokens/           # Colours, typography, spacing — single source of truth
│   └── components/              # Shared React components (eventually)
├── home/                        # The Hearth landing page (future frontend phase)
├── docker-compose.yml           # Orchestrates all running modules
├── docker-compose.dev.yml       # Local dev overrides
└── Caddyfile                    # Routing: purse.hearth.local, larder.hearth.local, etc.
```

### Adding a new module

When a new Hearth module is ready to start:

1. Create a new top-level folder (e.g. `larder/`) with its own `backend/` and
   `frontend/` subdirectories following the same structure as `purse/`
2. Add a new service block to `docker-compose.yml`
3. Add a routing rule to `Caddyfile` (e.g. `larder.yourdomain.com`)
4. Reference shared design tokens from `shared/design-tokens/`

No changes to existing modules are required. Each module is independently
deployable within the shared Compose stack.

### Google Calendar integration (Hearth Almanac concept)

The calendar/reminder idea — surfacing upcoming events with household-relevant
context like "Aine's friend's birthday party in 3 weeks, gift not yet sorted" —
is a concrete use case for a future module. The technical shape would be:

- OAuth connection to Google Calendar (both family members' calendars)
- A lightweight rules engine: event keywords or tags trigger reminder types
- Push to a notification channel (email digest, or a dashboard widget on the
  Hearth Home page)
- Integration with Hearth Purse: a birthday in 3 weeks could surface a budget
  prompt alongside the reminder

This is well-suited to a FastAPI backend module using the Google Calendar API,
with APScheduler running daily checks — the same pattern as the YNAB sync in
Hearth Purse.

### Scaling consideration

At personal/family scale, a monorepo with shared Docker Compose infrastructure
is the right architecture. If Hearth ever evolved toward a product offered to
other households, the natural evolution would be:

- Each module becomes a separately deployable service with its own Docker image
- A shared authentication service handles user identity across modules
- Modules communicate via internal API calls rather than shared database access
- The monorepo can remain — but deployment pipelines become per-module

That evolution requires no structural rework of the codebase as designed. The
service boundaries are already clean.

---

## 3. Goals and Non-Goals

### Goals

- Automate Nationwide transaction ingestion via the existing YNAB integration (no CSV steps)
- Provide all existing dashboard views (overview, cashflow, forecasting, categories, merchants, anomalies, budgets)
- Improve ML categorization by training on the full YNAB approved-transaction history
- Store ML confidence scores and prediction provenance for future explainability (SHAP)
- Keep architecture extensible: Prophet forecasting, SHAP explainability, and Polars pipeline migration should be addable without structural changes
- Support two concurrent users with shared credentials, upgradeable to individual logins
- Be genuinely maintainable: tested, documented, version-controlled

### Non-Goals

- Public access or multi-tenancy (personal tool only)
- Mobile-native application
- Direct Open Banking integration (no viable free personal-use provider currently exists)
- Replacing the paid Nationwide→YNAB sync service (the reauthorisation overhead is acceptable)

---

## 4. System Architecture

### High-level overview

```mermaid
graph TB
    subgraph External
        YNAB[YNAB API]
        NW[Nationwide\nvia paid sync]
    end

    subgraph VPS["Hetzner VPS — Docker Compose"]
        subgraph Caddy["Caddy (reverse proxy + TLS)"]
            AUTH[Basic Auth]
        end

        subgraph Backend["FastAPI Backend :8000"]
            API[REST API\nRouters]
            SCHED[APScheduler\nYNAB sync job]
            SVC[Services Layer\ncategorization · ml · forecasting · anomalies]
        end

        subgraph Frontend["React Frontend :3000"]
            UI[Dashboard Views]
            APICLIENT[Typed API Client]
        end

        PG[(PostgreSQL\n:5432)]
    end

    subgraph LocalDev["Developer Mac — OrbStack"]
        DEVCOMPOSE[docker-compose.yml\n same stack]
    end

    NW -->|bank sync| YNAB
    YNAB -->|scheduled pull| SCHED
    SCHED --> SVC
    SVC --> PG
    API --> SVC
    API --> PG
    APICLIENT -->|REST| Caddy
    Caddy --> API
    Caddy --> UI
    AUTH --> Caddy

    style VPS fill:#e8f4f8,stroke:#2196F3
    style Backend fill:#fff3e0,stroke:#FF9800
    style Frontend fill:#f3e5f5,stroke:#9C27B0
    style External fill:#f5f5f5,stroke:#9E9E9E
    style LocalDev fill:#e8f5e9,stroke:#4CAF50
```

### Repository structure (monorepo)

```
purse/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app factory, router registration, lifespan
│   │   ├── config.py                # Pydantic BaseSettings — reads from .env
│   │   ├── database.py              # SQLAlchemy async engine, session factory
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── transaction.py
│   │   │   ├── merchant_override.py
│   │   │   ├── budget_config.py
│   │   │   ├── forecast_scenario.py
│   │   │   └── ml_training_log.py
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   │   ├── transaction.py
│   │   │   ├── category.py
│   │   │   ├── budget.py
│   │   │   ├── forecast.py
│   │   │   └── ml.py
│   │   ├── routers/                 # HTTP layer only — no business logic
│   │   │   ├── transactions.py
│   │   │   ├── categories.py
│   │   │   ├── budgets.py
│   │   │   ├── forecasts.py
│   │   │   ├── anomalies.py
│   │   │   └── sync.py              # Manual sync trigger endpoint
│   │   └── services/                # All business logic — testable without HTTP
│   │       ├── ynab.py              # YNAB API client + sync orchestration
│   │       ├── payee_normalizer.py  # Ported from v1
│   │       ├── categorization.py    # Rule-based pipeline
│   │       ├── ml.py                # Training, inference, confidence scores
│   │       ├── forecasting.py       # Cashflow extrapolation (Prophet-ready)
│   │       ├── anomalies.py         # IQR outlier detection
│   │       └── budgets.py           # Budget vs actual computation
│   ├── sync/
│   │   └── scheduler.py             # APScheduler job definitions
│   ├── migrations/                  # Alembic migration files
│   │   └── versions/
│   ├── tests/
│   │   ├── conftest.py              # Fixtures: test DB, async client, factory_boy factories
│   │   ├── unit/                    # Pure service-layer tests, no HTTP
│   │   │   ├── test_payee_normalizer.py
│   │   │   ├── test_categorization.py
│   │   │   ├── test_ml.py
│   │   │   ├── test_forecasting.py
│   │   │   └── test_anomalies.py
│   │   └── integration/             # Full request cycle tests via httpx TestClient
│   │       ├── test_transactions.py
│   │       ├── test_categories.py
│   │       ├── test_budgets.py
│   │       └── test_sync.py
│   ├── docs/                        # MkDocs source
│   │   └── index.md
│   ├── mkdocs.yml
│   ├── pyproject.toml               # Dependencies + tool config (pytest, coverage, ruff)
│   ├── Dockerfile
│   └── alembic.ini
├── frontend/
│   ├── src/
│   │   ├── api/                     # Typed fetch wrappers — one file per router
│   │   │   ├── client.ts            # Base fetch with auth headers + error handling
│   │   │   ├── transactions.ts
│   │   │   ├── categories.ts
│   │   │   ├── budgets.ts
│   │   │   ├── forecasts.ts
│   │   │   └── anomalies.ts
│   │   ├── components/              # Reusable UI components
│   │   │   ├── charts/              # react-plotly.js wrappers
│   │   │   │   ├── BalanceChart.tsx
│   │   │   │   ├── CashflowChart.tsx
│   │   │   │   ├── CategoryTrendChart.tsx
│   │   │   │   ├── ForecastChart.tsx
│   │   │   │   └── AnomalyScatter.tsx
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── PageHeader.tsx
│   │   │   └── ui/                  # Generic: DateRangePicker, CategoryFilter, etc.
│   │   ├── pages/                   # One per dashboard view
│   │   │   ├── Overview.tsx
│   │   │   ├── Cashflow.tsx
│   │   │   ├── Forecast.tsx
│   │   │   ├── Categories.tsx
│   │   │   ├── Merchants.tsx
│   │   │   ├── Anomalies.tsx
│   │   │   └── Budgets.tsx
│   │   ├── hooks/                   # Custom React hooks
│   │   │   ├── useTransactions.ts
│   │   │   ├── useCategories.ts
│   │   │   └── useDateRange.ts
│   │   └── types/                   # TypeScript interfaces mirroring Pydantic schemas
│   │       ├── transaction.ts
│   │       ├── category.ts
│   │       ├── budget.ts
│   │       └── forecast.ts
│   ├── tests/
│   │   ├── setup.ts                 # MSW server setup
│   │   ├── mocks/                   # MSW request handlers
│   │   └── components/              # React Testing Library tests
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml               # Production
├── docker-compose.dev.yml           # Local dev overrides (hot reload, exposed ports)
├── Caddyfile
├── .env.example
├── .gitignore
└── README.md
```

---

## 5. Data Architecture

### PostgreSQL schema

```mermaid
erDiagram
    TRANSACTIONS {
        uuid id PK
        text ynab_transaction_id UK
        date date
        numeric amount
        char currency
        text merchant_raw
        text merchant_clean
        text category_ynab
        text category_dashboard
        text category_source
        numeric ml_confidence
        boolean ynab_approved
        boolean is_transfer
        text notes
        timestamptz created_at
        timestamptz updated_at
    }

    MERCHANT_OVERRIDES {
        text merchant_clean PK
        text category_dashboard
        timestamptz updated_at
    }

    BUDGET_CONFIG {
        text category_dashboard PK
        text mode
        numeric monthly_amount
        timestamptz updated_at
    }

    FORECAST_SCENARIOS {
        uuid id PK
        text name
        timestamptz created_at
        int days_ahead
        text[] exclude_categories
        uuid[] exclude_tx_ids
        jsonb parameters
    }

    ML_TRAINING_LOG {
        uuid id PK
        timestamptz trained_at
        int sample_count
        jsonb category_distribution
        jsonb metrics
    }

    TRANSACTIONS ||--o{ MERCHANT_OVERRIDES : "merchant_clean →"
    TRANSACTIONS ||--o{ BUDGET_CONFIG : "category_dashboard →"
```

### Key schema decisions

**`ynab_transaction_id` (UNIQUE)** — makes the sync idempotent. Re-running the sync job never produces duplicates; it upserts on this key.

**`category_source` enum: `'ynab' | 'ml' | 'manual_override'`** — tracks the provenance of every categorization. This powers the active learning loop and is the hook for SHAP explainability in a later phase.

**`ml_confidence` (nullable numeric)** — null when `category_source != 'ml'`. Enables surfacing low-confidence predictions to the user for review.

**`parameters jsonb` on `forecast_scenarios`** — schema-free storage for forecasting parameters. Means Prophet-specific config (seasonality mode, changepoint prior, etc.) can be added without a migration.

**`metrics jsonb` on `ml_training_log`** — same pattern. Stores accuracy and per-class F1 today; can record additional metrics as the pipeline evolves.

---

## 6. Backend — FastAPI

### Service layer class diagram

```mermaid
classDiagram
    class YNABService {
        +client: YNABClient
        +sync_transactions(budget_id: str) List~Transaction~
        +fetch_approved_transactions(since_date: date) List~YNABTransaction~
        +get_oldest_transaction_date() date
    }

    class YNABClient {
        -base_url: str
        -api_key: str
        +get_transactions(budget_id, since_date) dict
        +get_categories(budget_id) dict
        +get_payees(budget_id) dict
    }

    class PayeeNormalizer {
        +CANONICAL_MAP: dict
        +TRANSFER_PATTERNS: list
        +normalize(raw_name: str) str
        -strip_prefixes(name: str) str
        -strip_location_tokens(name: str) str
    }

    class CategorizationService {
        +overrides: dict
        +keyword_rules: dict
        +categorize(merchant_clean: str, ynab_category: str) CategoryResult
        -apply_manual_override(merchant: str) str | None
        -apply_ynab_fuzzy_match(ynab_category: str) str | None
        -apply_keyword_rules(merchant: str) str | None
    }

    class MLService {
        -model_cache: dict
        +train(transactions: List~Transaction~) MLTrainingResult
        +predict(merchant_clean: str) MLPrediction
        +predict_batch(merchants: List~str~) List~MLPrediction~
        -build_corpus(transactions) tuple
    }

    class MLPrediction {
        +category: str
        +confidence: float
        +source: str
    }

    class CategoryResult {
        +category: str
        +source: str
    }

    class ForecastingService {
        +build_cashflow_timeseries(transactions) DataFrame
        +add_simple_forecast(timeseries, days_ahead: int) DataFrame
        +get_scenario(scenario_id: uuid) ForecastScenario
    }

    class AnomalyService {
        +detect(transactions: List~Transaction~) List~AnomalyResult~
        -compute_iqr_bounds(group) tuple
    }

    class BudgetService {
        +compute_vs_actual(transactions, period: date) List~BudgetResult~
        +load_config() List~BudgetConfig~
        +save_config(config: List~BudgetConfig~) None
    }

    class SyncScheduler {
        +scheduler: AsyncIOScheduler
        +start() None
        +trigger_manual_sync() None
        -run_ynab_sync() None
    }

    YNABService --> YNABClient
    YNABService --> PayeeNormalizer
    YNABService --> CategorizationService
    YNABService --> MLService
    CategorizationService --> MLService
    MLService --> MLPrediction
    CategorizationService --> CategoryResult
    SyncScheduler --> YNABService
```

### API endpoints

#### Transactions

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/transactions` | List transactions. Query params: `from_date`, `to_date`, `categories[]`, `limit`, `offset` |
| `GET` | `/api/v1/transactions/{id}` | Single transaction detail |
| `PATCH` | `/api/v1/transactions/{id}/category` | Manual category override — updates DB and merchant_overrides |
| `GET` | `/api/v1/transactions/low-confidence` | Transactions where `ml_confidence < threshold` — active learning queue |

#### Categories

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/categories` | All category names (built-in + custom) |
| `GET` | `/api/v1/categories/summary` | Spend totals per category for a date range |
| `GET` | `/api/v1/categories/trends` | Monthly spend per category (time series) |
| `GET` | `/api/v1/categories/merchants` | Top merchants per category |

#### Budgets

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/budgets` | All budget configs |
| `PUT` | `/api/v1/budgets/{category}` | Set budget for a category |
| `GET` | `/api/v1/budgets/vs-actual` | Actual spend vs budget, current month |

#### Forecasts

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/forecasts/cashflow` | Historical cashflow timeseries |
| `POST` | `/api/v1/forecasts/scenarios` | Create a new scenario |
| `GET` | `/api/v1/forecasts/scenarios` | List saved scenarios |
| `GET` | `/api/v1/forecasts/scenarios/{id}` | Single scenario with projected vs actual |
| `DELETE` | `/api/v1/forecasts/scenarios/{id}` | Delete scenario |

#### Anomalies

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/anomalies` | IQR-flagged transactions. Query params: `from_date`, `to_date` |

#### Sync

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/sync/trigger` | Manually trigger YNAB sync |
| `GET` | `/api/v1/sync/status` | Last sync time, transaction count, any errors |

#### ML

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/ml/retrain` | Manually trigger model retraining |
| `GET` | `/api/v1/ml/training-log` | History of training runs with metrics |

### Pydantic schema examples

```python
# schemas/transaction.py

class TransactionResponse(BaseModel):
    id: UUID
    date: date
    amount: Decimal
    merchant_raw: str
    merchant_clean: str
    category_dashboard: str
    category_source: Literal["ynab", "ml", "manual_override"]
    ml_confidence: float | None
    ynab_approved: bool
    notes: str | None

class TransactionCategoryUpdate(BaseModel):
    category: str
    save_as_merchant_rule: bool = True  # whether to persist to merchant_overrides

class LowConfidenceTransaction(TransactionResponse):
    ml_confidence: float  # guaranteed non-null in this context
```

### Configuration (Pydantic BaseSettings)

```python
# app/config.py

class Settings(BaseSettings):
    # Database
    database_url: str

    # YNAB
    ynab_api_key: str
    ynab_budget_id: str

    # Sync
    sync_interval_hours: int = 6
    ynab_lookback_days: int = 90  # days to fetch on each sync

    # ML
    ml_min_training_samples: int = 5
    ml_low_confidence_threshold: float = 0.6

    model_config = SettingsConfigDict(env_file=".env")
```

---

## 7. Frontend — React

### Technology choices

| Concern | Choice | Rationale |
|---|---|---|
| Build tool | Vite | Fast, first-class TypeScript, built-in Vitest |
| Language | TypeScript | Type safety, mirrors Pydantic schema contracts |
| Charts | react-plotly.js | Preserves existing Plotly chart logic from v1 |
| State / data fetching | TanStack Query (React Query) | Handles caching, refetch, loading states cleanly |
| Routing | React Router v6 | Standard, well-understood |
| Styling | Tailwind CSS | Utility-first, no CSS-in-JS overhead |
| Testing | Vitest + React Testing Library + MSW | Fast, behaviour-focused, realistic API mocking |

### Design language — the Hearth aesthetic

Hearth Purse should feel like it belongs in your home, not in a bank's mobile
app. The visual design is an explicit rejection of the cold blues, sharp edges,
and anxious density of mainstream fintech interfaces. The guiding brief:

> Warm, unhurried, considered. The kind of tool that feels like it was made for
> your household specifically, not licensed to you by a corporation.

#### Why this matters for Hearth Purse

The name *Purse* is deliberately archaic — it evokes something personal and
domestic rather than financial and transactional. The UI should honour that.
Someone opening Hearth Purse to check their spending should feel oriented and
calm, not surveilled.

#### Colour and tone

- **Warm neutrals as the base** — parchment, linen, warm off-whites rather than
  pure white or cool grey
- **Earthy accent colours** — terracotta, forest green, ochre, deep teal; avoid
  the electric blues and greens of fintech
- **Dark mode should be warm too** — deep walnut or charcoal, not pure black

#### Typography

- A **serif or humanist typeface for headings** — something with personality,
  suggesting craft and permanence. Options to explore: Lora, Playfair Display,
  Source Serif, Fraunces
- A **clean, readable sans-serif for data and body text** — legibility matters
  for numbers; something like Inter or DM Sans works well alongside a display serif
- **Type should feel sized for reading**, not for scanning dashboards — generous
  line height, comfortable weight

#### Layout and interaction

- **Unhurried layout** — generous whitespace, nothing competing for attention
- **Charts should feel illustrative, not clinical** — warm colour palettes in
  Plotly, rounded corners where appropriate, annotations that feel hand-considered
- **No aggressive visual hierarchy** — avoid the fintech pattern of giant KPI
  numbers dominating every screen; the data tells the story, the design just
  holds it

#### The Hearth Home page (future phase)

A longer-term frontend ambition is a true Hearth landing page that serves as
the entry point to all modules. The design concept:

- The page is styled to evoke looking at a hearth — warm, textured, a focal point
- **Picture frames** are displayed as elements on the page, showing scaled-down
  images from the family photo collection — swappable, personal, genuinely yours
- Each module (Purse, Larder, Almanac) is accessible from this page as a
  distinct element — a book on a shelf, a door, a frame
- This is a **separate frontend phase** (effectively Hearth Frontend v2) and
  should not block the functional dashboard work

When this phase arrives, the `home/` directory in the monorepo becomes its own
React application, sharing design tokens from `shared/design-tokens/` to ensure
visual consistency across modules.

#### Design token structure (shared/)

```
shared/
└── design-tokens/
    ├── colours.css        # CSS custom properties: --hearth-parchment, --hearth-terracotta, etc.
    ├── typography.css     # Font stacks, size scale, line heights
    ├── spacing.css        # Consistent spacing scale
    └── index.css          # Imports all tokens — reference this in each module's Tailwind config
```

Tailwind can be configured to use these tokens as its colour and typography
palette, meaning every module automatically shares the Hearth visual language
without duplicating values.

---

### Page structure

```mermaid
graph LR
    ROOT[App Router] --> OV[Overview\n/]
    ROOT --> CF[Cashflow\n/cashflow]
    ROOT --> FC[Forecast\n/forecast]
    ROOT --> CAT[Categories\n/categories]
    ROOT --> MER[Merchants\n/merchants]
    ROOT --> AN[Anomalies\n/anomalies]
    ROOT --> BUD[Budgets\n/budgets]
```

### API client pattern

The `types/` directory contains TypeScript interfaces that are manually kept in sync with the Pydantic schemas. This is a deliberate trade-off: code generation from OpenAPI is possible (and worth revisiting later) but adds tooling complexity. For now, the FastAPI auto-generated `/docs` is the source of truth.

```typescript
// api/transactions.ts
import { apiClient } from "./client";
import type { TransactionResponse, TransactionFilters } from "../types/transaction";

export const transactionsApi = {
  list: (filters: TransactionFilters) =>
    apiClient.get<TransactionResponse[]>("/transactions", { params: filters }),

  updateCategory: (id: string, category: string, saveAsRule: boolean) =>
    apiClient.patch<TransactionResponse>(`/transactions/${id}/category`, {
      category,
      save_as_merchant_rule: saveAsRule,
    }),

  getLowConfidence: () =>
    apiClient.get<TransactionResponse[]>("/transactions/low-confidence"),
};
```

---

## 8. Infrastructure and Deployment

### Docker Compose (production)

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: hearth_purse
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/hearth_purse
      YNAB_API_KEY: ${YNAB_API_KEY}
      YNAB_BUDGET_ID: ${YNAB_BUDGET_ID}
    depends_on:
      - postgres
    restart: unless-stopped

  frontend:
    build: ./frontend
    restart: unless-stopped

  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
  caddy_data:
```

### Caddyfile

```
yourdomain.com {
    basicauth * {
        # htpasswd-generated entry
        shared_user_hash $2a$...
    }

    handle /api/* {
        reverse_proxy backend:8000
    }

    handle {
        reverse_proxy frontend:3000
    }
}
```

### Local development

```yaml
# docker-compose.dev.yml (extends base)
services:
  backend:
    volumes:
      - ./backend:/app       # hot reload via uvicorn --reload
    ports:
      - "8000:8000"          # direct access for testing
  frontend:
    volumes:
      - ./frontend/src:/app/src  # Vite HMR
    ports:
      - "3000:3000"
  postgres:
    ports:
      - "5432:5432"          # direct DB access from host tools
```

Run locally: `docker compose -f docker-compose.yml -f docker-compose.dev.yml up`

### Docker on macOS (Apple Silicon)

OrbStack handles ARM natively. No special configuration needed for local development. For production image builds targeting the Hetzner VPS (x86_64), GitHub Actions handles cross-compilation. A basic workflow:

```yaml
# .github/workflows/deploy.yml
- name: Build and push
  uses: docker/build-push-action@v5
  with:
    platforms: linux/amd64
    push: true
```

### Hetzner VPS

- **Instance:** CAX11 (2 ARM vCPU, 4 GB RAM) — ~£3.50/month
- **OS:** Ubuntu 24.04
- **Backups:** Hetzner automated snapshots (weekly) + `pg_dump` via cron to object storage
- **SSL:** Caddy automatic via Let's Encrypt — zero configuration required

---

## 9. Testing Strategy

### Philosophy

TDD where practical. For the services layer (pure functions with no HTTP) this is straightforward: write the test, write the function, make it pass. For routers, write the failing integration test against the endpoint contract before implementing the router.

### Backend

**Tools:** pytest, pytest-asyncio, httpx, factory_boy, pytest-cov

**Structure:**

```
tests/
├── conftest.py           # Shared fixtures
├── unit/                 # Service-layer tests — no DB, no HTTP
│   ├── test_payee_normalizer.py
│   ├── test_categorization.py
│   ├── test_ml.py
│   ├── test_forecasting.py
│   └── test_anomalies.py
└── integration/          # Full request cycle — test DB, httpx AsyncClient
    ├── test_transactions.py
    ├── test_categories.py
    ├── test_budgets.py
    └── test_sync.py
```

**Key fixtures:**

```python
# tests/conftest.py

@pytest.fixture
async def db_session():
    """Isolated async DB session using a test database,
    rolled back after each test."""
    ...

@pytest.fixture
def transaction_factory():
    """factory_boy factory for Transaction ORM model."""
    ...

@pytest.fixture
async def client(db_session):
    """httpx AsyncClient with overridden DB dependency."""
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

**Coverage target:** 80% minimum on the `services/` layer. Routers are covered by integration tests.

### Frontend

**Tools:** Vitest, React Testing Library, MSW

**Approach:** Test behaviour, not implementation. Tests should describe what a user sees and does, not internal component state.

```typescript
// tests/components/TransactionList.test.tsx

it("shows low-confidence badge on ML-categorised transactions", async () => {
  server.use(
    http.get("/api/v1/transactions", () =>
      HttpResponse.json([mockTransaction({ category_source: "ml", ml_confidence: 0.52 })])
    )
  );
  render(<TransactionList />);
  expect(await screen.findByText("Low confidence")).toBeInTheDocument();
});
```

### Running tests

```bash
# Backend
cd backend && pytest --cov=app --cov-report=term-missing

# Frontend
cd frontend && npx vitest run --coverage
```

### Running tests using `docker` command example:
```bash
docker compose exec backend pytest tests/unit/test_ml.py -v
```

---

## 10. Documentation

### Three layers

| Layer | Tool | Location | Audience |
|---|---|---|---|
| API reference | FastAPI auto-docs (Swagger + ReDoc) | `/docs`, `/redoc` | Developer during integration |
| Code documentation | MkDocs + Material + mkdocstrings | `backend/docs/`, GitHub Pages | Developer maintaining the project |
| Architecture | Markdown + Mermaid in repo | `README.md`, this spec | Anyone understanding the system |

### MkDocs setup

```yaml
# backend/mkdocs.yml
site_name: Hearth Purse — Backend
theme:
  name: material
plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
nav:
  - Home: index.md
  - Services:
    - YNAB Sync: services/ynab.md
    - categorization: services/categorization.md
    - ML Pipeline: services/ml.md
    - Forecasting: services/forecasting.md
```

### Docstring convention (Google style)

```python
def normalize(self, raw_name: str) -> str:
    """Canonicalise a raw merchant string from YNAB.

    Applies prefix stripping, location token removal, and canonical
    map lookup in order. Returns the cleaned merchant name.

    Args:
        raw_name: The raw payee name as received from YNAB.

    Returns:
        Cleaned, canonical merchant name (e.g. "Tesco").

    Examples:
        >>> normalizer.normalize("TESCO STORES 3456 GB")
        "Tesco"
    """
```

FastAPI endpoint docstrings become the description in the auto-generated Swagger UI automatically.

---

## 11. Phased Build Plan

### Phase 1 — Foundation

**Goal:** A running stack with an empty database.

- [ ] Monorepo scaffolded
- [ ] `docker-compose.yml` with Postgres, FastAPI stub, Caddy
- [ ] `docker-compose.dev.yml` with hot-reload volumes
- [ ] Alembic configured, initial migration (all tables)
- [ ] Pydantic `Settings` reading from `.env`
- [ ] Health check endpoint: `GET /api/v1/health`
- [ ] Basic Auth configured in Caddyfile
- [ ] OrbStack installed on Mac, stack runs locally
- [ ] GitHub repo created, `.gitignore` excluding `.env` and secrets

**Done when:** `docker compose up` on a fresh clone produces a healthy stack. `/api/v1/health` returns 200. Postgres has the schema.

### Phase 2 — YNAB sync

**Goal:** Real transaction data in Postgres, automatically refreshed.

- [ ] `YNABClient` with `get_transactions`, `get_categories`, `get_payees`
- [ ] `PayeeNormalizer` ported from v1, unit tested
- [ ] `CategorizationService` (rule-based only), unit tested
- [ ] `YNABService.sync_transactions()` — fetch, normalise, categorise, upsert
- [ ] APScheduler job running sync every 6 hours
- [ ] `GET /api/v1/sync/status` and `POST /api/v1/sync/trigger`
- [ ] Integration test: trigger sync against a mocked YNAB API, assert DB state
- [ ] Check oldest YNAB transaction date and document it

**Done when:** Sync job runs, transactions appear in Postgres with correct categorization.

### Phase 3 — ML pipeline

**Goal:** ML categorization improving on rule-based, low-confidence queue available.

- [ ] `MLService.train()` on YNAB-approved transactions
- [ ] `MLService.predict_batch()` filling `category_source = 'ml'` and `ml_confidence`
- [ ] `ml_training_log` entries on each retrain
- [ ] `PATCH /api/v1/transactions/{id}/category` — manual override + merchant rule
- [ ] `GET /api/v1/transactions/low-confidence`
- [ ] `POST /api/v1/ml/retrain`
- [ ] Unit tests for train/predict cycle with synthetic fixture data

**Done when:** ML is running in the sync pipeline, confidence scores are stored, overrides persist.

### Phase 4 — REST API completion

**Goal:** All analytical endpoints implemented and integration tested.

- [ ] Transaction list + filter endpoint
- [ ] Category summary + trends
- [ ] Anomaly detection endpoint
- [ ] Budget config endpoints
- [ ] Forecast cashflow + scenario endpoints
- [ ] Integration tests for each router
- [ ] FastAPI auto-docs reviewed and docstrings complete

**Done when:** Every endpoint in section 5 is implemented, tested, and visible in Swagger UI.

### Phase 5 — React frontend

**Goal:** Functional dashboard replacing the Streamlit v1 views.

- [ ] Vite + TypeScript + Tailwind scaffolded
- [ ] MSW set up for frontend tests
- [ ] `api/client.ts` with base fetch and 401 handling
- [ ] All `api/*.ts` wrappers with TypeScript types
- [ ] TanStack Query configured
- [ ] Overview page (balance chart, monthly stacked spend)
- [ ] Cashflow page
- [ ] Categories page
- [ ] Forecast page (with scenario management)
- [ ] Merchants page (top merchants, subscription detection)
- [ ] Anomalies page
- [ ] Budgets page
- [ ] React Testing Library tests for each page's key behaviour
- [ ] Frontend Dockerfile, added to Compose

**Done when:** All v1 dashboard views are reproduced in React, talking to the live FastAPI backend.

### Phase 6 — Production deployment

**Goal:** Running on Hetzner, accessible to both users.

- [ ] Hetzner VPS provisioned, Docker installed
- [ ] GitHub Actions workflow: build `linux/amd64` images, push to registry
- [ ] Deployment script or action: pull images, `docker compose up -d` on VPS
- [ ] Domain configured, Caddy auto-SSL confirmed
- [ ] `pg_dump` cron to Hetzner Object Storage for backups
- [ ] End-to-end smoke test from both users' browsers

**Done when:** The app is live, HTTPS working, both users can log in, sync is running automatically.

---

## 12. Future Considerations

These are deliberately out of scope for v2 but the architecture is structured to accommodate them without rework.

### SHAP explainability (v2.1)

`MLService` stores `ml_confidence` already. Adding SHAP means adding a `predict_with_explanation()` method that returns the top contributing n-grams alongside the prediction. The `TransactionResponse` schema gains an optional `explanation` field. The frontend can render this as a tooltip on ML-categorised transactions — helpful for the manual correction workflow.

### Prophet forecasting (v3)

`ForecastingService` today uses mean-net extrapolation. The `forecast_scenarios.parameters` JSONB column holds Prophet configuration without a migration. Swapping the implementation is isolated to `services/forecasting.py` and the forecast endpoints — no schema changes, no frontend changes beyond receiving richer timeseries data.

### Forecast backtesting

Hold out the last N months, run the forecast on truncated history, compare predicted vs actual. Produces a real accuracy metric displayable in the dashboard. Can be added as an endpoint and a new page without touching existing routes.

### Polars in the data pipeline

The services layer works with Python lists and dicts at the boundary with SQLAlchemy. Introducing Polars for the analytical transforms inside `forecasting.py`, `anomalies.py`, and `categorization.py` is an internal implementation change — no API or schema impact. The sklearn ML pipeline retains pandas (or raw lists) at the `TfidfVectorizer` boundary.

### Individual user logins (JWT)

Caddy Basic Auth is replaced by a `POST /api/v1/auth/login` endpoint returning a JWT. The React `api/client.ts` stores the token and attaches it as a Bearer header. The `transactions` table gains a `user_id` foreign key. This is the one change that touches the schema, but it's additive (a new column, a new table) and can be handled with a single Alembic migration.

### Per-user category overrides

Currently `merchant_overrides` is global. Adding a nullable `user_id` foreign key makes overrides per-user when populated, shared when null. Depends on individual logins being in place first.

### TypeScript client generation from OpenAPI

FastAPI exports an OpenAPI schema at `/openapi.json`. Tools like `openapi-typescript` can generate the TypeScript types automatically, eliminating the manual sync between `schemas/` and `types/`. Worth introducing once the API is stable and the manual maintenance becomes noticeable overhead.

---

## 13. Naming and Design Philosophy

### Why Hearth Purse

The name emerged from thinking about what this tool actually is: not a financial
analytics platform, not a budgeting app, but something made for a specific
household to understand its own money more clearly.

*Hearth* — the centre of a home, where things are managed and warmth originates.
It felt like the right name for a suite of tools built around home life, with
enough character to be distinctive without trying to sound like a startup.

*Purse* — an old English word for a household money holder, personal and domestic
in a way that "wallet", "finance", or "money" are not. It is slightly archaic,
which is intentional. The name is not trying to compete with Monzo or Plaid. It
is trying to feel like it belongs in your home.

The pairing works because it is honest about what it is: a household purse,
managed from the hearth.

### What the name should mean for design decisions

Every design decision in Hearth Purse should be tested against one question:
**does this feel like it belongs in our home?**

Commercial fintech design optimises for trust signals, conversion, and retention.
Hearth Purse has none of those pressures. It can optimise purely for the
experience of the two people who actually use it — which means it can be warmer,
quieter, and more personal than anything a product team would ship.

Concretely:

- Choose warmth over clinical precision in colour and type
- Choose calm over urgency in layout and information density
- Choose character over convention when naming things — "Purse" over "Wallet",
  "Larder" over "Pantry Manager"
- When something could be generic or specific, choose specific — a dashboard
  that feels made for your family is more useful than one that could be anyone's

This philosophy should be documented and revisited at the start of each frontend
phase, so that design drift toward generic fintech conventions is caught early.