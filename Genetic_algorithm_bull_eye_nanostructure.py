# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 01:24:33 2020

@author: stefa
"""

# -*- coding: utf-8 -*-
"""
Created on Mon May 25 16:23:29 2020

@author: stefa
"""
import importlib.util
#The default paths for windows
spec_win = importlib.util.spec_from_file_location('lumapi', 'C:\\Program Files\\Lumerical\\2020a\\api\\python\\lumapi.py')
#Functions that perform the actual loading
lumapi = importlib.util.module_from_spec(spec_win) # 
spec_win.loader.exec_module(lumapi)
import numpy as np
import matplotlib.pyplot as plt

import random as rd
from random import random
import math as m


Taux_De_Mutation  = 0.02
Taux_De_Selection_Alpha = 0.1
Taux_De_Selection_Beta = 0.005
Taille_Population = 1000
Nbr_Max_Generations = 5000



""" Chromosome = [Rayon_int1, Rayon_int2, Rayon_int3, Epaisseur] """

Epaisseur_max = 100e-9

def Population_initiale(taille_pop):
    Population = []
    for ind in range(taille_pop):
        Rayons_liste = np.linspace(90e-9,1000e-9,2000)
        Rayon_int1 = rd.choice(Rayons_liste)
        Rayon_int2 = rd.choice(Rayons_liste)
        Rayon_int3 = rd.choice(Rayons_liste)
        Epaisseur = Epaisseur_max*random()
        Individu = [Rayon_int1, Rayon_int2, Rayon_int3, Epaisseur]
        Population.append(Individu)
    return Population

def Score_individu(individu):
    Rayon_int1 = individu[0]
    Rayon_int2 = individu[1]
    Rayon_int3 = individu[2]
    Epaisseur = individu[3]
    
    Rayon_ext1 = Rayon_int1 + Epaisseur
    Rayon_ext2 = Rayon_int2 + Epaisseur
    Rayon_ext3 = Rayon_int3 + Epaisseur
    
    fdtd = lumapi.FDTD()
    fdtd.addring(name="new_ring", material="Si (Silicon) - Palik", x=0, y=0, inner_radius = 5e-9, outer_radius = 100e-9, z=0, z_span=150e-9, theta_start=0, theta_stop=360)
    fdtd.addring(name="ring1", material="Si (Silicon) - Palik", x=0, y=0, inner_radius = Rayon_int1, outer_radius = Rayon_ext1, z=0, z_span=150e-9, theta_start=0, theta_stop=360)
    fdtd.addring(name="ring2", material="Si (Silicon) - Palik", x=0, y=0, inner_radius = Rayon_int2, outer_radius = Rayon_ext2, z=0, z_span=150e-9, theta_start=0, theta_stop=360)
    fdtd.addring(name="ring3", material="Si (Silicon) - Palik", x=0, y=0, inner_radius = Rayon_int3, outer_radius = Rayon_ext3, z=0, z_span=150e-9, theta_start=0, theta_stop=360)
    fdtd.addplane(injection_axis='z', direction="backward", x=0, x_span=3000e-9, y=0, y_span=3000e-9, z=500e-9, wavelength_start = 600e-9, wavelength_stop=600e-9)
    fdtd.addpower(name="field_profile", monitor_type=7, x=0, x_span=500e-9, y=0, y_span=500e-9, z=0)
    fdtd.addfdtd(dimension=2, x=0, x_span=3000e-9, y=0, y_span=3000e-9, z=0, z_span=1000e-9) #dimension = 2 =3D
    fdtd.addmesh(structure="new_ring", override_x_mesh=1, override_y_mesh=1, override_z_mesh=1, dx=10e-9, dy=10e-9, dz=10e-9)
    fdtd.addmesh(structure="ring1", override_x_mesh=1, override_y_mesh=1, override_z_mesh=1, dx=10e-9, dy=10e-9, dz=10e-9)
    fdtd.addmesh(structure="ring2", override_x_mesh=1, override_y_mesh=1, override_z_mesh=1, dx=10e-9, dy=10e-9, dz=10e-9)
    fdtd.addmesh(structure="ring3", override_x_mesh=1, override_y_mesh=1, override_z_mesh=1, dx=10e-9, dy=10e-9, dz=10e-9)
    fdtd.setglobalmonitor("frequency points", 1.)
    
    fdtd.save("API_Test")
    fdtd.run()
    H2= fdtd.getmagnetic("field_profile");
    
    valeur_centre = H2[:,:,0][25,25][0]
    return valeur_centre
    
def Evaluation_Population(Population):
    #Classe la population.
    #Retourne une liste de tuple (individu, score) classé du meilleur au moins bon.
    notation_individus = []
    for individu in Population:
        notation_individus.append((individu, Score_individu(individu)))
    return sorted(notation_individus, key=lambda x: x[1], reverse=True)

def Selection_Population(Classement_population):
    score_pop = 0
    Population_tri = []
    for individu, score in Classement_population:
        score_pop += score
        Population_tri.append(individu)
    Taille_population = len(Population_tri)
    score_pop = score_pop / len(Population_tri)
    print("Score population : ", score_pop)
    
    Nbr_alpha = int(Taille_population*Taux_De_Selection_Alpha)
    # Selection des alpha pour devenir parents
    parents = Population_tri[:Nbr_alpha]
    
    # Selection de quelques Beta pour promouvor la diversité génétique
    for individu in Population_tri[Nbr_alpha:]:
        if random() < Taux_De_Selection_Beta:
            parents.append(individu)
    
    return parents

def Mutations(parents):
    for individu in parents:
        if random() < Taux_De_Mutation:
            Rayons_liste = np.linspace(90e-9,1000e-9,2000)
            individu[0] = rd.choice(Rayons_liste)
            individu[1] = rd.choice(Rayons_liste)
            individu[2] = rd.choice(Rayons_liste)
            individu[3] = Epaisseur_max*random()
    return parents

def Reproduction(parents):
    #parents_len = len(parents)
    desired_len = Taille_Population
    enfants = []
    while len(enfants) < desired_len:
        father = rd.choice(parents)
        mother = rd.choice(parents)
        if father != mother:
            rand_num = random()
            if rand_num < 0.2:
                child = [father[0], father[1], father[2], mother[3]]
            elif 0.2 <= rand_num < 0.4:
                child = [father[0], father[1], mother[2], father[3]]
            elif 0.4 <= rand_num < 0.6:
                child = [father[0], mother[1], father[2], father[3]]
            elif 0.6 <= rand_num < 0.8:
                child = [mother[0], father[1], father[2], father[3]]
            else:
                child = [mother[0], father[1], father[2], mother[3]]
            enfants.append(child)

    return enfants
            
            
            
#Création population initiale

population = Population_initiale(Taille_Population)
nbr_generations = 0

while nbr_generations < Nbr_Max_Generations:
    print('génération n°',nbr_generations)
    classement_population = Evaluation_Population(population)  
    print(classement_population)
    parents = Selection_Population(classement_population)
    parents_post_mutations = Mutations(parents)
    enfants = Reproduction(parents)
    population = enfants
    nbr_generations += 1 


    
        
    
    
