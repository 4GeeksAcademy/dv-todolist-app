from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    todos = db.relationship("Todos", back_populates="user", cascade="all, delete")

    def serialize(self):
        # self.todos = self.todos.order_by(Todos.label.asc()).all()
        
        return {
            "name": self.name,
            # "todos": [item.serialize() for item in self.todos]
            "todos": sorted(
                [item.serialize() for item in self.todos], key=lambda todo: todo["id"]
            )
        }
    
    def serialize_users(self):
        return {
            "id": self.id,
            "name":self.name
        }


class Todos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(255), nullable=False)
    is_done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    user = db.relationship("User", back_populates="todos")


    def serialize(self):
        return {
            "id": self.id,
            "label": self.label,
            "is_done":self.is_done
        }