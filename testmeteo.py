from typing import Union
from fastapi import FastAPI
from camembert import creerPage
import sqlite3
#api météo
from contextlib import closing
from urllib.request import urlopen
import dateutil.parser
import json




############### Meteo concept prévisions à afficher
# ville = 'Rennes-sur-Loue'
# MON_TOKEN = '04965bbbfb6fadabdd3e79edb27b21b78af295d90014db1c99c4b40cf9af5504'

# with closing(urlopen('https://api.meteo-concept.com/api/location/cities?token={}&search={}'.format(MON_TOKEN, ville))) as f:
#      cities = json.loads(f.read())['cities']
#      print(u'Il y a {} villes correspondant à la recherche'.format(len(cities)))
#      for city in cities:
#         print(u'\t{}, Code postal :{}, Code insee :{}\n'.format(city['name'], city['cp'], city['insee']))

#         # Pour chaque ville qui contient le nom de la ville cherchée, on affiche la météo pour les 5 prochains jours
#         insee_code = city['insee']
#         with closing(urlopen('https://api.meteo-concept.com/api/forecast/daily?token={}&insee={}'.format(MON_TOKEN, insee_code))) as f: #mon_token sera-il bien remplacé ?
#             decoded = json.loads(f.read()) #conversion JSON en dictionnaire : city={'name'=...} forecast={..........}
#             (city,forecast) = (decoded[k] for k in ('city','forecast')) # ({name="",...},{update="",...}) tuple de deux dictionnaires
            
#             print("Ville de {}".format(city['name']))
#             jour = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
#             for i ,f in enumerate(forecast): # forecast[0], forecast[1],...
#                 indiceDay = dateutil.parser.parse(f['datetime']).weekday() # Lundi : 0, Mardi : 1, etc.
#                 print(u"{} : Température minimum : {}°C, Température maximale : {}°C, Précipitations : {}mm\n".format(jour[indiceDay], f['tmin'], f['tmax'], f['rr10']))
#                 if i ==  5 : 
#                     break 


def fonction() :
    MON_TOKEN = '04965bbbfb6fadabdd3e79edb27b21b78af295d90014db1c99c4b40cf9af5504'
    insee_code = 0
    cp : int = 91300
    ville = 'massy'

    with closing(urlopen('https://api.meteo-concept.com/api/location/cities?token={}&search={}'.format(MON_TOKEN, ville))) as f:
        cities = json.loads(f.read())['cities']
        #print(u'Il y a {} villes correspondant à la recherche'.format(len(cities)))

        found = False
        for city in cities:
            #print('{}, Code postal :{}, Code insee :{},  Type CP retourné : {}\n'.format(city['name'], city['cp'], city['insee'], type(city['cp'])))
            if  cp == city['cp'] : #recherche de la ville dont on a tapé le nom et le cp
                insee_code = city['insee']
                print(insee_code)
                found = True
                break        
        if not found : 
            return {"Message" : "Ville non trouvée"}

        else : 
            with closing(urlopen('https://api.meteo-concept.com/api/forecast/daily?token={}&insee={}'.format(MON_TOKEN, insee_code))) as f: #mon_token sera-il bien remplacé ?
                decoded = json.loads(f.read()) #conversion JSON en dictionnaire : city={'name'=...} forecast={..........}
                (city,forecast) = (decoded[k] for k in ('city','forecast')) # ({name="",...},{update="",...}) tuple de deux dictionnaires
                previsions = {}
                #print("Ville de {}".format(city['name']))
                jour = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
                for i ,f in enumerate(forecast): # forecast[0], forecast[1],...
                    indiceDay = dateutil.parser.parse(f['datetime']).weekday() # Lundi : 0, Mardi : 1, etc.
                    #print(u"{} : Température minimum : {}°C, Température maximale : {}°C, Précipitations : {}mm\n".format(jour[indiceDay], f['tmin'], f['tmax'], f['rr10']))
                    previsions["jour[indiceDay]"] = {"Température minimum":f['tmin'], "Température maximale" : f['tmax'], "Précipitations" : f['rr10']}
                    if i ==  5 : 
                        break
                    
            return {"Ville" : city['name'], "Prévisions" : previsions }

    return {"Message" : "Requête à meteo concept non envoyée"}


# fonction()


# from contextlib import closing
# from urllib.request import urlopen
# import json

# MON_TOKEN = '04965bbbfb6fadabdd3e79edb27b21b78af295d90014db1c99c4b40cf9af5504'
# insee_code = 0
# cp = 91300  # Code postal recherché
# ville = 'Massy'  # Nom de la ville recherché

# def fonction() : 
# # Effectuer la requête API pour rechercher des villes
#     with closing(urlopen(f'https://api.meteo-concept.com/api/location/cities?token={MON_TOKEN}&search={ville}')) as f:
#         cities = json.loads(f.read())['cities']
#         print(f'Il y a {len(cities)} villes correspondant à la recherche')

#         found = False  # Variable pour savoir si on a trouvé la ville avec le bon code postal
#         for city in cities:
#             print(f"Ville trouvée : {city['name']}, CP retourné : {city['cp']}, Type CP retourné : {type(city['cp'])}")

#             # Vérification stricte du code postal
#             if city['name'] == ville and city['cp'] == cp:
#                 insee_code = city['insee']
#                 print(f"Ville correcte trouvée: {city['name']}, Code postal : {city['cp']}, Code INSEE : {insee_code}")
#                 found = True
#                 break

#         if not found:
#             print(f"Ville non trouvée avec le code postal {cp}")
#         return {"Message": "Ville non trouvée"}

fonction()
