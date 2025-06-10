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

@app.route('/all-user', methods=['GET'])
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

@app.route('/all-people', methods=['GET'])
def all_people():

    URL_PEOPLE = "https://www.swapi.tech/api/people?page=1&limit=20"
    response = requests.get(URL_PEOPLE)
    data = response.json()
    for item in data["results"]:
        response = requests.get(item["url"])
        item_data = response.json()
        item_data = item_data["result"]

        people = People()
        people.name = item_data["properties"]["name"]
        people.description = item_data["description"]

        db.session.add(people)

    try:
        db.session.commit()
        return jsonify("Personajes guardados"), 201
    except Exception as error:
        db.session.rollback()
        return jsonify(f"Error: {error.args}")

@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_people(people_id=None):
    person = People.query.get(people_id)

    if person is None:
        return jsonify("Personaje no encontrado"), 404
    else:
        return jsonify(person.serialize())

@app.route('/all-planets', methods=['GET'])
def all_planets():

    URL_PLANETS = "https://www.swapi.tech/api/planets?page=1&limit=20"
    response = requests.get(URL_PLANETS)
    data = response.json()
    for element in data["results"]:
        response = requests.get(element["url"])
        element_data = response.json()
        element_data = element_data["result"]

        planet = Planet()
        planet.name = element_data["properties"]["name"]
        planet.description = element_data["description"]

        db.session.add(planet)

    try:
        db.session.commit()
        return jsonify("Planetas guardados"), 201
    except Exception as error:
        db.session.rollback()
        return jsonify(f"Error: {error.args}") 

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id=None):
    planet_elem = Planet.query.get(planet_id)

    if planet_elem is None:
        return jsonify("Elemento planeta no encontrado"), 400    
    else:
        return jsonify(planet_elem.serialize())

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
    user_id = body.get('user_id')

    if not user_id:
        return jsonify("El user_id es inválido"), 400
   
    favorite_delete_people = Favorites_People.query.filter_by(people_id = people_id, user_id = user_id).first()
    
    if favorite_delete_people is None:
        return jsonify('Personaje favorito no encontrado'), 404
    
    db.session.commit()
    try:
        db.session.commit()
        return jsonify('Personaje favorito eliminado exitosamente'), 200
    except Exception as error:
        db.session.rollback()
        return jsonify(f'error: {error}')  

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    body = request.json
    user_id = body.get('user_id')

    if not user_id:
        return jsonify("El user_id es inválido"), 400
   
    favorite_delete_planet = Favorites_Planet.query.filter_by(planet_id = planet_id, user_id = user_id).first()
    
    if favorite_delete_planet is None:
        return jsonify('Planeta favorito no encontrado'), 404
    
    db.session.commit()
    try:
        db.session.commit()
        return jsonify('Planeta favorito eliminado exitosamente'), 200
    except Exception as error:
        db.session.rollback()
        return jsonify(f'error: {error}')  


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


