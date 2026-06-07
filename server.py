from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import requests
import os
import re
import time

BASE = "/ai-azure-table-query"
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(PROJECT_ROOT, "school.db")
API_FILE = os.path.join(PROJECT_ROOT, "api.txt")

def get_api_key():
    if os.path.exists(API_FILE):
        with open(API_FILE, "r") as f:
            for line in f:
                if "=" in line and line.strip().startswith("MISTRAL_API_KEY"):
                    return line.split("=")[1].strip()
    return ""

# ─────────────────────────────────────────────────────────────────────────────
# RATE-MANAGED API CLIENT WITH INTER-REQUEST PACING
# ─────────────────────────────────────────────────────────────────────────────

def ask_general_mistral(messages_payload):
    api_key = get_api_key()
    payload = {
        "model": "mistral-small-latest",
        "messages": messages_payload,
        "temperature": 0.1
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # ⏱️ MANDATORY INTER-REQUEST PACE: Forces a tiny 500ms sleep before hitting the API
    # This prevents instant concurrent hits that trigger immediate 429 locks.
    time.sleep(0.5)
    
    wait_time = 2.5  
    for attempt in range(4):
        try:
            api_url = "https://api.mistral.ai/v1/chat/completions"
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            
            # If rate limited, print diagnostic tracking and pause dynamically
            if response.status_code == 429:
                print(f"⚠️ Mistral 429 (Rate Limit). Pacing execution: Waiting {wait_time}s... (Attempt {attempt + 1}/4)")
                time.sleep(wait_time)
                wait_time *= 2.0  # Double backoff duration sequentially
                continue
                
            if response.status_code != 200:
                print(f"\n❌ MISTRAL API ERROR CODE {response.status_code}: {response.text}\n")
                return f"ERROR_SIGNAL: API returned status code {response.status_code}"
                
            return response.json()["choices"][0]["message"]["content"]
        except Exception as ex:
            print(f"\n❌ EXCEPTION ENCOUNTERED: {str(ex)}\n")
            return f"ERROR_SIGNAL: {str(ex)}"
            
    return "ERROR_SIGNAL: Rate limit persistently blocked requests after multiple paced retries."

def local_list_all_tables():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cur.fetchall()]
    conn.close()
    return tables

def local_read_table(table_name: str, limit: int = 500):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
    rows = cur.fetchall()
    columns = [c[0] for c in cur.description]
    conn.close()
    
    dataset = []
    for row in rows:
        dataset.append(dict(zip(columns, row)))
    return dataset

# ─────────────────────────────────────────────────────────────────────────────
# COLLAPSED SINGLE-HIT DATA PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def multi_agent_analytics_pipeline(question: str, target_tables: list) -> str:
    data_context = ""
    
    for table in local_list_all_tables():
        if table in target_tables:
            rows = local_read_table(table, limit=500)
            if rows:
                data_context += f"\n--- Active Ledger Rows from Table: {table} ---\n{str(rows)}\n"

    unified_orchestrator_prompt = [
        {
            "role": "system", 
            "content": """You are a School Workspace Analytics & Reporting Agent. Analyze the raw database context records provided and directly format a response for the school Principal.
            
            MANAGEMENT DIRECTIONS:
            1. Respond in clean, direct, conversational markdown like Gemini or ChatGPT. No corporate memo titles or fake dates.
            2. Automatically resolve casual typos: map 'hospital' to 'hostel' details, map 'boys' to 'Male', and 'girls' to 'Female'.
            3. Null values in 'HostelDetails.FeesPaid' mean the student hasn't paid their fees yet.
            
            CRITICAL CHART HANDLING RULE:
            If the user explicitly asks for a chart, graph, or visual layout comparison, draw a text-based horizontal bar chart using block characters (█).
            Example layout output:
            - **Grade 5**: ████████████ 125 Students
            - **Grade 8**: ██████████████ 140 Students
            Ensure bar lengths precisely scale with the differences in numbers."""
        },
        {
            "role": "user", 
            "content": f"User Request: '{question}'\n\nLive Database Rows Dataset Input:\n{data_context}"
        }
    ]
    
    final_output = ask_general_mistral(unified_orchestrator_prompt)
    
    if "ERROR_SIGNAL" in final_output:
        return "The system is currently pacing data requests to clear API rate limitations. Please wait a brief moment and re-run your inquiry."
        
    return final_output

# ─────────────────────────────────────────────────────────────────────────────
# FLASK-ALIGNED API ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.get(f"{BASE}/api/stats")
def api_stats():
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM students;")
        total_students = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM Staff;")
        total_staff = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM Subjects_Grade;")
        total_subjects = cur.fetchone()[0]
        
        cur.execute("SELECT AVG(Mark) FROM Marks;")
        avg_marks = round(cur.fetchone()[0] or 0.0, 1)
        
        cur.execute("""
            SELECT students.student_first_name || ' ' || students.student_last_name, AVG(Marks.Mark) as savg 
            FROM Marks 
            JOIN students ON Marks.Student_Id = students.student_id 
            GROUP BY Marks.Student_Id ORDER BY savg DESC LIMIT 1;
        """)
        top_student_row = cur.fetchone()
        top_student_name = top_student_row[0] if top_student_row else "N/A"
        
        cur.execute("""
            SELECT students.student_first_name || ' ' || students.student_last_name, CAST(AVG(Marks.Mark) AS INT) as savg 
            FROM Marks 
            JOIN students ON Marks.Student_Id = students.student_id 
            GROUP BY Marks.Student_Id ORDER BY savg DESC LIMIT 5;
        """)
        leaderboard = [{"name": r[0], "avg": r[1]} for r in cur.fetchall()]
        
        cur.execute("""
            SELECT Subjects_Grade.SubjectName, round(AVG(Marks.Mark), 1) 
            FROM Marks 
            JOIN Subjects_Grade ON Marks.SubjectId = Subjects_Grade.SubjectId 
            GROUP BY Marks.SubjectId;
        """)
        subject_avgs = [{"subject": r[0], "avg": r[1]} for r in cur.fetchall()]
        
        conn.close()
        
        return JSONResponse({
            "success": True,
            "data": {
                "total_students": total_students,
                "total_subjects": total_subjects,
                "total_records": total_staff,
                "avg_marks": avg_marks,
                "top_student": top_student_name,
                "student_leaderboard": leaderboard,
                "subject_avgs": subject_avgs
            }
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.get(f"{BASE}/api/tables")
def api_tables():
    try:
        tables = local_list_all_tables()
        result = {}
        for name in tables:
            rows = local_read_table(name, limit=500)
            result[name] = {
                "rows": rows,
                "count": len(rows),
                "columns": list(rows[0].keys()) if rows else []
            }
        return JSONResponse({"success": True, "tables": result})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.post(f"{BASE}/api/chat")
async def api_chat(request: Request):
    try:
        data = await request.json()
        question = data.get("question", "").strip()
        
        if not question:
            return JSONResponse({"success": False, "error": "Question cannot be empty"}, status_code=400)
            
        tables = local_list_all_tables()
        target_tables = []
        q_low = question.lower()
        
        if "hostel" in q_low or "hospital" in q_low:
            target_tables = ["HostelDetails", "students"]
        elif "marks" in q_low or "score" in q_low or "math" in q_low or "grade" in q_low or "chart" in q_low or "graph" in q_low:
            target_tables = ["Marks", "students", "grades", "Subjects_Grade", "AdmissionFees"]
        elif "staff" in q_low or "teacher" in q_low:
            target_tables = ["Staff", "Staff_Subject", "Subjects_Grade"]
        elif "event" in q_low:
            target_tables = ["Events"]
        else:
            target_tables = ["students"]

        answer_text = multi_agent_analytics_pipeline(question, target_tables)
        
        debug_logs = {
            "original_question": question,
            "isolated_target_tables": target_tables,
            "all_available_tables": tables,
            "pipeline_status": "Success" if "ERROR_SIGNAL" not in answer_text else "Timeout/Error Encountered"
        }
        
        return JSONResponse({
            "success": True,
            "answer": answer_text,
            "backend_debug_logs": debug_logs
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.get(f"{BASE}/api/quick-insights")
def api_quick_insights():
    questions = [
        "How many students are yet to pay hostel fees?",
        "Share me the list of boy students staying in the hostel",
        "Who is the top performing student overall?",
        "Which subject has the highest average marks?",
        "Show me the first 10 students with their IDs and names"
    ]
    return JSONResponse({"success": True, "questions": questions})

@app.get("/")
@app.get(f"{BASE}")
@app.get(f"{BASE}/")
def index():
    return FileResponse(os.path.join(PROJECT_ROOT, "index.html"))