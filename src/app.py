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
from models import db, User, People, Planet, Favorites_Planet, Favorites_People
import requests

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

@app.route('/users', methods=['GET'])
def all_user():
    users = User.query.all()

    users_serialize = [user.serialize() for user in users]

    return jsonify(users_serialize), 200

@app.route('/user', methods=['POST'])
def save_user():
    body = request.json

    if body.get("username") is None:
        return jsonify("Se debe enviar correctamente el username"), 400
    
    if body.get("name") is None:
        return jsonify("Se debe enviar correctamente el name"), 400
    
    if body.get("email") is None:
        return jsonify("Se debe enviar correctamente el email"), 400
    #ahora vamos a crear el usuario
    user = User()
    user.username = body.get("username") #este es el molde, 
    user.name = body.get("name")
    
    return jsonify("ok"), 200      

@app.route('/people', methods=['GET'])
def all_people():
    people_array = People.query.all()

    if len(people_array) == 0:
        URL_PEOPLE = "https://www.swapi.tech/api/people?page=1&limit=20"
        response = requests.get(URL_PEOPLE)
        data = response.json()

        for item in data["results"]:
            detail_person = requests.get(item["url"])
            detail_data = detail_person.json()
            result = detail_data["result"]
            name = result["properties"]["name"]
            description = result ["description"]

            people = People(name=name, description=description)
            db.session.add(people)

        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            return jsonify(f"Error: {error.args}")
    
    people_array = People.query.all()
 
    serialized_people = [people.serialize() for people in people_array]
    return jsonify(serialized_people), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_people(people_id=None):
    person = People.query.get(people_id)

    if person is None:
        return jsonify("Personaje no encontrado"), 404
    else:
        return jsonify(person.serialize())

@app.route('/planets', methods=['GET'])
def all_planets():
    planet_array = Planet.query.all()

    if len(planet_array) == 0:
        URL_PLANET = "https://www.swapi.tech/api/planets?page=2&limit=20"
        response = requests.get(URL_PLANET)
        data = response.json()

        for item in data["results"]:
            detail_planet = requests.get(item["url"])
            detail_data = detail_planet.json()
            result = detail_data["result"]
            name = result["properties"]["name"]
            description = result ["description"]

            planet = Planet(name=name, description=description)
            db.session.add(planet)

        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            return jsonify(f"Error: {error.args}")
    
    planet_array = Planet.query.all()

    serialized_planet = [planet.serialize() for planet in planet_array]
    return jsonify(serialized_planet), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id=None):
    planet = Planet.query.get(planet_id)

    if planet is None:
        return jsonify("Planeta no encontrado"), 404
    else:
        return jsonify(planet.serialize())
    
@app.route('/users/favorites', methods=['GET'])
def user_favorites():
    body = request.json
    user_id = body.get('user_id')

    if not user_id:
        return jsonify("Se debe enviar correctamente el user_id"), 400

    user = User.query.get(user_id)
    if user is None:
        return jsonify("Usuario no encontrado"), 400

    favorite_people = Favorites_People.query.filter_by(user_id = user_id).all()
    people_serialized = [fav.people_favorites.serialize() for fav in favorite_people]

    favorite_planet = Favorites_Planet.query.filter_by(user_id = user_id).all()
    planet_serialized = [fav.planet_favorites.serialize() for fav in favorite_planet]

    return jsonify({
        "user_id": user_id,
        "favorites": {
            "people": people_serialized,
            "planet": planet_serialized
        }
    }), 200   

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id=None):
    body = request.json
    favorite = Favorites_People(
        user_id = body['user_id'],
        people_id = people_id)
    db.session.add(favorite)
    try:
        db.session.commit()
        return jsonify('Personaje guardado exitosamente'), 201
    except Exception as error:
        db.session.rollback()
        return jsonify(f'error: {error}')
    
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id=None):
    body = request.json
    favorite = Favorites_Planet(
        user_id = body['user_id'],
        planet_id = planet_id)
    db.session.add(favorite)
    try:
        db.session.commit()
        return jsonify('Planeta guardado exitosamente'), 201
    except Exception as error:
        db.session.rollback()
        return jsonify(f'error: {error}')

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    body = request.json
    user_id = body.get('user_id') if body else None

    if not user_id:
        return jsonify("El user_id es inválido"), 400
   
    favorite_delete_people = Favorites_People.query.filter_by(people_id = people_id, user_id = user_id).first()
    
    if favorite_delete_people is None:
        return jsonify('Personaje favorito no encontrado'), 404
    
    try:
        db.session.delete(favorite_delete_people)
        db.session.commit()
        return jsonify('Personaje favorito eliminado exitosamente'), 200
    except Exception as error:
        db.session.rollback()
        return jsonify(f'error: {error}')  

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    body = request.json
    user_id = body.get('user_id') if body else None

    if not user_id:
        return jsonify("El user_id es inválido"), 400
   
    favorite_delete_planet = Favorites_Planet.query.filter_by(planet_id = planet_id, user_id = user_id).first()
    
    if favorite_delete_planet is None:
        return jsonify('Planeta favorito no encontrado'), 404
    
    try:
        db.session.delete(favorite_delete_planet)
        db.session.commit()
        return jsonify('Planeta favorito eliminado exitosamente'), 200
    except Exception as error:
        db.session.rollback()
        return jsonify(f'error: {error}')  

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)



