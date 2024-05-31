from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'zubair.zabir@gmail.com'
app.config['MAIL_PASSWORD'] = 'xhnu isxp wrdn jeab'

db = SQLAlchemy(app)
mail = Mail(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    parent_email = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # active, archived

@app.route('/students', methods=['POST'])
def add_student():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid input"}), 400
        new_student = Student(
            name=data.get('name'),
            email=data.get('email'),
            parent_email=data.get('parent_email'),
            status='active'
        )
        db.session.add(new_student)
        db.session.commit()
        return jsonify({"message": "Student added successfully"}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/students', methods=['GET'])
def get_students():
    try:
        students = Student.query.all()
        return jsonify([{
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "parent_email": student.parent_email,
            "status": student.status
        } for student in students]), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/students/<int:student_id>/send-email', methods=['POST'])
def send_email(student_id):
    try:
        student = Student.query.get_or_404(student_id)
        subject = f"Notification for {student.name}"
        body = f"""
        Dear Parent/Guardian,

        This is to inform you about the recent activities and updates regarding your child, {student.name}.

        Status: {student.status}
        Student Email: {student.email}

        Please feel free to contact us if you have any questions or need further information.

        Best regards,
        Your School Administration
        """
        msg = Message(
            subject,
            sender="zubair.zabir@gmail.com",
            recipients=[student.parent_email]
        )
        msg.body = body
        mail.send(msg)
        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/students/<int:student_id>/status', methods=['PUT'])
def update_student_status(student_id):
    try:
        student = Student.query.get_or_404(student_id)
        data = request.json
        if 'status' in data:
            student.status = data['status']
            db.session.commit()
            return jsonify({"message": "Student status updated successfully"}), 200
        else:
            return jsonify({"error": "Invalid input"}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
