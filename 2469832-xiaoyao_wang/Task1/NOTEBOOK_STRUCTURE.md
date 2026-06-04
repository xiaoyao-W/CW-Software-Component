# Notebook Refactored Structure

## Overview

The Jupyter Notebook is organized into **3 main sections**, each containing multiple phases that build upon each other. Run all cells from top to bottom for complete functionality.

---

## Section 1: Requirements

**Purpose:** Define the business problem and generate all requirement documentation.

**Phases:**
1. **Phase 1: Define Business Problem** - Input your business problem description
2. **Phase 2: Generate Problem Statement** - AI generates a clear problem statement
3. **Phase 3: Generate User Personas** - AI creates user personas based on requirements
4. **Phase 4: Generate PRD** - AI generates Product Requirements Document
5. **Phase 5: Classify Requirements** - AI classifies requirements as functional vs non-functional
6. **Phase 6: Generate User Stories** - AI creates user stories with acceptance criteria

**Output:**
- `artifacts/problem_statement.md`
- `artifacts/personas.md`
- `artifacts/prd.md`
- `artifacts/requirements_classification.md`
- `artifacts/user_stories.json`

---

## Section 2: Development

**Purpose:** Generate the software code and visualizations.

**Phases:**
7. **Phase 7: UML Diagram Type Selection** - AI automatically selects appropriate UML diagram types
8. **Phase 8: Generate UML Diagrams** - AI generates UML diagrams (Use Case, Activity, Sequence)
9. **Phase 9: Generate Flask API** - AI generates Flask REST API with endpoints
10. **Phase 10: Generate Website Frontend** - AI generates HTML templates
11. **Phase 10.5: Flask API Enhancement** - Add authentication and role-based access

**Output:**
- `artifacts/diagrams/use_case_diagram.png`
- `artifacts/diagrams/activity_diagram.png`
- `artifacts/diagrams/sequence_diagram.png`
- `app/main.py` (Flask API)
- `app/templates/*.html` (Website pages)
- `app/static/images/hero_banner.png`

---

## Section 3: Deployment & Maintenance

**Purpose:** Package and deploy the application with CI/CD.

**Phases:**
12. **Phase 11: Integrated Website & CI/CD Deployment** - Generate Docker config and CI/CD pipeline

**Output:**
- `Dockerfile`
- `docker-compose.yml`
- `.github/workflows/cicd.yml`
- `app/requirements.txt`

---

## How to Run

1. Open `meta_software_dev.ipynb` in Jupyter Notebook
2. Run **all cells from top to bottom**
3. Wait for AI generation (10-30 seconds per phase)
4. Check outputs below each cell

---

## Customization

To use your own business problem, edit **Phase 1** (first code cell):

```python
business_problem = """
YOUR BUSINESS PROBLEM HERE.
Include details about:
- Users (customers, merchants, admins)
- Features needed
- Workflows
- Special requirements
"""
```

---

## What Gets Generated

### SDLC Documentation
- Problem statement
- User personas
- Product Requirements Document
- Requirements classification
- User stories with acceptance criteria

### UML Diagrams
- Use Case Diagram (who interacts with the system)
- Activity Diagram (business workflows)
- Sequence Diagram (component interactions)

### Code
- Flask REST API with authentication
- Multiple HTML pages (varies by complexity):
  - Landing page
  - Login/Register
  - User dashboard
  - Merchant dashboard
  - Admin dashboard

### Deployment
- Docker configuration
- Docker Compose setup
- GitHub Actions CI/CD pipeline

---

## Testing

After running all cells:

```bash
# Start the Flask server
cd app
python main.py

# Access website at: http://127.0.0.1:5000/
```

### Test Accounts

| Role | Email | Password |
|------|-------|----------|
| Customer | test@example.com | password123 |
| Merchant | merchant@example.com | merchant123 |
| Admin | admin@example.com | admin123 |
