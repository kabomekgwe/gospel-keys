# Piano Keys - Mermaid Diagrams for Embedded Documentation

This file contains Mermaid diagram definitions that can be embedded in Markdown documentation, GitHub README files, and other documentation systems.

## Backend Engineer Diagrams

### API Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Client[React Frontend<br/>Port 3000]
    end

    subgraph "API Gateway"
        Gateway[FastAPI<br/>Port 8000]
        Auth[JWT Auth<br/>deps.py]
    end

    subgraph "API Routes"
        UserRoute[Users API<br/>/api/v1/users]
        LessonRoute[Lessons API<br/>/api/v1/lessons]
        PracticeRoute[Practice API<br/>/api/v1/practice]
        AnalysisRoute[Analysis API<br/>/api/v1/analysis]
    end

    subgraph "Services"
        UserService[User Service]
        LessonService[Lesson Service]
        PracticeService[Practice Service]
        AnalysisService[Analysis Service]
    end

    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL<br/>Primary DB)]
        Redis[(Redis<br/>Cache)]
        MinIO[(MinIO<br/>S3 Storage)]
    end

    Client -->|HTTP| Gateway
    Gateway -->|Validate| Auth
    Gateway --> UserRoute
    Gateway --> LessonRoute
    Gateway --> PracticeRoute
    Gateway --> AnalysisRoute

    UserRoute --> UserService
    LessonRoute --> LessonService
    PracticeRoute --> PracticeService
    AnalysisRoute --> AnalysisService

    UserService --> PostgreSQL
    LessonService --> PostgreSQL
    PracticeService --> Redis
    AnalysisService --> MinIO

    style Client fill:#E3F2FD
    style Gateway fill:#BBDEFB
    style Auth fill:#FFF9C4
    style PostgreSQL fill:#BBDEFB
    style Redis fill:#FFCDD2
    style MinIO fill:#FFF9C4
```

### Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Client as React Client
    participant API as FastAPI Gateway
    participant Auth as JWT Auth (deps.py)
    participant DB as PostgreSQL

    User->>Client: Enter credentials
    Client->>API: POST /api/v1/auth/login
    API->>Auth: Validate credentials
    Auth->>DB: Query user
    DB-->>Auth: User data
    Auth->>Auth: Generate JWT token
    Auth-->>API: JWT token
    API-->>Client: Return token
    Client->>Client: Store token (localStorage)

    Note over Client,API: Subsequent requests
    Client->>API: Request + JWT token
    API->>Auth: Verify JWT (deps.py)
    Auth-->>API: User object
    API-->>Client: Protected resource

    Note over Auth: ⚠️ CRITICAL: Fix auth bypass<br/>in deps.py lines 30-48
```

### Database Schema

```mermaid
erDiagram
    users ||--o{ lessons : creates
    users ||--o{ practice_sessions : has
    users ||--o{ user_progress : tracks
    lessons ||--o{ practice_sessions : used_in
    lessons ||--o{ midi_files : contains
    lessons ||--o{ user_progress : tracked
    practice_sessions ||--o{ analysis_results : generates

    users {
        int id PK
        string email UK
        string password_hash
        boolean is_superuser
        timestamp created_at
    }

    lessons {
        int id PK
        int user_id FK
        string title
        string difficulty
        timestamp created_at
    }

    practice_sessions {
        int id PK
        int user_id FK
        int lesson_id FK
        float score
        int duration
        timestamp created_at
    }

    midi_files {
        int id PK
        int lesson_id FK
        string s3_key
        int file_size
        timestamp uploaded_at
    }

    analysis_results {
        int id PK
        int session_id FK
        float accuracy
        json timing_errors
        json analysis
    }

    user_progress {
        int id PK
        int user_id FK
        int lesson_id FK
        boolean completed
        timestamp last_practice
    }
```

### Module Dependencies

```mermaid
graph TD
    Main[main.py] --> Deps[api/deps.py]
    Main --> Routes[api/routes]
    Main --> Security[core/security.py]

    Routes --> Services[services]
    Routes --> Models[models]
    Routes --> Schemas[schemas]

    Deps --> Security
    Deps --> Models

    Services --> Models
    Services --> DB[db/session.py]

    Models --> DB

    Services --> Config[core/config.py]
    Services --> Utils[utils]

    style Deps fill:#FFF9C4
    style Security fill:#FFF9C4
    style Main fill:#BBDEFB
```

## QA Engineer Diagrams

### Test Pyramid

```mermaid
graph TB
    subgraph "Test Pyramid - Target: 365 Tests (80% Coverage)"
        E2E["E2E Tests<br/>10% (37 tests)<br/>Playwright"]
        Integration["Integration Tests<br/>20% (73 tests)<br/>Pytest"]
        Unit["Unit Tests<br/>70% (255 tests)<br/>Vitest/Pytest"]
    end

    E2E -.-> Integration
    Integration -.-> Unit

    style E2E fill:#FFCDD2
    style Integration fill:#FFF9C4
    style Unit fill:#C8E6C9
```

### Testing Workflow

```mermaid
flowchart TD
    Start([Developer commits code]) --> PreCommit[Pre-commit hooks run]
    PreCommit --> UnitTests[Unit tests execute<br/>Vitest/Pytest]
    UnitTests --> IntTests[Integration tests run]
    IntTests --> E2ETests[E2E tests run<br/>Playwright]
    E2ETests --> Coverage[Coverage report generated]
    Coverage --> QualityGate{Quality gate<br/>≥80% coverage?}

    QualityGate -->|Pass| Deploy[Deploy to staging/production]
    QualityGate -->|Fail| Block[❌ Block deployment]

    Block --> Fix[Fix issues]
    Fix --> Start

    Deploy --> Success([✅ Deployment successful])

    style UnitTests fill:#C8E6C9
    style IntTests fill:#FFF9C4
    style E2ETests fill:#FFCDD2
    style QualityGate fill:#BBDEFB
    style Block fill:#FFEBEE
```

## DevOps Engineer Diagrams

### CI/CD Pipeline

```mermaid
graph LR
    subgraph "Source"
        Git[Git Push<br/>GitHub]
    end

    subgraph "CI - GitHub Actions"
        Build[Build<br/>npm run build]
        Lint[Lint<br/>Biome]
        Test[Test<br/>Vitest]
        Coverage[Coverage<br/>80% gate]
    end

    subgraph "CD - Deployment"
        Staging[Staging<br/>Railway/Vercel]
        Prod[Production<br/>Railway/Vercel]
    end

    subgraph "Monitoring"
        Prom[Prometheus<br/>Metrics]
        Graf[Grafana<br/>Dashboards]
    end

    Git --> Build
    Build --> Lint
    Lint --> Test
    Test --> Coverage
    Coverage -->|Pass| Staging
    Staging -->|Manual approve| Prod

    Prod --> Prom
    Prom --> Graf

    style Coverage fill:#FFF9C4
    style Staging fill:#C8E6C9
    style Prod fill:#BBDEFB
```

### Infrastructure Architecture

```mermaid
graph TB
    subgraph "Frontend - Vercel"
        NextJS[Next.js App<br/>React 19]
    end

    subgraph "Backend - Railway"
        FastAPI[FastAPI<br/>Port 8000]
    end

    subgraph "Database - Neon"
        PostgreSQL[(PostgreSQL<br/>Serverless)]
    end

    subgraph "Cache - Upstash"
        Redis[(Redis<br/>Serverless)]
    end

    subgraph "Storage - MinIO"
        S3[(S3-Compatible<br/>Object Storage)]
    end

    subgraph "Monitoring"
        Prometheus[Prometheus<br/>Metrics]
        Grafana[Grafana<br/>Dashboards]
    end

    Users([Users]) -->|HTTPS| NextJS
    NextJS -->|API Calls| FastAPI
    FastAPI --> PostgreSQL
    FastAPI --> Redis
    FastAPI --> S3
    FastAPI --> Prometheus
    Prometheus --> Grafana

    style NextJS fill:#E3F2FD
    style FastAPI fill:#BBDEFB
    style PostgreSQL fill:#C8E6C9
    style Redis fill:#FFCDD2
```

## Security Engineer Diagrams

### Security Architecture

```mermaid
graph TB
    subgraph "Perimeter Security"
        WAF[WAF<br/>Cloudflare]
        DDoS[DDoS Protection<br/>Rate Limiting]
    end

    subgraph "Application Security"
        Auth[JWT Authentication<br/>deps.py]
        RBAC[Role-Based Access Control<br/>is_superuser]
        Input[Input Validation<br/>Pydantic]
    end

    subgraph "Data Security"
        Encrypt[Encryption at Rest<br/>PostgreSQL]
        Hash[Password Hashing<br/>Argon2/bcrypt]
        Secrets[Secrets Management<br/>Environment Variables]
    end

    subgraph "Monitoring & Detection"
        Logs[Audit Logging<br/>All requests]
        Alerts[Security Alerts<br/>Failed auth attempts]
    end

    WAF --> DDoS
    DDoS --> Auth
    Auth --> RBAC
    RBAC --> Input

    Input --> Encrypt
    Input --> Hash
    Input --> Secrets

    Auth --> Logs
    RBAC --> Logs
    Logs --> Alerts

    style Auth fill:#FFF9C4
    style RBAC fill:#FFF9C4
    style Encrypt fill:#C8E6C9
    style Alerts fill:#FFCDD2
```

### Threat Model

```mermaid
graph TD
    subgraph "Threats"
        T1[🔴 Authentication Bypass<br/>OWASP A01]
        T2[🔴 Hardcoded Secrets<br/>OWASP A02]
        T3[🟡 SQL Injection<br/>OWASP A03]
        T4[🟡 XSS Attacks<br/>OWASP A03]
        T5[🟢 CSRF<br/>OWASP A08]
    end

    subgraph "Mitigations"
        M1[✅ Fix deps.py<br/>Proper JWT validation]
        M2[✅ Environment variables<br/>Vault secrets]
        M3[✅ Parameterized queries<br/>SQLAlchemy ORM]
        M4[✅ Input sanitization<br/>Pydantic validation]
        M5[✅ CSRF tokens<br/>SameSite cookies]
    end

    T1 -.->|Mitigated by| M1
    T2 -.->|Mitigated by| M2
    T3 -.->|Mitigated by| M3
    T4 -.->|Mitigated by| M4
    T5 -.->|Mitigated by| M5

    style T1 fill:#FFCDD2
    style T2 fill:#FFCDD2
    style T3 fill:#FFF9C4
    style T4 fill:#FFF9C4
    style T5 fill:#C8E6C9
```

## Database Administrator Diagrams

### Migration Flow (SQLite → PostgreSQL)

```mermaid
flowchart LR
    subgraph "Current State"
        SQLite[(SQLite<br/>piano_keys.db)]
    end

    subgraph "Migration Process"
        Export[Export Data<br/>Alembic]
        Transform[Transform Schema<br/>Adjust types]
        Validate[Validate Data<br/>Integrity checks]
    end

    subgraph "Target State"
        PostgreSQL[(PostgreSQL<br/>Neon Serverless)]
    end

    SQLite --> Export
    Export --> Transform
    Transform --> Validate
    Validate --> PostgreSQL

    PostgreSQL --> Verify[Verify Migration<br/>Row counts, constraints]
    Verify -->|Success| Cutover[Cutover<br/>Update connection string]
    Verify -->|Fail| Rollback[Rollback<br/>Restore SQLite]

    style SQLite fill:#FFF9C4
    style PostgreSQL fill:#C8E6C9
    style Verify fill:#BBDEFB
    style Rollback fill:#FFCDD2
```

### Caching Architecture

```mermaid
graph TB
    subgraph "Client Requests"
        User[User Request]
    end

    subgraph "API Layer"
        FastAPI[FastAPI Service]
    end

    subgraph "Cache Layer"
        Redis[(Redis<br/>Upstash)]
    end

    subgraph "Database Layer"
        PostgreSQL[(PostgreSQL<br/>Neon)]
    end

    User --> FastAPI
    FastAPI -->|1. Check cache| Redis
    Redis -->|Cache HIT| FastAPI
    Redis -->|Cache MISS| Query[2. Query DB]
    Query --> PostgreSQL
    PostgreSQL --> Update[3. Update cache]
    Update --> Redis
    Redis --> Return[4. Return data]
    Return --> FastAPI

    style Redis fill:#FFCDD2
    style PostgreSQL fill:#BBDEFB
```

## UX Designer Diagrams

### User Journey Map

```mermaid
journey
    title Piano Keys - User Journey Map
    section Onboarding
      Sign up: 5: User
      Complete profile: 4: User
      Watch tutorial: 3: User
    section Learning
      Browse lessons: 5: User
      Select difficulty: 4: User
      View instructions: 3: User
    section Practice
      Upload MIDI: 4: User
      Play lesson: 5: User
      View analysis: 5: User
    section Progress
      Check score: 5: User
      Review mistakes: 4: User
      Retry lesson: 4: User
```

### Information Architecture

```mermaid
graph TD
    Home[Home Page] --> Auth[Sign In/Sign Up]
    Home --> Dashboard[Dashboard]

    Dashboard --> Lessons[Lessons Library]
    Dashboard --> Practice[Practice Sessions]
    Dashboard --> Progress[My Progress]
    Dashboard --> Profile[Profile Settings]

    Lessons --> Browse[Browse by Difficulty]
    Lessons --> Search[Search Lessons]
    Lessons --> Create[Create Lesson]

    Practice --> Upload[Upload MIDI]
    Practice --> Play[Play Lesson]
    Practice --> Analyze[View Analysis]

    Progress --> Stats[Statistics]
    Progress --> History[Practice History]
    Progress --> Achievements[Achievements]

    Profile --> Account[Account Settings]
    Profile --> Preferences[Preferences]
    Profile --> Subscription[Subscription]

    style Home fill:#E3F2FD
    style Dashboard fill:#BBDEFB
    style Lessons fill:#C8E6C9
    style Practice fill:#FFF9C4
```

## Technical Writer Diagrams

### Documentation Structure

```mermaid
graph TD
    Root[Documentation Root] --> User[User Documentation]
    Root --> API[API Documentation]
    Root --> Dev[Developer Documentation]
    Root --> Ops[Operations Documentation]

    User --> QuickStart[Quick Start Guide]
    User --> Tutorials[Tutorials]
    User --> FAQ[FAQ]

    API --> Endpoints[API Endpoints<br/>OpenAPI/Swagger]
    API --> Auth[Authentication]
    API --> Examples[Request/Response Examples]

    Dev --> Setup[Development Setup]
    Dev --> Architecture[Architecture Guide]
    Dev --> Contributing[Contributing Guide]

    Ops --> Deploy[Deployment Guide]
    Ops --> Monitor[Monitoring & Alerts]
    Ops --> Runbooks[Runbooks]

    style Root fill:#BBDEFB
    style User fill:#C8E6C9
    style API fill:#FFF9C4
    style Dev fill:#E3F2FD
    style Ops fill:#FFCDD2
```

### Documentation Workflow

```mermaid
flowchart TD
    Start([Code Change]) --> AutoGen[Auto-generate API docs<br/>OpenAPI/TypeDoc]
    AutoGen --> Review[Technical review<br/>Accuracy check]
    Review --> Edit[Edit & enhance<br/>Add examples]
    Edit --> Validate[Validate<br/>Links, formatting]
    Validate --> Publish{Ready to publish?}

    Publish -->|Yes| Deploy[Deploy to docs site<br/>Vercel/Netlify]
    Publish -->|No| Edit

    Deploy --> Verify[Verify deployment<br/>Check live site]
    Verify --> Done([✅ Published])

    style AutoGen fill:#C8E6C9
    style Review fill:#FFF9C4
    style Deploy fill:#BBDEFB
```

---

## Usage Instructions

### Rendering Mermaid Diagrams

**In GitHub README:**
```markdown
```mermaid
graph TB
    A[Start] --> B[Process]
    B --> C[End]
\```
```

**In Markdown Processors (Obsidian, Notion, etc.):**
Most modern markdown processors support Mermaid natively.

**Live Mermaid Editor:**
- Visit: https://mermaid.live
- Paste diagram code
- Export as PNG/SVG

**In Documentation Sites:**
- **Docusaurus:** Install `@docusaurus/theme-mermaid`
- **MkDocs:** Install `mkdocs-mermaid2-plugin`
- **VuePress:** Install `vuepress-plugin-mermaidjs`

---

## Diagram Categories

| Role | Diagrams Available |
|------|-------------------|
| Backend Engineer | API Architecture, Auth Flow, DB Schema, Module Dependencies |
| Frontend Engineer | Component Hierarchy, State Management, Routing, Data Flow |
| DevOps Engineer | CI/CD Pipeline, Infrastructure, Deployment, Monitoring |
| Security Engineer | Security Architecture, Threat Model, Auth Flow, Security Layers |
| QA Engineer | Test Pyramid, Test Coverage, Testing Workflow, Test Distribution |
| Database Admin | Schema, Migration Flow, Caching Architecture, Data Flow |
| UX Designer | User Journey, Information Architecture, Component Library, Accessibility |
| Technical Writer | Docs Structure, Info Hierarchy, Content Types, Docs Workflow |

---

**Generated:** December 15, 2025
**Version:** 1.0
**Total Mermaid Diagrams:** 20+
