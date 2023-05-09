# RELINK
import os

# Spotify API
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# for  the lat and long work
from math import radians, acos, sin, cos

# for the directed graph https://networkx.org/documentation/stable/reference/classes/digraph.html how this was
# followed: https://stackoverflow.com/questions/20133479/how-to-draw-directed-graphs-using-networkx-in-python
import networkx as nx

# showcase the final graph for the picks
import matplotlib.pyplot as plt

# for running time
import time

# sets up to environ (when on laptop need to verify)
os.environ["SPOTIPY_CLIENT_ID"] = "2956ecdcef53422b89a179f531b14abf"
os.environ["SPOTIPY_CLIENT_SECRET"] = "4500954ae92f4c769e8129f27b23f15e"
os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:8000/callback"

# sets up the scope and authorization manager
scope = "playlist-modify-private"
auth = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

# allows the user to log in to the account
if not auth.current_user():
    print("Please Login to Spotify and Authorize!")
    auth = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))


# this formula is from this post <https://community.powerbi.com/t5/Desktop/How-to-calculate-lat-long-distance/td-p
# /1488227#:~:text=You%20need%20Latitude%20and%20Longitude,is%20Earth%20radius%20in%20km.)>
def distance_between_users(latitude_user_one, longitude_user_one, latitude_user_two, longitude_user_two):
    # radius of the earth is 6371
    return acos(
        sin(radians(latitude_user_one)) * sin(radians(latitude_user_two)) + cos(radians(latitude_user_one)) * cos(
            radians(latitude_user_two)) * cos(radians(longitude_user_two - longitude_user_one))) * 6371


# return the related artist list of the given artist
def get_related_artists(artist_input, auth):
    # searches for the related artists
    results = auth.artist_related_artists(artist_input)

    # adds the artist from the results to a list
    related_artist_list = [artist['id'] for artist in results['artists']]

    # returns the lists
    return related_artist_list


# gets the most similar song to the input song
def get_recommendation(song_input, artist_input, auth):
    # gets the recommendation based on input
    recommendation = auth.recommendations(seed_tracks=[song_input], seed_artists=[artist_input])

    # returns the recommendation
    return recommendation['tracks'][0]['id']


# creates the shortest path between to artists
def shortest_path(input_song, input_artist, end_song, end_artist, playlist, auth):
    # create the graph to find the shortest path
    graph = nx.DiGraph()

    # add input song to the graph
    graph.add_node(input_artist, weight=0)

    # add related artists to the graph
    adding = [input_artist]
    visited = []

    while adding:
        adding_artist = adding.pop(0)

        # adding related artist to the graph
        if adding_artist not in visited:
            # add to the visited list
            visited.append(adding_artist)

            # get the related artists
            adding_related = get_related_artists(adding_artist, auth)

            for related in adding_related:

                if not graph.has_node(related):
                    graph.add_node(related, weight=float('inf'))

                graph.add_edge(adding_artist, related, weight=1)

                if related not in adding:
                    adding.append(related)

    # display graph
    plot = nx.circulant_graph(graph)
    nx.draw(graph, with_labels=True)
    plt.show()

    # uses the path function to find the shortest path
    shortest_path_result = nx.dijkstra_path(graph, source=input_artist, target=end_artist, weight='weight')

    # puts songs in the playlist based on the path

    # add original song
    auth.playlist_add_items(playlist, input_song)
    for tracks in range(len(shortest_path_result) - 1):
        current_song = shortest_path_result[tracks]
        rec = get_recommendation(current_song, graph.nodes[current_song]['artist'][0], auth)
        auth.playlist_add_items(playlist, rec)

    # add ending song
    auth.playlist_add_items(playlist, end_song)


# main function
if __name__ == "__main__":

    # to calculate run time
    starting_time = time.time()

    # creates the playlist name, description, and adds the playlist to the user account
    playlist_name = input("What would you like to name the playlist? \n")
    playlist_description = "This playlist was generated through ReLink! :)"
    playlist = auth.user_playlist_create(auth.current_user()['id'], name=playlist_name, public=False,
                                         description=playlist_description)

    # ask the user what type of user (nearness) they would like to accept
    frequency_type = input(
        "Who would you like to recommend you songs? \n 1. Frequently Nearby \n 2. Sometimes Nearby \n "
        "3. Nearby Once \n")

    # FAKE USERS!!
    users = {
        'Jennifer': {'song_url': 'https://open.spotify.com/track/7cqnoQkEdgIhl0zzhqrEns?si=71690360a7c94fd4',
                     'coordinates': [(27.779701323291697, -97.41124281262692), (27.777367325016684, -97.41301801361622),
                                     (27.771242556638633, -97.4087260486171), (27.76714830715196, -97.4155826316293),
                                     (27.76366375180409, -97.4183852486239), (27.768264347848486, -97.42420484534851),
                                     (27.773884407603195, -97.43129914580274)]},

        'Shawn': {'song_url': 'https://open.spotify.com/track/3lUQpvfWFcxZC3RYAVGE7F?si=886e1e835555433a',
                  'coordinates': [(27.76681988996927, -97.42374270629152), (27.761555395965907, -97.43267957846969),
                                  (27.76252826610077, -97.43143917301998), (27.76448190926532, -97.4308831873989),
                                  (27.767291327906804, -97.42661104433081), (27.775321173935314, -97.4180129288392),
                                  (27.76702653189237, -97.41045245758588)]},

        'Joshua': {'song_url': 'https://open.spotify.com/track/54bm2e3tk8cliUz3VSdCPZ?si=93ad3cb263b14ccf',
                   'coordinates': [(27.76271876869386, -97.41733601627041), (27.767867587718452, -97.41896010650974),
                                   (27.758693242983803, -97.42737415010491), (27.76537061568545, -97.42971923717727),
                                   (27.7682972899036, -97.42140757105038), (27.761257302966925, -97.4180664333851),
                                   (27.767567855123623, -97.42398716651955)]},

        'Nicky': {'song_url': 'https://open.spotify.com/track/7BFc7ffruhZ4Hecnqf5xju?si=5a6ea283dcf2470e',
                  'coordinates': [(27.776175660188077, -97.43180222698366), (27.774352145520446, -97.42914314143569),
                                  (27.770510656496754, -97.4238636315693), (27.76809265830245, -97.42560948312881),
                                  (27.77186370453035, -97.43550650822525), (27.771391247766456, -97.4388947560671),
                                  (27.770083872308483, -97.44740726483967)]},

        'Michael': {'song_url': 'https://open.spotify.com/track/00qOE7OjRl0BpYiCiweZB2?si=af56d5c9f3f34ab2',
                    'coordinates': [(27.770839729006692, -97.44074628496256), (27.7668744164277, -97.43909317880617),
                                    (27.76898963540127, -97.43192331383247), (27.771913215486144, -97.43611111723341),
                                    (27.779297325478026, -97.43584790097961), (27.77188803603578, -97.44187338741187),
                                    (27.773007733185853, -97.43868470388946)]},

        'Alex': {'song_url': 'https://open.spotify.com/track/1fCeXjoRExPP2qwSBh2aST?si=0858bcf9d16142c1',
                 'coordinates': [(27.77354676130836, -97.43279481603578), (27.77303899943061, -97.43018802227962),
                                 (27.78211128553692, -97.43053522028785), (27.783200032569773, -97.43376293961553),
                                 (27.784992071615278, -97.43235785606983), (27.793830848580512, -97.42927711062148),
                                 (27.80106097259567, -97.42606612683335)]},

        'Adriana': {'song_url': 'https://open.spotify.com/track/3cIKojC2JBVIno9b35MJWn?si=97e2f650b007429e',
                    'coordinates': [(27.796734294405677, -97.43131715989082), (27.795187977337434, -97.42251651072178),
                                    (27.800699511392146, -97.41417735316652), (27.79191558138719, -97.41757623961094),
                                    (27.784543402146422, -97.42501236289972), (27.782534642670026, -97.42826954209868),
                                    (27.781919054476596, -97.43292200548319)]}
    }

    # setting up how to get how frequently users are nearby
    threshold = 2.0  # how close they need to be
    count = 0

    # for the type of users
    frequent_users = {}  # more than five times
    common_users = {}  # more than two times but less than four times
    nearby_users = {}  # at least once

    # getting the distance between user one (me) and the rest of the users
    for user in users.keys():
        if user == 'original':
            continue

        count = 0
        for i in range(len(users['Jennifer']['coordinates'])):
            dist = distance_between_users(users['Jennifer']['coordinates'][i][0],
                                          users['Jennifer']['coordinates'][i][1],
                                          users[user]['coordinates'][i][0], users[user]['coordinates'][i][1])
            if dist < threshold:
                count += 1

        # Add the count to the dictionary
        if count >= 5:
            frequent_users[user] = count
        if count >= 2:
            common_users[user] = count
        if count >= 1:
            nearby_users[user] = count

    # sort list by the count
    # syntax gathered from https://www.w3schools.com/python/ref_func_sorted.asp
    # and here https://www.programiz.com/python-programming/methods/built-in/sorted
    freq_user = sorted(frequent_users.items(), key=lambda x: x[1], reverse=True)
    comm_user = sorted(common_users.items(), key=lambda x: x[1], reverse=True)
    near_user = sorted(nearby_users.items(), key=lambda x: x[1], reverse=True)

    if frequency_type == '1':
        for user, count in freq_user:
            if user == 'Jennifer':
                continue
            print(f"{user} has been close to the original user {count} times.")

    if frequency_type == '2':
        for user, count in comm_user:
            if user == 'Jennifer':
                continue
            print(f"{user} has been close to the original user {count} times.")

    if frequency_type == '3':
        for user, count in near_user:
            if user == 'Jennifer':
                continue
            print(f"{user} has been close to the original user {count} times.")

    #  based on frequency
    song_urls = []
    if frequency_type == '1':
        for user, user_info in freq_user:
            if user == 'Jennifer':
                continue
            for username, song in users.items():
                if username == user:
                    song_urls.append(song['song_url'])

    if frequency_type == '2':
        for user, user_info in comm_user:
            if user == 'Jennifer':
                continue
            for username, song in users.items():
                if username == user:
                    song_urls.append(song['song_url'])

    if frequency_type == '3':
        for user, user_info in near_user:
            if user == 'Jennifer':
                continue
            for username, song in users.items():
                if username == user:
                    song_urls.append(song['song_url'])

    # print the tracks
    track_list = []
    artist_names = []
    for song in song_urls:
        track_info = auth.track(song, market='US')
        track_list.append(track_info['name'])
        artist_names.append([artist['name'] for artist in track_info['artists']])

    print(track_list)

    # now get the user they would like to pick
    chosen_track = input("What user would you like to pick (starting @ 0)? \n")

    # set the song as chosen for end goal
    end_track = track_list[int(chosen_track)]
    end_artist = artist_names[int(chosen_track)]

    # print option
    print(f"{end_track} by {', '.join(end_artist)}")

    # request the user to search for a song
    search = input("What song would you like to use as the base song?\n")
    search_spotify = auth.search(q=search, type='track')

    # gets the ending track information
    search_spotify_end = auth.search(q=end_track, type='track')
    ending_track = search_spotify_end['tracks']['items'][0]
    ending_track_id = ending_track['id']
    ending_track_artist = ending_track['artists'][0]['id']

    # gets the beginning track information (id, name of track, and the artist)
    beginning_track = search_spotify['tracks']['items'][0]
    beginning_track_id = beginning_track['id']
    beginning_track_artist = beginning_track['artists'][0]['id']

    # call the shortest_path function that should connect the beginning song to the send song
    shortest_path(beginning_track_id, beginning_track_artist, ending_track, ending_track_artist, playlist, auth)

    # ending time
    ending_time = time.time()

    print(f"Finished in {ending_time-starting_time} seconds.")
