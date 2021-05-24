from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Attraction(db.Model):
    __tablename__ = 'attraction'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    transport = db.Column(db.Text)
    mrt = db.Column(db.String(255))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    images = db.Column(db.JSON)
    booking = db.relationship('Booking', backref='booking_attraction')
    
    def as_dict(self):
        return{c.name: getattr(self, c.name) for c in self.__table__.columns}

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    db.Index('email_pwd_index', 'email', 'password')
    booking = db.relationship('Booking', backref='orderer')

    def as_dict(self):
        return{c.name: getattr(self, c.name) for c in self.__table__.columns}

class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    attraction_id = db.Column(db.Integer, db.ForeignKey('attraction.id'))
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Enum('morning', 'afternoon'), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    order_number = db.Column(db.String(255))
    rec_trade_id = db.Column(db.String(255))
    pay = db.Column(db.Boolean, default=False)
    refund = db.Column(db.Boolean, default=False)

    def as_dict(self):
        return{c.name: getattr(self, c.name) for c in self.__table__.columns}