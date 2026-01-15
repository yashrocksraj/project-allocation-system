from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- MODELS ---------------- #

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'project_id', name='unique_assignment'),
    )



# --------------- ROUTES ---------------- #

@app.route("/")
def home():
    return jsonify({"message": "Project Allocation System API is running"})

@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    user = User(name=data["name"], email=data["email"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created successfully"})

@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user_email(user_id):
    data = request.json

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        user.email = data["email"]
        db.session.commit()
        return jsonify({"message": "User email updated successfully"})
    except:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 400


@app.route("/projects", methods=["POST"])
def create_project():
    data = request.json
    project = Project(title=data["title"], description=data["description"])
    db.session.add(project)
    db.session.commit()
    return jsonify({"message": "Project created successfully"})

@app.route("/assign", methods=["POST"])
def assign_user_to_project():
    data = request.json

    user_id = data["user_id"]
    project_id = data["project_id"]

    assignment = Assignment(user_id=user_id, project_id=project_id)

    try:
        db.session.add(assignment)
        db.session.commit()
        return jsonify({"message": "User assigned to project successfully"})
    except:
        db.session.rollback()
        return jsonify({"error": "User already assigned to this project"}), 400


# --------------- RUN ---------------- #

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
