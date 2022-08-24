# -*- coding: utf-8 -*-
"""
Created on Sun Aug 21 20:31:13 2022

@author: BilKu

Slouží k získání meterologických dat z webu https://meteobox.cz/
"""

import requests
from bs4 import BeautifulSoup
import datetime
import unicodedata


def correct_time(time, row):
    # Porovnává zadaný čas s časem v řádku html tabulky.
    
    time_1 = row.find("td", class_="pocprvyst")
    if time_1 != None:

        time_2 = time_1.b
        time_3 = time_2.getText()
        
        if time_3 == time:
            return True 

    return False
     
def check_place(place):
    # Kontroluje, zda pro dané místo má meteobox předpověď.
    
    place = unicodedata.normalize('NFD', place)
    place = place.encode('ascii', 'ignore')
    place = place.decode("utf-8")
    place = place.lower()
    place = place.replace(" ","-")
    
    today = datetime.date.today()
    date = today.strftime("%Y%m%d")

    URL = "https://meteobox.cz/" + place + "/dlouhodoba-predpoved/?d=" + date
    page = requests.get(URL)  

    soup = BeautifulSoup(page.content, "html.parser")
    title = soup.find("title")
    
    if "Chyba 404, stránka neexistuje" in title:
        return False
    else:
        return place

def check_date(date_str):
    # Kontroluje, zda má meteobox pro dané datum předpověď.
    
    try:

        date = datetime.datetime.strptime(date_str, "%d. %m. %Y")
        date = date.date()
         
        today = datetime.date.today()
        new_date = date.strftime("%Y%m%d")
        
        if today <= date <= today + datetime.timedelta(days = 9):
            return new_date
        else:
            return False
    except ValueError:
        return False

def check_time(place, date, time_str):
    # Kontroluje, zda má meteobox pro daný čas předpověď.
    
    if len(time_str) != 5:
        return False
    if time_str[2:] != ":00":
        return False
    try:
        a = int(time_str[:2])
        if 0 > a or a > 24:
            return False
    except ValueError:
        return False

    URL = "https://meteobox.cz/" + place + "/dlouhodoba-predpoved/?d=" + date
    page = requests.get(URL)  

    soup = BeautifulSoup(page.content, "html.parser")

    for row in soup.find_all("td", class_="pocprvyst"):
        time = row.find("b")
        time = time.getText()

        if time == time_str:
            return time
    
    date = datetime.datetime.strptime(date + time_str, "%Y%m%d%H:%M")
    date_moved =  date - datetime.timedelta(hours = 1)

    date_new = date_moved.strftime("%Y%m%d")
    time_new = date_moved.strftime("%H:%M")
    
    ("Pro tento čas (" + time_str + ") nemá meteobox předpověď, zkouším o hodinu dříve." + time_new)
    
    return check_time(place, date_new, time_new)


def main(info):
    
    place = info[0]
    date = info[1]
    time = info[2]
 
    URL = "https://meteobox.cz/" + place + "/dlouhodoba-predpoved/?d=" + date
    page = requests.get(URL)
    
    soup = BeautifulSoup(page.content, "html.parser")
    
    table = soup.find("table", class_="poctable2")
    
    res_1 = []
    res_2 = []
    
    for row in table.find_all("tr"):
        if correct_time(time, row) == True:
            items = row.find_all("td")
            row = [row.text.strip() for row in items if row.text.strip()]
            if row:
                res_1.append(row)
    
    temp_1 = str(res_1[0][2])
    temp_2 = temp_1.replace("," ,".")
    index_temp = temp_2.index("\xa0")
    temp_3 = float(temp_2[0:index_temp])
    res_2.append(temp_3)
    
    wind_1 = res_1[0][4]
    wind_2 = wind_1.replace("," ,".")
    index_wind = wind_2.index("m/s")
    wind_3 = float(wind_2[0:index_wind - 1])
    res_2.append(wind_3) 
    
    press_1 = res_1[0][5]
    press_2 = press_1.replace("," ,".")
    index_press = press_2.index("hPa")
    press_3 = float(press_2[0:index_press - 1])
    res_2.append(press_3) 
    
    humid_1 = res_1[0][6]
    humid_2 = humid_1.replace("," ,".")
    index_humid = humid_2.index("%")
    humid_3 = float(humid_2[0:index_humid - 1])
    res_2.append(humid_3) 
    
    rain_1 = res_1[0][3]
    rain_2 = rain_1.replace("," ,".")
    index_rain = rain_2.index("mm")
    rain_3 = float(rain_2[0:index_rain - 1])
    res_2.append(rain_3) 
     
    return res_2
