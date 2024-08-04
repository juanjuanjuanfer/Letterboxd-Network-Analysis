from bs4 import BeautifulSoup
import requests
import re
import json


def get_fav_films_names(user_id, save = False):
    url = f"https://letterboxd.com/{user_id}/likes/films/"

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve data: {e}")
        return []

    # Extracting all the 'data-film-slug' attributes using a regular expression
    film_slugs = re.findall(r'data-film-slug="([^"]+)"', str(soup))
    if save:
        #jsonify
        key = f"{user_id}_liked_films"
        data = {key: film_slugs}
        with open(f"{user_id}_liked_films.json", "w") as file:
            json.dump(data, file)
    return film_slugs


def get_movie_genres(movie):
    url = f"https://letterboxd.com/film/{movie}/genres"

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve data: {e}")
        return []
    
    # Extracting all the genres from the page
    genres = re.findall(r'href="/films/genre/([^"]+)/', str(soup))
    return genres

def get_user_fav_genres(user_id, save = False):
    fav_films = get_fav_films_names(user_id, save)
    genres_dict = {}
    for film in fav_films:
        genres = get_movie_genres(film)
        for genre in genres:
            if genre in genres_dict:
                genres_dict[genre] += 1
            else:
                genres_dict[genre] = 1
    data = {user_id: genres_dict}
    if save:
        with open(f"{user_id}_fav_genres.json", "w") as file:
            json.dump(data, file)
    return genres_dict

def get_user_friends(user):
    attempt = requests.get(f"https://letterboxd.com/{user}")
    if attempt.status_code != 200:
        print(f"User {user} not found.")
        return [], []

    followingurl = f"https://letterboxd.com/{user}/following"
    followersurl = f"https://letterboxd.com/{user}/followers"

    def extract_following(user, mainurl, n=1, follow=[]):
        response = requests.get(mainurl).text
        pattern = r'<a\s+href="\/[a-z0-9_]+\/"\s+class="name">'
        matches = re.findall(pattern, response)
        following = [re.search(r'<a\s+href="\/([a-z0-9_]+)\/"\s+class="name">', x) for x in matches]
        following = [x.group(1) for x in following if x]
        follow.extend(following)

        if re.findall(f'<a class="next" href="/{user}/following/page/{n+1}/">Next</a>', response):
            newmainurl = f"https://letterboxd.com/{user}/following/page/{n+1}/"
            extract_following(user, newmainurl, n+1, follow)
        elif re.findall(f'<a class="next" href="/{user}/followers/page/{n+1}/">Next</a>', response):
            newmainurl = f"https://letterboxd.com/{user}/followers/page/{n+1}/"
            extract_following(user, newmainurl, n+1, follow)
        return follow

    following = extract_following(user, followingurl)
    followers = extract_following(user, followersurl)
    data = {user: {"following": following, "followers": followers}}
    return data

def get_friends_fav_genres(user, save_data = False):
    friends = get_user_friends(user)
    fav_genres = {}
    for friend in friends[user]["following"]:
        fav_genres[friend] = get_user_fav_genres(friend, save=False)
    for friend in friends[user]["followers"]:
        fav_genres[friend] = get_user_fav_genres(friend, save=False)
    if save_data:
        with open(f"{user}_friends_fav_genres.json", "w") as file:
            json.dump(fav_genres, file)
    return fav_genres