# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from models import *
from forms import *
from flask_migrate import Migrate

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db.init_app(app)
# create instance migrate for data migration
migrate = Migrate(app, db)


# connection in configuration file added
# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value

    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters[ 'datetime' ] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # num_shows should be aggregated based on number of upcoming shows per venue.
    q_cities = Venue.query.with_entities(Venue.city).order_by('city').all()
    cities = list(q_cities)
    cities = list(dict.fromkeys(cities))
    area = {}
    areas = [ ]
    x = ",(')"
    for city in cities:
        area['city'] = str(city).translate({ord(i): None for i in x})
        state = Venue.query.with_entities(Venue.state).filter_by(city=city).first()
        area['state'] = str(state).translate({ord(i): None for i in x})
        venue_q = Venue.query.with_entities(Venue.id,Venue.name).filter_by(city=city)
        area['venues'] = venue_q
        area_c = area. copy()
        areas.append(area_c)
    return render_template('pages/venues.html', areas=areas);


@app.route('/venues/search', methods=[ 'POST' ])
def search_venues():

    search_term = '%' + request.form.get('search_term', '') + '%'
    data = Venue.query.filter(Venue.name.ilike(search_term))
    count= Venue.query.filter(Venue.name.ilike(search_term)).count()
    response = {
        "count": count,
        "data": data
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.filter_by(id=venue_id).first()
    #venue_shows
    venue_shows = Show.query.filter_by(venue_id=venue_id).all()
    past_shows = []
    upcoming_shows = []
    past_shows_count = 0
    upcoming_shows_count = 0

    for venue_show in venue_shows:
        artist_data = Artist.query.get(venue_show.artist_id)
        if venue_show.start_time < datetime.now():
            past_shows_count += 1
            past_show = {
                "artist_id": artist_data.id,
                "artist_name": artist_data.name,
                "artist_image_link": artist_data.image_link,
                "start_time": venue_show.start_time
            }
            past_shows.append(past_show.copy())
        else:
            upcoming_shows_count += 1
            upcoming_show = {
                "artist_id": artist_data.id,
                "artist_name": artist_data.name,
                "artist_image_link": artist_data.image_link,
                "start_time": venue_show.start_time
            }
            upcoming_shows.append(upcoming_show.copy())
    data = {
        'id': venue.id,
        'name': venue.name,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'genres': venue.genre.split(','),
        'image_link': venue.image_link,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'past_shows': past_shows.copy(),
        'upcoming_shows': upcoming_shows.copy(),
        'past_shows_count': past_shows_count,
        'upcoming_shows_count': upcoming_shows_count
    }

    return render_template('pages/show_venue.html', venue=data)



#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=[ 'GET' ])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=[ 'POST' ])
def create_venue_submission():
    error = False
    data = ''
    try:

        genres = ','.join(request.form.getlist('genres'))
        seeking_talent_str = request.form.get('seeking_talent', '')
        if len(seeking_talent_str) > 0:
            check = True
        else:
            check = False

        venue = Venue(
            name=request.form[ 'name' ],
            city=request.form[ 'city' ],
            state=request.form[ 'state' ],
            address=request.form[ 'address' ],
            phone=request.form[ 'phone' ],
            image_link=request.form[ 'image_link' ],
            facebook_link=request.form[ 'facebook_link' ],
            genre=genres,
            seeking_talent=check,
            seeking_description=request.form[ 'seeking_description' ],
            website=request.form[ 'website' ]

        )
        data = request.form['name']
        db.session.add(venue)
        db.session.commit()

    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())


    finally:
        db.session.close()

    if error:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + data + ' could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Venue ' + data + ' was successfully listed!')

    return render_template('pages/venues.html', area=Venue.query.order_by('id').all())


@app.route('/venues/<venue_id>', methods=[ 'DELETE' ])
def delete_venue(venue_id):
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    data = {}
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        data[ 'description' ] = "Venue is deleted successfully"
        data[ 'id' ] = venue_id
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())


    finally:
        db.session.close()

    if error:
        abort(400)
    else:
        return render_template('pages/venues.html', area=Venue.query.order_by('id').all())
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.order_by('id').all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=[ 'POST' ])
def search_artists():

    search_term = '%' + request.form.get('search_term', '') + '%'
    data = Artist.query.filter(Artist.name.ilike(search_term))
    count = Artist.query.filter(Artist.name.ilike(search_term)).count()
    response = {
        "count": count,
        "data": data
    }

    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the Artist page with the given artist_id
    artist = Artist.query.filter_by(id=artist_id).first()
    # Artist_shows
    artist_shows = Show.query.filter_by(artist_id=artist_id).all()
    past_shows = [ ]
    upcoming_shows = [ ]
    past_shows_count = 0
    upcoming_shows_count = 0

    for artist_show in artist_shows:
        venue_data = Venue.query.get(artist_show.venue_id)
        if artist_show.start_time < datetime.now():
            past_shows_count += 1
            past_show = {
                "venue_id": venue_data.id,
                "venue_name": venue_data.name,
                "venue_image_link": venue_data.image_link,
                "start_time": artist_show.start_time
            }
            past_shows.append(past_show.copy())
        else:
            upcoming_shows_count += 1
            upcoming_show = {
                "venue_id": venue_data.id,
                "venue_name": venue_data.name,
                "venue_image_link": venue_data.image_link,
                "start_time": artist_show.start_time
            }
            upcoming_shows.append(upcoming_show.copy())

    data = {
        'id': artist.id,
        'name': artist.name,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'genres': artist.genres.split(','),
        'image_link': artist.image_link,
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'past_shows': past_shows.copy(),
        'upcoming_shows': upcoming_shows.copy(),
        'past_shows_count': past_shows_count,
        'upcoming_shows_count': upcoming_shows_count
    }

    return render_template('pages/show_artist.html', artist=data)

    '''data1 = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": [ "Rock n Roll" ],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "past_shows": [ {
            "venue_id": 1,
            "venue_name": "The Musical Hop",
            "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
            "start_time": "2019-05-21T21:30:00.000Z"
        } ],
        "upcoming_shows": [ ],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data2 = {
        "id": 5,
        "name": "Matt Quevedo",
        "genres": [ "Jazz" ],
        "city": "New York",
        "state": "NY",
        "phone": "300-400-5000",
        "facebook_link": "https://www.facebook.com/mattquevedo923251523",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "past_shows": [ {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2019-06-15T23:00:00.000Z"
        } ],
        "upcoming_shows": [ ],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data3 = {
        "id": 6,
        "name": "The Wild Sax Band",
        "genres": [ "Jazz", "Classical" ],
        "city": "San Francisco",
        "state": "CA",
        "phone": "432-325-5432",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "past_shows": [ ],
        "upcoming_shows": [ {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2035-04-01T20:00:00.000Z"
        }, {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2035-04-08T20:00:00.000Z"
        }, {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2035-04-15T20:00:00.000Z"
        } ],
        "past_shows_count": 0,
        "upcoming_shows_count": 3,
    }
    data = list(filter(lambda d: d[ 'id' ] == artist_id, [ data1, data2, data3 ]))[ 0 ]
    return render_template('pages/show_artist.html', artist=data)'''


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=[ 'GET' ])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter_by(id=artist_id).first()
    '''{
        "id": 4,
        "name": "Guns N Petals",
        "genres": [ "Rock n Roll" ],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }'''
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=[ 'POST' ])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=[ 'GET' ])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": [ "Jazz", "Reggae", "Swing", "Classical", "Folk" ],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=[ 'POST' ])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=[ 'GET' ])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=[ 'POST' ])
def create_artist_submission():
    # called upon submitting the new artist listing form
    error = False
    data = ''
    try:

        genres = ','.join(request.form.getlist('genres'))
        seeking_talent_str = request.form.get('seeking_venue', '')
        if len(seeking_talent_str) > 0:
            check = True
        else:
            check = False

        artist = Artist(
            name=request.form[ 'name' ],
            city=request.form[ 'city' ],
            state=request.form[ 'state' ],
            phone=request.form[ 'phone' ],
            image_link=request.form[ 'image_link' ],
            facebook_link=request.form[ 'facebook_link' ],
            genres=genres,
            seeking_venue=check,
            seeking_description=request.form[ 'seeking_description' ],
            website=request.form[ 'website' ]

        )
        data = request.form[ 'name' ]
        db.session.add(artist)
        db.session.commit()

    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())


    finally:
        db.session.close()

    if error:
        # on unsuccessful db insert, flash an error.
        flash('An error occurred. Artist ' + data + ' could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Artist ' + data + ' was successfully listed!')

    return render_template('pages/venues.html', area=Venue.query.order_by('id').all())


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    x = ",(')"
    data_show = Show.query.order_by('id').all()
    shows = []
    for data in data_show:
        ven_id = data.venue_id
        ven_query = Venue.query.with_entities(Venue.name).filter_by(id=ven_id).first()
        venue_name = str(ven_query).translate({ord(i): None for i in x})
        art_id = data.artist_id
        art_query = Artist.query.with_entities(Artist.name, Artist.image_link).filter_by(id=art_id).first()
        artist_name = str(art_query.name).translate({ord(i): None for i in x})
        artist_image_link = art_query.image_link
        start_time = data.start_time
        show = {
            "venue_id": ven_id,
            "venue_name": venue_name,
            "artist_id": art_id,
            "artist_name": artist_name,
            "artist_image_link": artist_image_link,
            "start_time": start_time
        }
        shows.append(show.copy())
    return render_template('pages/shows.html', shows=shows)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=[ 'POST' ])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    error = False
    try:
        if Artist.query.get(request.form[ 'artist_id' ]):
            if Venue.query.get(request.form[ 'venue_id' ]):
                show = Show(
                    artist_id=request.form[ 'artist_id' ],
                    venue_id=request.form[ 'venue_id' ],
                    start_time=request.form[ 'start_time' ]
                )
        else:
            error = "artist_id or venue_id doesn't exist"

        db.session.add(show)
        db.session.commit()

    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())


    finally:
        db.session.close()

    if error:
        # on unsuccessful db insert, flash an error.
        flash('An error occurred. Show could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Show was successfully listed!')

    return render_template('pages/shows.html', shows=Show.query.order_by('id').all())



@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
