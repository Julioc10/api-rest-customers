from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_api import status
from flask_cors import CORS
import pymysql
from flask import request, jsonify
from marshmallow import Schema, fields, validate
import os
from dotenv import load_dotenv
import uuid
import logging

logging.basicConfig(level=logging.DEBUG)

pymysql.install_as_MySQLdb()
load_dotenv()

# db = SQLAlchemy()
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('MYSQL_URL')
# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# db.init_app(app)
# CORS(app)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
db = SQLAlchemy(app)

class Customers(db.Model):
    guid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), nullable=False)
    cpf = db.Column(db.String(14), nullable=False)
    date_of_birth = db.Column(db.Date(), nullable=False)
    emails = db.Column(db.String(50))

with app.app_context():
    db.create_all()

def remover(obj):
    db.session.delete(obj)
    db.session.commit()


class CustomerSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    cpf = fields.String(required=True, validate=validate.Length(min=1))
    date_of_birth = fields.String(required=True, validate=validate.Length(min=1))
    emails = fields.String(required=False, validate=validate.Length(min=1))

@app.route("/", methods=["GET"])
def clientes():
    customers = Customers.query.all()
    return jsonify([{
                    "guid": customers.guid,
                    "name": customers.name,
                    "cpf": customers.cpf,
                    "date_of_birth": customers.date_of_birth,
                    "emails": customers.emails,
                    } for customers in customers]), status.HTTP_200_OK


@app.route("/", methods=["POST"])
def criar_cliente():
    data = request.get_json()
    schema = CustomerSchema()
    errors = schema.validate(data)

    if errors:
        return jsonify({"mensagem": "Dados inválidos", "erros": errors}), status.HTTP_400_BAD_REQUEST

    customers = Customers(
        name=data.get('name'),
        cpf=data.get('cpf'),
        date_of_birth=data.get('date_of_birth'),
        emails=data.get('emails'),
    )

    db.session.add(customers)
    db.session.commit()

    return jsonify({"mensagem": "Cliente criado com sucesso!"}), status.HTTP_201_CREATED


@app.route("/<guid>", methods=["GET"])
def achar_cliente(guid):
    customers = Customers.query.get(guid)

    if customers is None:
        return jsonify({"mensagem": "Cliente não encontrado"}), status.HTTP_404_NOT_FOUND

    return jsonify({
        "guid": customers.guid,
        "name": customers.name,
        "cpf": customers.cpf,
        "date_of_birth": customers.date_of_birth,
        "emails": customers.emails
    })

@app.route("/<guid>", methods=["PUT"])
def editar_cliente(guid):
    customers = Customers.query.get(guid)

    if customers is None:
        return jsonify({"mensagem": "Cliente não encontrado"}), status.HTTP_404_NOT_FOUND

    form = Customers(request.json)
    if form.validate():
        customers.name = form.name.dados
        customers.cpf = form.cpf.dados
        customers.date_of_birth = form.date_of_birth.dados
        customers.emails = form.emails.dados
        db.session.commit()

        return jsonify({"mensagem": "Cliente editado com sucesso!"}), status.HTTP_200_OK
    else:
        return jsonify({"mensagem": "Dados inválidos", "erros": form.errors}), status.HTTP_400_BAD_REQUEST


@app.route("/<guid>", methods=["DELETE"])
def deletar_cliente(guid):
    customers = Customers.query.get(guid)

    if customers is None:
        return jsonify({"mensagem": "Cliente não encontrado"}), status.HTTP_404_NOT_FOUND

    db.session.delete(customers)
    db.session.commit()

    return jsonify({"mensagem": "Cliente removido com sucesso!"}), status.HTTP_200_OK

logging.debug("Mensagem de log aqui.")


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8080)
