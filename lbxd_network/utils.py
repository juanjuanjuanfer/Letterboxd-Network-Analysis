import requests 
import re

def get_user_data(user):
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
        return follow

    following = extract_following(user, followingurl)
    followers = extract_following(user, followersurl)
    return following, followers

def scrape_network(user, depth=2):
    to_scrape = {user}
    scraped = set()
    network = {user: {"following": [], "followers": []}}

    for _ in range(depth):
        next_to_scrape = set()
        for user in to_scrape:
            if user not in scraped:
                following, followers = get_user_data(user)
                if user not in network:
                    network[user] = {"following": [], "followers": []}
                network[user]["following"] = following
                network[user]["followers"] = followers
                next_to_scrape.update(following)
                next_to_scrape.update(followers)
                scraped.add(user)
        to_scrape = next_to_scrape

    return network