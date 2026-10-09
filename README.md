# SkillSwap AI
### A Hybrid Recommendation System for Student Skill Exchange

SkillSwap AI is a full-stack web application that connects students for reciprocal skill exchange. It recommends potential learning partners by analyzing the skills students can teach, the skills they want to learn, and their interaction history.

The goal is to make peer-to-peer learning more accessible by helping students find partners who can learn from each other.

**Live Demo:** [SkillSwap AI](https://skillswap-ai-alpha.vercel.app)  
**Backend API:** [FastAPI Service](https://skillswap-ai-backend-obqv.onrender.com)  
**API Documentation:** [Swagger UI](https://skillswap-ai-backend-obqv.onrender.com/docs)  
**Repository:** [GitHub](https://github.com/shreydarshan/skillswap-ai)

---

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [Recommendation Algorithm](#recommendation-algorithm)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Database Design](#database-design)
- [API Overview](#api-overview)
- [Getting Started](#getting-started)
- [Environment Configuration](#environment-configuration)
- [Testing](#testing)
- [Deployment](#deployment)
- [Security](#security)
- [Limitations and Future Improvements](#limitations-and-future-improvements)
- [Author](#author)

---

## Overview

Students often possess skills that others want to learn, while also having their own learning goals. SkillSwap AI connects these complementary needs through a recommendation engine designed around mutual skill compatibility.

For example:

| Student | Can Teach | Wants to Learn |
|---|---|---|
| Student A | Python, SQL | React, UI/UX Design |
| Student B | React, UI/UX Design | Python, SQL |

These students are strong potential exchange partners because each can teach skills the other wants to learn.

Unlike a conventional course platform, SkillSwap AI focuses on **reciprocal learning between students**.

### Problem Statement

Finding a suitable peer-learning partner can be difficult. Students may not know who has the skills they need or whether they can offer something valuable in return.

SkillSwap AI addresses this problem by comparing teaching skills and learning goals, ranking potential partners, and providing a platform for students to request swaps, communicate, and complete exchanges.

## Key Features

### Student Profiles
- User registration and login.
- Profile information, biography, and university details.
- Customizable avatar or profile image.
- Separate teaching-skill and learning-goal lists.
- Persistent profile data stored in PostgreSQL.

### Recommendation System
- Reciprocal skill compatibility scoring.
- Cosine similarity for skill-profile comparison.
- Collaborative filtering based on user interactions.
- Hybrid ranking with configurable weights.
- Cold-start handling for users with limited interaction history.
- Explanations based on actual skill overlap.

### Skill Exchange
- Discover and explore students.
- View student profiles and relevant skills.
- Send, accept, or decline swap requests.
- Prevent duplicate active requests in either direction.
- Track pending, connected, and completed relationships.
- Complete an exchange while preserving chat history.

### Messaging
- Chat between connected students.
- Persistent message storage.
- Authorization checks for conversation participants.
- Protection against unauthorized messaging.

### User Experience
- Responsive desktop and mobile interface.
- Reusable React components.
- Search and discovery interfaces.
- Profile cards, skill tags, and recommendation scores.
- Authentication state persistence.

---

## How It Works

1. **Create an account:** A student registers and creates a profile.
2. **Add skills:** The student specifies what they can teach and want to learn.
3. **Generate recommendations:** The backend compares student profiles and available interaction history.
4. **Rank potential partners:** The hybrid recommendation engine combines the available signals.
5. **Request a swap:** A student sends a request to a compatible partner.
6. **Connect and communicate:** After acceptance, connected students can chat.
7. **Complete the exchange:** The students can mark their skill swap as completed.

---

## Recommendation Algorithm

The recommendation engine combines content-based filtering and collaborative filtering.

### 1. Content-Based Filtering

Content-based filtering compares the skills one student wants to learn with the skills another student offers.

For students \(A\) and \(B\), the engine calculates two directional similarities.

**Forward compatibility**

How well B's offered skills match A's learning goals:

\[
F(A,B)=\operatorname{Cosine}(W_A,O_B)
\]

**Reverse compatibility**

How well A's offered skills match B's learning goals:

\[
R(A,B)=\operatorname{Cosine}(O_A,W_B)
\]

Where:

- \(O_A\): skills offered by student A.
- \(W_A\): skills wanted by student A.
- \(O_B\): skills offered by student B.
- \(W_B\): skills wanted by student B.

The reciprocal content score is:

\[
C(A,B)=\frac{F(A,B)+R(A,B)}{2}
\]

This approach rewards mutual compatibility rather than matching only one student's needs.

#### Cosine Similarity

Cosine similarity measures the similarity between two vectors:

\[
\operatorname{Cosine}(x,y)=
\frac{x\cdot y}{\|x\|\|y\|}
\]

SkillSwap AI represents skills using binary vectors derived from a shared skill vocabulary. A value of `1` indicates the presence of a skill, while `0` indicates its absence.

The implementation safely handles zero vectors to avoid division-by-zero errors.

### 2. Collaborative Filtering

Collaborative filtering uses interaction history to identify behavioral patterns among users.

The system records signals such as profile views, likes, swap requests, accepted swaps, and completed swaps.

The configured interaction weights are:

| Interaction | Weight |
|---|---:|
| View | 0.1 |
| Like | 0.3 |
| Request | 0.6 |
| Accept | 0.8 |
| Complete | 1.0 |

For a user-target pair, the implementation uses the maximum applicable interaction weight as its observed preference signal.

The collaborative engine calculates user-user cosine similarity and uses positively similar users to estimate interest in other candidates.

Conceptually:

\[
CF(A,C)=
\frac{\sum_U s(A,U)\,r(U,C)}
{\sum_U s(A,U)}
\]

Where:

- \(A\) is the current user.
- \(C\) is a candidate.
- \(U\) represents users with relevant interaction history.
- \(s(A,U)\) is the similarity between users.
- \(r(U,C)\) is the observed interaction signal.

The implementation handles unavailable collaborative evidence rather than inventing scores when interaction data is insufficient.

### 3. Hybrid Recommendation

The hybrid model combines reciprocal skill compatibility and collaborative evidence.

\[
H(A,B)=0.70C(A,B)+0.30CF(A,B)
\]

The initial configuration assigns:

- **70% weight** to reciprocal content-based compatibility.
- **30% weight** to collaborative filtering.

The weighting is a configurable baseline, not a claim that 70/30 is universally optimal.

### Cold-Start Handling

New users may have little or no interaction history. In these cases, collaborative filtering may not provide a meaningful score.

SkillSwap AI falls back to content-based recommendations when collaborative evidence is unavailable. This allows new users to receive recommendations without fabricated interaction data.

### Explainable Recommendations

The application can show why a student was recommended by identifying:

- Skills the candidate offers that the current student wants.
- Skills the current student offers that the candidate wants.
- Collaborative evidence when available.

### Evaluation

The project's evaluation work compares content-based, collaborative, and hybrid configurations, including 80/20, 70/30, 60/40, and 50/50 weightings.

Relevant ranking metrics include:

- Precision@K
- Recall@K
- Normalized Discounted Cumulative Gain (NDCG@K)
- Hit Rate@K
- Reciprocity-oriented evaluation

The preferred weighting should be justified using measured results rather than assumed to be optimal.

---

## System Architecture

SkillSwap AI uses a frontend-backend-database architecture.

```text
+----------------------------------+
|          React Frontend          |
|                                  |
| Vite | Tailwind CSS | Lucide     |
|                                  |
| Profiles, Explore, Chats, Swaps  |
+----------------+-----------------+
                 |
                 | HTTPS / REST API
                 | JWT Authentication
                 v
+----------------------------------+
|          FastAPI Backend         |
|                                  |
| Authentication and Authorization |
| Profile and Skill APIs           |
| Swap and Messaging APIs           |
| Recommendation Engine             |
+----------------+-----------------+
                 |
                 | SQLAlchemy / SQL
                 v
+----------------------------------+
|          PostgreSQL              |
|                                  |
| Users, Profiles, Skills           |
| Interactions, Swap Requests       |
| Messages, Ratings                 |
+----------------------------------+
```

### Frontend

The React frontend manages the user interface, navigation, forms, authentication state, and API communication.

### Backend

FastAPI handles authentication, authorization, profile management, skill operations, recommendations, swap requests, messaging, and database access.

### Database

PostgreSQL stores user accounts, profiles, skills, interactions, swap requests, messages, and ratings. The recommendation engine runs on the backend in Python.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| React | Frontend user interface |
| Vite | Development server and build tooling |
| Tailwind CSS | Responsive styling |
| Lucide React | Icons |
| Python | Backend and recommendation logic |
| FastAPI | REST API framework |
| SQLAlchemy | ORM and database access |
| PostgreSQL | Relational database |
| Neon | Hosted PostgreSQL |
| NumPy | Numerical operations |
| Scikit-learn | Cosine similarity and machine-learning utilities |
| JWT | Authentication tokens |
| pwdlib | Password hashing support |
| Pytest | Automated testing |
| Git and GitHub | Version control |
| Vercel | Frontend hosting |
| Render | Backend hosting |

---

## Database Design

The PostgreSQL database uses UUID-based primary keys, foreign keys, timestamps, relationships, and data-integrity constraints.

| Table | Purpose |
|---|---|
| `users` | Account and authentication information |
| `profiles` | Student profiles and preferences |
| `skills` | Shared skill vocabulary |
| `user_skills` | Skills associated with users |
| `interactions` | Behavioral signals for recommendations |
| `swap_requests` | Skill-exchange request lifecycle |
| `messages` | Chat messages |
| `ratings` | Ratings associated with exchanges |

Database constraints and backend validation help maintain consistent relationships and prevent invalid operations, including self-directed swaps and unauthorized access to private resources.

Demo profiles are distinguished from test accounts so test records can be excluded from recommendations.

---

## API Overview

The backend exposes REST endpoints through FastAPI.

| Endpoint | Purpose |
|---|---|
| `/api/health` | Backend health check |
| `/api/health/db` | Database connectivity check |
| `/api/auth/register` | Register a user |
| `/api/auth/login` | Authenticate a user |
| `/api/auth/me` | Retrieve the authenticated user |
| `/api/users` | User-related operations |
| `/api/profiles` | Profile management |
| `/api/skills` | Skill management |
| `/api/students` | Student discovery |
| `/api/recommendations` | Hybrid recommendations |
| `/api/recommendations/collaborative` | Collaborative recommendations |
| `/api/recommendations/hybrid` | Hybrid recommendation endpoint |
| `/api/messages/me` | Retrieve the current user's messages |
| `/api/messages/me/unread-count` | Retrieve unread message count |
| `/api/swap-requests` | Swap request operations |

Additional routes support individual resources and relationship-state queries.

Explore the interactive API documentation for available request schemas, parameters, and responses:

- [Swagger UI](https://skillswap-ai-backend-obqv.onrender.com/docs)
- [ReDoc](https://skillswap-ai-backend-obqv.onrender.com/redoc)

---

## Getting Started

### Prerequisites

Install:

- Git
- Node.js and npm
- Python compatible with the backend dependencies
- PostgreSQL, either locally or through a hosted provider such as Neon

### 1. Clone the repository

```bash
git clone https://github.com/shreydarshan/skillswap-ai.git
cd skillswap-ai
```

### 2. Set up the backend

```powershell
cd backend

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

For macOS/Linux, activate the virtual environment using:

```bash
source venv/bin/activate
```

### 3. Configure the database

Create a PostgreSQL database and configure the backend environment variables as described in the next section.

Use the repository's environment example and backend settings module to confirm the exact configuration names.

### 4. Start the backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

The API should be available at `http://127.0.0.1:8000`.

### 5. Install frontend dependencies

Open a new terminal at the repository root:

```bash
npm install
```

Create the frontend `.env` file:

```env
VITE_API_URL=http://127.0.0.1:8000/api
```

### 6. Start the frontend

```bash
npm run dev
```

Open the local URL printed by Vite, typically `http://localhost:5173`.

### 7. Build the frontend

```bash
npm run build
```

---

## Environment Configuration

### Backend

Configure the database URL, JWT signing secret, and allowed frontend origins using the exact variable names expected by the backend settings module.

Example local configuration:

```env
DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@localhost:5432/skillswap_db
JWT_SECRET=replace_with_a_secure_random_secret
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

These are illustrative values. Use the actual variable names and expected format defined in the project configuration.

Never commit real credentials or signing secrets.

### Frontend

The frontend uses `VITE_API_URL` to identify the backend API.

Local development:

```env
VITE_API_URL=http://127.0.0.1:8000/api
```

Production:

```env
VITE_API_URL=https://skillswap-ai-backend-obqv.onrender.com/api
```

Variables prefixed with `VITE_` are included in the client-side application bundle. Do not store secrets in frontend environment variables.

---

## Testing

The project includes automated backend tests for core functionality, including:

- Authentication and account lifecycle.
- Profile and skill operations.
- Reciprocal similarity calculations.
- Collaborative and hybrid recommendation logic.
- Cold-start behavior.
- Interaction tracking.
- Swap creation, acceptance, decline, and completion.
- Duplicate request prevention.
- Messaging permissions and account isolation.
- Test-account exclusion and demo-data behavior.

Run the backend tests from the repository root:

```bash
python -m pytest backend/tests/ -v
```

If using the Windows virtual environment:

```powershell
.\backend\venv\Scripts\python.exe -m pytest backend/tests/ -v
```

The final release verification recorded **54 passing backend tests** and a successful frontend production build. Test results apply to the tested version and environment and do not guarantee that every possible production scenario has been covered.

---

## Deployment

The application is deployed using separate services for source control, frontend hosting, backend hosting, and database hosting.

| Component | Platform |
|---|---|
| Source code | GitHub |
| Frontend | Vercel |
| Backend | Render |
| Database | Neon PostgreSQL |

### Deployment Flow

```text
GitHub
  |
  +----> Vercel: React Frontend
  |
  +----> Render: FastAPI Backend
                    |
                    v
                Neon PostgreSQL
```

### Production Links

- **Application:** https://skillswap-ai-alpha.vercel.app
- **Backend:** https://skillswap-ai-backend-obqv.onrender.com
- **API Documentation:** https://skillswap-ai-backend-obqv.onrender.com/docs

With automatic deployment configured, pushing to the connected GitHub branch can trigger a new deployment.

The backend's CORS configuration must allow the deployed frontend origin, and the Render service must use the intended Neon database connection string.

On Render's free tier, the backend may spin down after inactivity, delaying the first request.

---

## Security

Security measures include:

- Password hashing rather than plaintext password storage.
- JWT-based authentication for protected API operations.
- Server-side identity validation.
- Ownership and participation checks.
- Authorization checks for messaging and swap operations.
- Validation of swap lifecycle transitions.
- Filtering of test accounts from user-facing recommendations.
- Environment-based configuration for database credentials and JWT secrets.

The backend remains responsible for authorization decisions; the frontend does not serve as the security boundary.

---

## Limitations and Future Improvements

Potential future work includes:

- Evaluating recommendation quality on a larger set of genuine interactions.
- Comparing hybrid weights using ranking metrics.
- Improving cold-start performance when behavioral data is sparse.
- Exploring semantic skill similarity and learning-to-rank approaches.
- Considering proficiency, availability, and scheduling compatibility.
- Adding notifications, reporting, and moderation tools.
- Expanding accessibility and performance testing.

These are possible extensions, not claims about currently implemented functionality.

---

## Author

**Shrey Darshan**
**Raghuraj Singh Chauhan** 

- GitHub: [@shreydarshan](https://github.com/shreydarshan)
- Repository: [SkillSwap AI](https://github.com/shreydarshan/skillswap-ai)
- Live Application: [SkillSwap AI](https://skillswap-ai-alpha.vercel.app)

---


