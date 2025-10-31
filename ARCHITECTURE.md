# Arquitetura da Plataforma

Este documento detalha a arquitetura completa da Plataforma de Ensino de IA.

## Visão Geral do Sistema

```mermaid
flowchart LR
  subgraph Client["React PWA"]
    UI[Dashboard do Aluno]
    Tutor[LLM Tutor Widget]
    Labs[Code Labs 'Pyodide']
    Pipelines[No-code Pipelines 'WASM sklearn']
    Player[Video Player Interativo 'questions/bookmarks']
    Editor[Editor de Curso 'Rich text + Quiz Builder']
    Uploader[Uploader de Mídia 'video/pdf/img']
    Search[Busca + Filtros]
    Reco[Recomendações]
    Instr[Painel Instrutor\nAnalytics básico]
    Cache[IndexedDB + PWA Cache]
  end

  subgraph Edge["BaaS (Grátis/baixo custo)"]
    SBAUTH[Supabase Auth]
    SDB[(Supabase Postgres ≤500MB)]
    SSTOR[(Supabase Storage ≤1GB)]
  end

  subgraph API["FastAPI (/v1)"]
    GW[Gateway + Auth JWT + Rate Limit]
    LMS[Learning API 'paths, modules, lessons, enrollment, progress']
    CMS[CMS API\nconteúdo, assets, versionamento]
    LLM[LLM Proxy\nquota + cache + custo]
    SRCH[Search API\nconsulta + sugestão]
    RECO[Recommendations API\nnext-best-module]
    AN[Analytics API\nagregados aluno/instrutor]
    USG[Usage API\nllm_usage, export]
  end

  subgraph Workers["CPU-only Workers"]
    IDX[Search Indexer 'tsvector/FTS']
    AGG[Analytics Aggregator 'Eventos→Snapshots']
    FAQ[FAQ Precompute\nrespostas cache]
  end

  Client <-->|OAuth| SBAUTH
  Client <--> GW
  GW --- SDB
  GW --- SSTOR
  GW --> LLM
  LLM --- SDB

  GW --> LMS
  GW --> CMS
  GW --> SRCH
  GW --> RECO
  GW --> AN

  IDX <-. batch .-> SDB
  AGG <-. batch .-> SDB
  FAQ -. lê lições .-> SSTOR
  FAQ -. grava .-> SDB

  Client <--> Cache
```

## Arquitetura do Frontend

```mermaid
graph TD
  App[React PWA 'Vite+TS'] --> Router[React Router]
  App --> Store[Zustand/Context]
  App --> I18N[i18next + A11y]
  App --> PWA[Workbox + IndexedDB]

  Router --> AuthGate
  AuthGate --> Home
  AuthGate --> Dashboard
  AuthGate --> OnboardingQuiz
  AuthGate --> PathSelector
  AuthGate --> ModuleList
  AuthGate --> LessonViewer
  AuthGate --> VideoLesson[Video Player Interativo]
  AuthGate --> TutorWidget
  AuthGate --> CodeLabs[Pyodide]
  AuthGate --> PipelineBuilder[WASM sklearn]
  AuthGate --> SearchPage[Busca + Filtros]
  AuthGate --> RecoPage[Recomendações]
  AuthGate --> ProgressPage
  AuthGate --> InstructorLite
  AuthGate --> CourseEditor[Editor de Curso]
  AuthGate --> MediaManager[Uploader/Gerenciador]
  AuthGate --> Profile

  LessonViewer --> GlossaryPopover
  TutorWidget --> TokenMeter
  TutorWidget --> QuotaBanner
  VideoLesson --> InlineQuiz[Embedded Questions]
  VideoLesson --> Bookmarks[Marcadores/Pontos-chave]

  CodeLabs --> NotebookFrame
  CodeLabs --> TestsPanel

  PipelineBuilder --> BlockLibrary
  PipelineBuilder --> Canvas
  PipelineBuilder --> RunPanel

  CourseEditor --> RichText
  CourseEditor --> QuizBuilder
  CourseEditor --> OutlineManager
  MediaManager --> VideoUpload
  MediaManager --> PdfUpload
  MediaManager --> AssetTable
```

## Arquitetura do Backend

```mermaid
flowchart LR
  subgraph FastAPI["FastAPI Monolito (v1)"]
    GW[API Gateway · JWT · CORS · RateLimit]
    AUTHZ[RBAC Middleware]
    LMS[Learning API 'paths, modules, lessons, enrollments, progress']
    CMS[CMS API 'content, assets, versions, quizzes']
    MEDIA[Media API 'signed-url, metadata']
    LLM[LLM Proxy 'tutor chat, quota, cache, cost']
    SRCH[Search API 'search, suggest']
    RECO[Recommendations API 'next best module']
    ANALYTICS[Analytics API 'learner, instructor']
    USAGE[Usage API 'usage me/admin, export progress.csv']
    EVENTS[Events API 'video_play, inline_quiz, search_click']
  end

  subgraph Supabase["Supabase"]
    AUTH[Auth]
    DB[(Postgres)]
    STOR[(Storage)]
  end

  Client[React PWA] <-->|OAuth| AUTH
  Client <--> GW

  GW --- DB
  CMS --- STOR
  MEDIA --- STOR
  LLM --- DB
  SRCH --- DB
  RECO --- DB
  ANALYTICS --- DB
  EVENTS --- DB
```

## Modelo de Dados

```mermaid
erDiagram
  USERS ||--o{ ENROLLMENTS : matricula
  USERS ||--o{ PROGRESS : progresso
  USERS ||--o{ USER_BADGES : badges
  USERS ||--o{ LLM_USAGE : cotas
  PATHS ||--o{ MODULES : contem
  MODULES ||--o{ LESSONS : contem
  LESSONS ||--o{ QUIZZES : quizzes
  LESSONS ||--o{ LESSON_ASSETS : assets
  LESSONS ||--o{ FAQ_CACHE : faq
  LESSONS ||--o{ VIDEO_EVENTS : video_eventos
  COURSES ||--o{ ENROLLMENTS : tem
  COURSES ||--o{ COURSE_VERSIONS : versoes
  BADGES ||--o{ USER_BADGES : associa

  USERS {
    uuid id
    text email
    text name
    text role
    timestamptz created_at
  }

  COURSES {
    uuid id
    text slug
    text title
    text locale
    text description
    boolean published
  }

  ENROLLMENTS {
    uuid id
    uuid user_id
    uuid course_id
    timestamptz enrolled_at
  }

  PATHS {
    uuid id
    text slug
    text title
    text locale
  }

  MODULES {
    uuid id
    uuid path_id
    int ord
    text title
    text summary
  }

  LESSONS {
    uuid id
    uuid module_id
    text slug
    text title
    text md_url
    int rev
    text type
  }

  LESSON_ASSETS {
    uuid id
    uuid lesson_id
    text asset_type
    text storage_key
    jsonb metadata
  }

  QUIZZES {
    uuid id
    uuid lesson_id
    jsonb spec_json
  }

  PROGRESS {
    uuid id
    uuid user_id
    uuid lesson_id
    int score
    jsonb detail_json
    timestamptz updated_at
  }

  BADGES {
    uuid id
    text code
    text title
  }

  USER_BADGES {
    uuid id
    uuid user_id
    uuid badge_id
    timestamptz awarded_at
  }

  FAQ_CACHE {
    uuid id
    uuid lesson_id
    text qhash
    text answer
    timestamptz created_at
  }

  LLM_USAGE {
    uuid id
    uuid user_id
    date day
    int calls
    int in_tokens
    int out_tokens
    int cost_cents
  }

  VIDEO_EVENTS {
    uuid id
    uuid lesson_id
    uuid user_id
    text event_type
    jsonb payload
    timestamptz ts
  }

  SEARCH_INDEX {
    uuid id
    text doc_type
    uuid doc_id
    text text_blob
    text tsv
  }

  RECO_EVENTS {
    uuid id
    uuid user_id
    text action
    uuid ref_id
    text ref_type
    timestamptz ts
  }

  COURSE_VERSIONS {
    uuid id
    uuid course_id
    int rev
    jsonb diff_json
    timestamptz created_at
  }
```

## Fluxos Principais

### 1. Tutor Chat com Orçamento

```mermaid
sequenceDiagram
  participant UI as React Tutor
  participant API as FastAPI /tutor/chat
  participant LLM as Provider API
  participant DB as supabase(Postgres)

  UI->>API: POST messages + lesson_context
  API->>API: trim + estimate + quota check
  API->>DB: read llm_usage(user, day)
  alt cache hit
    API-->>UI: cached answer + usage=0
  else within quota
    API->>LLM: call(model, max_tokens=200)
    LLM-->>API: text + usage(in,out)
    API->>DB: upsert llm_usage(in,out,cost)
    API-->>UI: text + token+R$ estimate
  else quota exceeded
    API-->>UI: fallback answer + quota banner
  end
```

### 2. Carregamento de Lição com Cache

```mermaid
sequenceDiagram
  participant UI
  participant SW as PWA Cache
  participant ST as Supabase Storage

  UI->>SW: GET /lessons/slug.md
  alt cached
    SW-->>UI: cached MD
  else
    SW->>ST: signed GET
    ST-->>SW: 200 MD
    SW-->>UI: MD + add to cache
  end
```

### 3. Sincronização Offline de Progresso

```mermaid
sequenceDiagram
  participant UI as React PWA
  participant SW as Service Worker
  participant API as FastAPI /progress
  participant DB as supabase(Postgres)

  UI->>SW: enqueue progress payload
  SW-->>UI: stored in IndexedDB (queued)
  SW->>API: sync batch when online
  API->>DB: insert rows with auth.uid()
  DB-->>API: 200
  API-->>SW: ack/ purge queue
```

### 4. Pré-computação de FAQ

```mermaid
sequenceDiagram
  participant WK as Cache Builder
  participant ST as Storage
  participant DB as Postgres

  WK->>ST: read lesson MD
  WK->>WK: extract Q pairs offline (dev task)
  WK->>DB: upsert faq_cache(qhash, answer)
```

## Decisões Arquiteturais

### Escolha do Stack

- **FastAPI**: Performance Python + OpenAPI docs + async nativo
- **React + Vite**: DX rápido, TypeScript, PWA moderna
- **Supabase**: Free tier generoso, Postgres real, Auth OAuth
- **Pyodide**: Python no browser sem backend
- **WASM**: sklearn/numpy em pipeline visual

### Offline-First

- Service Worker + IndexedDB para lições em cache
- Queue de progresso sincroniza em background
- Fallback gracioso quando API offline

### Custo e Escalabilidade

- Free tier do Supabase (500MB DB, 1GB storage)
- Workers CPU-only (sem GPU)
- LLM quota por usuário + cache de perguntas frequentes

### Segurança

- JWT tokens via Supabase Auth
- Row Level Security (RLS) no Postgres
- Rate limiting no gateway
- CORS configurado

## Próximos Passos

1. Implementar autenticação JWT e RBAC
2. Criar tabelas no Supabase Postgres
3. Desenvolver endpoints modulares (LMS, CMS, etc)
4. Construir componentes React para dashboard e lições
5. Integrar Pyodide para code labs
6. Adicionar PWA offline capabilities com IndexedDB
7. Implementar workers para indexação e analytics
