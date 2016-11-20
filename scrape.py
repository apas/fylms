import requests
import sys, time, json, datetime, locale, itertools
from lxml import html, etree
from collections import defaultdict
import terminalmdb as imdb
import config

reload(sys) # helpers for utf-8
sys.setdefaultencoding('utf-8')

def isTime(input):
  try:
    time.strptime(input, "%H:%M")
    return True
  except ValueError:
    return False

artis_url = "http://www.cineplexx.at/service/program.\
php?type=program&centerId=2&originalVersionTypeFilter=OV"
apollo_url = "http://www.cineplexx.at/service/program.\
php?type=program&centerId=8&originalVersionTypeFilter=OV"
village_url = "http://www.cineplexx.at/service/program.\
php?type=program&centerId=115&originalVersionTypeFilter=OV"

artis = requests.get(artis_url)
apollo = requests.get(apollo_url)
village = requests.get(village_url)

tree_artis = html.fromstring(artis.content.encode('utf-16'))
tree_apollo = html.fromstring(apollo.content.encode('utf-16'))
tree_village = html.fromstring(village.content.encode('utf-16'))

xpath_str = "//div[@class='overview-element separator']//h2//a/text() \
| //div[@class='span6']//p[@class='time-desc']/text()"
artis_films = tree_artis.xpath(xpath_str)
apollo_films = tree_apollo.xpath(xpath_str)
village_films = tree_village.xpath(xpath_str)

def create_dict(films):
  key = films[0].encode('utf-8').strip()
  d = defaultdict(list)
  for film in films:
    if isTime(film.encode('utf-8').strip()):
      d[key].append(film.encode('utf-8').strip())
    else:
      key = film.encode('utf-8').strip()

  return d

def get_ids(dicts):
  for k, v in dicts.iteritems():
    try:
      iid = imdb.getID(k)
      dicts[k].append(iid)
    except ValueError:
      pass

# provided with an imdb id letterboxd redirects to film page
def get_rating(input):
  movie_url = "http://letterboxd.com/imdb/" + input
  movie = requests.get(movie_url)
  tree_movie = html.fromstring(movie.content.encode('utf-16'))
  xpath_str2 = "//*[@id=\"film-page-wrapper\"]/div[2]/aside/section[2]\
  /span/span/text()"
  movie_rating = str(tree_movie.xpath(xpath_str2)[0])
  return movie_rating

def append_ratings(dicts):
  for k, v in dicts.iteritems():
    for val in v:
      if val.startswith("tt"):
        dicts[k].append(get_rating(val))

# print "\n##########################################\n"
# print json.dumps(artis_dict, ensure_ascii=False, indent=2)
# print "\n##########################################\n"
# print json.dumps(apollo_dict, ensure_ascii=False, indent=2)
# print "\n##########################################\n"
# print json.dumps(village_dict, ensure_ascii=False, indent=2)

def print_data(dicts):
  res = ""
  for k, v in dicts.iteritems():
    rating = 0.0
    times = ""
    for val in v:
      if not isTime(val) and not val.startswith("tt"):
        if float(val) >= 3.2:
          rating = float(val)
      if isTime(val):
        times = times + " " + val + " "

    if rating >= 3.2:
      res = res + "\t" + k + "\n"
      res = res + "\t" + times[1:] + "\n"
      res = res + "\t" + "Rating: " + str(rating) + "\n"
      res = res + "\n"

  return res

def prepare_data():
  global artis_dict # ugly globals but print_movies() needs access
  global apollo_dict
  global village_dict

  artis_dict = create_dict(artis_films)
  apollo_dict = create_dict(apollo_films)
  village_dict = create_dict(village_films)

  get_ids(artis_dict)
  get_ids(apollo_dict)
  get_ids(village_dict)

  append_ratings(artis_dict)
  append_ratings(apollo_dict)
  append_ratings(village_dict)

def print_movies():
  res = ""
  res = res + "Today's movie recommendations:\n\n"
  res = res + "@ Artis International Cinema" + "\n"
  res = res + print_data(artis_dict)
  res = res + "@ Apollo Cinema" + "\n"
  res = res + print_data(apollo_dict)
  res = res + "@ Village Wien Mitte" + "\n"
  res = res + print_data(village_dict)

  return res 

def send_email():
  return requests.post(config.api_url,
      auth=("api", config.api_key),
      data={"from": config.from_mail,
            "to": config.to_mail,
            "subject": "Today's movie recommendations",
            "text": print_movies()})

if __name__ == '__main__':
  prepare_data()
  send_email()
