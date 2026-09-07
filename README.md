# Kishan Bari — full-stack MVP

Kishan Bari is a Bangla-first soil-test recording and decision-support prototype. This repository contains a static frontend, a FastAPI backend, PostgreSQL-compatible data models, a conservative rules engine, and an ML training pipeline that refuses to train on fewer than 200 verified records.

## What is actually implemented

- Account registration and JWT login
- Farmer-owned fields
- Soil-test submissions
- pH, N, P, K, texture, moisture and drainage validation
- Safe rule-based Bangla analysis
- Confidence and expert-review flags
- Analysis history and farmer feedback
- Admin verification queue
- Supabase/PostgreSQL compatibility
- Local SQLite development
- District-grouped ML evaluation pipeline
- API tests and interactive API documentation

The project does **not** claim to contain a trained agricultural model. `training_data_template.csv` contains one clearly marked fake example to document the schema. A model should only be trained after verified laboratory or expert-labelled records are collected.

## Project structure

```text
frontend/                 Static HTML, CSS and JavaScript
backend/app/              FastAPI application
backend/sql/              Supabase SQL schema
backend/tests/            Automated API tests
backend/train_model.py    Auditable baseline training script
backend/render.yaml       Render deployment configuration
```

## Run locally

### 1. Backend

Open a terminal in `backend`:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to use every backend route without building extra UI forms.

### 2. Frontend

In another terminal:

```bash
cd frontend
python -m http.server 5500
```

Open `http://127.0.0.1:5500`. `frontend/config.js` already points to the local backend.

### 3. Tests

From `backend`:

```bash
pytest -q
```

## Create the Supabase database

1. Create a project at Supabase.
2. Open **SQL Editor**.
3. Paste and run `backend/sql/001_initial_schema.sql`.
4. Click **Connect** in Supabase and copy the **Session pooler** connection string if your host requires IPv4.
5. Change the prefix from `postgres://` to `postgresql://` if necessary.
6. Store the complete value as `DATABASE_URL` on Render. Never place it in GitHub or frontend JavaScript.

The backend connects to Supabase as a trusted server. Farmers never receive the database password.

## Deploy the backend on Render

1. Push the complete repository to GitHub.
2. Create a **Web Service** in Render and connect the repository.
3. Set **Root Directory** to `backend`.
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:

```text
APP_ENV=production
DATABASE_URL=<Supabase session-pooler connection string>
JWT_SECRET=<a randomly generated long secret>
FRONTEND_ORIGINS=https://your-frontend.vercel.app
ADMIN_EMAIL=<your private admin email>
```

7. Deploy and open `https://YOUR-RENDER-URL/health`.
8. Confirm that `status` is `ok`.

## Deploy the frontend on Vercel

1. Import the same GitHub repository in Vercel.
2. Set **Root Directory** to `frontend`.
3. No build command is required.
4. Before deployment, change `API_BASE_URL` inside `frontend/config.js`:

```js
window.KISHAN_CONFIG = {
  API_BASE_URL: "https://YOUR-RENDER-URL/api/v1"
};
```

5. Deploy.
6. Copy the final Vercel URL into Render's `FRONTEND_ORIGINS` and redeploy the backend.

## First API workflow

In `/docs`, use the routes in this order:

1. `POST /api/v1/auth/register`
2. Copy the returned token and click **Authorize**
3. `POST /api/v1/fields`
4. Copy the returned field ID
5. `POST /api/v1/soil-tests`
6. Copy the returned test ID
7. `POST /api/v1/soil-tests/{test_id}/analyze`

## Training the first real model

Create a verified CSV following `training_data_template.csv`, then run:

```bash
python train_model.py verified_soil_data.csv
```

The script:

- requires at least 200 verified rows;
- separates training and testing by district;
- encodes categorical data;
- trains a balanced random forest baseline;
- prints a classification report; and
- saves a versioned model artifact.

Do not commit private farmer data, database passwords, JWT secrets, raw location histories or unlicensed datasets.

## What must happen before public agricultural use

- Validate the kit against laboratory measurements.
- Review thresholds with Bangladeshi soil/agriculture specialists.
- Add source and verification fields to every training record.
- Measure errors separately by district, crop and season.
- Establish a model approval and rollback procedure.
- Add rate limiting, password reset, email verification and audit logs.
- Obtain a privacy policy and user consent for precise location or photographs.

This repository is a functional engineering MVP, not a certified fertilizer-prescription system.
