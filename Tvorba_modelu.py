# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 20:07:02 2022

@author: BilKu

Vytváří a pracuje s modely pro předpověď IKO
"""

import numpy
import pandas
from scipy.stats import t
from math import sqrt

class model:
    def __init__(self, coef = None, data = None, results = None, head = None, p_values = None, R2adj = None ):
        self.coef = coef
        self.data = data
        self.results = results
        self.head = head
        self.p_values = p_values
        self.R2adj = R2adj

    def get_data():
        # Vytváří globální proměnnou s daty pro další funkce/metody
        
        global data_all
        data_all = pandas.read_excel("data_2018.xlsx")

    def basic_model():
        # Vytvoří základní model metodou nejmenších čtverců/lineární regrese
        
        model.get_data()
        
        y = data_all["IKO"].values
        data_all.insert(16, "konstanta", [1]*365, True)
        head = data_all.columns
        data = data_all.drop(columns = {"date", "IKO"})
        head = head.drop({"date", "IKO"})
        data = data.values
        data_T = numpy.transpose(data)
       
        first_model = numpy.matmul(numpy.matmul(numpy.linalg.inv(numpy.matmul(data_T, data)), data_T), y)
        
        basic_model = model()
        basic_model.coef = first_model
        basic_model.data = data 
        basic_model.results = y
        basic_model.head = head
        
        return basic_model
    
    def calc_p_values(self):
        # Počítá p hodnoty pro daný model
        
        data = self.data
        IKO = self.results
        
        data_T = numpy.transpose(data)
        IKO_T = numpy.transpose(IKO)
        
        
        dof_SSe = data.shape[0] - self.coef.shape[0]
        Hat_matrix = numpy.matmul(data, numpy.matmul(numpy.linalg.inv(numpy.matmul(data_T, data)), data_T))
        Hat_order = Hat_matrix.shape[0]
        
        SSe = numpy.matmul(IKO_T, numpy.matmul((numpy.identity(Hat_order) - Hat_matrix), IKO))
        MSe = SSe/dof_SSe
        
        C = MSe * numpy.linalg.inv(numpy.matmul(data_T, data))
        p_values = []
        
        for i in range(C.shape[0]):
            
            se_i = sqrt((C[i, i]))
            t_i = self.coef[i] / se_i
        
            p_value =  2 * (1 - t.cdf(abs(t_i), dof_SSe))
            p_values.append(p_value)
    
        p_values = numpy.asarray(p_values)
        return p_values
    
    def add_p_values(self):
        # Přídává p hodnoty k modelu
        
        self.p_values = self.calc_p_values()
        return self

    def adv_model_with_constant(self):
        # Vytváří lepší model vypuštěním veličin, které mají vysokou p hodnotu, ponechává konstantu
        
        new_data = data_all.drop(columns = {"date", "IKO"})
        head = new_data.columns
        columns_to_delete = []

        for i in range(len(self.p_values)):
            if self.p_values[i] > 0.05 and head[i] != "konstanta":
                column_name = head[i]
                new_data = new_data.drop(columns = {column_name})
                columns_to_delete.append(i)
                
        new_head = head.delete(columns_to_delete)

        new_data = new_data.values
        new_data_T = numpy.transpose(new_data)
        new_model_coef = numpy.matmul(numpy.matmul(numpy.linalg.inv(numpy.matmul(new_data_T, new_data)), new_data_T), self.results)
    
        new_model = model()
        
        new_model.coef = new_model_coef
        new_model.data = new_data
        new_model.results = self.results
        new_model.head = new_head
        
        return new_model

    def adv_model_without_constant(self):
        # Vytváří lepší model vypuštěním veličin, které mají vysokou p hodnotu, včetně konstanty     
        
        new_data = data_all.drop(columns = {"date", "IKO"})
        head = new_data.columns
        columns_to_delete = []

        for i in range(len(self.p_values)):
            if self.p_values[i] > 0.05:
                column_name = head[i]
                new_data = new_data.drop(columns = {column_name})
                columns_to_delete.append(i)
                
        new_head = head.delete(columns_to_delete)

        new_data = new_data.values
        new_data_T = numpy.transpose(new_data)
        new_model_coef = numpy.matmul(numpy.matmul(numpy.linalg.inv(numpy.matmul(new_data_T, new_data)), new_data_T), self.results)
    
        new_model = model()
        
        new_model.coef = new_model_coef
        new_model.data = new_data
        new_model.results = self.results
        new_model.head = new_head
        
        return new_model


    def calc_R2adj(self):
        # Vypočítá hodnotu R2adj pro daný model
        
        data = self.data
        IKO = self.results
        
        data_T = numpy.transpose(data)
        IKO_T = numpy.transpose(IKO)
        
        dof_SSt = data.shape[0]
        SSt = numpy.matmul(IKO_T, numpy.matmul((numpy.identity(dof_SSt) - (1/dof_SSt) * numpy.ones(dof_SSt)), IKO))
        MSt = SSt/dof_SSt
        
        dof_SSe = data.shape[0] - self.coef.shape[0]
        Hat_matrix = numpy.matmul(data, numpy.matmul(numpy.linalg.inv(numpy.matmul(data_T, data)), data_T))
        Hat_order = data.shape[0]
        
        SSe = numpy.matmul(IKO_T, numpy.matmul((numpy.identity(Hat_order) - Hat_matrix), IKO))
        MSe = SSe/dof_SSe
        
        R2adj = 1 - (MSe / MSt)
        
        return R2adj
        
    def add_R2adj(self):
        # Přídává R2adj k modelu
        
        a = self.calc_R2adj()
        if a < 1 and a > 0:
            self.R2adj = a
        else:
            self.R2adj = "Nelze vypočíst"
        return self

    def print_model(self):
        # Zobrazí reprezentaci modelu
        
        for_print = ["proměnná                      koeficient                    p_hodnota"]
        for i in range(len(self.head)):
            variable = self.head[i]
            variable = variable + " " * (30-len(variable)) + str(self.coef[i])
            variable = variable + " " * (60-len(variable)) + str(self.p_values[i])

            for_print.append(variable)

        for i in for_print:
            print(i)

        print("R2adj of model = ", self.R2adj)

def main():
    
    global model_1
    model_1 = model.basic_model()
    model_1.add_p_values()
    model_1.add_R2adj()

    global model_2
    model_2 = model_1.adv_model_with_constant()
    model_2.add_p_values()
    model_2.add_R2adj()
    
    global model_3
    model_3 = model_1.adv_model_without_constant()
    model_3.add_p_values()
    model_3.add_R2adj()
        
main()
