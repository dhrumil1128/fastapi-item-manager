# FastAPI Item Management Backend

This repository contains the backend implementation built using FastAPI.

## Project Structure

```
fastapi-item-manager/
├── backend/
│   ├── main.py
│   └── requirements.txt
└── README.md
```

## Setup Instructions

1. **Create Environment (Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Run the Server:**
   ```bash
   uvicorn backend.main:app --reload
   ```

This will start the server, typically accessible at `http://127.0.0.1:8000`.

## API Documentation

Access the interactive API documentation (Swagger UI) at: `http://127.0.0.1:8000/docs`