import uuid

import pydantic as pydantic
from sqlalchemy.dialects.postgresql import UUID
from flask import Flask, jsonify, request
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from flask.views import MethodView
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from typing import Union


app = Flask('app')

engine = create_engine('postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/flask_netology')
Base = declarative_base()
Session = sessionmaker(bind=engine)


class HTTPError(Exception):

    def __init__(self, status_code: int, message: Union[str, dict, list]):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HTTPError)
def handle_error(error):
    response = jsonify({
        'message': error.message
    })
    response.status_code = error.status_code
    return response

def validate(input_model, output_model):
    try:
        return output_model(**input_model).dict()
    except pydantic.error_wrappers.ValidationError as er:
        raise HTTPError(400, er.errors())

class CreateAdvertModel(pydantic.BaseModel):
    header: str
    description: str

class Advert(Base):
    __tablename__ = 'adverts'
    id = Column(Integer, primary_key=True)
    header = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))

    def create(cls, session: Session, header: str, description: str):
        new_advert = Advert(header=header, description=description)
        session.add(new_advert)
        return new_advert

    def to_dict(self):
        return {
            'header': self.header,
            'description': self.description,
            'user_id': self.user_id,
            'id': self.id,
        }


Base.metadata.create_all(engine)

class AdvertView(MethodView):

    def get(self, adv_id: str):
        with Session() as session:
            my_advert = session.query(Advert).get(adv_id)
            return jsonify(my_advert.to_dict())

    def post(self):
        with Session() as session:
            new_advert = Advert.create_advert(session, **validate(request.json, CreateAdvertModel))
            session.add(new_advert)
            return jsonify(new_advert.to_dict())

    def delete(self, adv_id: int):
        with Session() as session:
            my_advert = session.query(Advert).get(adv_id)
            session.delete(my_advert)
            session.commit()
            return {'204': 'no content'}


app.add_url_rule('/advert/', methods=['POST'], view_func=AdvertView.as_view('advert_create'))
app.add_url_rule('/advert/<int:adv_id>', view_func=AdvertView.as_view('get_advert'), methods=[
    'GET', 'DELETE'])
app.run()
