import os
from flask import Flask, request, redirect, url_for, session, flash, jsonify
import json
from flask import render_template
from flask import current_app as app
from application.models import User, Subjects, Chapters, Questions, Options, QuizDetails, Scores, QuizResponse, File, Viewed, Reminder
from flask import request
from .database import db
from sqlalchemy import text
from sqlalchemy.engine import ResultProxy
from datetime import datetime, date, timedelta
from flask_mail import Message
from main import app, mail
import hashlib
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/", methods=["GET", "POST"])
def first():
    return jsonify({"message": "API is running"}), 200

@app.route("/api/user_register", methods=["GET", "POST"])
def register():
    return jsonify({"message": "Register page"}), 200

@app.route("/api/register/login", methods=["GET", "POST"])
def login1():
    username = request.json.get("username")
    fullname = request.json.get("fullname")
    dob = request.json.get("dob")
    qualification = request.json.get("qualification")
    password = request.json.get("password")
    
    if not username or not password or not fullname or not dob or not qualification:
        return jsonify({"error": "All fields are required."}), 400
    
    existing_user = db.session.query(User).filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Account already exists."}), 400
    else:
        new_user = User(username=username, fullname=fullname, dob=dob, qualification=qualification, password=password)
        new_file=  File(uid=new_user.uid, file_url='/static/upload/user.png')
        db.session.add(new_file)
        db.session.add(new_user)  
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201

@app.route("/api/admin", methods=["GET", "POST"])
def admin():
    ausername = request.json.get("ausername")
    apassword = request.json.get("apassword")
    
    if not ausername or not apassword:
        return jsonify({"error": "All fields are required."}), 400
    
    query = text("SELECT password FROM admin WHERE username = :ausername")
    result = db.session.execute(query, {"ausername": ausername}).fetchone()
    
    if result:
        stored_password = result[0]
        if apassword == stored_password:
            # Create JWT token for admin
            token = create_access_token(identity=ausername, additional_claims={"is_admin": True})
            return jsonify({"message": "Admin login successful", "token": token}), 200
        else:
            return jsonify({"error": "Incorrect password."}), 401
    return jsonify({"error": "Admin username not found."}), 404

@app.route("/api/login", methods=["GET", "POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")
    
    if not username or not password:
        return jsonify({"error": "All fields are required."}), 400
    
    query = text("SELECT password, uid, fullname FROM user WHERE username = :username")
    result = db.session.execute(query, {"username": username}).fetchone()
    
    if result:
        stored_password, uid, fullname = result
        if password == stored_password:
            # Create JWT token
            token = create_access_token(identity=username)
            return jsonify({
                "message": "Login successful",
                "token": token,
                "fullname": fullname,
                "uid": uid
            }), 200
        else:
            return jsonify({"error": "Incorrect password."}), 401
    return jsonify({"error": "Username not found."}), 404

@app.route("/api/profile", methods=["GET", "POST"])
@jwt_required()
def profile():
    return jsonify({"message": "Profile page"}), 200

@app.route("/api/personal_details", methods=["GET", "POST"])
@jwt_required()
def personal_details():
    username = get_jwt_identity()
    print(username)
    
    query = text("""
    SELECT uid, fullname, dob, qualification, password
    FROM user
    WHERE username = :username
    """)
    result = db.session.execute(query, {"username": username}).fetchone()
    
    if result:
        uid, fullname, dob, qualification, password = result
    else:
        return jsonify({"error": "User not found"}), 404
    
    result2 = db.session.execute(text("select file_url from File where uid=:uid"), {"uid": uid})
    img_url = result2.fetchone()
    url = img_url
        
    return jsonify({
        "id": uid,
        "fullname": fullname,
        "dob": dob,
        "img_url": url[0],
        "username": username,
        "qualification": qualification,
        "password": password
    }), 200

@app.route("/api/upload/<int:uid>", methods=["POST"])
@jwt_required()
def upload(uid):
    old_file = db.session.execute(text("SELECT file_url FROM File WHERE uid=:uid"), {"uid": uid}).fetchone()
    
    if old_file and old_file[0]:
        old_filepath = os.path.join(app.config["UPLOAD_FOLDER"], os.path.basename(old_file[0]))
        if os.path.exists(old_filepath):
            os.remove(old_filepath)
    
    db.session.execute(text("delete from File where uid=:uid"), {"uid": uid})
    db.session.commit()
    
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["image"]
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)
        file_url = f"/static/upload/{file.filename}"
        new_file = File(uid=uid, file_url=file_url) 
        db.session.add(new_file)
        db.session.commit()
        return jsonify({"message": "File uploaded successfully", "file_url": file_url}), 200
    
    return jsonify({"error": "File type not allowed"}), 400

@app.route("/api/academic_details", methods=["GET", "POST"])
@jwt_required()
def academic_details():
    username = get_jwt_identity()
    userid = db.session.execute(text("select uid from user where username= :username"), {"username": username})
    uid = userid.scalar()
    
    result = db.session.execute(text("select distinct(quizid) from quizresponse where uid=:userid"), {"userid": uid})
    quizid = result.fetchall()
    quizids = [id[0] for id in quizid]
    
    result2 = db.session.execute(text("select subject_name from subjects"))
    subject = result2.fetchall()
    subjectnames = [subjectname[0] for subjectname in subject]
    
    subjectcount = []
    result3 = db.session.execute(text("select * from quiz_details q join chapters c on c.chaoter_id=q.chapter_id join subjects s on s.subject_id=c.subject_id"))
    column_names = result3.keys()
    details = [dict(zip(column_names, rows)) for rows in result3.fetchall()]
    
    for subjectname in subjectnames:
        counter = 0
        for quizid1 in quizids:
            for detail in details:
                if detail['quizid'] == quizid1 and detail['subject_name'] == subjectname:
                    counter += 1
        subjectcount.append({"subject_name": subjectname, "count": counter})
    
    subjectmarks = []
    for subjectname in subjectnames:
        result5 = db.session.execute(text("select sum(score) from scores where quiz_id in (select quizid from quiz_details where chapter_id in (select chaoter_id from chapters where subject_id in (select subject_id from subjects where subject_name=:subject))) and uid=:uid"), {"subject": subjectname, "uid": uid})
        subjectsum = result5.scalar() or 0
        subject_entry = next((item for item in subjectcount if item["subject_name"] == subjectname), None)
        if subject_entry:
            subjectavg = subjectsum / subject_entry["count"] if subject_entry["count"] > 0 else 0
        else:
            subjectavg = 0
        subjectmarks.append({"subject_name": subjectname, "avg": round(subjectavg, 2)})
    
    result4 = db.session.execute(text("select * from scores s join quiz_details q on q.quizid=s.quiz_id join chapters c on c.chaoter_id=q.chapter_id join subjects d on c.subject_id=d.subject_id where s.uid=:userid order by s.uid,s.quiz_id"), {"userid": uid})
    column_names4 = result4.keys()
    quizdetails = [dict(zip(column_names4, rows4)) for rows4 in result4.fetchall()]

    return jsonify({
        "subjectcount": subjectcount, 
        "quizdetails": quizdetails, 
        "uid": uid, 
        "subjectmarks": subjectmarks
    }), 200

@app.route("/api/home", methods=["GET", "POST"])
@jwt_required()
def home():
    username = get_jwt_identity()
    fullname = db.session.execute(text("select fullname from user where username= :username"), {"username": username}).fetchone()
    
    if fullname:
        return jsonify({"fullname": fullname[0]}), 200
    return jsonify({"error": "User not found"}), 404

@app.route("/api/contact", methods=["GET", "POST"])
def contact():
    return jsonify({"message": "Contact page"}), 200

@app.route("/api/complaint", methods=["POST"])
@jwt_required()
def complaint():
    name = request.json.get('name')
    email = get_jwt_identity()
    issue = request.json.get('issue')
    details = request.json.get('details')
    
    if not name or not issue or not details:
        return jsonify({"error": "All fields are required"}), 400
    
    # Generate a reference ID based on email, issue and timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    reference_hash = hashlib.md5(f"{email}{issue}{timestamp}".encode()).hexdigest()[:8].upper()
    
    msg = Message("Complaint Received", recipients=[email])
    msg.html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2a5885;">Complaint Confirmation</h2>
        <p>Hello {name},</p>
        <p>We have received your complaint regarding:</p>
        
        <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #2a5885; margin: 15px 0;">
            <strong>{issue}</strong>
        </div>
        
        <p><strong>Details provided:</strong></p>
        <div style="background-color: #f9f9f9; padding: 15px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 20px;">
            {details}
        </div>
        
        <p>Our support team has been notified and will review your complaint promptly. You can expect to hear back from us within 2 business days.</p>
        
        <p>If you have any additional information to provide, please reply to this email.</p>
        
        <p>Thank you for bringing this matter to our attention.</p>
        
        <p>Best regards,<br>
        Customer Support Team</p>
        
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #777;">
            <p>Reference: #{reference_hash}</p>
        </div>
    </div>
</body>
</html>
"""

    # Also include a plain text version as fallback
    msg.body = f"""
Hello {name},

We have received your complaint regarding: {issue}

Details provided:
-------------------
{details}
-------------------

Our support team has been notified and will review your complaint promptly. You can expect to hear back from us within 2 business days.

If you have any additional information to provide, please reply to this email.

Thank you for bringing this matter to our attention.

Best regards,
Customer Support Team

Reference: #{reference_hash}
"""

    try:
        mail.send(msg)
        
        # Here you would typically also save the complaint to a database
        # Example (commented out):
        # new_complaint = Complaint(
        #     name=name,
        #     email=email,
        #     issue=issue,
        #     details=details,
        #     reference=reference_hash,
        #     created_at=datetime.now()
        # )
        # db.session.add(new_complaint)
        # db.session.commit()
        
        return jsonify({
            "message": "Your complaint has been submitted successfully. Check your email for confirmation!",
            "reference": reference_hash
        }), 200
    except Exception as e:
        # Log the error here
        print(f"Error sending email: {str(e)}")
        return jsonify({"error": "There was an issue processing your complaint. Please try again later."}), 500


@app.route("/api/adminhome", methods=["GET", "POST"])
@jwt_required()
def adminhome():
    try:
        result = db.session.execute(text("SELECT * FROM quiz_details ORDER BY quizid DESC"))
        result2 = db.session.execute(text("SELECT * FROM questions"))
        result3 = db.session.execute(text("SELECT * FROM chapters"))
        column_names = result.keys()
        column_names2 = result2.keys()
        column_names3 = result3.keys()
        quiz_details = [dict(zip(column_names, row)) for row in result.fetchall()]
        questions = [dict(zip(column_names2, rows2)) for rows2 in result2.fetchall()]
        chapters = [dict(zip(column_names3, rows)) for rows in result3.fetchall()]
        
        counter = []
        for chapter in chapters:
            count = 0
            for question in questions:
                if question["chapter_id"] == chapter["chaoter_id"]:
                    count += 1
            counter.append({'chapter_id': chapter["chaoter_id"], "question_count": count})
           
        return jsonify({
            "quiz_details": quiz_details,
            "chapters": chapters,
            "counter": counter
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/subjects", methods=["GET", "POST"])
def subjects():
    result = db.session.execute(text("SELECT * FROM subjects "))
    result2 = db.session.execute(text("SELECT * FROM chapters "))
    column_names = result.keys()
    column_names2 = result2.keys()
    subjects = [dict(zip(column_names, row)) for row in result.fetchall()]
    chapters = [dict(zip(column_names2, rows)) for rows in result2.fetchall()]
    
    return jsonify({
        "subjects": subjects,
        "chapters": chapters
    }), 200

@app.route("/api/chapters", methods=["GET", "POST"])
def chapters():
    result = db.session.execute(text("SELECT * FROM subjects "))
    result2 = db.session.execute(text("SELECT * FROM chapters "))
    column_names = result.keys()
    column_names2 = result2.keys()
    subjects = [dict(zip(column_names, row)) for row in result.fetchall()]
    chapters = [dict(zip(column_names2, rows)) for rows in result2.fetchall()]
    
    return jsonify({
        "subjects": subjects,
        "chapters": chapters
    }), 200

@app.route("/api/questions", methods=["GET", "POST"])
def questions():
    try:
        result = db.session.execute(text("SELECT * FROM subjects"))
        column_names = result.keys()
        subjects = [dict(zip(column_names, row)) for row in result.fetchall()]
        
        result2 = db.session.execute(text("SELECT * FROM chapters"))
        column_names2 = result2.keys()
        chapters = [dict(zip(column_names2, rows)) for rows in result2.fetchall()]
        
        questions_query = db.session.execute(text("""
            SELECT q.qid, q.chapter_id, q.question, o.option, o.option_id, q.answer
            FROM questions q
            LEFT JOIN options o ON q.qid = o.question_id
        """))
        
        questions = {}
        for row in questions_query:
            if row.qid not in questions:
                questions[row.qid] = {
                    "chapter_id": row.chapter_id,
                    "question_text": row.question,
                    "options": [],
                    "answer": row.answer
                }
            if row.option:
                questions[row.qid]["options"].append({"text": row.option, "id": row.option_id})
        
        questions_list = []
        for qid, qdata in questions.items():
            questions_list.append({
                "question_id": qid,
                "chapter_id": qdata["chapter_id"],
                "question_text": qdata["question_text"],
                "options": qdata["options"],
                "answer": qdata["answer"]
            })
            
        return jsonify({
            "subjects": subjects,
            "chapters": chapters,
            "questions": questions_list
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/student_academic_details", methods=["GET", "POST"])
@jwt_required()
def student_academic_details():
    usid = db.session.execute(text("select uid from user"))
    column_names9= usid.keys()
    useridall=[dict(zip(column_names9, rows)) for rows in usid.fetchall()]
    userids = usid.fetchall()
    userquiz = []
    
    for userid in userids:
        result = db.session.execute(text("select distinct quizid from quizresponse where uid=:userid"), {"userid": userid[0]})
        quizid1 = result.fetchall()
        for quizid in quizid1:
            userquiz.append({"uid": userid[0], "quizid": quizid})
    
    result2 = db.session.execute(text("select subject_name from subjects"))
    subject = result2.fetchall()
    subjectnames = [subjectname[0] for subjectname in subject]
    
    subjectcount = []
    result3 = db.session.execute(text("select distinct * from scores a join quiz_details q on a.quiz_id=q.quizid join chapters c on c.chaoter_id=q.chapter_id join subjects s on s.subject_id=c.subject_id"))
    column_names = result3.keys()
    details = [dict(zip(column_names, rows)) for rows in result3.fetchall()]
    
    for subjectname in subjectnames:
        counter = 0
        for detail in details:
            if detail['subject_name'] == subjectname:
                counter += 1
        subjectcount.append({"subject_name": subjectname, "count": counter})
   
    subjectmarks = []
    for subjectname in subjectnames:
        result5 = db.session.execute(text("select sum(score) from scores where quiz_id in (select quizid from quiz_details where chapter_id in (select chaoter_id from chapters where subject_id in (select subject_id from subjects where subject_name=:subject)))"), {"subject": subjectname})
        subjectsum = result5.scalar() or 0
        subject_entry = next((item for item in subjectcount if item["subject_name"] == subjectname), None)
        if subject_entry:
            subjectavg = subjectsum / subject_entry["count"] if subject_entry["count"] > 0 else 0
        else:
            subjectavg = 0
        subjectmarks.append({"subject_name": subjectname, "avg": round(subjectavg, 2)})
    
    result4 = db.session.execute(text("select * from scores s join quiz_details q on q.quizid=s.quiz_id join chapters c on c.chaoter_id=q.chapter_id order by s.uid, s.quiz_id"))
    column_names4 = result4.keys()
    quizdetails = [dict(zip(column_names4, rows4)) for rows4 in result4.fetchall()]
    
    return jsonify({
        "users": useridall,
        "subjectcount": subjectcount,
        "quizdetails": quizdetails,
        "subjectmarks": subjectmarks
    }), 200

@app.route("/api/edit/username", methods=["GET"])
@jwt_required()
def editusername():
    username = get_jwt_identity()
    return jsonify({"username": username}), 200

@app.route("/api/edit/dob", methods=["GET"])
@jwt_required()
def editdob():
    username = get_jwt_identity()
    dob = db.session.execute(text("select dob from user where username=:username"), {"username": username})
    return jsonify({"dob": dob.scalar()}), 200

@app.route("/api/edit/fullname", methods=["GET"])
@jwt_required()
def editname():
    username = get_jwt_identity()
    fullname = db.session.execute(text("select fullname from user where username=:username"), {"username": username})
    return jsonify({"fullname": fullname.scalar()}), 200

@app.route("/api/edit/qualification", methods=["GET"])
@jwt_required()
def editqualification():
    username = get_jwt_identity()
    qualification = db.session.execute(text("select qualification from user where username=:username"), {"username": username})
    return jsonify({"qualification": qualification.scalar()}), 200

@app.route("/api/edit/password", methods=["GET"])
@jwt_required()
def editpassword():
    return jsonify({"message": "Ready to edit password"}), 200

@app.route("/api/editcomplete", methods=["POST"])
@jwt_required()
def editcomplete():
    new_username = request.json.get("username")
    new_dob = request.json.get("dob")
    new_qualification = request.json.get("qualification")
    new_name = request.json.get("name")
    new_password = request.json.get("password1")
    password = request.json.get("password")
    
    if not password:
        return jsonify({"error": "Password is required"}), 400
    
    current_username = get_jwt_identity()
    storedpass_result = db.session.execute(text("SELECT password FROM user WHERE username = :username"), {"username": current_username}).fetchone()
    
    if not storedpass_result:
        return jsonify({"error": "User not found"}), 404
        
    storedpass = storedpass_result[0]
    
    if password != storedpass:
        return jsonify({"error": "Incorrect password"}), 401
    
    updates = {}
    if new_username:
        updates['username'] = new_username
    if new_dob:
        updates['dob'] = new_dob
    if new_qualification:   
        updates['qualification'] = new_qualification
    if new_name:
        updates['fullname'] = new_name
    if new_password:
        updates['password'] = new_password
    
    if not updates:
        return jsonify({"message": "No changes requested"}), 200
        
    try:
        for field, value in updates.items():
            query = text(f"UPDATE user SET {field} = :value WHERE username = :current_username")
            db.session.execute(query, {"value": value, "current_username": current_username})
        db.session.commit()
        
        result = None
        new_token = None
        
        if new_username:
            result = db.session.execute(text("SELECT username FROM user WHERE username = :username"), {"username": new_username}).fetchone()
            if result and result[0] == new_username:
                # Create new token with updated username
                new_token = create_access_token(identity=new_username)
                
        return jsonify({
            "message": "Profile updated successfully",
            "new_token": new_token
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unable to edit: {str(e)}"}), 500

@app.route("/api/student_personal_details", methods=["GET", "POST"])
@jwt_required()
def student_personal_details():
    try:
        result = db.session.execute(text("SELECT * FROM user a left join File b on a.uid=b.uid"))
        column_names = result.keys()
        users = [dict(zip(column_names, row)) for row in result.fetchall()]
       
        if not users:
            return jsonify({"message": "No users registered", "users": []}), 200
        else:
            return jsonify({
                "message": "Here are the details of all the users registered",
                "users": users
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/addsubject", methods=["GET"])
def addsubject():
    return jsonify({"message": "Ready to add subject"}), 200

@app.route("/api/edit/<int:subject_id>", methods=["GET"])
def edit_subject(subject_id):
    sub = db.session.execute(
        text("SELECT subject_name FROM subjects WHERE subject_id = :subject_id"),
        {"subject_id": subject_id}).fetchone()
    descript = db.session.execute(
        text("SELECT description FROM subjects WHERE subject_id = :subject_id"),
        {"subject_id": subject_id}).fetchone()
    
    if not sub or not descript:
        return jsonify({"error": "Subject not found"}), 404
        
    subject1 = sub[0]
    description = descript[0]
    
    return jsonify({
        "subject_id": subject_id,
        "subject_name": subject1,
        "description": description
    }), 200

@app.route("/api/editch/<int:chapter_id>", methods=["GET"])
def edit_chapter(chapter_id):
    try:
        result = db.session.execute(text("SELECT * FROM subjects"))
        column_names = result.keys()
        subjects1 = [dict(zip(column_names, row)) for row in result.fetchall()]
        
        chapter = db.session.execute(
            text("SELECT chapter_name, subject_id, description FROM chapters WHERE chaoter_id = :chapter_id"),
            {"chapter_id": chapter_id}
        ).fetchone()
        
        if not chapter:
            return jsonify({"error": "Chapter not found"}), 404
            
        chapter_name = chapter[0]
        current_subject_id = chapter[1]
        description = chapter[2]
        
        return jsonify({
            "subjects": subjects1,
            "chapter_id": chapter_id,
            "chapter_name": chapter_name,
            "current_subject_id": current_subject_id,
            "description": description
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/edit_quiz/<int:quiz_id>", methods=["GET"])
def edit_quiz(quiz_id):
    result = db.session.execute(text("SELECT * FROM quiz_details where quizid=:quiz_id"), {"quiz_id": quiz_id})
    column_names = result.keys()
    quiz_detail = [dict(zip(column_names, row)) for row in result.fetchall()]
    
    if not quiz_detail:
        return jsonify({"error": "Quiz not found"}), 404
        
    quiz_details = quiz_detail[0]
    
    result2 = db.session.execute(text("SELECT * FROM chapters"))
    column_names2 = result2.keys()
    chapters = [dict(zip(column_names2, rows)) for rows in result2.fetchall()]
    
    return jsonify({
        "chapters": chapters,
        "quiz_id": quiz_id,
        "quiz_date": quiz_details["quiz_date"],
        "duration": int(quiz_details["duration"]),
        "current_chapter_id": int(quiz_details["chapter_id"])
    }), 200

@app.route("/api/editcompletequiz/<int:quiz_id>", methods=["POST"])
@jwt_required()
def editcompletequiz(quiz_id):
    date = request.json.get("date")
    chapter_id = request.json.get("chapter_id")
    duration = request.json.get("duration")
    
    if not date or not chapter_id or not duration:
        return jsonify({"error": "All fields are required"}), 400
        
    try:
        db.session.execute(
            text("update quiz_details set quiz_date=:date, duration=:duration, chapter_id=:chapter_id where quizid=:quizid"),
            {"quizid": quiz_id, "chapter_id": chapter_id, "duration": duration, "date": date}
        )
        db.session.commit()
        return jsonify({"message": "Quiz updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/editcompletech/<int:chapter_id>", methods=["POST"])
@jwt_required()
def edit_chapter_complete(chapter_id):
    try:
        new_chapter_name = request.json.get("chapter")
        new_subject_id = request.json.get("sub_id")
        new_description = request.json.get("description")
        
        if not chapter_id or not new_chapter_name or not new_subject_id or not new_description:
            return jsonify({"error": "Missing data. Please provide all required fields."}), 400
            
        db.session.execute(
            text("UPDATE chapters SET chapter_name = :new_chapter_name, subject_id = :new_subject_id, description = :new_description WHERE chaoter_id = :chapter_id"),
            {
                "new_chapter_name": new_chapter_name,
                "new_subject_id": new_subject_id,
                "new_description": new_description,
                "chapter_id": chapter_id
            }
        )
        db.session.commit()

        return jsonify({"message": "Chapter updated successfully"}), 200
    except Exception as e:
        db.session.rollback() 
        return jsonify({"error": str(e)}), 500

@app.route("/api/edit_question/<int:question_id>", methods=["GET"])
def edit_question(question_id):
    try:
        chapters_result = db.session.execute(text("SELECT * FROM chapters"))
        chapters = [dict(row._mapping) for row in chapters_result.fetchall()] 
        
        question = db.session.execute(
            text("SELECT question, chapter_id, answer FROM questions WHERE qid = :question_id"),
            {"question_id": question_id}
        ).fetchone()

        if not question:
            return jsonify({"error": "Question not found"}), 404
            
        options_result = db.session.execute(
            text("SELECT option_id, `option` FROM options WHERE question_id = :question_id"),
            {"question_id": question_id}
        ).fetchall()
        
        options = [dict(row._mapping) for row in options_result] 
        question_text = question[0]
        current_chapter_id = question[1]
        current_answer_id = question[2]

        return jsonify({
            "chapters": chapters,
            "options": options,
            "question_id": question_id,
            "question_text": question_text,
            "current_chapter_id": current_chapter_id,
            "current_answer_id": current_answer_id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/api/editcompleteque/<int:question_id>", methods=["GET", "POST"])
@jwt_required()
def editcompleteque(question_id):
    try:
        new_question_text = request.form.get("question_text")
        new_answer = request.form.get("correct_option")
        new_chapter_id = request.form.get("chapter_id")
        options = []
        optionids = []
        for i in range(1, 5):
            opt = request.form.get(f"option{i}")
            options.append(opt)
        
        optids = db.session.execute(text("select option_id from options where question_id=:question_id"), {"question_id": question_id})
        optid = optids.fetchall()
        for optid1 in optid:
            optionids.append(optid1[0])
        
        for i in range(0, 4):
            db.session.execute(
                text("""
                    UPDATE options
                    SET `option` = :new_option
                    WHERE question_id = :question_id AND option_id = :option_id
                """),
                {
                    "new_option": options[i],
                    "question_id": question_id,
                    "option_id": optionids[i],
                }
            )
        db.session.commit()
    
        corrid = optionids[int(new_answer) - 1]
        db.session.execute(
            text("""
                UPDATE questions
                SET question = :new_question_text, chapter_id = :new_chapter_id, answer = :opt_id
                WHERE qid = :question_id
            """),
            {
                "new_question_text": new_question_text,
                "new_chapter_id": new_chapter_id,
                "opt_id": corrid,
                "question_id": question_id,
            }
        )
        db.session.commit()
        return jsonify({"message": "Question updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/editsubjectcomplete/<int:subject_id>", methods=["POST"])
@jwt_required()
def edit_subject_complete(subject_id):
    try:
        new_subject_name = request.form.get("subject")
        new_description = request.form.get("description")
        if not subject_id or not new_subject_name or not new_description:
            return jsonify({"error": "Missing data. Please provide all required fields."}), 400
        
        db.session.execute(
            text("UPDATE subjects SET subject_name = :new_subject_name, description = :new_description WHERE subject_id = :subject_id"),
            {
                "new_subject_name": new_subject_name,
                "new_description": new_description,
                "subject_id": subject_id
            }
        )
        db.session.commit()

        return jsonify({"message": "Subject updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/addcomplete/", methods=["GET", "POST"])
@jwt_required()
def addcomplete():
    new_subject = request.form.get("subject")
    new_description = request.form.get("description")
    if not new_subject or not new_description:
        return jsonify({"error": "Fill the required field"}), 400
    else:
        new_entry = Subjects(subject_name=new_subject, description=new_description)
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"message": "Subject added successfully"}), 201

@app.route("/api/addchapter", methods=["GET", "POST"])
@jwt_required()
def addchapter():
    result = db.session.execute(text("SELECT * FROM subjects"))
    column_names = result.keys()
    subjects1 = [dict(zip(column_names, row)) for row in result.fetchall()]
    return jsonify({"subjects": subjects1}), 200

@app.route("/api/addquiz", methods=["GET", "POST"])
@jwt_required()
def addquiz():
    result = db.session.execute(text("SELECT * FROM chapters"))
    column_names = result.keys()
    chapters = [dict(zip(column_names, row)) for row in result.fetchall()]
    return jsonify({"chapters": chapters}), 200

@app.route("/api/addcompletequiz", methods=["GET", "POST"])
@jwt_required()
def addcompletequiz():
    date = request.form.get("date")
    chapter_id = request.form.get("chapter_id")
    duration = request.form.get("duration")
    
    if not date or not chapter_id or not duration:
        return jsonify({"error": "Fill the required field"}), 400
    
    new_quiz = QuizDetails(quiz_date=date, duration=duration, chapter_id=chapter_id)
    db.session.add(new_quiz)
    db.session.commit()
    return jsonify({"message": "Quiz added successfully", "quiz_id": new_quiz.quizid}), 201

@app.route("/api/addcompletech/", methods=["GET", "POST"])
@jwt_required()
def addcompletech():
    new_chapter = request.form.get("chapter")
    sub_id = request.form.get("sub_id")
    new_description = request.form.get("description")
    print(new_chapter, sub_id, new_description)
    
    exist_sub_query = db.session.execute(text("SELECT subject_id FROM subjects"))
    exist_sub = [row.subject_id for row in exist_sub_query] 
    
    if not new_chapter or not new_description or not sub_id:
        return jsonify({"error": "Fill the required field"}), 400
    
    if int(sub_id) not in exist_sub:
        return jsonify({"error": "Subject doesn't exist"}), 400
    else:
        new_entry = Chapters(subject_id=sub_id, chapter_name=new_chapter, description=new_description)
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"message": "Chapter added successfully", "chapter_id": new_entry.chaoter_id}), 201

@app.route("/api/addquestion", methods=["GET", "POST"])
@jwt_required()
def addquestion():
    result = db.session.execute(text("SELECT * FROM chapters"))
    column_names = result.keys()
    chapters = [dict(zip(column_names, row)) for row in result.fetchall()]
    return jsonify({"chapters": chapters}), 200

@app.route("/api/addcompleteque", methods=["POST"])
@jwt_required()
def addcompletequestion():
    question_text = request.form.get("question_text")
    chapter_id = request.form.get("chapter_id")
    options = [
        request.form.get("option1"),
        request.form.get("option2"),
        request.form.get("option3"),
        request.form.get("option4"),
    ]
    correct_option = request.form.get("correct_option")
    
    if not question_text or not chapter_id or not all(options) or not correct_option:
        return jsonify({"error": "All fields are required."}), 400
    
    if not chapter_id.isdigit() or int(correct_option) not in range(1, 5):
        return jsonify({"error": "Invalid chapter ID or correct option."}), 400
    
    try:
        new_question = Questions(
            chapter_id=int(chapter_id),
            question=question_text, 
        )
        db.session.add(new_question)
        db.session.commit()
        question_id = new_question.qid
        
        for option in options:
            new_option = Options(
                question_id=question_id,
                option=option,
            )   
            db.session.add(new_option)
        db.session.commit()
        
        corr = options[int(correct_option) - 1]
        result2 = db.session.execute(
            text("select option_id from options where option=:option and question_id= :question_id"),
            {"option": corr, "question_id": question_id}
        )

        opt_id = result2.scalar()
        db.session.execute(
            text("UPDATE questions SET answer = :opt_id WHERE qid = :question_id"), 
            {"opt_id": opt_id, "question_id": question_id}
        )
        db.session.commit()
        return jsonify({"message": "Question added successfully", "question_id": question_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/deletesubject/<int:subject_id>", methods=["GET", "POST"])
@jwt_required()
def delete_subject(subject_id):
    try:
        db.session.execute(text("delete from subjects where subject_id=:subject_id"), {"subject_id": subject_id})
        db.session.execute(
            text("delete from options where question_id in (Select qid from questions where chapter_id in (select chaoter_id from chapters WHERE subject_id = :subject_id))"), 
            {"subject_id": subject_id}
        )
        db.session.execute(
            text("DELETE FROM questions where chapter_id in (select chaoter_id from chapters WHERE subject_id = :subject_id)"), 
            {"subject_id": subject_id}
        )
        db.session.execute(text("delete from chapters where subject_id=:subject_id"), {"subject_id": subject_id})
        db.session.commit()
        return jsonify({"message": "Subject deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/deletechapter/<int:chapter_id>", methods=["GET", "POST"])
@jwt_required()
def delete_chapter(chapter_id):
    try:
        db.session.execute(text("delete from chapters where chaoter_id=:chapter_id"), {"chapter_id": chapter_id})
        db.session.execute(
            text("delete from options where question_id in (Select qid from questions where chapter_id=:chapter_id)"),
            {"chapter_id": chapter_id}
        )
        db.session.execute(text("delete from questions where chapter_id=:chapter_id"), {"chapter_id": chapter_id})
        db.session.commit()
        return jsonify({"message": "Chapter deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/delete_question/<int:question_id>", methods=["GET", "POST"])
@jwt_required()
def delete_question(question_id):
    try:
        db.session.execute(text("delete from options where question_id=:question_id"), {"question_id": question_id})
        db.session.execute(text("delete from questions where qid=:question_id"), {"question_id": question_id})
        db.session.commit()
        return jsonify({"message": "Question deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/quizzes/<int:quiz_id>", methods=["DELETE"])
@jwt_required()
def delete_quiz(quiz_id):
    try:
        db.session.execute(text("delete from quiz_details where quizid=:quiz_id"), {"quiz_id": quiz_id})
        db.session.commit()
        db.session.execute(text("delete from quizresponse where quizid=:quiz_id"), {"quiz_id": quiz_id})
        db.session.commit()
        db.session.execute(text("delete from scores where quiz_id=:quiz_id"), {"quiz_id": quiz_id})
        db.session.commit()
        return jsonify({"message": "Quiz deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/delete_user/<int:userid>", methods=["DELETE"])
@jwt_required()
def delete_user(userid):
    try:
        db.session.execute(text("delete from scores where uid=:uid"), {"uid": userid})
        db.session.execute(text("delete from quizresponse where uid=:uid"), {"uid": userid})
        db.session.execute(text("delete from user where uid=:uid"), {"uid": userid})
        db.session.execute(text("delete from File where uid=:uid"), {"uid": userid})
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/api/user/<fullname>', methods=['GET', 'POST'])
@jwt_required()
def user_profile(fullname):
    result = db.session.execute(text("SELECT * FROM subjects"))
    result2 = db.session.execute(text("SELECT * FROM chapters"))
    column_names = result.keys()
    column_names2 = result2.keys()
    subjects = [dict(zip(column_names, row)) for row in result.fetchall()]
    chapters = [dict(zip(column_names2, rows)) for rows in result2.fetchall()]
    return jsonify({"subjects": subjects, "chapters": chapters}), 200


@app.route("/api/quizinstructions/<int:quiz_id>", methods=["GET", "POST"])
@jwt_required()
def quizinstructions(quiz_id):
    result = db.session.execute(text("select duration from quiz_details where quizid=:quiz_id"), {"quiz_id": quiz_id})
    duration = result.scalar()
    return jsonify({"name": "chapter", "id": quiz_id, "duration": duration}), 200

@app.route("/api/startquiz/<int:quiz_id>", methods=["GET", "POST"])
@jwt_required()
def startquiz(quiz_id):
    result3 = db.session.execute(text("select * from quiz_details where quizid=:quiz_id"), {"quiz_id": quiz_id})
    column_names3 = result3.keys()
    quiz_details = [dict(zip(column_names3, rows3)) for rows3 in result3.fetchall()]
    
    result = db.session.execute(
        text("SELECT * FROM questions where chapter_id= :chapter_id"),
        {"chapter_id": quiz_details[0]["chapter_id"]}
    )
    result2 = db.session.execute(text("SELECT * FROM options"))
    column_names = result.keys()
    column_names2 = result2.keys()
    questions = [dict(zip(column_names, row)) for row in result.fetchall()]
    options = [dict(zip(column_names2, rows)) for rows in result2.fetchall()]
    
    return jsonify({
        "questions": questions, 
        "options": options, 
        "duration": quiz_details[0]["duration"], 
        "quiz_id": quiz_id
    }), 200

@app.route("/api/submitquiz/<int:quiz_id>", methods=["GET", "POST"])
@jwt_required()
def submitquiz(quiz_id):
    try:
        result = db.session.execute(text("select chapter_id from quiz_details where quizid=:quiz_id"), {"quiz_id": quiz_id})
        chapter_id = result.scalar()
        result2 = db.session.execute(
            text("SELECT * FROM questions where chapter_id= :chapter_id"),
            {"chapter_id": chapter_id}
        ).mappings()
        questions = [dict(row) for row in result2.fetchall()]
        
        username = get_jwt_identity()
        userid_result = db.session.execute(text("select uid from user where username= :username"), {"username": username})
        userid = userid_result.scalar()
        
        for question in questions:
            opt_id = request.form.get(f"question_{question['qid']}")
            new_quizresponse = QuizResponse(quizid=quiz_id, uid=userid, questionid=question['qid'], optionid=opt_id)
            db.session.add(new_quizresponse)
        
        db.session.commit()
        time_taken = request.form.get("time_taken")
        
        return jsonify({
            "message": "Quiz submitted successfully", 
            "quiz_id": quiz_id, 
            "uid": userid, 
            "time_taken": time_taken
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/scores/<int:quiz_id>/<int:uid>/<int:time_taken>", methods=["GET", "POST"])
@jwt_required()
def scores(quiz_id, uid, time_taken):
    minutes = int(time_taken / 60)
    seconds = time_taken % 60
    
    result3 = db.session.execute(text("select * from quiz_details where quizid=:quiz_id"), {"quiz_id": quiz_id})
    column_names3 = result3.keys()
    quiz_details = [dict(zip(column_names3, rows3)) for rows3 in result3.fetchall()]
    
    result = db.session.execute(
        text("SELECT * FROM questions where chapter_id= :chapter_id"),
        {"chapter_id": quiz_details[0]["chapter_id"]}
    )
    result2 = db.session.execute(text("SELECT * FROM options"))
    column_names = result.keys()
    column_names2 = result2.keys()
    questions = [dict(zip(column_names, row)) for row in result.fetchall()]
    options = [dict(zip(column_names2, rows)) for rows in result2.fetchall()]
    
    result4 = db.session.execute(text("select * from quizresponse where quizid=:quiz_id"), {"quiz_id": quiz_id})
    column_names4 = result4.keys()
    quizresponses = [dict(zip(column_names4, rows4)) for rows4 in result4.fetchall()]
    
    scorecount = 0
    questioncount = 0
    result3 = db.session.execute(
        text("SELECT * FROM quizresponse where quizid= :quiz_id AND uid=:userid"),
        {"quiz_id": quiz_id, "userid": uid}
    ).mappings()
    responses = [dict(row) for row in result3.fetchall()]
    
    for response in responses:
        for question in questions:
            if question['qid'] == response['questionid']:
                questioncount = questioncount + 1
                if question['answer'] == response['optionid']:
                    scorecount = scorecount + 1
    
    result6 = db.session.execute(
        text("select * from scores where quiz_id=:quiz_id and uid=:uid"),
        {"quiz_id": quiz_id, "uid": uid}
    )
    result7 = result6.fetchall()
    
    if not result7:
        new_score = Scores(quiz_id=quiz_id, uid=uid, time_stamp=time_taken, score=scorecount, total=questioncount)
        db.session.add(new_score)
        db.session.commit()
    
    return jsonify({
        "score": scorecount,
        "minutes": minutes,
        "seconds": seconds,
        "total": questioncount,
        "questions": questions,
        "options": options,
        "quizresponses": quizresponses
    }), 200

@app.route("/api/viewchapter/<int:chapter_id>", methods=["GET", "POST"])
@jwt_required()
def viewchapter(chapter_id):
    chapter = Chapters.query.get(chapter_id)
    if chapter:
        return jsonify({
            "chaoter_id": chapter.chaoter_id,
            "subject_id": chapter.subject_id,
            "chapter_name": chapter.chapter_name,
            "description": chapter.description
        }), 200
    else:
        return jsonify({"error": "Chapter not found"}), 404

@app.route("/api/livequiz", methods=["GET", "POST"])
@jwt_required()
def livequiz():
    tdate = date.today()
    
    result = db.session.execute(
        text("select * from quiz_details where quiz_date>=:date order by (quiz_date)"),
        {"date": str(tdate)}
    )
    column_names = result.keys()
    quiz_details = [dict(zip(column_names, row)) for row in result.fetchall()]

    result2 = db.session.execute(text("select * from chapters"))
    column_names2 = result2.keys()
    chapters = [dict(zip(column_names2, row2)) for row2 in result2.fetchall()]
    
    result3 = db.session.execute(text("select * from subjects"))
    column_names3 = result3.keys()
    subjects = [dict(zip(column_names3, row3)) for row3 in result3.fetchall()]
    
    username = get_jwt_identity()
    userid = db.session.execute(text("select uid from user where username= :username"), {"username": username})
    uid = userid.scalar()

    result4 = db.session.execute(text("select distinct(quizid) from quizresponse where uid=:uid"), {"uid": uid})
    column_names4 = result4.keys()
    quizresponses = [dict(zip(column_names4, rows4)) for rows4 in result4.fetchall()]
    
    listforquiz = []
    for quiz_detail in quiz_details:
        arg = 0
        if quiz_detail["quiz_date"] == str(tdate):
            arg = 1
        for chapter in chapters:
            for subject in subjects:
                if quiz_detail["chapter_id"] == chapter["chaoter_id"]:
                    if chapter["subject_id"] == subject["subject_id"]:
                        result4 = db.session.execute(
                            text("select count(*) from questions where chapter_id in (select chaoter_id from chapters where chaoter_id=:chapter_id) order by(qid);"),
                            {"chapter_id": chapter["chaoter_id"]}
                        )
                        listforquiz.append({
                            "quizid": quiz_detail["quizid"],
                            "chapter_id": chapter["chaoter_id"],
                            "chapter_name": chapter["chapter_name"],
                            "subjectname": subject["subject_name"],
                            "questioncount": result4.scalar(),
                            "arg": arg
                        })
    

    return jsonify({
        "listforquiz": listforquiz,
        "quiz_details": quiz_details,
        "quizresponses": quizresponses,
        "curr_id": uid
    }), 200

@app.route("/api/transcript/<int:quiz_id>/<int:uid>", methods=["GET", "POST"])
@jwt_required()
def transcript(quiz_id, uid):
    time_taken = request.form.get("time_taken")
    
    result3 = db.session.execute(text("select * from quiz_details where quizid=:quiz_id"), {"quiz_id": quiz_id})
    column_names3 = result3.keys()
    quiz_details = [dict(zip(column_names3, rows3)) for rows3 in result3.fetchall()]
    
    result = db.session.execute(
        text("SELECT * FROM questions where chapter_id= :chapter_id"),
        {"chapter_id": quiz_details[0]["chapter_id"]}
    )
    result2 = db.session.execute(text("SELECT * FROM options"))
    column_names = result.keys()
    column_names2 = result2.keys()
    questions = [dict(zip(column_names, row)) for row in result.fetchall()]
    options = [dict(zip(column_names2, rows)) for rows in result2.fetchall()]
    
    result4 = db.session.execute(text("select * from quizresponse where quizid=:quiz_id"), {"quiz_id": quiz_id})
    column_names4 = result4.keys()
    quizresponses = [dict(zip(column_names4, rows4)) for rows4 in result4.fetchall()]
    
    scorecount = 0
    questioncount = 0
    result3 = db.session.execute(
        text("SELECT * FROM quizresponse where quizid= :quiz_id AND uid=:userid"),
        {"quiz_id": quiz_id, "userid": uid}
    ).mappings()
    responses = [dict(row) for row in result3.fetchall()]
    
    for response in responses:
        for question in questions:
            if question['qid'] == response['questionid']:
                questioncount = questioncount + 1
                if question['answer'] == response['optionid']:
                    scorecount = scorecount + 1
    
    time = db.session.execute(
        text("select time_stamp from scores where quiz_id=:quiz_id and uid=:uid"),
        {"quiz_id": quiz_id, "uid": uid}
    )
    timestamps = time.fetchone()
    timestamp = timestamps[0]
    minutes = int(int(timestamp) / 60)
    seconds = int(int(timestamp) % 60)
    
    return jsonify({
        "minutes": minutes,
        "seconds": seconds,
        "score": scorecount,
        "total": questioncount,
        "questions": questions,
        "options": options,
        "quizresponses": quizresponses
    }), 200
