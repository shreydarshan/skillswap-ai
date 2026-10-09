# SkillSwap AI 🎓🤝

### A Hybrid Recommendation System for Student Skill Exchange

**Learn what you want. Teach what you know. Grow together.**

SkillSwap AI is a full-stack web application that connects students who want to exchange skills. It uses a hybrid recommendation system to identify compatible learning partners by analyzing the skills students can teach, the skills they want to learn, and their interactions with other students.

Instead of relying on a traditional course marketplace or paid tutoring model, SkillSwap AI encourages **peer-to-peer learning through reciprocal skill exchange**.

🌐 **Live Demo:** [Open SkillSwap AI](https://skillswap-ai-alpha.vercel.app)  
📦 **GitHub Repository:** [shreydarshan/skillswap-ai](https://github.com/shreydarshan/skillswap-ai)

---

## 📌 Table of Contents

- [Project Overview](#-project-overview)
- [Problem Statement](#-problem-statement)
- [Our Solution](#-our-solution)
- [Key Features](#-key-features)
- [How It Works](#-how-it-works)
- [Recommendation System](#-recommendation-system)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Database Design](#-database-design)
- [API Overview](#-api-overview)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Deployment](#-deployment)
- [Security and Privacy](#-security-and-privacy)
- [Testing and Quality Assurance](#-testing-and-quality-assurance)
- [Limitations and Future Improvements](#-limitations-and-future-improvements)
- [Learning Outcomes](#-learning-outcomes)
- [Author](#-author)
- [License](#-license)

---

## 🎯 Project Overview

SkillSwap AI is a student-focused skill-sharing platform powered by a hybrid recommendation engine.

Students create profiles, list the skills they can teach, and specify the skills they want to learn. The system compares student profiles and recommends potential partners based on **reciprocal skill compatibility**.

The application also tracks meaningful interactions, such as likes, swap requests, accepted swaps, and completed exchanges. These signals can support more personalized recommendations as interaction history grows.

### Example

Imagine two students:

| Student | Skills They Can Teach | Skills They Want to Learn |
|---|---|---|
| Student A | Python, SQL | React, UI/UX Design |
| Student B | React, UI/UX Design | Python, SQL |

These students are strong potential matches because each student can teach what the other wants to learn.

SkillSwap AI identifies this mutual compatibility and presents the students with an explainable recommendation.

### Project Goals

- Encourage collaborative and peer-to-peer learning.
- Help students discover learning partners more efficiently.
- Make skill exchange accessible through a responsive web application.
- Apply machine-learning concepts to a practical recommendation problem.
- Combine profile-based compatibility with behavioral interaction signals.
- Provide transparent recommendations instead of unexplained scores.

---

## ❗ Problem Statement

Students often want to learn practical skills but may face barriers such as expensive courses, limited access to mentors, and difficulty finding suitable learning partners.

At the same time, many students already possess valuable knowledge they could share with others.

Traditional learning platforms primarily help users find content, courses, or instructors. They do not necessarily help students find peers who can exchange skills with them in a mutually beneficial way.

**The problem:** How can we efficiently identify students whose learning goals and teaching abilities complement one another?

SkillSwap AI addresses this challenge through reciprocal skill matching and hybrid recommendations.

---

## 💡 Our Solution

SkillSwap AI provides a centralized platform where students can:

1. Create an account and build a profile.
2. Add skills they can teach.
3. Add skills they want to learn.
4. Discover recommended students.
5. Understand why a student was recommended.
6. Send, accept, or decline skill-swap requests.
7. Chat with connected students.
8. Mark an exchange as completed.

The recommendation engine initially focuses on skill compatibility. As users interact with the platform, collaborative signals can contribute to personalized rankings.

The system is designed to remain useful for new users who have little or no interaction history.

---

## ✨ Key Features

### 👤 Student Profiles

- Secure registration and login.
- Profile information, biography, and university details.
- Customizable avatar or profile image.
- Separate lists for teaching skills and learning goals.
- Persistent profile data stored in PostgreSQL.

### 🤖 Hybrid Recommendation Engine

- Reciprocal skill compatibility scoring.
- Cosine similarity for skill-profile comparison.
- User-user collaborative filtering.
- Configurable hybrid recommendation weights.
- Cold-start handling for users without interaction history.
- Duplicate and ineligible candidate filtering.

### 🔍 Explore and Discover

- Browse potential learning partners.
- View profile details and skill tags.
- See recommendation scores.
- Understand the skills that make a match relevant.

### 🔄 Skill-Swap Lifecycle

- Create and manage swap requests.
- Accept or decline incoming requests.
- Prevent duplicate active requests in either direction.
- Identify pending, connected, and completed relationships.
- Complete an exchange and reconnect later if desired.

### 💬 Messaging

- Chat with connected students.
- Persist messages in the database.
- Enforce conversation-participant permissions.
- Preserve chat history after an exchange is completed.

### 🔐 Authentication and Data Protection

- JWT-based authentication.
- Password hashing using Argon2/Bcrypt.
- Protected API endpoints.
- User-specific resource access controls.
- Validation of swap and messaging permissions.

### 📱 Responsive User Interface

- Modern React interface.
- Responsive layouts for desktop and mobile.
- Reusable UI components.
- Student cards, profile modals, skill chips, and navigation.
- Clear feedback for recommendation and swap states.

---

## ⚙️ How It Works

The application follows this workflow:

```text
        Student Registration
                 |
                 v
          Create Profile
                 |
                 v
       Add Teaching Skills
       and Learning Goals
                 |
                 v
       Recommendation Engine
                 |
        +--------+--------+
        |                 |
        v                 v
  Content-Based     Collaborative
    Matching         Filtering
        |                 |
        +--------+--------+
                 |
                 v
        Hybrid Ranking
                 |
                 v
     Recommended Students
                 |
                 v
      Send Swap Request
                 |
                 v
       Accept / Decline
                 |
                 v
          Chat & Learn
                 |
                 v
        Complete the Swap
```

### Recommendation workflow

1. The backend retrieves eligible student profiles and their skills.
2. The content-based engine calculates reciprocal skill compatibility.
3. The collaborative engine uses available interaction history.
4. The hybrid engine combines the available recommendation signals.
5. Candidates are filtered and ranked.
6. The frontend displays recommendations and relevant explanations.
7. Subsequent interactions can provide additional behavioral signals.

---

## 🧠 Recommendation System

The recommendation engine is the core technical component of SkillSwap AI.

It combines two recommendation approaches:

1. **Content-Based Filtering**
2. **Collaborative Filtering**

These are combined using a weighted hybrid scoring strategy.

### 1. Content-Based Filtering

Content-based filtering compares the skills a student wants to learn with the skills another student can teach.

For two students, A and B, the system evaluates two directions.

**Forward compatibility:** Can B teach A what A wants to learn?

\[
F(A,B)=\operatorname{Cosine}(W_A,O_B)
\]

**Reverse compatibility:** Can A teach B what B wants to learn?

\[
R(A,B)=\operatorname{Cosine}(O_A,W_B)
\]

Where:

- \(O_A\) = skills offered by student A.
- \(W_A\) = skills wanted by student A.
- \(O_B\) = skills offered by student B.
- \(W_B\) = skills wanted by student B.

The reciprocal content score is the average of the two directional scores:

\[
C(A,B)=\frac{F(A,B)+R(A,B)}{2}
\]

#### Why reciprocal matching matters

A student who can teach another student is not automatically a good exchange partner. The reverse direction must also be considered.

By evaluating both directions, the system prioritizes students who can potentially benefit each other.

#### Cosine Similarity

Cosine similarity measures the similarity between two vectors:

\[
\operatorname{Cosine}(x,y)=
\frac{x\cdot y}{\|x\|\|y\|}
\]

The implementation represents skills using binary vectors constructed from a shared skill vocabulary.

For example, if the skill vocabulary is:

```text
[Python, React, UI/UX]
```

A student who offers Python and React can be represented as:

```text
[1, 1, 0]
```

A student who wants React can be represented as:

```text
[0, 1, 0]
```

The resulting cosine similarity measures the overlap between the represented skill sets.

The engine also handles zero vectors safely, avoiding division-by-zero errors when a student has no relevant skills.

### 2. Collaborative Filtering

Content-based matching uses profile information. Collaborative filtering adds information from user interactions.

SkillSwap AI tracks behavioral signals such as:

| Interaction | Weight |
|---|---:|
| Profile view | 0.1 |
| Like | 0.3 |
| Swap request | 0.6 |
| Accepted swap | 0.8 |
| Completed swap | 1.0 |

For a user-target pair, the implementation uses the maximum applicable interaction weight as the observed preference signal.

The system then calculates user-user cosine similarity based on interaction histories and uses positively similar users to estimate potential interest in other candidates.

Conceptually:

\[
CF(A,C)=
\frac{\sum_{U} s(A,U)\,r(U,C)}
{\sum_{U} s(A,U)}
\]

Where:

- \(A\) is the requesting student.
- \(C\) is a candidate.
- \(U\) represents other users with relevant interaction history.
- \(s(A,U)\) is the similarity between users A and U.
- \(r(U,C)\) is the observed interaction signal between U and C.

The actual implementation uses eligible positive-similarity neighbors and handles cases where a meaningful collaborative score cannot be calculated.

**Important:** Interaction weights are engineering choices used to model relative preference strength. They are not learned probabilities or empirically proven universal values.

### 3. Hybrid Recommendation

The hybrid model combines content compatibility and collaborative evidence.

The configured scoring formula is:

\[
H(A,B)=0.70C(A,B)+0.30CF(A,B)
\]

Where:

- \(H(A,B)\) = hybrid score.
- \(C(A,B)\) = reciprocal content-based score.
- \(CF(A,B)\) = collaborative filtering score.

The initial weighting gives more importance to direct skill compatibility while still allowing interaction history to influence recommendations.

#### Cold-start handling

New users may not have enough interaction history for collaborative filtering.

When collaborative evidence is unavailable, the system falls back to content-based scoring instead of assigning an artificial collaborative score or penalizing the new user.

This makes the system useful even when the platform has limited behavioral data.

#### Recommendation explainability

The application can explain recommendations using the actual skills that overlap in each direction:

- Skills the recommended student offers that the current student wants.
- Skills the current student offers that the recommended student wants.
- Collaborative evidence when it is available.

The goal is to make recommendations understandable to users rather than displaying a score without context.

#### Algorithm evaluation

The project includes an evaluation stage designed to compare content-based, collaborative, and hybrid configurations.

The planned comparisons include:

- Content-only recommendations.
- Collaborative-only recommendations.
- Hybrid configurations using 80/20, 70/30, 60/40, and 50/50 weights.
- Precision@K, Recall@K, NDCG@K, Hit Rate@K, and reciprocity-oriented evaluation.

The 70/30 configuration is the project's initial hybrid baseline; it should not be described as universally optimal without supporting experimental results.

---

## 🏗️ System Architecture

SkillSwap AI follows a frontend-backend-database architecture.

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
|                                  |
| NumPy | Scikit-learn | SQLAlchemy |
+----------------+-----------------+
                 |
                 | SQL
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

The frontend is responsible for:

- Rendering the user interface.
- Handling navigation and form interactions.
- Managing authentication state.
- Calling backend REST endpoints.
- Displaying recommendations and swap states.

### Backend

The backend is responsible for:

- Authentication and access control.
- Profile and skill management.
- Database operations.
- Recommendation generation and ranking.
- Swap request state transitions.
- Messaging and interaction tracking.

### Database

PostgreSQL provides persistent storage for application entities, user profiles, skill information, interactions, swap requests, messages, and ratings.

The recommendation engine runs in the Python backend rather than relying on client-side calculations.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| React | Component-based frontend |
| Vite | Frontend development server and build tool |
| Tailwind CSS | Responsive UI styling |
| Lucide React | Icons |
| Python | Backend and recommendation logic |
| FastAPI | REST API framework |
| SQLAlchemy | ORM and database operations |
| PostgreSQL | Relational database |
| Neon | Hosted PostgreSQL in production |
| NumPy | Numerical operations |
| Scikit-learn | Cosine similarity and related ML utilities |
| JWT | Authentication tokens |
| pwdlib | Password hashing support |
| Pytest | Automated backend testing |
| Git and GitHub | Version control and source hosting |
| Vercel | Frontend deployment |
| Render | Backend deployment |

---

## 🗄️ Database Design

The application uses a relational PostgreSQL database with UUID-based primary keys, foreign keys, timestamps, constraints, and SQLAlchemy relationships.

The main entities include:

| Table | Responsibility |
|---|---|
| `users` | Account identity and authentication information |
| `profiles` | Student profile information and preferences |
| `skills` | Shared skill vocabulary |
| `user_skills` | Skills associated with users, including their role and proficiency |
| `interactions` | User activity used for recommendation signals |
| `swap_requests` | Skill-exchange request lifecycle |
| `messages` | Messages between connected students |
| `ratings` | Ratings associated with exchanges |

### Data integrity

The schema uses relational constraints and validation to help maintain consistent data, including:

- Foreign-key relationships.
- Unique constraints where appropriate.
- Proficiency range validation.
- Restrictions against self-directed interactions or swaps.
- Ownership and participation checks in relevant API operations.

The application also distinguishes demonstration profiles from test accounts so that test records can be excluded from user-facing recommendations.

---

## 🔌 API Overview

FastAPI exposes REST endpoints for the frontend.

The backend's interactive API documentation is available at:

- Swagger UI: `https://skillswap-ai-backend-obqv.onrender.com/docs`
- ReDoc: `https://skillswap-ai-backend-obqv.onrender.com/redoc`

### Main API areas

| API Area | Purpose |
|---|---|
| `/api/health` | Check backend health |
| `/api/health/db` | Check database connectivity |
| `/api/auth/register` | Register a student |
| `/api/auth/login` | Authenticate a student |
| `/api/auth/me` | Retrieve the authenticated user |
| `/api/users` | User-related operations |
| `/api/profiles` | Profile management |
| `/api/skills` | Skill management |
| `/api/students` | Discover eligible students |
| `/api/recommendations` | Retrieve hybrid recommendations |
| `/api/recommendations/collaborative` | Retrieve collaborative recommendations |
| `/api/recommendations/hybrid` | Retrieve hybrid recommendations |
| `/api/messages/me` | Retrieve the current user's messages |
| `/api/messages/me/unread-count` | Retrieve unread message count |
| `/api/swap-requests` | Manage skill-swap requests |

Additional endpoints support individual resources and relationship-state queries.

For exact request parameters, response schemas, and available operations, refer to the running Swagger documentation. The documentation generated by FastAPI reflects the actual backend API.

---

## 🚀 Getting Started

Follow these instructions to run the project locally.

### Prerequisites

Install the following:

- Git
- Node.js and npm
- Python 3.10 or a compatible version supported by the project dependencies
- PostgreSQL, or an accessible PostgreSQL database such as Neon

### 1. Clone the repository

```bash
git clone https://github.com/shreydarshan/skillswap-ai.git
cd skillswap-ai
```

### 2. Configure the backend

Create and activate a Python virtual environment.

**Windows PowerShell:**

```powershell
cd backend

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, you can run the environment's Python executable directly.

**macOS/Linux:**

```bash
cd backend

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file inside the `backend` directory using the project's environment-variable example as a reference, if available.

Configure your database connection and authentication settings before starting the backend.

See [Environment Variables](#-environment-variables) below.

### 4. Start the backend

From the `backend` directory, run:

```bash
uvicorn app.main:app --reload
```

The API should be available at:

```text
http://127.0.0.1:8000
```

Open the interactive documentation:

```text
http://127.0.0.1:8000/docs
```

### 5. Configure the frontend

Open a new terminal at the repository root.

Install the frontend dependencies:

```bash
npm install
```

Create a `.env` file in the frontend project root and configure the API URL:

```env
VITE_API_URL=http://127.0.0.1:8000/api
```

### 6. Start the frontend

```bash
npm run dev
```

Vite will display the local URL, typically:

```text
http://localhost:5173
```

Open that URL in your browser.

### 7. Build the frontend

To verify that the frontend can be built for production:

```bash
npm run build
```

To run the backend test suite from the repository root:

```bash
python -m pytest backend/tests/ -v
```

If your active Python environment is inside `backend/venv`, use:

```powershell
.\backend\venv\Scripts\python.exe -m pytest backend/tests/ -v
```

**Note:** Database configuration, required environment variables, and seed-data setup must be completed before the application can run successfully. Use the repository's actual dependency files and environment example as the source of truth if they differ from these general instructions.

---

## 🔑 Environment Variables

Keep secrets out of source control. The backend's `.env` file and the frontend's local `.env` file should not be committed.

### Backend

The backend requires a database connection and JWT configuration. The following table describes the settings to configure; use the exact names expected by the current backend settings module.

| Setting | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | Secret used to sign authentication tokens |
| `CORS_ORIGINS` | Allowed frontend origins |

Example values for local development:

```env
DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@localhost:5432/skillswap_db
JWT_SECRET=replace_with_a_secure_random_secret
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

These are illustrative settings, not production credentials. Confirm the exact variable names and formatting in the backend configuration before use.

For production:

- Use a strong, unique JWT secret.
- Use the PostgreSQL connection string supplied by your database provider.
- Include the deployed frontend origin in the backend's allowed CORS origins.
- Never commit real passwords, database URLs, or signing secrets.

### Frontend

The frontend uses:

```env
VITE_API_URL=https://skillswap-ai-backend-obqv.onrender.com/api
```

For local development, use the local API URL shown above.

Variables prefixed with `VITE_` are exposed to the browser bundle. **Never put passwords, private keys, or other secrets in frontend environment variables.**

---

## ☁️ Deployment

SkillSwap AI uses separate services for its frontend, backend, and database.

| Component | Platform | Responsibility |
|---|---|---|
| Source code | GitHub | Version control and repository hosting |
| Frontend | Vercel | Hosts the React application |
| Backend | Render | Runs the FastAPI service |
| Database | Neon | Hosts PostgreSQL |

### Deployment workflow

```text
Developer
    |
    v
GitHub Repository
    |
    +----------------------+
    |                      |
    v                      v
Vercel                 Render
Frontend               FastAPI Backend
                           |
                           v
                       Neon PostgreSQL
```

With automatic deployment configured, pushing changes to the connected GitHub branch can trigger new deployments.

### Live services

- **Application:** https://skillswap-ai-alpha.vercel.app
- **Backend health:** https://skillswap-ai-backend-obqv.onrender.com/api/health
- **API documentation:** https://skillswap-ai-backend-obqv.onrender.com/docs

The backend must be configured to accept requests from the production frontend, and its database connection must point to the intended Neon PostgreSQL database.

On Render's free tier, the service may spin down after inactivity, which can cause a delay on the first request.

---

## 🔐 Security and Privacy

Security is implemented across authentication, API access, and data operations.

Key measures include:

- Password hashing rather than storing plaintext passwords.
- JWT-based authentication for protected endpoints.
- Server-side identity validation.
- Resource ownership and conversation-participant checks.
- Restrictions on unauthorized messaging.
- Validation of swap-request participation and state transitions.
- Filtering of test accounts from recommendation results.
- Environment-based configuration for secrets and database access.

Authentication alone does not grant access to every resource. The backend must also validate that the authenticated user is authorized to perform the requested operation.

---

## 🧪 Testing and Quality Assurance

Testing is an important part of the project because recommendation integrity, authentication, and swap-state transitions affect the application's core functionality.

The project includes automated backend tests covering areas such as:

- Authentication and account lifecycle.
- Profile and skill operations.
- Reciprocal skill similarity.
- Collaborative and hybrid recommendation logic.
- Cold-start behavior.
- Interaction tracking.
- Swap creation, acceptance, decline, and completion.
- Duplicate swap prevention.
- Messaging permissions and account isolation.
- Test-account exclusion and seed-data behavior.

The release verification recorded **54 passing backend tests**, alongside a successful frontend production build.

Test results describe the tested project version and test environment; they do not guarantee the absence of every possible production issue.

### Manual verification

Important user flows include:

1. Register and log in with two separate accounts.
2. Create different profiles and teaching/learning skill lists.
3. Verify that recommendations reflect reciprocal skill compatibility.
4. Send a swap request and accept it from the other account.
5. Confirm that connected students can chat.
6. Complete the exchange.
7. Verify that chat history remains available.
8. Check that unrelated users cannot access another user's private resources.
9. Verify that profiles and avatars persist across sessions.

---

## ⚠️ Limitations and Future Improvements

The project establishes a working hybrid recommendation architecture, but there are several valuable directions for further development.

### Recommendation evaluation

- Evaluate the ranking system on a sufficiently representative set of genuine interactions.
- Compare hybrid weighting configurations using Precision@K, Recall@K, NDCG@K, and Hit Rate@K.
- Measure how effectively the recommendations support reciprocal exchanges.
- Investigate how sparse interaction data affects collaborative filtering.

### Recommendation improvements

- Introduce richer skill representations and semantic similarity.
- Explore learning-to-rank techniques after collecting adequate training data.
- Consider skill proficiency, availability, learning preferences, and scheduling compatibility.
- Improve personalization while preserving transparent explanations.

### Product improvements

- Add notifications for swap requests and messages.
- Provide richer progress tracking for completed exchanges.
- Introduce moderation and reporting features.
- Expand accessibility and usability testing.
- Add monitoring, analytics, and performance testing as usage grows.

These are potential future improvements, not claims about features already implemented.

---

## 🎓 Learning Outcomes

This project demonstrates the integration of several computer science concepts into a practical application.

**Machine Learning**
- Content-based recommendation.
- Collaborative filtering.
- Cosine similarity.
- Hybrid scoring.
- Cold-start handling.
- Ranking evaluation.

**Full-Stack Development**
- React component architecture.
- REST API design.
- Frontend-backend integration.
- Authentication state management.
- Responsive web development.

**Database Engineering**
- Relational schema design.
- Foreign keys and integrity constraints.
- SQLAlchemy ORM.
- Persistent storage.
- Transaction-aware operations.

**Software Engineering**
- Modular code organization.
- Automated testing.
- Version control with Git.
- Deployment workflows.
- Input validation and access control.
- Debugging and release verification.

---

## 🌟 Why SkillSwap AI?

SkillSwap AI combines the practical value of peer learning with the technical capabilities of recommendation systems.

Its defining idea is **reciprocity**: the best exchange partner is not merely someone who possesses a skill you want, but someone with whom both students have an opportunity to learn from each other.

By combining skill-based compatibility with behavioral signals, the project provides a foundation for more relevant, explainable, and personalized student connections.

---

## 👨‍💻 Author

**Shrey Darshan**

- GitHub: [@shreydarshan](https://github.com/shreydarshan)
- Project Repository: [SkillSwap AI](https://github.com/shreydarshan/skillswap-ai)
- Live Application: [skillswap-ai-alpha.vercel.app](https://skillswap-ai-alpha.vercel.app)

---

## 📄 License

No license has been specified for this repository in this README. If you intend to make the project open source, add an appropriate license file and update this section.

---

**Built to make learning collaborative, reciprocal, and accessible.** 🚀

