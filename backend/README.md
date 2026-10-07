# SkillSwap AI — Backend Foundation API

FastAPI & PostgreSQL backend foundation for **SkillSwap AI**, a student skill exchange and recommendation system.

---

## 🏗️ Backend Architecture & Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Server:** [Uvicorn](https://www.uvicorn.org/)
- **Database ORM:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Database Driver:** [Psycopg 3](https://www.psycopg.org/)
- **Data Validation & Settings:** [Pydantic v2](https://docs.pydantic.dev/) & `pydantic-settings`
- **Future Recommendation Engine Module:** Scikit-learn (cosine similarity & 2-way skill matching matrix)

---

## 📁 Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point & CORS configuration
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Environment settings & Pydantic validation
│   │   └── database.py          # SQLAlchemy engine, SessionLocal, Base & get_db dependency
│   ├── models/                  # Database ORM models (Planned for Stage 3)
│   │   ├── __init__.py
│   │   └── README.md
│   ├── schemas/                 # Pydantic schemas (Planned for Stage 3)
│   │   ├── __init__.py
│   │   └── README.md
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── health.py        # GET /api/health endpoint
│   └── services/                # Business logic & recommendation engine services
│       ├── __init__.py
│       └── README.md
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Setup & Local Execution Guide

### 1. Create a Python Virtual Environment

From inside the `backend/` directory:

#### On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Environment Configuration (`.env`)

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Open `.env` and configure your local PostgreSQL credentials:

```env
PROJECT_NAME="SkillSwap AI API"
API_V1_STR="/api"
ENVIRONMENT="development"
CORS_ORIGINS="http://localhost:5173,http://localhost:5174"

# PostgreSQL connection string format:
# postgresql+psycopg://username:password@localhost:5432/database_name
DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/skillswap_db"
```

---

### 4. Run the FastAPI Development Server

Start the server using `uvicorn`:

```bash
uvicorn app.main:app --reload --port 8000
```

The server will launch at `http://localhost:8000`.

---

### 5. Verify the API Health Check Endpoint

Open your browser or run cURL:

```bash
curl http://localhost:8000/api/health
```

#### Expected JSON Response:
```json
{
  "status": "ok",
  "service": "SkillSwap AI API"
}
```

Interactive OpenAPI documentation is available at `http://localhost:8000/docs`.
