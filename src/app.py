from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from models.User import User
from models.Skill import Skill
from mongoengine import connect as db
import bcrypt
import jwt
from dotenv import load_dotenv
import os


# intializations
load_dotenv()

app = Flask(__name__)

DB_URI = os.getenv("MONGO_URI")
db(host=DB_URI)

# middlewares
CORS(app)

# secret key for jwt
secret_key = 'secretrandom'


# get single object
def get_user_by_email(email):
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return False


def get_skill_by_name(name):
    try:
        return Skill.objects.get(name=name)
    except Skill.DoesNotExist:
        return False

# decode token


def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, secret_key)
        return payload['_id']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'


# routes

# register user
@app.route('/api/user/register', methods=['POST'])
def signup_user():
    new_user = User(
        full_name=request.json['full_name'],
        country=request.json['country'],
        username=request.json['username'],
        email=request.json['email'],
        skills=[],
        password=request.json['password']
    )

    user = get_user_by_email(new_user.email)

    # checking if user already exist
    if user:
        return Response(response=str({"message": 'email already exist.'}), status=401)

    # encrypting password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(
        new_user.password.encode('utf8'), salt).decode('utf8')

    new_user.password = str(hashed)
    new_user.save()

    token = jwt.encode({"_id": str(new_user.id)}, secret_key)

    res = Response(str(new_user.id))
    res.headers['token'] = token

    return res

# login user


@app.route('/api/user/login', methods=['POST'])
def signin_user():
    user = get_user_by_email(request.json['email'])

    if not user:
        return Response(response=str({"message": 'Email not found.'}), status=401)

    match = bcrypt.checkpw(
        request.json['password'].encode('utf8'), user.password.encode('utf8'))

    if not match:
        return Response(response=str({"message": 'Invalid password.'}), status=401)

    token = jwt.encode({"_id": str(user.id)}, secret_key)

    res = Response(str(user.id))
    res.headers['token'] = token

    return res


# create skills

@app.route('/api/skills/register', methods=['POST'])
def create_skill():
    token = request.headers.get('token')

    if not token:
        return Response(response=str({"message": 'You need to login first!'}), status=401)

    # creating and saving skill
    new_skill = Skill(name=request.json["name"].lower())

    # checking if skill already exist
    skill = get_skill_by_name(request.json["name"].lower())

    if skill:
        return Response(response=str({"message": 'Skill already exist.'}), status=401)

    new_skill.save()

    return Response(response=str({"name": new_skill.name}), status=200)


# assign skills
@app.route('/api/user/skills', methods=['POST'])
def assign_skill():
    token = request.headers.get('token')

    if not token:
        return Response(response=str({"message": 'You need to login first!'}), status=401)

    userId = decode_auth_token(token)

    user = User.objects.get(id=userId)
    skill = get_skill_by_name(request.json["skill"])

    if not skill:
        Response(response=str({"message": 'Skill not found.'}), status=404)

    # verifiyng if user already have the skill
    for skill_id in user.skills:
        db_skill = Skill.objects.get(id=skill_id)

        if request.json['skill'] == db_skill.name:
            return Response(response=str(
                {"message": 'You already have this skill.'}), status=400)
        else:
            pass

    # pushing the skill into user
    user.update(push__skills=str(skill.id))

    return Response(response=str({"message": "Skill added."}), status=200)


# user profile
@app.route('/api/user/profile', methods=['GET'])
def profile_user():
    token = request.headers.get('token')

    if not token:
        return Response(response=str({"message": 'You need to login first!'}), status=401)

    userId = decode_auth_token(token)

    user = User.objects.get(id=userId)

    user_skills = []

    # getting skill's name
    for skill in user.skills:
        db_skill = Skill.objects.get(id=skill)

        user_skills.append(db_skill.name)

    sendUser = {
        "_id": str(user.id),
        "full_name": user.full_name,
        "country": user.country,
        "username": user.username,
        "skills": user_skills,
        "email": user.email,
        "created_at": str(user.created_at),
    }

    return jsonify(sendUser)


if __name__ == "__main__":
    app.run(port=3000, debug=True)
