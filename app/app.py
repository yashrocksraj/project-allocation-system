from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

# -------------------- APP SETUP --------------------
app = Flask(__name__)

# -------------------- DATABASE CONFIG --------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -------------------- MODELS --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "project_id", name="unique_assignment"),
    )

# -------------------- ROUTES --------------------

@app.route("/")
def home():
    return jsonify({"message": "Project Allocation System API is running"})


@app.route("/about")
def about():
    return jsonify({"message": "This project manages users, projects and assignments"})


# -------------------- USERS --------------------
@app.route("/users", methods=["GET", "POST"])
def users():
    if request.method == "POST":
        data = request.json
        user = User(name=data["name"], email=data["email"])
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully"})

    # GET all users
    users = User.query.all()
    result = []

    for user in users:
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email
        })

    return jsonify(result)


@app.route("/users/<int:user_id>", methods=["GET", "PUT"])
def user_by_id(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if request.method == "PUT":
        data = request.json
        try:
            user.email = data["email"]
            db.session.commit()
            return jsonify({"message": "User email updated successfully"})
        except:
            db.session.rollback()
            return jsonify({"error": "Email already exists"}), 400

    # GET single user
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email
    })


# -------------------- PROJECTS --------------------
@app.route("/projects", methods=["POST", "GET"])
def projects():
    if request.method == "POST":
        data = request.json
        project = Project(
            title=data["title"],
            description=data["description"]
        )
        db.session.add(project)
        db.session.commit()
        return jsonify({"message": "Project created successfully"})

    projects = Project.query.all()
    result = []

    for project in projects:
        result.append({
            "id": project.id,
            "title": project.title,
            "description": project.description
        })

    return jsonify(result)


# -------------------- ASSIGN USER TO PROJECT --------------------
@app.route("/assign", methods=["POST"])
def assign_user_to_project():
    data = request.json

    assignment = Assignment(
        user_id=data["user_id"],
        project_id=data["project_id"]
    )

    try:
        db.session.add(assignment)
        db.session.commit()
        return jsonify({"message": "User assigned to project successfully"})
    except:
        db.session.rollback()
        return jsonify({"error": "User already assigned to this project"}), 400


# -------------------- RUN APP --------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

