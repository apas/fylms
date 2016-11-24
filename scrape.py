import requests
import sys, time, json, datetime, locale, itertools, logging
from lxml import html, etree
from collections import defaultdict
import terminalmdb as imdb
import config

reload(sys) # helpers for utf-8
sys.setdefaultencoding("utf-8")
logger = logging.getLogger("scrape")
hdlr = logging.FileHandler("error.log")
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.WARNING)

# return True if string is time HH:MM
def isTime(input):
  try:
    time.strptime(input, "%H:%M")
    return True
  except ValueError:
    return False

# theater urls showing only OV films
artis_url = "http://www.cineplexx.at/service/program.\
php?type=program&centerId=2&originalVersionTypeFilter=OV"
apollo_url = "http://www.cineplexx.at/service/program.\
php?type=program&centerId=8&originalVersionTypeFilter=OV"
village_url = "http://www.cineplexx.at/service/program.\
php?type=program&centerId=115&originalVersionTypeFilter=OV"
haydn_url = "http://www.haydnkino.at/Cinema/OverviewList?tabSelected=0"

# load the url
artis = requests.get(artis_url)
apollo = requests.get(apollo_url)
village = requests.get(village_url)
haydn = requests.get(haydn_url)

# construct tree out of html
tree_artis = html.fromstring(artis.content.encode('utf-16'))
tree_apollo = html.fromstring(apollo.content.encode('utf-16'))
tree_village = html.fromstring(village.content.encode('utf-16'))
tree_haydn = html.fromstring(haydn.content.encode('utf-16'))

# access the elements we want with `or` constructor
# h2/a/ = film name
# p class 'time-desc' = showtimes
xpath_str = "//div[@class='overview-element separator']//h2//a/text() \
| //div[@class='span6']//p[@class='time-desc']/text()"
artis_films = tree_artis.xpath(xpath_str)
apollo_films = tree_apollo.xpath(xpath_str)
village_films = tree_village.xpath(xpath_str)

xpath_str_haydn = "//div[@id='tabsAll']//table[@class='movie']//span[\
@class='title teen_bold']/text() | //div[@id='tabsAll']//div[@class=\
'events']//a/text()"
haydn_films = tree_haydn.xpath(xpath_str_haydn)

for film in haydn_films:
  film = film.replace("\n", "")

# return a <film, [showtimes]> dictionary out of the accessed films
def create_dict(films):
  try:
    key = films[0].encode('utf-8').strip()
  except Exception, e:
    logger.exception(e)
    pass
  d = defaultdict(list)
  for film in films:
    if isTime(film.encode('utf-8').strip()):
      try:
        d[key].append(film.encode('utf-8').strip())
      except Exception, e:
        logger.exception(e)
        pass
    else:
      try:
        key = film.encode('utf-8').strip()
      except Exception, e:
        logger.exception(e)
        pass

  return d

# get imdb id for letterboxd permalink via zac's terminalmdb
# append as extra value in dictionary
def get_ids(dicts):
  for k, v in dicts.iteritems():
    try:
      iid = imdb.getID(k)
      dicts[k].append(iid)
    except ValueError, e:
      logger.exception(e)
      pass

# (provided with an imdb id, letterboxd redirects to film page)
# return the film's letterboxd rating in a string
def get_rating(input):
  movie_url = "http://letterboxd.com/imdb/" + input
  movie = requests.get(movie_url)
  tree_movie = html.fromstring(movie.content.encode('utf-16'))
  xpath_str2 = "//*[@id=\"film-page-wrapper\"]/div[2]/aside/section[2]\
  /span/span/text()"
  try:
    movie_rating = str(tree_movie.xpath(xpath_str2)[0])
    return movie_rating
  except Exception, e:
    logger.exception(e)
    return "0"

# append letterboxd rating in dictionary as extra value
def append_ratings(dicts):
  for k, v in dicts.iteritems():
    for val in v:
      if val.startswith("tt"):
        try:
          dicts[k].append(get_rating(val))
        except Exception, e:
          logger.exception(e)
          pass

# helper funcs to print jsonified dicts
# print "\n##########################################\n"
# print json.dumps(artis_dict, ensure_ascii=False, indent=2)
# print "\n##########################################\n"
# print json.dumps(apollo_dict, ensure_ascii=False, indent=2)
# print "\n##########################################\n"
# print json.dumps(village_dict, ensure_ascii=False, indent=2)

# for a specific theater:
# for its films with a letterboxd rating >= 3.2
# return film name, letterboxd url, showtimes, and rating in a string
def print_data(dicts):
  res = ""
  for k, v in dicts.iteritems():
    rating = 0.0
    times = ""
    imdb = ""
    for val in v:
      if not isTime(val) and not val.startswith("tt"):
        if float(val) >= 3.2:
          rating = float(val)
      if isTime(val):
        times = times + " " + val + " "
      if val.startswith("tt"):
        imdb = str(val)

    if rating >= 3.2:
      url = "http://letterboxd.com/imdb/" + imdb
      res = res + "\t" + k + "\n"
      res = res + "\t" + url + "\n"
      res = res + "\t" + times[1:] + "\n"
      res = res + "\t" + "Rating: " + str(rating) + "\n"
      res = res + "\n"

  return res

# prepare the dictionaries, ratings, etc
def prepare_data():
  global artis_dict # ugly globals but print_movies() needs access
  global apollo_dict
  global village_dict
  global haydn_dict

  artis_dict = create_dict(artis_films)
  apollo_dict = create_dict(apollo_films)
  village_dict = create_dict(village_films)
  haydn_dict = create_dict(haydn_films)

  get_ids(artis_dict)
  get_ids(apollo_dict)
  get_ids(village_dict)
  get_ids(haydn_dict)

  append_ratings(artis_dict)
  append_ratings(apollo_dict)
  append_ratings(village_dict)
  append_ratings(haydn_dict)

# return all movie recommendations for all theaters in a string
def print_movies():
  res = ""
  res = res + "Today's movie recommendations:\n\n"
  res = res + "@ Artis International Cinema" + "\n"
  res = res + print_data(artis_dict)
  res = res + "@ Apollo Cinema" + "\n"
  res = res + print_data(apollo_dict)
  res = res + "@ Village Wien Mitte" + "\n"
  res = res + print_data(village_dict)
  res = res + "@ Haydn Kino" + "\n"
  res = res + print_data(haydn_dict)

  return res 

# customize mailgun keys in `config.py`
# send movie recommendations in mail
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
