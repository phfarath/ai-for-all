# AI Learning Platform Backend

This directory contains the FastAPI application that serves the AI Learning Platform API (`/v1`).

## Features

- FastAPI + Uvicorn base application
- Modular API router for versioned endpoints
- Centralized configuration via Pydantic settings
- Supabase client dependency (not yet used by endpoints)

## Getting Started

1. Create a virtual environment and install dependencies:

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy the example environment file and fill in your Supabase credentials:

   ```bash
   cp .env.example .env
   ```

3. Run the development server:

   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`. The primary API prefix is `/v1`.
