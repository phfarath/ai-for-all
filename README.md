# Plataforma de Ensino de IA

Uma plataforma de aprendizado interativo baseada em IA que combina:

- **Backend**: FastAPI com arquitetura modular (LMS, CMS, LLM proxy, analytics)
- **Frontend**: React PWA com TypeScript, Vite, e Zustand
- **BaaS**: Supabase (Auth, Postgres, Storage)

## Arquitetura

A arquitetura completa é documentada nos diagramas Mermaid incluídos na documentação do projeto, abrangendo:

- **Client**: React PWA com dashboard do aluno, tutor LLM, labs de código (Pyodide), pipelines no-code (WASM sklearn), player de vídeo interativo, editor de curso, uploader de mídia, busca e recomendações
- **API**: FastAPI monolítico com gateway, autenticação JWT, rate limiting, e APIs modulares (Learning, CMS, LLM Proxy, Search, Recommendations, Analytics, Usage)
- **BaaS**: Supabase para autenticação OAuth, banco de dados Postgres (≤500MB), e storage (≤1GB)
- **Workers**: Indexador de busca, agregador de analytics, e pré-computação de FAQ

## Primeiros Passos

### Backend

1. Navegue até o diretório `backend/`
2. Crie um ambiente virtual Python e instale as dependências:

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # ou .venv\Scripts\activate no Windows
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente:

   ```bash
   cp .env.example .env
   # Edite .env com suas credenciais do Supabase
   ```

4. Inicie o servidor de desenvolvimento:

   ```bash
   uvicorn app.main:app --reload
   ```

   A API estará disponível em `http://localhost:8000`.

### Frontend

1. Navegue até o diretório `frontend/`
2. Instale as dependências:

   ```bash
   cd frontend
   npm install
   ```

3. Configure as variáveis de ambiente:

   ```bash
   cp .env.example .env
   # Edite .env com suas credenciais do Supabase e URL da API
   ```

4. Inicie o servidor de desenvolvimento:

   ```bash
   npm run dev
   ```

   O aplicativo estará disponível em `http://localhost:5173`.

## Estrutura do Projeto

```
.
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # Routers versionados (v1)
│   │   ├── core/     # Configuração central
│   │   ├── dependencies/  # Dependências injetáveis (Supabase, etc)
│   │   └── schemas/  # Pydantic models
│   └── requirements.txt
├── frontend/          # React PWA
│   ├── src/
│   │   ├── lib/      # Clientes (Supabase, API)
│   │   ├── pages/    # Componentes de página
│   │   └── store/    # Gerenciamento de estado (Zustand)
│   └── package.json
└── README.md
```

## Principais Recursos (Planejados)

- **LMS completo**: trilhas de aprendizado, módulos, lições, inscrições e progresso
- **Tutor com IA**: chat contextualizado com orçamento de tokens e cache
- **Labs de código**: ambiente Pyodide para executar Python no navegador
- **Pipelines no-code**: construtor visual usando WASM + sklearn
- **Player de vídeo interativo**: perguntas inline e marcadores
- **Editor de curso**: rich text editor + quiz builder
- **Busca e recomendações**: FTS no Postgres + algoritmos de recomendação
- **Analytics**: agregação de eventos para alunos e instrutores

## Status Atual

Este é o commit inicial da arquitetura base. Implementações futuras incluirão:

- Autenticação JWT e RBAC
- Endpoints modulares para LMS, CMS, LLM, busca, analytics
- Componentes de UI para dashboard, lições, labs
- Workers para indexação e agregação
- PWA offline-first com IndexedDB

## Documentação

Consulte os READMEs individuais:

- [Backend README](./backend/README.md)
- Mais documentação será adicionada conforme o projeto evolui

## Licença

Projeto interno / a definir.
