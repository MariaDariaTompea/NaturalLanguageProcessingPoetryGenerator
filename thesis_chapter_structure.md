# Chapter X — Technologies and Tools Used in the Development of Tenjin'ya

> This document provides a complete chapter structure for your bachelor thesis, based on an exhaustive analysis of your actual codebase. Each section includes **guidance notes** (in *italics*) telling you what to write. Remove the guidance notes when writing the final version.

---

## X.1 Overview of the Technology Stack

*Start with a short introductory paragraph (half a page) explaining the overall architecture of Tenjin'ya: a **monolithic full-stack web application** built with Python on the backend and vanilla HTML/CSS/JavaScript on the frontend, connected to a relational database. Mention the client-server model and that the application follows a modular, feature-based directory structure.*

*Include a **diagram** here showing the high-level architecture:*

```
┌─────────────────────────────────┐
│         Client (Browser)        │
│  HTML5 · CSS3 · JavaScript      │
│  Canvas API · Wanakana.js       │
└────────────┬────────────────────┘
             │ HTTP / JSON
┌────────────▼────────────────────┐
│       FastAPI (Python 3.12)     │
│    Uvicorn ASGI Server          │
│  Pydantic · SQLAlchemy ORM      │
└────────────┬────────────────────┘
             │ SQL / ORM
┌────────────▼────────────────────┐
│  SQLite (local) / PostgreSQL    │
│  Supabase (cloud)               │
└─────────────────────────────────┘
             │ gRPC / REST
┌────────────▼────────────────────┐
│   Google Cloud Vision API       │
│  (Handwriting OCR)              │
└─────────────────────────────────┘
```

---

## X.2 Programming Languages

### X.2.1 Python (v3.12)

*Describe Python as the primary backend language. Cover:*
- *Why Python was chosen (readability, rich ecosystem, fast prototyping, strong support for web frameworks and AI/ML libraries)*
- *Python 3.12 specific features used (type hints with Pydantic, f-strings, async/await on route handlers)*
- *Its role in the project: application server logic, database modeling, data seeding scripts, API endpoint definitions, Google Cloud Vision integration*

### X.2.2 JavaScript (ES6+)

*Describe JavaScript as the client-side scripting language. Cover:*
- *Used for all frontend interactivity: DOM manipulation, event handling, animations, page transitions*
- *The HTML5 Canvas API for the handwriting recognition drawing interface (stroke capture, image compositing with `drawImage()`, Base64 encoding via `toDataURL()`)*
- *Drag-and-drop functionality in the sentence-builder exercise type*
- *Dynamic state management (progress bars, exercise flow, quiz logic)*
- *Asynchronous communication with the backend via `fetch()` and JSON payloads*

### X.2.3 HTML5

*Describe HTML5 as the structure/markup language. Cover:*
- *Server-side rendered HTML templates (generated as Python f-strings inside route handlers)*
- *Semantic elements used throughout the application*
- *The `<canvas>` element for handwriting recognition input*
- *`<video>` elements for stroke-order demonstrations and page transition effects*
- *Form elements for authentication (login/register)*

### X.2.4 CSS3

*Describe CSS3 as the styling and animation language. Cover:*
- *Custom design system built from scratch without CSS frameworks (no Bootstrap, no Tailwind)*
- *Advanced CSS features used:*
  - *CSS custom properties and gradients (`linear-gradient`, `radial-gradient`)*
  - *`@keyframes` animations (fadeUp, slide-in, zoom effects)*
  - *`transition` properties for micro-animations on hover states*
  - *`backdrop-filter: blur()` for glassmorphism effects*
  - *CSS Flexbox for responsive layouts*
  - *`clamp()` for responsive typography*
  - *`object-fit` and `background-size: cover` for image handling*
- *Google Fonts integration (Playfair Display for headings, Inter for body text)*

### X.2.5 SQL

*Describe SQL as the database query language. Cover:*
- *Used for direct database manipulation via migration scripts (`supabase_migration.sql`)*
- *PostgreSQL-compatible SQL syntax (SERIAL, CASCADE, COALESCE)*
- *Database schema creation, data migration, and column restructuring operations*
- *Mention that day-to-day database interaction is abstracted through the SQLAlchemy ORM*

---

## X.3 Frameworks and Libraries

### X.3.1 FastAPI — Web Framework

*Describe FastAPI as the core web framework. Cover:*
- *What FastAPI is: a modern, high-performance Python web framework based on the ASGI (Asynchronous Server Gateway Interface) standard*
- *Key features used in the project:*
  - *Route decorators (`@router.get()`, `@router.post()`) for defining API endpoints*
  - *`HTMLResponse` for server-rendered pages*
  - *`JSONResponse` for API data endpoints*
  - *`StaticFiles` mounting for serving images, audio, video, icons, and textures*
  - *Automatic interactive API documentation (Swagger UI at `/docs`)*
  - *Cookie-based session management for user authentication*
  - *`APIRouter` for modular route organization (separate routers for user, grammar, exercises, customization, japanese)*

### X.3.2 Uvicorn — ASGI Server

*Describe Uvicorn as the application server. Cover:*
- *Lightweight, high-performance ASGI server*
- *Runs the FastAPI application on `127.0.0.1:8000`*
- *Hot-reload capability during development (`reload=True`)*
- *Handles concurrent HTTP connections efficiently*

### X.3.3 SQLAlchemy — Object-Relational Mapping (ORM)

*Describe SQLAlchemy as the database abstraction layer. Cover:*
- *What an ORM is and why it's beneficial (mapping Python classes to database tables)*
- *Key components used:*
  - *`declarative_base()`: creates the base class for all ORM models*
  - *`create_engine()`: establishes the database connection*
  - *`sessionmaker()` and `get_db()`: manage database session lifecycle per request*
  - *Column types used: `Integer`, `String`, `Text`, `DateTime`, `Boolean`, `ForeignKey`*
  - *`relationship()`: defines inter-table relationships with cascade behavior*
- *Benefits: SQL injection prevention, database-agnostic code (easily switch between SQLite and PostgreSQL), improved code readability*

### X.3.4 Pydantic — Data Validation

*Describe Pydantic as the request validation library. Cover:*
- *Used for defining request body schemas (`BaseModel` subclasses)*
- *Automatic validation of incoming JSON data (e.g., `UserLogin`, `UserRegister`, `WritingSubmission`)*
- *Integration with FastAPI's automatic documentation*

### X.3.5 Wanakana.js — Japanese Input Library

*Describe Wanakana as a specialized frontend library. Cover:*
- *Third-party JavaScript library loaded via CDN (`unpkg.com/wanakana`)*
- *Automatically converts Romaji keyboard input into Hiragana/Katakana characters in real-time*
- *Bound to text input fields in the exercise runner for the `text_input` test type*
- *Enables users without a Japanese keyboard to practice typing Japanese characters*

### X.3.6 Google Cloud Vision Client Library (Python)

*Describe the Google Cloud Vision client. Cover:*
- *`google-cloud-vision` Python package*
- *Used for AI-powered handwriting character recognition*
- *`ImageAnnotatorClient`: creates the API connection*
- *`document_text_detection()` method: specialized OCR for dense text and handwriting*
- *`ImageContext(language_hints=["ja"])`: constrains recognition to Japanese characters*
- *Graceful import fallback: application continues to function even if the library is not installed*

### X.3.7 Python Standard Library Modules

*Briefly mention built-in Python modules used:*
- *`hashlib`: SHA-256 password hashing for user authentication*
- *`base64`: encoding/decoding handwriting images for API transmission*
- *`json`: parsing and generating JSON data for exercise options and API responses*
- *`os`: file path management and environment variable configuration*
- *`io`: in-memory byte stream handling for image processing*
- *`random`: shuffling exercise options (matching pairs, sentence builder word blocks)*
- *`datetime`: timestamping user photos and exercise scores*

---

## X.4 Database Systems

### X.4.1 SQLite — Local Development Database

*Describe SQLite as the local database. Cover:*
- *Lightweight, file-based relational database (`japanese_app.db`)*
- *Zero-configuration: no server process needed*
- *Used during development and local testing*
- *Connection string: `sqlite:///./japanese_app.db`*

### X.4.2 PostgreSQL via Supabase — Production Database

*Describe the production database strategy. Cover:*
- *PostgreSQL: an industry-standard, open-source relational database system*
- *Supabase: a Backend-as-a-Service (BaaS) platform hosting the PostgreSQL instance*
- *Benefits of cloud hosting: scalability, availability, managed backups*
- *Migration scripts (`supabase_migration.sql`) for schema evolution*
- *The SQLAlchemy ORM enables seamless switching between SQLite (local) and PostgreSQL (production) by simply changing the connection URL*

### X.4.3 Database Schema Design

*Describe the key tables and their relationships (use a diagram from your `docs/database_schema.png`). Mention the hierarchy:*

```
Proficiency (N5 → N1)
  └── Chapter (grammar / vocabulary / culture)
        └── Exercise (quiz, course, examination, interactive)
              └── Test (individual questions with flexible JSON options)
```

*And the user system:*

```
User
  ├── UserProfile (avatar, banner, equipped achievements)
  ├── UserPhoto (uploaded images)
  ├── UserItem (owned achievements and items)
  ├── StatusLearning (per-module progress tracking)
  └── UserExerciseScore (stars and completion per exercise)
```

---

## X.5 Cloud Platforms and External Services

### X.5.1 Google Cloud Platform (GCP)

*Describe the Google Cloud integration. Cover:*
- *Service used: **Cloud Vision API** — specifically the `document_text_detection` endpoint*
- *Purpose: AI-powered optical character recognition (OCR) for validating handwritten Japanese characters*
- *Authentication: Service Account key (`google-credentials.json`) loaded as an environment variable at application startup*
- *Underlying AI: Convolutional Neural Networks (CNNs) combined with Bi-Directional LSTMs for feature extraction and sequence processing*

### X.5.2 Supabase

*Describe Supabase as the cloud database platform. Cover:*
- *Open-source Firebase alternative built on PostgreSQL*
- *Provides the hosted relational database for the production environment*
- *Offers built-in REST APIs, real-time subscriptions, and authentication services*

### X.5.3 Google Fonts

*Briefly mention Google Fonts as an external CDN service. Cover:*
- *Fonts used: **Playfair Display** (serif, for headings and decorative text) and **Inter** (sans-serif, for body content and UI elements)*
- *Loaded via `fonts.googleapis.com` CDN for fast delivery*

---

## X.6 Development Tools and Environment

### X.6.1 Development Environment

*Describe the development setup:*
- *Operating System: **Windows***
- *IDE: **Visual Studio Code** (inferred from `.vscode/` in `.gitignore`)*
- *Python Version: **3.12.2** (64-bit, MSC compiler)*

### X.6.2 Version Control — Git & GitHub

*Describe the version control strategy:*
- *Git for local version control*
- *GitHub for remote repository hosting (project name: `ProiectLicenta-Tenjin-Ya-JapaneseLearningApp`)*
- *`.gitignore` configured to exclude virtual environments, compiled Python files, database files, credentials, and temporary uploads*

### X.6.3 Python Virtual Environment (venv)

*Describe the dependency isolation strategy:*
- *Python's built-in `venv` module used to create an isolated environment (`.venv/` directory)*
- *Ensures project dependencies do not conflict with system-wide packages*
- *Key dependencies installed: `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `google-cloud-vision`*

---

## X.7 Frontend Architecture and Techniques

### X.7.1 Server-Side Rendered HTML (No Frontend Framework)

*Explain the deliberate architectural choice. Cover:*
- *The application does **not** use a frontend framework (no React, Vue, Angular)*
- *HTML pages are generated server-side as Python f-strings within route handler functions*
- *Templates are organized in `templates/` subdirectories within each feature module*
- *This approach was chosen for simplicity, minimal dependencies, and full control over the rendering pipeline*

### X.7.2 HTML5 Canvas API — Handwriting Recognition Interface

*Describe the Canvas-based drawing system. Cover:*
- *Interactive canvas element for capturing user strokes (mouse and touch input)*
- *Offscreen canvas technique for resolving alpha transparency issues (compositing user strokes onto an opaque white background)*
- *`toDataURL("image/png")` for converting drawings to Base64-encoded PNG images*
- *Bounding-box cropping algorithm (`getCroppedCanvas`) for optimizing payload size*

### X.7.3 CSS Animation and Design System

*Describe the premium visual design approach. Cover:*
- *Custom-built design system with a curated pink/dark color palette (`#E56AB3`, `#FCBCD7`, `#0d0608`, `#BF5082`)*
- *Glassmorphism: semi-transparent backgrounds with `backdrop-filter: blur()` and subtle borders*
- *Page transitions: multi-stage animations (ribbon slide-in, fox video overlay, fade-to-black)*
- *Micro-animations: hover effects on cards, buttons, and ribbon menu items*
- *Responsive typography with `clamp()` for screen adaptation*

### X.7.4 Asynchronous Frontend Communication

*Describe the client-server data exchange. Cover:*
- *`fetch()` API for sending JSON POST requests (login, register, writing verification)*
- *Cookie-based session management (`user_email` cookie set on login)*
- *Dynamic DOM updates based on API responses (exercise results, handwriting verification feedback)*

---

## X.8 Application Modules and File Organization

*Describe the modular project structure. Cover:*

```
JapaneseApp/
├── main.py                      # Application entry point
├── core/
│   ├── database.py              # Database engine and session management
│   └── routes.py                # Central router aggregating all feature routers
├── features/
│   ├── user/                    # Authentication, registration, user models
│   │   ├── models.py            # User, UserProfile, UserPhoto, StatusLearning, UserItem, UserExerciseScore
│   │   ├── routes.py            # Login/register endpoints
│   │   └── templates/           # Auth page templates
│   ├── grammar/                 # Course pages, welcome screen, writing exercises
│   │   ├── models.py            # Proficiency, Chapter, Exercise, Test
│   │   └── routes.py            # Welcome, grammar, vocabulary, culture, writing routes
│   ├── exercises/               # Exercise runner and test renderers
│   │   ├── renderer.py          # HTML renderers for 6 test types
│   │   ├── routes.py            # Exercise endpoints
│   │   └── templates/           # Exercise runner template
│   ├── customization/           # Profile customization and achievements
│   │   ├── models.py            # Achievement model
│   │   ├── routes.py            # Profile and achievement endpoints
│   │   └── templates/           # Profile and achievement page templates
│   └── japanese/                # Writing system tables (Hiragana, Katakana, Kanji)
│       ├── models.py            # Hiragana, Katakana models
│       ├── routes.py            # Character table endpoints
│       ├── templates/           # Hiragana and Katakana table templates
│       └── static/              # Audio files, character assets
├── docs/                        # Documentation and schema diagrams
├── uploads/                     # User-uploaded files (avatars, culture PDFs)
└── seed_*.py                    # Database seeding scripts
```

*Explain the **separation of concerns**: each feature module (user, grammar, exercises, customization, japanese) contains its own models, routes, and templates, enabling independent development and testing.*

---

## X.9 Summary Table

| Category | Technology | Purpose |
|:---|:---|:---|
| **Backend Language** | Python 3.12 | Server logic, API routes, database models, AI integration |
| **Frontend Languages** | JavaScript (ES6+), HTML5, CSS3 | UI interactivity, structure, styling & animations |
| **Database Language** | SQL | Schema definition, migration scripts |
| **Web Framework** | FastAPI | HTTP routing, request handling, API documentation |
| **Application Server** | Uvicorn | ASGI server running FastAPI |
| **ORM** | SQLAlchemy | Python-to-database abstraction layer |
| **Validation** | Pydantic | Request data validation |
| **Local Database** | SQLite | Development database |
| **Production Database** | PostgreSQL (Supabase) | Cloud-hosted relational database |
| **AI/OCR** | Google Cloud Vision API | Handwriting character recognition |
| **Japanese Input** | Wanakana.js | Romaji-to-Kana conversion in text fields |
| **Password Security** | hashlib (SHA-256) | User password hashing |
| **Typography** | Playfair Display, Inter (Google Fonts) | Premium UI typography |
| **Canvas** | HTML5 Canvas API | Stroke capture for writing practice |
| **Version Control** | Git & GitHub | Source code management |
| **IDE** | Visual Studio Code | Development environment |
| **Package Management** | pip + venv | Python dependency management |

---

> [!TIP]
> **Writing Tips for this Chapter:**
> - Aim for **5–8 pages** total
> - Include the architecture diagram from Section X.1 and the database schema from `docs/database_schema.png`
> - For each technology, briefly explain **what it is**, **why you chose it**, and **how it is used in this specific project**
> - Reference official documentation where relevant (e.g., FastAPI docs, SQLAlchemy docs, Google Cloud Vision docs)
> - The Summary Table (X.9) works well as a closing element that gives the reader a quick reference
