from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_mcq_key_123")

# Connect to MongoDB
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://umiraoutlook_db_user:umira123@cluster0.x4b4h0j.mongodb.net/?appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client["mcq_system"]

import random
import urllib.request
import json
import html
import datetime
import smtplib
from email.message import EmailMessage
import threading

def send_result_email_async(user, score, total, correct, wrong, unanswered, violation, exam_date):
    def send_email():
        try:
            sender_email = os.environ.get("SMTP_EMAIL", "thenewcollegemcq@gmail.com")
            sender_password = os.environ.get("SMTP_PASSWORD", "slsk jyio adui qzej")

            msg = EmailMessage()
            msg["Subject"] = "Assessment Result - The New College"
            msg["From"] = sender_email
            msg["To"] = user.get("email")
            
            percentage = (score / total) * 100 if total > 0 else 0
            status_text = "Exam Terminated (Violation)" if violation else ("Passed" if percentage >= 50 else "Failed")
            status_color = "#991b1b" if violation or percentage < 50 else "#166534"
            status_bg = "#fee2e2" if violation or percentage < 50 else "#dcfce7"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f9f4ec; margin: 0; padding: 20px; color: #101828; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
                .header {{ background-color: #7a0b0b; padding: 30px 20px; text-align: center; color: white; }}
                .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; letter-spacing: 1px; }}
                .content {{ padding: 30px; }}
                .greeting {{ font-size: 18px; margin-bottom: 20px; color: #333; }}
                .card {{ background: #fdfbf7; border: 1px solid #e0d5c5; border-radius: 8px; padding: 20px; margin-bottom: 25px; }}
                .status-badge {{ display: inline-block; padding: 8px 16px; background-color: {status_bg}; color: {status_color}; border-radius: 20px; font-weight: bold; font-size: 14px; margin-bottom: 20px; }}
                .stat-row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee; }}
                .stat-row:last-child {{ border-bottom: none; }}
                .stat-label {{ color: #667085; font-weight: 500; }}
                .stat-value {{ font-weight: 600; color: #101828; }}
                .footer {{ background: #f1f1f1; padding: 20px; text-align: center; font-size: 12px; color: #777; }}
            </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>The New College</h1>
                        <p style="margin: 5px 0 0 0; opacity: 0.8; font-size: 14px;">Assessment Result</p>
                    </div>
                    <div class="content">
                        <div class="greeting">Hello {user.get('first_name', '')} {user.get('last_name', '')},</div>
                        <p>Thank you for completing your internal examination. Your results are summarized below.</p>
                        
                        <div style="text-align: center;">
                            <div class="status-badge">{status_text}</div>
                        </div>

                        <div class="card">
                            <div class="stat-row">
                                <span class="stat-label">Register Number</span>
                                <span class="stat-value">{user.get('register_number', '')}</span>
                            </div>
                            <div class="stat-row">
                                <span class="stat-label">Subject</span>
                                <span class="stat-value">{user.get('subject', '')}</span>
                            </div>
                            <div class="stat-row">
                                <span class="stat-label">Date &amp; Time</span>
                                <span class="stat-value">{exam_date}</span>
                            </div>
                        </div>

                        <div class="card">
                            <div class="stat-row">
                                <span class="stat-label">Total Questions</span>
                                <span class="stat-value">{total}</span>
                            </div>
                            <div class="stat-row">
                                <span class="stat-label">Correct Answers</span>
                                <span class="stat-value" style="color: #166534;">{correct}</span>
                            </div>
                            <div class="stat-row">
                                <span class="stat-label">Wrong Answers</span>
                                <span class="stat-value" style="color: #991b1b;">{wrong}</span>
                            </div>
                            <div class="stat-row">
                                <span class="stat-label">Unanswered</span>
                                <span class="stat-value">{unanswered}</span>
                            </div>
                            <div class="stat-row">
                                <span class="stat-label">Final Score</span>
                                <span class="stat-value">{score}</span>
                            </div>
                            <div class="stat-row">
                                <span class="stat-label">Percentage</span>
                                <span class="stat-value">{percentage:.2f}%</span>
                            </div>
                        </div>
                        
                        <p style="font-size: 14px; color: #666; margin-top: 30px;">If you have any questions regarding your results, please contact your department administrator.</p>
                    </div>
                    <div class="footer">
                        &copy; 2026 The New College. All rights reserved.
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.set_content("Please enable HTML to view this message.")
            msg.add_alternative(html_content, subtype='html')

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send email: {e}")
            
    threading.Thread(target=send_email).start()

# Question Bank (Fallback)
QUESTION_BANK = [
    {"id": "q1", "question": "Which of the following is an immutable data type in Python?", "options": {"a": "Tuple", "b": "List", "c": "Dictionary", "d": "Set"}, "answer": "a"},
    {"id": "q2", "question": "What does HTML stand for?", "options": {"a": "Hyper Text Markup Language", "b": "High Text Markup Language", "c": "Hyper Tabular Markup Language", "d": "None of the above"}, "answer": "a"},
    {"id": "q3", "question": "Which SQL statement is used to extract data from a database?", "options": {"a": "OPEN", "b": "SELECT", "c": "EXTRACT", "d": "GET"}, "answer": "b"},
    {"id": "q4", "question": "What is the default port for HTTP?", "options": {"a": "21", "b": "22", "c": "443", "d": "80"}, "answer": "d"},
    {"id": "q5", "question": "Which of the following is NOT a JavaScript framework?", "options": {"a": "Django", "b": "React", "c": "Vue", "d": "Angular"}, "answer": "a"},
    {"id": "q6", "question": "Which company developed the Java programming language?", "options": {"a": "Microsoft", "b": "Apple", "c": "Sun Microsystems", "d": "Google"}, "answer": "c"},
    {"id": "q7", "question": "What is the time complexity of binary search?", "options": {"a": "O(n)", "b": "O(n log n)", "c": "O(1)", "d": "O(log n)"}, "answer": "d"},
    {"id": "q8", "question": "Which HTTP method is typically used to update an existing resource?", "options": {"a": "GET", "b": "POST", "c": "PUT", "d": "DELETE"}, "answer": "c"},
    {"id": "q9", "question": "What does CSS stand for?", "options": {"a": "Creative Style Sheets", "b": "Cascading Style Sheets", "c": "Computer Style Sheets", "d": "Colorful Style Sheets"}, "answer": "b"},
    {"id": "q10", "question": "In React, what hook is used to manage state in a functional component?", "options": {"a": "useEffect", "b": "useContext", "c": "useState", "d": "useReducer"}, "answer": "c"}
]

@app.route("/api/questions")
def api_questions():
    if "user" not in session:
        return {"error": "Unauthorized"}, 401
    
    # Pick 10 random questions from the bank
    selected = random.sample(QUESTION_BANK, 10)
    
    # Store correct answers in session for grading later
    session["exam_answers"] = {q["id"]: q["answer"] for q in selected}
    
    # Remove the answers before sending to frontend
    frontend_questions = []
    for q in selected:
        frontend_questions.append({
            "id": q["id"],
            "question": q["question"],
            "options": q["options"]
        })
        
    return {"questions": frontend_questions}

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_data = {
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name"),
            "email": request.form.get("email"),
            "register_number": request.form.get("register_number"),
            "mobile": request.form.get("mobile"),
            "dob": request.form.get("dob"),
            "degree": request.form.get("degree"),
            "batch": request.form.get("batch"),
            "level": request.form.get("level"),
            "semester": request.form.get("semester"),
            "internal_exam": request.form.get("internal_exam"),
            "subject": request.form.get("subject")
        }
        
        # Check if user already exists
        existing_user = db.users.find_one({
            "$or": [
                {"register_number": user_data["register_number"]},
                {"email": user_data["email"]}
            ]
        })
        
        if existing_user:
            if existing_user.get("email") == user_data["email"]:
                return render_template("register.html", error="This Email ID is already registered. Please login instead.")
            return render_template("register.html", error="This Register Number is already registered. Please login instead.")
            
        # Insert user to database
        db.users.insert_one(user_data.copy())
        
        # Save user to session
        session["user"] = user_data
        return redirect("/exam")
        
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")  # User uses register_number as password
        
        user = db.users.find_one({"email": email, "register_number": password})
        
        if user:
            user.pop("_id", None)
            session["user"] = user
            
            # Check if user has already taken the exam
            result = db.results.find_one({"register_number": password})
            if result:
                session["score"] = result["score"]
                session["total"] = result["total"]
                session["correct"] = result.get("correct", result["score"])
                session["wrong"] = result.get("wrong", result["total"] - result["score"])
                session["unanswered"] = result.get("unanswered", 0)
                session["exam_date"] = result.get("exam_date", "N/A")
                session["violation"] = result.get("terminated_due_to_violation", False)
                return redirect("/result")
            else:
                return redirect("/exam")
        else:
            return render_template("login.html", error="Invalid Email or Register Number.")
            
    return render_template("login.html")

@app.route("/exam", methods=["GET", "POST"])
def exam():
    if "user" not in session:
        return redirect("/")
        
    # If the user already took the exam, redirect them straight to the results
    if request.method == "GET":
        existing_result = db.results.find_one({"register_number": session["user"]["register_number"]})
        if existing_result:
            session["score"] = existing_result["score"]
            session["total"] = existing_result["total"]
            session["correct"] = existing_result.get("correct", existing_result["score"])
            session["wrong"] = existing_result.get("wrong", existing_result["total"] - existing_result["score"])
            session["unanswered"] = existing_result.get("unanswered", 0)
            session["exam_date"] = existing_result.get("exam_date", "N/A")
            session["violation"] = existing_result.get("terminated_due_to_violation", False)
            return redirect("/result")
            
    if request.method == "POST":
        score = 0
        unanswered = 0
        wrong = 0
        exam_answers = session.get("exam_answers", {})
        
        for q_id, correct_ans in exam_answers.items():
            user_ans = request.form.get(q_id)
            if not user_ans:
                unanswered += 1
            elif user_ans == correct_ans:
                score += 1
            else:
                wrong += 1
                
        # Handle tab violation auto-submit scenario
        violation_submit = request.form.get("violation_submit") == "true"
        
        exam_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
        db.results.insert_one({
            "register_number": session["user"]["register_number"],
            "score": score,
            "total": len(exam_answers),
            "correct": score,
            "wrong": wrong,
            "unanswered": unanswered,
            "terminated_due_to_violation": violation_submit,
            "exam_date": exam_date
        })
        
        session["score"] = score
        session["total"] = len(exam_answers)
        session["correct"] = score
        session["wrong"] = wrong
        session["unanswered"] = unanswered
        session["violation"] = violation_submit
        session["exam_date"] = exam_date
        
        # Send result email asynchronously
        send_result_email_async(
            user=session["user"],
            score=score,
            total=len(exam_answers),
            correct=score,
            wrong=wrong,
            unanswered=unanswered,
            violation=violation_submit,
            exam_date=exam_date
        )
        
        return redirect("/result")

    return render_template("exam.html", user=session["user"])

@app.route("/result")
def result():
    if "score" not in session:
        return redirect("/")
    
    return render_template(
        "result.html", 
        score=session["score"], 
        total=session["total"], 
        correct=session.get("correct", session["score"]),
        wrong=session.get("wrong", session["total"] - session["score"]),
        unanswered=session.get("unanswered", 0),
        exam_date=session.get("exam_date", "N/A"),
        user=session.get("user"),
        violation=session.get("violation", False)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)