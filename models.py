from flask_sqlalchemy import SQLAlchemy

#intiate db with no assigment
db = SQLAlchemy()


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genre = db.Column(db.String(), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Show', lazy=True, cascade="all, delete-orphan")
    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'


# add columns to db table venue
Venue.seeking_talent = db.Column(db.Boolean, default=False)
Venue.seeking_description = db.Column(db.String())
Venue.website = db.Column(db.String())


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Show', lazy=True, cascade="all, delete-orphan")
    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'


# add columns to db table venue
Artist.seeking_venue = db.Column(db.Boolean, default=False)
Artist.seeking_description = db.Column(db.String())
Artist.website = db.Column(db.String())

#add show table
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)

    def __repr__(self):
        return f'<Show {self.id} {self.artist_id} {self.venue_id}>'

