# DigiSahay &bull; Citizen Document Assistance Platform

DigiSahay is an upgraded civic assistance platform and document guidance dossier designed for first-time citizen applicants aged 18–19. It simplifies applying for, updating, and tracking essential government documents while booking physical appointments at verified facilitation counters (Jan Seva Kendra, CSC, ASK, RTO) across Ahmedabad and Gujarat.

---

## 🇮🇳 Statutory Scope & Design Notice
> **Notice:** This platform does **NOT** support biometric Aadhaar updates (fingerprints, iris scans, Aadhaar photographs) or passport services. Biometric enrolments and updates must be completed in person at an official Aadhaar Seva Kendra. Passport services are also strictly excluded. DigiSahay is an independent citizen guidance platform and is not an official government portal.

---

## 🚀 How to Run the Project

DigiSahay offers two seamless modes: a full Flask enterprise web application and a self-contained offline browser prototype.

### Mode 1: Full Flask Web Application (Recommended)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run Flask server
python app.py
```
Open **`http://127.0.0.1:5000`** in your browser:
- **`/dashboard`**: Citizen Guidance Dashboard
- **`/services`**: Government Services Catalogue
- **`/prerequisite-checker`**: Prerequisite & Eligibility Evaluator
- **`/apply`**: Direct Citizen Application Dossier
- **`/documents`**: Documents Vault Locker
- **`/applications`**: Application Status Tracker
- **`/centers`**: Jan Seva Kendra / CSC Facilitation Centres Map
- **`/profile`**: Citizen Profile Management & Auto-Fill
- **`/prototype`**: Interactive Frontend Prototype Mode

### Mode 2: Standalone Offline Browser Prototype (No Server Needed)
Simply open **`prototype/index.html`** directly in any web browser (Chrome, Edge, Firefox, Safari).
No Node.js, npm, or build tools are required.

---

## 📁 Clean Project Structure

All HTML files are organized strictly inside `templates/`, with assets in `static/` and modular architecture across all folders:

```
DigiSahay/
├── app.py                      # Flask entry point & blueprint registration
├── model.py                    # SQLAlchemy database models
├── extension.py                # db instance
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation, architecture & viva guide
├── .env                        # Environment configurations
├── routes/                     # 14 Modular Flask Blueprints
│   ├── frontend_routes.py      # Frontend Jinja routes (/dashboard, /services, /profile, /prototype, etc.)
│   ├── survey_routes.py        # Survey metrics, rulebook stats & feature matrix APIs
│   ├── service_routes.py       # Services REST APIs
│   ├── requirement_routes.py   # Document requirements APIs
│   ├── eligibility_routes.py   # Eligibility rules APIs
│   ├── center_routes.py        # Facilitation centers APIs
│   ├── application_routes.py   # Application management APIs
│   ├── appointment_routes.py   # Appointment booking APIs
│   ├── auth_routes.py          # Citizen JWT authentication
│   ├── document_routes.py      # Documents vault APIs
│   ├── application_document_routes.py
│   ├── application_readiness_routes.py
│   ├── application_status_routes.py
│   └── requirement_evaluation_routes.py
├── templates/                  # All HTML templates live here!
│   ├── base.html               # Shared layout (Header, Sidebar, Drawer, i18n)
│   ├── index.html              # Citizen Dashboard
│   ├── services.html           # Government Services Catalogue
│   ├── prerequisite_checker.html # Prerequisite & Eligibility Evaluator
│   ├── apply.html              # Direct Citizen Application Dossier
│   ├── documents.html          # Documents Vault
│   ├── applications.html       # Application Status & Tracking
│   ├── centers.html            # Facilitation Centres (CSC / Jan Seva Kendra)
│   ├── auth.html               # Citizen Authentication & Sign In
│   ├── profile.html            # Citizen Profile Management (extending base.html)
│   └── prototype/              # Prototype HTML templates served via Flask
│       ├── index.html          # Prototype Login
│       ├── home.html           # Prototype Home & Locker
│       ├── profile.html        # Prototype Profile
│       └── apply.html          # Prototype Application Wizard & Map
├── static/                     # All static web assets live here!
│   ├── css/
│   │   ├── variables.css       # Design tokens & color system
│   │   ├── components.css      # Reusable UI component styles
│   │   └── main.css            # Base styles, typography, layout
│   ├── js/
│   │   ├── main.js             # Core app JS, interactions, token handling
│   │   └── translations.js     # Multilingual dictionaries (EN, HI, GU)
│   ├── images/
│   │   └── logo.svg            # DigiSahay Vector Logo
│   └── prototype/              # Prototype specific static assets
│       ├── css/
│       │   └── style.css       # Prototype CSS with patriotic Indian theme
│       └── js/
│           ├── app.js          # Prototype navigation & UI state
│           ├── apply.js        # Prototype wizard, Leaflet map & token booking
│           └── data.js         # Curated document requirements & center directory
├── prototype/                  # Self-contained offline runnable prototype (double-click index.html)
│   ├── index.html
│   ├── home.html
│   ├── profile.html
│   ├── apply.html
│   ├── css/style.css
│   └── js/
│       ├── app.js
│       ├── apply.js
│       └── data.js
├── data/                       # Research datasets & rulebooks
│   ├── DigiSahay_rulebook (1).xlsx
│   └── survey_responses.csv
├── docs/                       # Research papers & presentation deck
│   ├── DigiSahay_Presentation.pptx # 20-slide widescreen presentation deck
│   ├── PRESENTATION_DECK.md    # Complete slide-by-slide script & notes
│   ├── project_report.pdf
│   └── research_paper.pdf
├── scripts/                    # Automation utilities
│   ├── generate_deck.py        # Presentation slide generator
│   ├── import_excel.py         # Rulebook data importer
│   ├── check_users.py          # User verification utility
│   └── Validat_script.py       # Validation tester
└── uploads/                    # User document storage directory
```

---

## 📊 Research Data & Citations

- **Survey Sample**: N=55 Valid Responses (56 Raw Entries, Ahmedabad & Gujarat, 2026).
- **73%** of citizens unaware of required prerequisite proofs.
- **75%** of citizens revisited centers 2 or more times (63% visited 2–3 times; 12% visited >3 times).
- **73%** endured wait times of 1 hour or more (41% waited >1 hr, 32% waited 1 hr).
- **41%** traveled to the wrong facilitation office or counter.
- **41%** suffered application rejection at the counter.
- **96%** frustrated by repetitive manual data entry.
- **91%** demanded a single unified digital guidance platform.
- **Statutory Rulebook**: 9 in-scope services, 19 eligibility rules, 69 requirement options, 26 standardized document types, 18 submission routes, and 12 facilitation centers cited to `data/DigiSahay_rulebook (1).xlsx`.

---

## 🎓 Viva Questions & Answers

### Q1: How does DigiSahay solve the 75% revisit problem?
**Answer:** DigiSahay introduces an interactive pre-application prerequisite checker backed by the official departmental rulebook (`data/DigiSahay_rulebook (1).xlsx`). By verifying whether applicants have all mandatory secondary proofs (e.g. SLC or 10th marksheet for age proof) before they travel, it eliminates the missing document drop-off that causes 73% of citizens to be caught off guard.

### Q2: What is the architectural difference between DigiSahay and DigiLocker?
**Answer:** DigiLocker is a passive cloud repository for issued documents without pre-application validation or appointment routing. DigiSahay is an active, guided citizen preparation platform that evaluates eligibility, auto-fills application dossiers from a local citizen profile, identifies the correct certified facilitation center with wait-time estimation, and books fixed-slot appointment tokens.

### Q3: What is explicitly outside the platform scope?
**Answer:** DigiSahay explicitly excludes biometric Aadhaar updates (fingerprints, iris scans, and photographic updates) which statutorily require in-person capture at official Aadhaar Seva Kendras with UIDAI hardware. Passport services are also excluded.

### Q4: How is the project structured to ensure enterprise code quality?
**Answer:** The repository strictly follows standard Flask conventions: all HTML files reside inside `templates/` (with modular sub-templates in `templates/prototype/`), static assets in `static/`, business logic segregated into 14 REST blueprints in `routes/`, datasets in `data/`, documentation in `docs/`, and offline browser testing in `prototype/`. No loose HTML files or temporary scripts exist in the root directory.
