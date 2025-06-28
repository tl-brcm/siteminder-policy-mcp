# Gemini Project Configuration

This file helps the Gemini assistant understand how to work with your project.

## 🚀 Run

### Development Server
This command starts the development server with live reloading.
`uvicorn dev:app --reload --port 3123 --host 0.0.0.0`

### Standard I/O Mode
This command runs the agent for integration with other processes.
`python main.py`

## 🧪 Test

*   **No test commands specified.**
*   If you have a testing framework set up (e.g., pytest), you can add the command here.
*   Example: `pytest`

## 📦 Build

*   **No build command specified.**
*   For typical Python projects, a build step might not be necessary. If you have a build process (e.g., for creating a wheel or an executable), add the command here.

## ⚙️ Dependencies

To install or update dependencies, run:
`pip install -r requirements.txt`

## 🔧 Configuration

This project uses a `.env` file for configuration. Ensure the following variables are set in a `.env` file in the project root:
- `SITE_MINDER_BASE_URL`
- `SITE_MINDER_USERNAME`
- `SITE_MINDER_PASSWORD`
- `VERIFY_SSL`
