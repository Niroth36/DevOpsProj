from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:3663@mysql/appdb'     # 'sqlite:///test.db'
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    pet = db.relationship("Pet", backref="user")

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable=False)
    pet_type = db.Column(db.String(200), nullable=False)
    date_of_birth = db.Column(db.DateTime, default=datetime.utcnow)
    owner = db.Column(db.Integer, db.ForeignKey(Users.id))

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable=False)
    exam_type = db.Column(db.String(200), nullable=False)
    date_of_exam = db.Column(db.DateTime, default=datetime.utcnow)
    pet_exam = db.Column(db.Integer, db.ForeignKey(Pet.id))

@app.before_first_request
def before_first_request():
    db.create_all()
 
 
@app.route("/")
def main():
    users = getallusers()
    return render_template("index.html", users=json.loads(users))

@app.route("/insert_user", methods=['POST'])
def insert_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        role = 'user'
        new_user = Users(first_name=first_name, last_name=last_name, email=email, role=role)

        db.session.add(new_user)
        db.session.commit()
    return redirect('/')

def getallusers():
    users = Users.query.filter_by(role='user').all()
    results = []
    for user in users:
        results.append({'id': user.id,'first_name': user.first_name,'last_name': user.last_name, 'email': user.email, 'role': user.role })
    return json.dumps(results)

@app.route('/allusers')
def allusers():
    return getallusers()

@app.route('/adduser')
def adduser():
    return render_template('adduser.html')

@app.route("/insert_pet", methods=['POST'])
def insert_pet():
    if request.method == 'POST':
        name = request.form['name']
        pet_type = request.form['pet_type']
        owner = int(request.form['owner'])
        date_of_birth = datetime.strptime(request.form['date_of_birth'], "%Y-%m-%d")
        new_pet = Pet(name=name, pet_type=pet_type, owner=owner, date_of_birth=date_of_birth)

        db.session.add(new_pet)
        db.session.commit()
    return redirect('/mypets/' + str(owner))

@app.route('/addpet/<user_id>')
def addpet(user_id):
    return render_template('addpet.html', user_id=user_id)

@app.route('/mypets/<user_id>')
def mypets(user_id):
    pets = getmypets(user_id)
    first_name = Users.query.filter_by(id=user_id).first().first_name
    return render_template("pets.html", pets=json.loads(pets), user_id=user_id, first_name=first_name)

def getmypets(user_id):
    pets = Pet.query.filter_by(owner=user_id).all()
    results = []
    for pet in pets:
        results.append({'id': pet.id,'name': pet.name, 'pet_type': pet.pet_type, 'date_of_birth': pet.date_of_birth.strftime("%m/%d/%Y") })
    return json.dumps(results)

@app.route('/allpets')
def allpets():
    pets = Pet.query.all()
    results = []
    for pet in pets:
        results.append({'id': pet.id,'name': pet.name, 'pet_type': pet.pet_type, 'owner': pet.owner })
    return json.dumps(results)

@app.route("/insert_exam", methods=['POST'])
def insert_exam():
    if request.method == 'POST':
        name = request.form['name']
        exam_type = request.form['exam_type']
        pet_exam = int(request.form['pet_exam'])
        date_of_exam = datetime.strptime(request.form['date_of_exam'], "%Y-%m-%d")
        new_exam = Exam(name=name, exam_type=exam_type, pet_exam=pet_exam, date_of_exam=date_of_exam)

        db.session.add(new_exam)
        db.session.commit()
    return redirect('/myexams/' + str(pet_exam))

@app.route('/addexam/<pet_id>')
def addexam(pet_id):
    return render_template('addexam.html', pet_id=pet_id)

@app.route('/myexams/<pet_id>')
def myexams(pet_id):
    owner = Pet.query.filter_by(id=pet_id).first().owner
    exams = getmyexams(pet_id)
    name = Pet.query.filter_by(id=pet_id).first().name
    return render_template("exams.html", exams=json.loads(exams), pet_id=pet_id, owner=owner, name=name)

def getmyexams(pet_id):
    exams = Exam.query.filter_by(pet_exam=pet_id).all()
    results = []
    for exam in exams:
        results.append({'id': exam.id,'name': exam.name, 'exam_type': exam.exam_type, 'date_of_exam': exam.date_of_exam.strftime("%m/%d/%Y")})
    return json.dumps(results)

@app.route('/deletepet/<pet_id>')
def deletepet(pet_id):
    pet = Pet.query.filter_by(id=pet_id).first()
    owner = Pet.query.filter_by(id=pet_id).first().owner
    
    try:
        db.session.delete(pet)
        db.session.commit()
        return redirect('/mypets/' + str(owner))
    except:
        return 'There was a problem deleting that pet'

@app.route('/deleteuser/<user_id>')
def deleteuser(user_id):
    user = Users.query.filter_by(id=user_id).first()
    
    try:
        db.session.delete(user)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that user'

@app.route('/deleteexam/<exam_id>')
def deleteexam(exam_id):
    exam = Exam.query.filter_by(id=exam_id).first()
    pet_exam = Exam.query.filter_by(id=exam_id).first().pet_exam

    try:
        db.session.delete(exam)
        db.session.commit()
        return redirect('/myexams/' + str(pet_exam))
    except:
        return 'There was a problem deleting that exam'
    

@app.route('/allexam')
def allexam():
    exams = Exam.query.all()
    results = []
    for exam in exams:
        results.append({'id': exam.id,'name': exam.name, 'exam_type': exam.exam_type, 'pet_exam': exam.pet_exam })
    return json.dumps(results)    

@app.route('/pet_by_user/<id>')
def pet_by_user(id):
    user = Users.query.filter_by(id=id).one()
    pets = Pet.query.filter_by(owner=id).all()
    results = []
    for pet in pets:
        exam_list = []
        exams = Exam.query.filter_by(pet_exam=pet.id).all()
        for exam in exams:
            exam_list.append({'id': exam.id,'name': exam.name, 'exam_type': exam.exam_type})
        results.append({'id': pet.id,'name': pet.name, 'exams': exam_list})
        
    
    data = {'id': user.id,'first_name': user.first_name,'last_name': user.last_name, 'email': user.email, 'pets':results}

    return json.dumps(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
