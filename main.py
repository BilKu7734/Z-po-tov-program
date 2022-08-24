# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 09:18:04 2022

@author: BilKu

Program předpovídající index kvality ovzduší z předpovědi počasí
"""

print("Vítejte v zápočtovém programu - Určování indexu kvality ovzduší(IKO) na základě předpovědi počasí, program si nyní připraví kalibrační data a vytvoří modely pro předpověď IKO. \n")

import numpy
import pandas
import Zpracovani_dat
import Tvorba_modelu
import Scraping
from math import inf

def count_IKO(model, weather_data):
    # Spočítá IKO ze zadaných dat pomocí zadaného modelu
    
    list_of_quantities = ["teplota průměrná", "rychlost větru", "tlak vzduchu", "vlhkost vzduchu", "úhrn srážek"]
    weather_data_to_model = []
    list_of_quantities_to_model = []
    
    
    for i in weather_data:
        weather_data_to_model.append(i)
        weather_data_to_model.append(i**2)
        weather_data_to_model.append(i**3)
    
    weather_data_to_model.append(1)

    for i in list_of_quantities:
        list_of_quantities_to_model.append(i)
        list_of_quantities_to_model.append(i + "^2")
        list_of_quantities_to_model.append(i + "^3")
    
    list_of_quantities_to_model.append("konstanta")
    
    data_df = pandas.DataFrame(weather_data_to_model, index = list_of_quantities_to_model)
    data_df = data_df.transpose()

    for i in data_df.columns:
        if i not in model.head:
            data_df = data_df.drop(columns = i)

    matrix_1 = data_df.values
    matrix_2 = numpy.transpose(model.coef)

    IKO = float(numpy.matmul(matrix_1, matrix_2))
    
    return IKO
 
def interpret_IKO(IKO):
    # Krátce komentuje danou hodnotu IKO
    
    IKO_rates = [[0.34, "1A - velmi dobrá"], [0.67, "1B - dobrá"], [1, "2A - přijatelná"], [1.5, "2B - přijatelná"], [2, "3A - zhoršená"], [ inf , "3B - špatná"]]
    
    for i in range(len(IKO_rates)):
        if IKO_rates[i][0] > IKO:
            comment = IKO_rates[i][1]
            break
    
    print( "Hodnota IKO = " + str(IKO) + ", což odpovídá stupni " + comment + ". Pro podrobnější informace navštivte: https://www.chmi.cz/files/portal/docs/uoco/web_generator/d_szu.pdf" )
    return

def manual_data():

    temp = float(input("Zadejte teplotu v stupních C \n"))
    wind = float(input("Zadejte rychlost větru v m/s \n"))
    press = float(input("Zadejte atmosférický tlak v hPa \n"))
    humid = float(input("Zadejte vlhkost vzduchu v procentech \n"))
    rain = float(input("Zadejte úhrn srážek v mm \n"))
    
    weather_data = [temp, wind, press, humid, rain]
    return weather_data

def forecast_data():
        
    place_in = input("Vyberte místo, pro které má být IKO vypočítáno (např. Ústí nad Labem). \n")
    while True:
        place = Scraping.check_place(place_in)
        if place == False:
            place_in = input("Toto místo meteobox nezná, zkuste větší město v okolí. \n") 
        else:
            break
        
    date_in = input("Zadejte datum, pro které chcete najít předpověď ve formátu dd. mm. yyyy (např. 03. 07. 2022), můžete využít data do 10 dnů ode dneška. \n")
    while True:
        date = Scraping.check_date(date_in)
        if date == False:
            date_in = input("Toto datum není platné, zkuste ho zadat znovu. \n") 
        else:
            break
        
    time_in = input("Zadejte hodinu, pro kterou chcete najít předpověd ve formátu hh:00 (např. 05:00)\n")
    while True:
        time = Scraping.check_time(place, date, time_in)
        if time == False:
            time_in = input("Tato hodina není platná, zkuste jí zadat znovu. \n") 
        else:
            break
    info = [place, date, time]
    return info

def main():
    
    print("\nNyní můžete zvolit model (doporučuji model 3) a zadat ručně potřebné hodnoty, nebo zadat název obce, datum a čas a nechat program spočítat IKO z předpovědi počasí na https://meteobox.cz/. \n")
    
    mod = input("Zvolte model (model 1, model 2, nebo model 3). \n")
    while True:
        if mod == "model 1" or mod == "model 2" or mod == "model 3":
            break 
        else:
            mod = input("Model špatně zadán, zkuste to znovu. \n")
        
    mod = mod.replace(" ","_")
    model = getattr(Tvorba_modelu, mod)
        
    method = input("Zvolte, zda chcete data zadat manuálně, nebo použít předpověď (manual, nebo forecast). \n")
    while True:
        if method == "manual" or method == "forecast":
            break 
        else:
            method = input("Metoda vstupu špatně zadána, zkuste to znovu. \n")
    if method == "manual":
        interpret_IKO(count_IKO(model, manual_data()))
    else:
        interpret_IKO(count_IKO(model, Scraping.main(forecast_data())))
    print("Chcete spočítat jinou hodnotu? (Ano, nebo Ne)")

Zpracovani_dat.main()
Tvorba_modelu.main()

print("Modely připraveny: \n")

print("model 1:")
Tvorba_modelu.model_1.print_model()

print("\nmodel 2:")
Tvorba_modelu.model_2.print_model()

print("\nmodel 3:")
Tvorba_modelu.model_3.print_model()

main()
an = input()
while an != "Ne":
    if an == "Ano":
        main()
    else:
        print("Chcete spočítat jinou hodnotu? (Ano, nebo Ne)")
    an = input()
print("Děkuji za použití programu, Bílý Jakub")