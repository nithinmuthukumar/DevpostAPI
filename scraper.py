import pprint
import re

import requests
from bs4 import BeautifulSoup
import urllib.parse

# api.devpost.com/software
# ?page=
# https://devpost.com/api/hackathons?challenge_type[]=in-person
parser = "html.parser"
baseurl = "https://devpost.com/"

param_indicators = ["?", "&"]


def add_queries_to_url(url, params):
    url_parts = list(urllib.parse.urlparse(url))
    query = dict(urllib.parse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib.parse.urlencode(query)
    req_url = urllib.parse.urlunparse(url_parts)
    return req_url

def get_hackathon_info(hackathon_url):
    return []
def get_project_info(project_url):
    page = requests.get(project_url)
    soup = BeautifulSoup(page.content, parser)

    hackathon_soup = soup.find("div", {"id": 'submissions'}).find('ul', {"class": "software-list-with-thumbnail"})
    hackathons = []
    likes = soup.find('a', {'class': 'like-button'}).find('span', {'class': 'side-count'})
    comments = soup.find('a', {'class': 'comment-button'}).find('span', {'class': 'side-count'})

    for h in hackathon_soup.findChildren('li', recursive=False):
        hackathon = dict()
        hackathon['name'] = h.find('p').get_text().strip()
        hackathon['imgUrl'] = "https:" + h.find('img', src=True)['src']
        hackathon['hackathonUrl'] = h.find('p').find('a')['href']
        hackathon['awards'] = []
        if h.find('ul'):
            hackathon['awards'] = ["".join(i.findAll(text=True, recursive=False)).strip() for i in h.findAll('li')]
        hackathons.append(hackathon)
    project = {
        'videoLink': soup.find('div', {'id': 'gallery'}).find('iframe')['src'],
        'hackathons': hackathons,
        'members': get_info_from_user_photos(soup.find("section", {"id": "app-team"})),
        'details': "\n".join(t.get_text().strip('\n') for t in
                             soup.find('div', {'id': 'app-details-left'})
                             .findChildren('div', recursive=False)[1].findAll(["p", "h2"])),

        "externalLinks": [link['href'] for link in soup.find('ul', {'data-role': 'software-urls'}).findAll("a")],
        "builtWith": [i.get_text() for i in soup.find('div', {'id': 'built-with'}).findAll('li')],
        "likes": int(likes.get_text()) if likes else 0,
        "comments": int(comments.get_text()) if comments else 0

    }
    return project


def get_hackathons(*, amount, options={}, ):
    page = 1
    url = baseurl + "api/hackathons"
    params = {"orderBy": 'order_by', 'location': "challenge_type[]", 'status': 'status[]', "length": 'length[]',
              "themes": 'themes[]', "organization": 'organization', "openTo": 'open_to[]', "search": 'search'}
    if options:
        params = {params[k]: v for k, v in options.items()}
    else:
        params = {}
    hackathons = []
    req_url = add_queries_to_url(url, params)

    paging_data = requests.get(req_url).json()["meta"]
    amount = min(amount, paging_data["total_count"])

    while amount > 0:
        data = requests.get(req_url + param_indicators[len(params)] + f"{page=}").json()["hackathons"]

        hackathons_in_data = []
        for hackathon in data:
            currency = hackathon['prize_amount'][0]
            prize_amount = re.findall(r'>(.+?)<', hackathon['prize_amount'])[0]  # removes html tags around prize

            hackathons_in_data.append({
                "name": hackathon['title'],
                "location": hackathon['displayed_location']['location'],
                "organizationName": hackathon['organization_name'],
                "prizeAmount": currency + prize_amount,
                "registrationsCount": hackathon['registrations_count'],
                "submissionPeriod": hackathon['submission_period_dates'],
                "themes": [theme['name'] for theme in hackathon['themes']],
                "hackathonUrl": hackathon['url'],
                "image": "https:" + hackathon['thumbnail_url'],
                "winnersAnnounced": hackathon['winners_announced'],
                "openTo": hackathon['open_state'],
                "submissionGalleryUrl": hackathon['submission_gallery_url'],
                "startSubmissionUrl": hackathon['start_a_submission_url']

            })

        if amount >= len(hackathons_in_data):
            amount -= len(hackathons_in_data)
            hackathons.extend(hackathons_in_data)
        else:
            hackathons.extend(hackathons_in_data[:amount])
            amount = 0

        page += 1
    return hackathons


def get_profile_projects(username):
    page = requests.get(baseurl + username)
    soup = BeautifulSoup(page.content, parser)
    return get_projects_from_page(soup)


def get_profile(username):
    page = requests.get(baseurl + username)
    soup = BeautifulSoup(page.content, parser)

    user_aliases = soup.find("h1", {"id": "portfolio-user-name"}).get_text()
    name, username = [re.sub("[()]", "", i.strip()) for i in user_aliases.strip().split('\n')]
    links = soup.find("ul", {'id': "portfolio-user-links"})
    # location is the first value in the list
    location = links.find("li").get_text().strip()
    external_links = [a['href'] for a in links.findAll("a")]

    projects, hackathons, achievements, followers, following, likes = [i.get_text() for i in soup.find("nav", {
        "id": "portfolio-navigation"}).findAll("div", {"class": "totals"})]

    profile = {

        "imageUrl": soup.find("div", {"id": "portfolio-user-photo"}).find("img", {"class": "user-photo"})['src'],
        "name": name,
        "username": username,
        "location": location,
        "externalLinks": external_links,
        "stats": {
            "projects":projects,
            "hackathons":hackathons,
            "achievements":achievements,
            "followers":followers,
            "following":following,
            "likes":likes
        },
        "profile_url":baseurl+username

    }
    return profile


def get_projects_from_page(soup):
    projects = []

    project_divs = soup.findAll("div", {'data-software-id': re.compile(r".*")})
    for project in project_divs:
        image = project.find("img", {"class": "software_thumbnail_image"}, src=True, alt=True)
        project = {
            "url": project.find("a", {"class": 'link-to-software'}, href=True)['href'],
            "imageUrl": image['src'],
            'name': image['alt'],
            'tagLine': project.find('p', {"class": "tagline"}).get_text().strip(),
            'likes': int(project.find('span', {"data-count": "like"}).get_text().strip()),
            'commentCount': int(project.find('span', {"data-count": "comment"}).get_text().strip()),
            'members': get_info_from_user_photos(project),
            'isWinner': bool(project.find("aside", {"class": "entry-badge"}))

        }
        projects.append(project)
    return projects


def get_info_from_user_photos(soup):
    users = []
    for s in soup.find_all("img", {"class": "user-photo"}, alt=True, src=True, title=True):

        if 'href' in s.parent.attrs:
            profile_url = s.parent['href']
        elif 'data-url' in s.parent.attrs:
            profile_url = s.parent['data-url']
        else:
            profile_url = 'https://devpost.com/software/ghs-global-healthcare-system'

        user = {"name": s["alt"], "username": urllib.parse.urlparse(profile_url).path[1:], "imageUrl": s["src"],
                "profileUrl": profile_url}

        users.append(user)
    return users


def get_hackathon_submissions(hackathon_url, category=None, sort_by=None):
    if not sort_by and not category:
        projects_url = hackathon_url + "project-gallery"
    else:
        projects_url = hackathon_url + "submissions/search"
    params = {}
    if sort_by:
        params['sort'] = sort_by
    if category:
        category_info = next(i for i in get_hackathon_categories(hackathon_url) if i['name'] == category)
        params = {"prize_filter[prizes][]": category_info['id']}
        if sort_by:
            params['sort'] = sort_by
        projects_url = add_queries_to_url(projects_url, params)

    # large-4 small-12 columns gallery-item
    # print([img['src'] for img in soup.findAll(True, {'class': ['software_thumbnail_image']})])

    projects = []

    while True:
        page = requests.get(projects_url)

        soup = BeautifulSoup(page.content, parser)
        projects.extend(get_projects_from_page(soup))
        next_button = soup.find("li", {"class": "next_page"})

        if not next_button or "unavailable" in next_button['class']:
            break
        else:
            projects_url = hackathon_url + next_button.find('a')['href']
            if category or sort_by:
                projects_url = add_queries_to_url(projects_url, params)

    return projects


def get_hackathon_categories(hackathon_url):
    projects_url = hackathon_url + "submissions/search"
    page = requests.get(projects_url)
    soup = BeautifulSoup(page.content, parser)

    submission_filters = soup.findAll("label", {"class": "checkbox"})
    return [{"name": f.get_text(),
             "id": int(f.find("input", {"name": "prize_filter[prizes][]"})["value"])} for
            f in submission_filters]


def get_projects(*, amount):
    page = 1
    projects = []
    url = "https://api.devpost.com/software"
    while amount > 0:
        data = requests.get(url + param_indicators[0] + f"{page=}").json()["software"]
        if amount >= len(data):
            amount -= len(data)
            projects.extend(data)
        else:
            projects.extend(data[:amount])
            amount = 0

        page += 1
    return projects


if __name__ == "__main__":
    # pprint.pprint([i for i in get_hackathons(amount=6, options={'search':"MasseyHacks"})])
    # print([i["name"] for i in get_projects(amount=4)])
    # print(get_hackathon_projects("https://hack-the-valley-v.devpost.com/"))
    # print(get_hackathon_projects("https://hack-the-valley-v.devpost.com/", None, None))
    # print(get_profile_projects('https://devpost.com/shutong5s'))
    # pprint.pprint(get_project_info('https://devpost.com/software/shopadvisr'))
    print(get_profile("pinosaur"))
    print(get_hackathon_categories("https://hack-the-valley-v.devpost.com/"))

