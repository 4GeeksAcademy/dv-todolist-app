"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Todos
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route("/user/<string:username>", methods=["POST"])
def create_user(username=None):
    
    user = User()
    user_1 = user.query.filter_by(name=username).one_or_none()
   
    if user_1 is not None: 
        return jsonify("El usuario ya existe"), 400
    
    user.name = username
    db.session.add(user)

    try:
        db.session.commit()

        return jsonify({
            "id":user.id,
            "name": user.name,
        }), 201
    except Exception as err:
        print(err.args)
        return jsonify(err.args), 500


@app.route("/user/<string:username>", methods=["DELETE"])
def delete_user(username=None):
    user = User.query.filter_by(name=username).one_or_none()

    if user is None:
        return jsonify({"message":"el usuario no existe"}), 400

    else:
        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify([]), 204
        except Exception as err:
            return jsonify(err), 500
        

@app.route("/user/<string:username>", methods=["GET"])
def get_one_user(username=None):
    user = User.query.filter_by(name=username).one_or_none()
    print(user)

    if user is None:
        return jsonify({"message": f"El usuario {username} no existe"}), 404

    return jsonify(user.serialize()), 201


@app.route("/user", methods=["GET"])
def get_all_users():
    user = User.query.all()
    
    return jsonify({
        "users": list(map(lambda item: item.serialize_users(), user))
    }), 200


@app.route("/todos/<string:username>", methods=["POST"])
def add_todo(username=None):
    body = request.json

    user_id = User.query.filter_by(name=username).one_or_none()

    user = Todos()
    if body.get("label") is None:
        return jsonify("debes tener un label"), 400
    
    if body.get("is_done") is None:
        return jsonify("debes tener un is_done"), 400
    
    user.label = body.get("label")
    user.is_done = body.get("is_done")
    user.user_id = user_id.id
    db.session.add(user)


    try:
        db.session.commit()
        return jsonify("tarea agregada exitosamente"), 201
    except Exception as err:
        return jsonify(err), 500

    print(body)

    return jsonify("trabajando por usted")


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
