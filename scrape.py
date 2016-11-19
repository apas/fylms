import requests
import sys, time, json, datetime, locale, itertools
from lxml import html, etree
from collections import defaultdict

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

print json.dumps(create_dict(artis_films), ensure_ascii=False, indent=2)
print "\n##########################################\n"
print json.dumps(create_dict(apollo_films), ensure_ascii=False, indent=2)
print "\n##########################################\n"
print json.dumps(create_dict(village_films), ensure_ascii=False, indent=2)
