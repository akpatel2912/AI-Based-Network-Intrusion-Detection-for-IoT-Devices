# AI-Based Network Intrusion Detection for IoT Devices

Dataset: CICIoT2023 (binary, 0 = Normal, 1 = Attack). Models: XGBoost + Random Forest.
Stack: Python, scikit-learn, XGBoost, FastAPI, SQLite/PostgreSQL (Supabase), HTML/CSS/JS.

## Before you start
- Python 3.10 - 3.12 is recommended. Use `python3` / `pip3` on Mac and Linux.
- If `uvicorn` is not recognized, use `python -m uvicorn app.main:app --reload --port 8000`.
- Always run `train.py` on your own computer. No trained models are included, because saved models
  can break when library versions differ.

## Setup (once)
    pip install -r requirements.txt
Put `df_Binary_FL_CICIoT2023.csv` into `ml/data/raw/`.

## 1. Machine learning (run from ml/src)
    cd ml/src
    python preprocess.py     # clean data -> ml/data/processed/processed_data.csv
    python eda.py            # statistics + plots -> ml/data/processed/eda/
    python train.py          # trains both models -> ml/models/*.pkl
    python evaluate.py       # test metrics -> ml/models/metrics.json
    python predict.py        # quick test of one prediction

## 2. Backend (Terminal A, from backend)
    cd backend
    uvicorn app.main:app --reload --port 8000
API docs: http://127.0.0.1:8000/docs

## 3. Frontend
Open the `frontend` folder in VS Code, right-click `index.html`, choose "Open with Live Server" (port 5500).
Demo mode must stay OFF (it is off by default).

## 4. Live data (Terminal B, from backend)
    python simulate_traffic.py --count 200 --interval 1
The dashboard refreshes every 5 seconds and shows the results as they arrive.

## Database
SQLite file `backend/iot_shield.db` is created automatically.
For Supabase: run `database/schema.sql` in the SQL editor, copy `backend/.env.example` to `backend/.env`
and set DATABASE_URL.
