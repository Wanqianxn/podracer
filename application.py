import os, re
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_session import Session
from mygpoclient.json import JsonClient
from functools import wraps
from tempfile import mkdtemp
from helpers import *


# Create Flask application and set configuration.
app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    SECRET_KEY='podracer_dev',
    SESSION_FILE_DIR = mkdtemp(),
    SESSION_PERMANENT = False,
    SESSION_TYPE = "filesystem"
))
Session(app)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def login_required(f):
    """ Decorator function enforcing login for all pages. """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

#############################
# Page views here.
#############################

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Login page. """
    session.clear()
    if request.method == 'POST':
        if not request.form['username']:
            error = 'Missing username.'
        elif not request.form['password']:
            error = 'Missing password.'
        else:
            try:
                client = authenticate(request.form['username'], request.form['password'])
                session["logged_in"] = True
                session["username"] = request.form['username']
                session["password"] = request.form['password']
                return redirect(url_for('index'))
            except:
                error = 'Invalid login credentials.'
        return render_template('login.html', error=error)
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    """ Logout page. """
    session.clear()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """ Home page. Displays subscription info and smart-sorted episodes. """
    client = JsonClient(session["username"], session["password"])
    subs = get_subscriptions(client, session["username"])
    recent_episodes = smart_sort(client, session["username"])
    for ep in recent_episodes:
        ep['description'] = re.sub(r'http\S+', '', ep['description'])
        ep['released'] = ep['released'].split('T', 1)[0]

    if request.method == 'POST':
        if request.form['submit'] == 'fetch':
            if not request.form['queryvalue']:
                return render_template('index.html', subs=subs)
            else:
                return redirect(url_for('searchresults', query=request.form['queryvalue']))
        elif request.form['submit'] == 'advanced':
            return redirect(url_for('advancedsearch'))
        elif request.form['submit'] == 'sugg':
            return redirect(url_for('suggestions'))
    return render_template('index.html', subs=subs, recent_episodes=recent_episodes)

@app.route('/searchresults')
@login_required
def searchresults():
    """ Results of search. Both simple and advanced search share the same results page. """
    client = JsonClient(session["username"], session["password"])
    query, genre, pop = request.args.get('query'), request.args.get('genre'), request.args.get('pop')

    # Check whether we were directed to this page via a genre, popularity or simple search query.
    if genre:
        results = get_genre_podcasts(client, genre)
    elif query:
        results = simple_search_results(client, query)
    elif pop:
        results = get_popular_podcasts(client, pop)
    else:
        results = []
    return render_template('searchresults.html', results=results)

@app.route('/advancedsearch')
@login_required
def advancedsearch():
    """ Search by genre or popularity. """
    client = JsonClient(session["username"], session["password"])
    genres = top_genres(client)
    genre_names = [(url_for('searchresults', genre=gr['tag']), gr['title']) for gr in genres]
    return render_template('advancedsearch.html', genre_names=genre_names)

@app.route('/suggestions')
@login_required
def suggestions():
    """ Suggestions by gpodder and clustering. """
    client = JsonClient(session["username"], session["password"])
    suggestions = get_suggestions(client)
    ml_suggestions = clustering(client, session["username"])[:5]
    return render_template('suggestions.html', suggestions=suggestions, ml_suggestions=ml_suggestions)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
