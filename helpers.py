"""
Helper functions for the web application.
"""

import json, time, datetime
from mygpoclient.json import JsonClient
from collections import Counter

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import KMeans


ROOT_URL = "https://gpodder.net"


def timestamp(s):
    """ Converts date to timestamp. """
    return time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())


def query(client, qstring, method='GET', data=None):
    """ Executes a HTTP request on gpodder.net. """
    qstring = ROOT_URL + qstring
    if method == 'GET':
        return client.GET(qstring)
    else:
        return client.POST(qstring, data)


def authenticate(username, password):
    """ HTTQ Request: Checks that login credentials are valid. """
    client = JsonClient(username, password)
    qstring = "/api/2/auth/{}/login.json".format(username)
    query(client, qstring, 'POST', {'username': username})
    return client


def podcast_info(podcast_obj):
    """ Converts gpodder podcast object to a dictionary structure. """
    podcast_dict = dict()
    fields = ['title', 'description', 'website', 'subscribers', 'logo_url']
    for f in fields:
        podcast_dict[f] = podcast_obj[f]
    return podcast_dict


def get_subscriptions(client, username):
    """ HTTQ Request: Returns user's subscriptions. """
    qstring = "/subscriptions/{}.json".format(username)
    all_subs = query(client, qstring)
    return [podcast_info(sub) for sub in all_subs if sub['title'] != '']


def simple_search_results(client, search_term):
    """ HTTQ Request: Returns podcasts returned by gpodder's (simple) search function. """
    qstring = "/search.json?q={}".format(search_term)
    results = query(client, qstring)
    return [podcast_info(result) for result in results if result['title'] != '']


def top_genres(client, num=20):
    """ HTTQ Request:  Returns the top n genres ranked by gpodder. """
    qstring = "/api/2/tags/{}.json".format(num)
    return query(client, qstring)


def get_genre_podcasts(client, genre, num=15):
    """ HTTQ Request: Returns the top n podcasts for each genre (as sorted by gpodder). """
    qstring = "/api/2/tag/{}/{}.json".format(genre, num)
    return query(client, qstring)


def get_popular_podcasts(client, num):
    """ HTTQ Request: Returns the n most popular podcasts by subscriber count. """
    qstring = "/toplist/{}.json".format(num)
    return query(client, qstring)


def smart_sort(client, username):
    """ Sorts the podcasts by frequency and lists the episodes the user should listen to next. """
    # HTTQ Request: Get all devices of the user.
    dev_qstring = "/api/2/devices/{}.json".format(username)
    devices = query(client, dev_qstring)

    # Set query date to a week ago.
    today = datetime.date.today()
    last_week = today - datetime.timedelta(days=7)
    last_week = last_week.strftime("%d/%m/%Y")

    # Get all episodes from a week ago until now.
    all_episodes = []
    for dev in devices:
        recent_qstring = "/api/2/updates/{}/{}.json?since={}".format(username, dev['id'], timestamp(last_week))
        episodes = query(client, recent_qstring)
        all_episodes += episodes['updates']

    # Sorting based on frequency of podcasts. User watches 1 episode of the podcast(s) with the most episodes remaining
    # until all episodes have been watched.
    counts = Counter()
    index = dict()
    for i in range(len(all_episodes)):
        pod = all_episodes[i]['podcast_title']
        counts[pod] += 1
        if pod not in index:
            index[pod] = []
        index[pod].append(i)
    freq = counts.most_common()
    for i in range(len(freq)):
        freq[i] = list(freq[i])
    max_freq = freq[0][1]
    sorted_list = []
    for j in range(max_freq, 0, -1):
        for k in range(len(freq)):
            if freq[k][1] == j:
                sorted_list.append(all_episodes[index[freq[k][0]][0]])
                if j > 1:
                    index[freq[k][0]] = index[freq[k][0]][1:]
                freq[k][1] -= 1
            else:
                break
    return sorted_list


def get_suggestions(client, num=5):
    """ HTTQ Request: Get podcast suggestions from gpodder. """
    qstring = "/suggestions/{}.json".format(num)
    return query(client, qstring)


def clustering(client, username):
    """ Use simple text vectorizing and K-means clustering to determine similar podcasts. """
    all_subs = get_subscriptions(client, username)
    X_data = [sub['description'] for sub in all_subs]
    tops = get_popular_podcasts(client, 100)
    Y_data = [pod['description'] for pod in tops]
    data = X_data + Y_data
    X_size, Y_size = len(X_data), len(Y_data)

    count_vect = CountVectorizer()
    data_counts = count_vect.fit_transform(data)
    tf_transformer = TfidfTransformer(use_idf=False).fit(data_counts)
    data_tf = tf_transformer.transform(data_counts)

    kmeans = KMeans(n_clusters=15)
    kmeans.fit(data_tf)
    X_set = set()
    desirables = []
    for i in range(X_size):
        X_set.add(kmeans.predict(data_tf[i])[0])
    for j in range(X_size, len(data)):
        if kmeans.predict(data_tf[j])[0] in X_set:
            desirables.append(tops[j - X_size])
    return desirables