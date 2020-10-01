import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

## ROUTES

'''
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    selection = Drink.query.all()
    drinks = [drink.short() for drink in selection]
    return jsonify({
        'succes': True,
        'drinks': drinks
    })


'''
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    selection = Drink.query.all()
    drinks = [drink.long() for drink in selection]
    return jsonify({
        'succes': True,
        'drinks': drinks
    })


'''
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    form = request.get_json()
    recipe = "[" + json.dumps(form.get('recipe')) + "]"
    title = form.get('title')
    drinks = Drink.query.all()
    for dr in drinks:
        if title == dr.title:
            return "drink already exists"
    drink = Drink(title=title, recipe=recipe)
    drink.insert()
    return jsonify({
        'succes': True,
        'drinks': drink.long()
    })


'''
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if not drink:
            abort(404)
    initial_recipe = drink.recipe
    initial_title = drink.title
    form = request.get_json()

    recipe = "[" + json.dumps(form.get('recipe')) + "]"
    title = form.get('title')
    drinks = Drink.query.all()
    for dr in drinks:
        if title == dr.title:
            return "drink already exists"
    if recipe == "[null]":
        recipe = initial_recipe
    if title == None:
        title = initial_title

    drink.title = title
    drink.recipe = recipe
    drink.update()


    return jsonify({
        'succes': True,
        'drinks': [drink.long()]
    })

'''
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if not drink:
            abort(404)
    drink.delete()


    return jsonify({
        'succes': True,
        'delete': drink_id
    })

## Error Handling

# Unprocessable entity

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

# Not found

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

# AuthError

@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
