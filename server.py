from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
guide_trip = db.Table('guide_trip',
    db.Column('guide_id', db.Integer, db.ForeignKey('guide.id')),
    db.Column('trip_id', db.Integer, db.ForeignKey('trip.id'))
)

class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Integer())
    id_participant = db.Column(db.Integer())
    id_trip = db.Column(db.Integer())
    def __init__(self,text, id_participant,id_trip):
        self.text = text
        self.id_participant = id_participant
        self.id_trip = id_trip


class Guide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guide_first_name = db.Column(db.String(30))
    guide_second_name = db.Column(db.String(30))
    guide_rating = db.Column(db.Integer())
    company_id = db.Column(db.Integer())
    following = db.relationship('Trip', secondary=guide_trip, backref='organizers')
    def __init__(self, first_name, last_name,guide_rating,company_id) -> None:
        self.guide_first_name = first_name
        self.guide_second_name = last_name
        self.guide_rating = guide_rating
        self.company_id = company_id


participant_trip = db.Table('participant_trip',
    db.Column('participant_id', db.Integer, db.ForeignKey('participant.id')),
    db.Column('trip_id', db.Integer, db.ForeignKey('trip.id'))
)


class Participant(db.Model):
    __tablename__ = 'participant'
    id = db.Column(db.Integer, primary_key=True)
    participant_first_name = db.Column(db.String(30))
    participant_second_name = db.Column(db.String(30))
    participant_health_doc_id = db.Column(db.Integer, db.ForeignKey('health.id'))
    following = db.relationship('Trip', secondary=participant_trip, backref='participants')
    def __init__(self, participant_first_name, participant_second_name) -> None:
        self.participant_first_name = participant_first_name
        self.participant_second_name = participant_second_name

class Track(db.Model):
    __tablename__ = 'track'
    id = db.Column(db.Integer, primary_key=True)
    track_difficulty = db.Column(db.Integer())
    track_duration = db.Column(db.String(30))
    track_description = db.Column(db.String(300))
    trips = db.relationship('Trip', backref='track')
    def __init__(self, track_difficulty, track_duration,track_description) -> None:
        self.track_difficulty = track_difficulty
        self.track_duration = track_duration
        self.track_description = track_description

class Trip(db.Model):
    __tablename__ = 'trip'
    id = db.Column(db.Integer, primary_key=True)
    trip_description = db.Column(db.String(300))
    trip_start_date = db.Column(db.String(30))
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'))
    def __init__(self, trip_description, trip_start_date) -> None:
        self.trip_description = trip_description
        self.trip_start_date = trip_start_date

class HealthDocument(db.Model):
    __tablename__ = 'health'
    id = db.Column(db.Integer, primary_key=True)
    participant_age = db.Column(db.Integer())
    participant_health_condition = db.Column(db.String(300))
    participant = db.relationship('Participant', uselist=False, backref='health_document')
    def __init__(self, participant_age, participant_health_condition) -> None:
        self.participant_age = participant_age
        self.participant_health_condition = participant_health_condition

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(30))
    def __init__(self, company_name) -> None:
        self.company_name = company_name

def create_companies():
    data = ["MoveOn", "YourTour"]
    for company in data:
        landmark = Company(company)
        db.session.add(landmark)
    db.session.commit()
def create_tracks():
    data = [[3,"3 days", "Forest track"],[1,"2 days", "Seaside track"]]
    for company in data:
        track = Track(*company)
        db.session.add(track)
    db.session.commit()

with app.app_context():
    db.create_all()
    create_companies()
    create_tracks()
@app.route('/', methods = ['GET'])
def main_page():
    return render_template("index.html")


@app.route('/guide_reg', methods = ['GET'])
def guide_reg_g():
    res = Guide.query.all()
    return render_template("guide_create.html", guides = res)

@app.route('/guide_reg', methods = ['POST'])
def guide_reg_p():
    first_name = request.form.get('firstName')
    # track = request.form.get('firstName')
    last_name = request.form.get('lastName')
    rating = request.form.get('rating')
    company_id = request.form.get('companyId')
    guide = Guide(first_name,last_name,rating,int(company_id)-1)
    db.session.add(guide)
    db.session.commit()
    res = Guide.query.all()
    return render_template("guide_create.html", flag = 1 , guides = res)

@app.route('/participant_reg', methods = ['GET'])
def participant_reg_g():
    res = Participant.query.all()
    return render_template("participant_create.html", participants = res)

@app.route('/participant_reg', methods = ['POST'])
def participant_reg_p():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    age = request.form.get('age')
    hc = request.form.get('health_condition')
    hd = HealthDocument(age,hc)
    participant = Participant(first_name,last_name)
    participant.health_document = hd
    db.session.add(participant)
    db.session.add(hd)
    db.session.commit()
    res = Participant.query.all()
    return render_template("participant_create.html", participants = res, flag = 1 )

@app.route('/create_trip', methods = ['GET'])
def sendalp():
    res = Trip.query.all()
    res1 = Guide.query.all()
    return render_template("create_application.html", participants = res,guides = res1)
@app.route('/create_trip', methods = ['POST'])
def sendalp12():
    date = request.form.get('date')
    guide_id = request.form.get('guide_id')
    desc = request.form.get('desc')
    trackId = request.form.get('trackId')
    res = db.session.query(Track).get(int(trackId))
    guide = db.session.query(Guide).get(int(guide_id))
    trip = Trip(desc,date)
    trip.organizers.append(guide)
    trip.track = res
    db.session.add(trip)
    db.session.commit()
    res = Trip.query.all()
    res1 = Guide.query.all()
    return render_template("create_application.html", participants = res, flag = 1 ,guides = res1)

@app.route('/send_application', methods = ['GET'])
def sendalp1():
    res = Participant.query.all()
    res1 = Trip.query.all()
    return render_template("send_aplication.html", participants = res,trips = res1)
@app.route('/send_application', methods = ['POST'])
def sendalp13():
    trip = request.form.get('trip_id')
    part = request.form.get('participant_id')
   
    res1 = db.session.query(Trip).get(int(trip))
    res2 = db.session.query(Participant).get(int(part))

    res1.participants.append(res2)
    res = Participant.query.all()
    res1 = Trip.query.all()
    db.session.commit()
    return render_template("send_aplication.html", participants = res,trips = res1)

@app.route('/review_health_doc', methods = ['GET'])
def doc_review():

    data = []
    res = Trip.query.all()
    for i in res:
        for j in i.participants:
            print(j)
            data.append({"doc":j.health_document,"trip":i.id})
    print(data)
    return render_template("hd_review.html", hd = data)
@app.route('/decline', methods = ['POST'])
def doc_review_accept():
    trip = request.form.get('trip_id')
    hd_id = request.form.get('hd_id')
    trip = db.session.query(Trip).get(int(trip))
    hd = db.session.query(HealthDocument).get(int(hd_id))
    participant = db.session.query(Participant).get(hd.participant.id)
    trip.participants.remove(participant)
    db.session.commit()
    data = []
    res = Trip.query.all()
    for i in res:
        for j in i.participants:
            print(j)
            data.append({"doc":j.health_document,"trip":i.id})
    print(data)
    return render_template("hd_review.html", hd = data)

@app.route('/accept', methods = ['POST'])
def doc_review_accept1():
    trip_id = request.form.get('trip_id')
    hd_id = request.form.get('hd_id')
    trip = db.session.query(Trip).get(int(trip_id))
    hd = db.session.query(HealthDocument).get(int(hd_id))
    participant = db.session.query(Participant).get(hd.participant.id)
    trip.participants.remove(participant)
    inv = Invitation("Welcome to your new trip",participant.id,trip_id) 
    db.session.add(inv)
    db.session.commit()
    data = []
    res = Trip.query.all()
    for i in res:
        for j in i.participants:
            print(j)
            data.append({"doc":j.health_document,"trip":i.id})
    print(data)
    return render_template("hd_review.html", hd = data)

@app.route('/review_invitation', methods = ['GET'])
def doc_review_accept11():
    res = Invitation.query.all()
    return render_template("invites.html", inv = res)
@app.route('/sql_query_1', methods = ['GET'])
def get_tracks_with_high_difficulty():
    query = text("SELECT * FROM health WHERE participant_age > 18;")
    result = db.session.execute(query)
    track = [{'id': row[0], 'age': row[1], 'health condition': row[2]} for row in result]
    return jsonify(track)

@app.route('/sql_query_2', methods = ['GET'])
def participants_in_trips():
    sql_query = db.text("""
        SELECT DISTINCT p.*
        FROM participant p
        JOIN invitation i ON p.id = i.id_participant
    """)
    print(sql_query)
    result = db.session.execute(sql_query)
    participants = [{'id': row[0], 'First Name': row[1], 'Second Name': row[2]} for row in result]
    return jsonify(participants)

@app.route('/sql_query_3', methods = ['GET'])
def participants_in_trips3():
    sql_query = db.text("""
        SELECT *
        FROM guide
        WHERE guide_rating = (
            SELECT MAX(guide_rating)
            FROM guide
        )
    """)
    print(sql_query)
    result = db.session.execute(sql_query)

    participants = [{'id': row[0], 'First Name': row[1], 'Second Name': row[2], "Rating":row[3]} for row in result]
    return jsonify(participants)


if __name__ == "__main__":
    app.run(port=4000,debug=True) 