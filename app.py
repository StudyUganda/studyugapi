from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
import json
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

# User Class/Model
class User(db.Model):
  __tablename__ = 'User'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(100), unique=True)
  email = db.Column(db.String(200), unique = True)
  district = db.Column(db.String(200))
  phone = db.Column(db.String(20))
  password = db.Column(db.String(30))

  def __init__(self, username, email, district, phone, password):
    self.username = username
    self.email = email
    self.district = district
    self.phone = phone
    self.password = password

# User Schema
class UserSchema(ma.Schema):
  class Meta:
    fields = ('id', 'username', 'email', 'district', 'phone' , 'password')

# Init schema
user_schema = UserSchema(strict=True)
users_schema = UserSchema(many=True, strict=True)


# Get All Users
@app.route('/users', methods=['GET'])
def get_users():
  all_users = User.query.all()
  result = users_schema.dump(all_users)
  return jsonify(result.data)

# Get Single Users
@app.route('/user/<email>', methods=['GET'])
def get_user(email):
  user = User.query.get(email)
  return user_schema.jsonify(user)

# Update a User
@app.route('/user/<email>', methods=['PUT'])
def update_user(email):
  user = User.query.get(email)
  username = request.json['username']
  email = request.json['email']
  district = request.json['district']
  phone = request.json['phone']

  user.username = username
  user.email = email
  user.district = district
  user.phone = phone

  db.session.commit()

  return user_schema.jsonify(user)

# Delete User
@app.route('/user/<email>', methods=['DELETE'])
def delete_user(email):
  user = User.query.get(email)
  db.session.delete(user)
  db.session.commit()

  return user_schema.jsonify(user)
db.create_all()


@app.route('/api/v2/login', methods=['POST'])
def login():
  #body= request.body.json()
  email = request.json['email']
  password = request.json ['password']
  exists = db.session.query(User.email).filter_by(email=email).first()

  if exists is not None:
    exists2 = db.session.query(User.password).filter_by(password=password).first()
    if exists2 is not None:
      username = db.session.query(User.username).filter_by(email=email).first()
      print(username)
      username= list(username)
      return json.dumps({ "message":"sucessful",
      "data" : username})
    else:
        return jsonify('unsucessful', "wrong password")
  else:
    return jsonify('unsucessful', "wrong email")

# Create a User
@app.route('/api/v2/signup', methods=['POST'])
def add_user():
  username = request.json['username']
  email = request.json['email']
  district = request.json['district']
  phone = request.json['phone']
  password = request.json['password']
  exists = db.session.query(User.email).filter_by(email=email).first()
  if exists is not None:
    return jsonify('unsucessful',"user email alraedy taken")
  else:
    new_user = User(username, email, district, phone , password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify('successful' ,"user account formed")
      


# Run Server
if __name__ == '__main__':
  app.run()
