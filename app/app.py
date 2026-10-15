from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory storage — a simple Python list
students = [
    {"id": 1, "name": "vijay", "course": "DevOps"},
    {"id": 2, "name": "ajay", "course": "Cloud"},
     {"id": 3, "name": "atul", "course": "AI/ML"},
      {"id": 4, "name": "rajat", "course": "Data Science"},
       {"id": 5, "name": "rahul", "course": "Bigdata"},
        {"id": 6, "name": "kajal", "course": "salesforce"},
        {"id": 7, "name": "puneet", "course": "SDE"},
]


# ---------- Home ----------
@app.route("/")
def home():
    return jsonify({"message": "Student Management API", "version": "1.0"})


# ---------- Health check (used by Kubernetes later) ----------
@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# ---------- List all students ----------
@app.route("/students", methods=["GET"])
def get_students():
    return jsonify(students)


# ---------- Get one student by id ----------
@app.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    for s in students:
        if s["id"] == student_id:
            return jsonify(s)
    return jsonify({"error": "Student not found"}), 404


# ---------- Add a new student ----------
@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "name is required"}), 400

    new_id = max([s["id"] for s in students], default=0) + 1
    new_student = {
        "id": new_id,
        "name": data["name"],
        "course": data.get("course", "Unknown"),
    }
    students.append(new_student)
    return jsonify(new_student), 201


# ---------- Delete a student ----------
@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    for i, s in enumerate(students):
        if s["id"] == student_id:
            removed = students.pop(i)
            return jsonify({"deleted": removed})
    return jsonify({"error": "Student not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)