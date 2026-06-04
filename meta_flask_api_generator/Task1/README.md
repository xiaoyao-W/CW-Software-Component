# AI-Powered Meta Software Development System

## From Business Problem to Complete Software Solution

This Jupyter Notebook demonstrates how to transform **any business problem** into a complete software system using AI-assisted development. The notebook automatically generates:

- **SDLC Documentation** (Problem statements, User stories, UML diagrams)
- **Flask REST API** (Backend with authentication and business logic)
- **Website Frontend** (Multiple HTML pages based on requirements)
- **Auto-generated Images** (UML diagrams, hero banners)
- **Docker Configuration** (Containerization ready)
- **CI/CD Pipeline** (Automated testing and deployment)

> **Important:** The number of generated web pages may vary depending on your business requirements. Simple projects may generate one page, while complex multi-role systems generate multiple pages (login, user dashboard, merchant dashboard, admin dashboard, etc.).

***

## Quick Start

### 5-Minute Setup

```bash
# 1. Navigate to project directory
cd Task1

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure API keys (IMPORTANT!)
# Open .env file and replace YOUR_API_KEY_HERE with your actual API key
# Get free API key at: https://apifree.ai

# 6. Open the notebook
jupyter notebook meta_software_dev.ipynb

# 7. Run all cells from top to bottom
```

The website will be available at: **<http://127.0.0.1:5000/>**

> ⚠️ **IMPORTANT:** You MUST configure the `.env` file with your API keys before running the notebook for full functionality. Without API keys, the system will use a mock client with simulated responses.

***

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Guide](#installation-guide)
3. [API Key Configuration](#api-key-configuration)
4. [Notebook Structure](#notebook-structure)
5. [What Gets Generated](#what-gets-generated)
6. [Running the Application](#running-the-application)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

***

## System Requirements

### Hardware

- 4GB RAM
- 10GB free disk space
- Internet connection (for API calls and package installation)

### Operating Systems

- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu 20.04+, Debian 11+)

### Software

| Component | Minimum Version | Required   | Notes                   |
| --------- | --------------- | ---------- | ----------------------- |
| Python    | 3.10+           | ✅ Yes      | Python 3.12 recommended |
| pip       | Latest          | ✅ Yes      | Comes with Python       |
| Jupyter   | Notebook 6.5+   | ✅ Yes      | Or JupyterLab 3.0+      |
| Git       | 2.30+           | ⭕ Optional | For version control     |
| Docker    | 20.10+          | ⭕ Optional | For containerization    |

***

## Installation Guide

### Step 1: Install Python

**Windows:**

1. Download from <https://www.python.org/downloads/>
2. Run installer, **CHECK "Add Python to PATH"**
3. Verify: Open CMD and type `python --version`

**macOS:**

```bash
brew install python3
python3 --version
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv
python3 --version
```

### Step 2: Install Jupyter

```bash
pip install jupyter notebook

# Or for JupyterLab (recommended):
pip install jupyterlab
```

### Step 3: Download Project

```bash
# If using Git:
git clone https://github.com/xiaoyao-W/CW-Software-Component.git
cd CW-Software-Component

# Or download ZIP and extract
```

### Step 4: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Install development dependencies
pip install nbformat pytest
```

**Dependencies included:**

```
flask==2.3.3          # Web framework
flask-cors==4.0.0     # Cross-origin resource sharing
requests==2.31.0      # HTTP library for API calls
pillow==10.1.0        # Image processing
python-dotenv==1.0.0  # Environment variable management
```

***

## API Key Configuration

### Step 5: Configure .env File (Required for Full Functionality)

The `.env` file is already included in the project. You just need to add your API keys.

**Steps:**

1. **Open the** **`.env`** **file** in the `Task1/` directory
2. **Get your free API key** from <https://apifree.ai>:
   - Visit <https://apifree.ai>
   - Create a free account
   - Copy your API key
3. **Replace** **`YOUR_API_KEY_HERE`** with your actual API key in these two places:
   ```env
   APIFREE_API_KEY=your_actual_api_key_here
   FREEAPI_KEY=your_actual_api_key_here
   ```
4. **Save the file**

**Complete .env template:**

```env
# ============================================
# AI-Powered Meta Software Development System
# Environment Configuration
# ============================================

# Flask Configuration
FLASK_SECRET=your-secret-key-change-this-in-production
PORT=5000

# APIFree Configuration (Required for AI features)
APIFREE_API_KEY=YOUR_API_KEY_HERE
APIFREE_API_BASE=https://api.apifree.ai

# LLM Configuration (Text Generation)
FREEAPI_URL=https://api.apifree.ai/v1/chat/completions
FREEAPI_KEY=YOUR_API_KEY_HERE

# Image Generation Configuration
FREEIMAGE_URL=https://api.apifree.ai/v1/image/submit
IMAGE_MODEL=google/nano-banana-2
```

> ⚠️ **IMPORTANT:** Without API keys, the system will use a mock client with simulated responses. The notebook will still run, but AI features will be limited.

***

## Notebook Structure

The notebook is organized into **3 main sections**. Run all cells from top to bottom:

### **Section 1: Requirements** (Phase 1-6)

Define the business problem and generate all requirement documentation.

- Phase 1: Define Business Problem
- Phase 2: Generate Problem Statement
- Phase 3: Generate User Personas
- Phase 4: Generate PRD
- Phase 5: Classify Requirements
- Phase 6: Generate User Stories

### **Section 2: Development** (Phase 7-10.5)

Generate the software code and visualizations.

- Phase 7: UML Diagram Type Selection
- Phase 8: Generate UML Diagrams
- Phase 9: Generate Flask API
- Phase 10: Generate Website Frontend
- Phase 10.5: Flask API Enhancement

### **Section 3: Deployment & Maintenance** (Phase 11)

Package and deploy the application with CI/CD.

- Generate Docker configuration
- Create CI/CD pipeline
- Verify deployment

***

## What Gets Generated

### 1. SDLC Documentation (Artifacts)

| File                             | Description                                     |
| -------------------------------- | ----------------------------------------------- |
| `problem_statement.md`           | Clear articulation of the business problem      |
| `personas.md`                    | User personas (Customer, Merchant, Admin, etc.) |
| `prd.md`                         | Product Requirements Document                   |
| `requirements_classification.md` | Functional vs Non-functional requirements       |
| `user_stories.json`              | User stories with acceptance criteria           |

### 2. UML Diagrams (Auto-Generated Images)

| Diagram          | Description                                   |
| ---------------- | --------------------------------------------- |
| Use Case Diagram | Actors and their interactions with the system |
| Activity Diagram | Business workflow and processes               |
| Sequence Diagram | Time-ordered interactions between components  |

### 3. Flask REST API

A complete Python Flask application with:

- User authentication (register, login, logout)
- Role-based access control (customer, merchant, admin)
- Business logic endpoints
- RESTful API design

### 4. Website Frontend

**Note: The number of web pages varies by project complexity:**

**Simple projects (1-2 user roles):**

- Single-page application with all features

**Complex projects (3+ user roles):**

- `index.html` - Landing page with hero banner
- `login.html` - Registration and login
- `user_dashboard.html` - Customer features
- `merchant_dashboard.html` - Merchant features
- `admin_dashboard.html` - Admin features

All pages include:

- Bootstrap 5 responsive design
- Modern dark theme UI with cards, forms, and tables
- JavaScript for API integration
- LocalStorage for session management
- Path-based navigation (e.g., `/login`, `/register`, `/`) - no anchor links (#)

### Frontend Design Features

- **Dark Theme**: Modern dark background with high-contrast white text
- **Responsive Layout**: Mobile-friendly design with Bootstrap 5
- **Role-based Cards**: Four role cards displayed in a 2-column grid (Customer, Platform User, Merchant, Admin)
- **Hero Section**: Centered layout with title, subtitle, image, and description
- **Navigation**: Brand logo with path-based links for seamless page transitions
- **Visual Effects**: Card hover animations and modern styling

### 5. Docker & CI/CD Configuration

| File                         | Purpose                 |
| ---------------------------- | ----------------------- |
| `Dockerfile`                 | Docker image definition |
| `docker-compose.yml`         | Multi-container setup   |
| `.github/workflows/cicd.yml` | GitHub Actions pipeline |

***

## Project Structure

```
Task1/
├── meta_software_dev.ipynb    # Main notebook (RUN THIS!)
├── utils.py                   # AI utilities and LLM client
├── .env                       # Environment configuration (EDIT THIS!)
├── requirements.txt           # Python dependencies
│
├── app/                       # Generated Flask application
│   ├── main.py               # Flask API (auto-generated)
│   ├── requirements.txt      # App dependencies
│   ├── templates/            # HTML templates (auto-generated)
│   │   ├── index.html        # Landing page
│   │   ├── login.html        # Login/Register page
│   │   ├── user_dashboard.html
│   │   ├── merchant_dashboard.html
│   │   └── admin_dashboard.html
│   └── static/
│       └── images/           # Auto-generated images
│           └── hero_banner.png  # AI-generated hero banner image
│
├── .env                       # Environment configuration (EDIT THIS!)
│
├── artifacts/                 # Generated SDLC documents
│   ├── problem_statement.md
│   ├── personas.md
│   ├── prd.md
│   ├── requirements_classification.md
│   ├── user_stories.json
│   └── diagrams/             # Generated UML diagrams
│       ├── use_case_diagram.png
│       ├── activity_diagram.png
│       └── sequence_diagram.png
│
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose setup
└── .github/
    └── workflows/
        └── cicd.yml          # CI/CD pipeline
```

***

## Running the Application

### Method 1: Direct Python (Recommended for Development)

```bash
cd Task1/app
python main.py
```

Access at: **<http://127.0.0.1:5000/>**

### Method 2: Docker (For Production)

```bash
# Build Docker image
docker build -t meta-flask-app .

# Run container
docker run -p 5000:5000 meta-flask-app
```

Access at: **<http://localhost:5000/>**

### Method 3: Docker Compose

```bash
docker-compose up --build
```

***

## Testing

### Test User Accounts

After running the notebook and starting the server, you can test with:

| Role     | Email                  | Password    |
| -------- | ---------------------- | ----------- |
| Customer | <test@example.com>     | password123 |
| Merchant | <merchant@example.com> | merchant123 |
| Admin    | <admin@example.com>    | admin123    |

### API Endpoints

| Endpoint         | Method | Description       |
| ---------------- | ------ | ----------------- |
| `/`              | GET    | Homepage          |
| `/login`         | GET    | Login/Register page |
| `/register`      | GET    | Register page (same as login) |
| `/user_dashboard`| GET    | Customer dashboard |
| `/merchant_dashboard` | GET | Merchant dashboard |
| `/admin_dashboard` | GET   | Admin dashboard   |
| `/api/register`  | POST   | Register new user |
| `/api/login`     | POST   | User login        |
| `/api/me`        | GET    | Get current user  |
| `/cart/checkout` | POST   | Process checkout  |
| `/orders`        | GET    | Get user orders   |
| `/health`        | GET    | Health check      |

***

## Troubleshooting

### Common Issues

| Issue                      | Cause                      | Solution                                              |
| -------------------------- | -------------------------- | ----------------------------------------------------- |
| "Module not found"         | Dependencies not installed | Run `pip install -r requirements.txt`                 |
| "python command not found" | Python not in PATH         | Use `python3` on macOS/Linux                          |
| "Port 5000 in use"         | Another process using port | Kill process: `taskkill /F /PID <pid>` or change port |
| "API key not set"          | No API keys configured     | Add keys to `.env` file                               |
| "Permission denied"        | No write permission        | Use `pip install --user` or virtual environment       |

### Detailed Solutions

**Issue: "Port 5000 already in use"**

```bash
# Windows: Find and kill the process
netstat -ano | findstr :5000
taskkill /PID <process_id> /F

# Or change port in app/main.py
```

**Issue: "Permission denied" on pip install**

```bash
# Linux/macOS - add --user flag
pip install --user -r requirements.txt

# Or create a virtual environment
python -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
```

***

## Customization

### Using Your Own Business Problem

To use your own business problem, edit **Phase 1** (first code cell):

```python
business_problem = """
YOUR BUSINESS PROBLEM DESCRIPTION HERE.
Include details about:
- Who are the users (customers, merchants, admins, etc.)
- What features are needed
- What workflows should exist
- Any specific requirements
"""
```

### Example Business Problems

- "A hotel booking system for managing reservations"
- "A student attendance tracking application"
- "An inventory management system for retail stores"
- "A recipe sharing social platform"
- "A task management system for project teams"

***

## Submission Checklist

Before submitting, ensure:

- [ ] All notebook cells run successfully
- [ ] `.env` file configured with API keys
- [ ] Website loads at <http://127.0.0.1:5000/>
- [ ] Registration and login work
- [ ] At least one UML diagram is generated
- [ ] Flask API is functional
- [ ] Frontend pages are generated
- [ ] README.md is included and complete

***

## License

MIT License - Free to use for educational purposes.

***

## Credits

This project demonstrates AI-assisted software development using:

- **APIFree** for LLM and image generation
- **Flask** for web framework
- **Bootstrap 5** for responsive UI
- **GitHub Actions** for CI/CD

