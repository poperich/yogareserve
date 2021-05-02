import requests
import logging
import datetime
import yaml

from bs4 import BeautifulSoup
from random import randint
from time import sleep

BASEURL = "https://reservas.yogaone.es"

def loginYoga(session, user, password):
  url = BASEURL + '/Account/Login?ReturnUrl=%2F'
  g = session.get(url)
  token = BeautifulSoup(g.text, 'html.parser').find('input',{'name':'__RequestVerificationToken'})['value']
  logging.debug("Verification Token for loggin: %s",token)
  payload = { 'Input.Email': user,
              'Input.Password': password,
              'Input.Remember': 'true',
              '__RequestVerificationToken': token }
  sleep(randint(1,60))
  p = session.post(url, data=payload)
  soup = BeautifulSoup(p.text, 'html.parser')
  logging.debug(soup.title)
  #logging.debug(soup.prettify())

def getYogaActivity(session):
  '''
  return a list of activity that can be reserved
  '''
  sleep(randint(1,10))
  activity = s.get(BASEURL)
  logging.debug(activity)
  soup = BeautifulSoup(activity.text, 'html.parser')
  classesActive = soup.find_all("tr", {"class": "active"})
  #print(classesActive)
  lista_classi = []
  for row in classesActive:
      dict_classe = {}
      cell = row.find_all('td')
      dict_classe["ora"] = cell[0].find(text=True)
      dict_classe["tipo"] = cell[1].find(text=True)
      dict_classe["posti"] = cell[2].find(text=True)
      cell = row.find_all('a')
      if len(cell) == 1:
          dict_classe["cod_classe"] = cell[0]["data-target"]
          dict_classe["data"] = cell[0]["data-target"].split("-")[4]  
          lista_classi.append(dict_classe)
  logging.debug("Lista classi: %s",lista_classi)
  return lista_classi

def reserve_yoga_class(session,cod_classe):
  url = BASEURL + '/Activities/CreateBooking'
  payload = { 'ContractConditions': "true",
              'UniqueActivityCode': cod_classe,
             }

  p = session.post(url, data=payload)
  soup = BeautifulSoup(p.text, 'html.parser')
  #logging.debug(soup.prettify())
  logging.debug("recived status code: %d",p.status_code)
  if p.status_code == 200:
    return True
  else:
    logging.error("unable to reserve the class respose from server: %s", p.text)

def get_my_reserve(session):
  myreserve = s.get(BASEURL+"/Account/MyAccount")
  soup = BeautifulSoup(myreserve.text, 'html.parser')
  logging.debug(soup.prettify())
  logging.debug(activity)

  reserve_table = soup.find_all("div", {"id": "proximascitaslist"})
  #print(classesActive)
  lista_classi = []
  for row in classesActive:
      dict_classe = {}
      cell = row.find_all('td')
      dict_classe["ora"] = cell[0].find(text=True)
      dict_classe["tipo"] = cell[1].find(text=True)
      dict_classe["posti"] = cell[2].find(text=True)
      cell = row.find_all('a')
      if len(cell) == 1:
          dict_classe["cod_classe"] = cell[0]["data-target"]
          dict_classe["data"] = cell[0]["data-target"].split("-")[4]  
          lista_classi.append(dict_classe)
  logging.debug("Lista classi: %s",lista_classi)
  return lista_classi
  #print(myreserve.content)

def selectClass(yogaclass):
  """
  """
  classi_riservate = get_my_reserve()

  # data di oggi
  # if data di oggi sabato-giovedi
  # else return null

  # if exist riserva domani-dopodomani
  # return null
  # else select from dict class that have ora 19:45 and rerutn codice

if __name__ == "__main__":


  with open("config.yml", "r") as ymlfile:
      cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

  level_config = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO}

  if cfg["log"]["file"] == "" :
    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S', level=level_config[cfg["log"]["level"]])
  else:
    logging.basicConfig(filename=cfg["log"]["file"], format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S', level=level_config[cfg["log"]["level"]])

  USER = cfg["access"]["user"]
  PASSWORD = cfg["access"]["password"]
  YOGA_WEEK_DAY = cfg["schedule"]["day"]
  YOGA_HOUR_CLASS = cfg["schedule"]["hour"]

  logging.debug("Starting session with following credential usr: %s, psw: %s", USER, PASSWORD)
  logging.info("Staring reserving for day of the week: %s, at time: %s", str(YOGA_WEEK_DAY), YOGA_HOUR_CLASS)

  if cfg["test"]["test"]:

    s = requests.Session()
    
    # login
    loginYoga(session=s, user=USER, password=PASSWORD)
    
    reserve = False
    yogaclass = getYogaActivity(s)
    logging.debug("found the following class:")
    logging.debug(yogaclass)
    reserved = reserve_yoga_class(s, "38-SDIR1-YOGA-191-210430")
    logging.debug(reserved)
    exit()

  # weekday()
  day_to_reserve = datetime.datetime.today() + datetime.timedelta(days=2) 

  if day_to_reserve.weekday() in YOGA_WEEK_DAY:

    s = requests.Session()
    
    # login
    loginYoga(session=s, user=USER, password=PASSWORD)
    
    reserve = False
    yogaclass = getYogaActivity(s)
    logging.debug("found the following class:")
    logging.debug(yogaclass)
    for yoga in yogaclass:
      if yoga["data"] == day_to_reserve.strftime("%y%m%d") and yoga["ora"] == YOGA_HOUR_CLASS:
        logging.debug("try to reserve class %s on day: %s ora: %s", yoga["tipo"], yoga["data"], yoga["ora"])
        reserved = reserve_yoga_class(s,yoga["cod_classe"])
        if reserved:
          logging.info("reserverd class date: %s hour: %s", yoga["data"], yoga["ora"])
    if not reserved:
      logging.debug("Should reserve a class but some error occurred")
  else:
    logging.debug("No class to reserve")
