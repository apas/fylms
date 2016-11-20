"""
simplified https://github.com/zacoppotamus/TerminaIMdB
"""

import urllib
import argparse
import sys
from xml.etree import ElementTree

def getXML(**url_args):
  url_params = {
    'r': 'xml',
    'plot': 'full'
  }
  url_params.update(url_args)
  url = "http://www.omdbapi.com/?" + urllib.urlencode(url_params)
  xml = ElementTree.parse(urllib.urlopen(url))
  return xml

def retrieveMovie(xml):
  # fall back to movie search if no movie is found
  for node in xml.iter('root'):
    if node.get('response') == 'False':
      raise ValueError("Movie not found.")
    else:
      xml = xml.getroot()
      return printInfo(xml)

def printInfo(xml):
  id = ""
  for movie in xml.findall('movie'):
    id = movie.get("imdbID").decode("utf-8")
  return id

def getID(input):
  return retrieveMovie(getXML(t=input))
