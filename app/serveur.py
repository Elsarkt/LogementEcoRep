from typing import Union
from fastapi import FastAPI, Request #ajout request
# from app.templates.camembert import creerPage
import sqlite3
#interfaçage
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

#api météo
from contextlib import closing
from urllib.request import urlopen
import dateutil.parser
import json
import os.path

#graphe
from datetime import datetime
import random

#configuration : création capteur
from fastapi import Form
from fastapi.responses import JSONResponse


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static") #route crée : http://localhost:8000/public/..

templates = Jinja2Templates(directory="app/templates") #objet va chercher les templates dans le repertoire adequat

# @app.on_event("startup")
# async def startup():
#     await remplissage()

def dict_factory(cursor, row): 
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("home.html",{'request':request}) #templateResponse crée html à partir d'un template


############### Meteo concept prévisions à afficher
@app.post("/affichageMeteoCommune")
async def affichageMeteoCommune(request : Request, ville : str = Form(...), cp : int = Form(...)):
    MON_TOKEN = '04965bbbfb6fadabdd3e79edb27b21b78af295d90014db1c99c4b40cf9af5504'
    insee_code = 0

    conn = sqlite3.connect("./app/logement.db")
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    res = cursor.execute("SELECT id, ref_commerce, date_insertion, port_comm, idType, idPiece FROM Capteur_actio")
    res = res.fetchall()
    mesures={}
    unites={}

    for i in res:
        #recuperation mesure
        cursor.execute("SELECT valeur FROM Mesure WHERE id = ?", (i['id'],))
        mesure = cursor.fetchone()
        mesures[i['id']] = mesure['valeur']

        #recuperation unite
        cursor.execute("SELECT unite FROM Type_capteur_actio WHERE id = ?", (i['idType'],))
        unite = cursor.fetchone()
        unites[i['id']] = unite['unite']

    conn.close()    

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
            return templates.TemplateResponse("tempsreel.html", {'request': request, "erreur": "Ville non trouvée"})

        else : 
            with closing(urlopen('https://api.meteo-concept.com/api/forecast/daily?token={}&insee={}'.format(MON_TOKEN, insee_code))) as f: #mon_token sera-il bien remplacé ?
                decoded = json.loads(f.read()) #conversion JSON en dictionnaire : city={'name'=...} forecast={..........}
                (city,forecast) = (decoded[k] for k in ('city','forecast')) # ({name="",...},{update="",...}) tuple de deux dictionnaires
                previsions=[]
                #print("Ville de {}".format(city['name']))
                jour = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
                for i ,f in enumerate(forecast): # forecast[0], forecast[1],...
                    indiceDay = dateutil.parser.parse(f['datetime']).weekday() # Lundi : 0, Mardi : 1, etc. 
                    #print(u"{} : Température minimum : {}°C, Température maximale : {}°C, Précipitations : {}mm\n".format(jour[indiceDay], f['tmin'], f['tmax'], f['rr10']))
                    previsions.append({"jour":jour[indiceDay], "temp_min":f['tmin'], "temp_max" : f['tmax'], "precipitations" : f['rr10']})
                    if i ==  5 : 
                        break
                    
            # return {"Ville" : city['name'], "Prévisions" : previsions }
            return templates.TemplateResponse("tempsreel.html",{'request':request, "Ville": decoded['city']['name'],"previsions":previsions, "res":res, "mesures":mesures, "unites":unites}) #templateResponse crée html à partir d'un template
            
    return {"Message" : "Requête à meteo concept non envoyée"}


################# Affichage Google Chart
@app.get("/syntheseCamembert")
async def syntheseCamembert(request : Request, periode : str): #prend en paramètres des factures
    conn = sqlite3.connect("./app/logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT type_fact, montant, date_fact  FROM Facture;") #interroge la base de donnée
    res = res.fetchall()
    conn.close()
      
    elec = copro = dechets = autres = eau = 0
    for i in res:
        if i[0] == "électricité" :
            elec += i[1]
        elif i[0] == "eau" : 
            eau += i[1]
        elif i[0] == "déchets" :
            dechets += i[1]
        elif i[0] == "copropriété" :
            copro = i[1]
        else :
            autres += i[1]

    # Création html libre sans interface
    liste = [["Type de Facture", "Montant"],["électricité", elec], ["eau", eau], ["déchets", dechets], ["copropriété", copro]] # Liste imbriquée avec type_fact et montant
    creerPage(liste)
    return {"message": "Données générées pour Google Charts", "données": liste}

    
################# Affichage Graphe conso
@app.get("/grapheConso")
async def grapheConso(request : Request, periode : str, asked: str): #prend en paramètres des factures
    conn = sqlite3.connect("./app/logement.db") 
    cursor = conn.cursor() 
    #disjonction de cas conso ou eco 
    if asked == "conso" : #récupération de la conso des facturse
        res = cursor.execute("SELECT type_fact, conso, date_fact  FROM Facture;") #interroge la base de donnée
    elif asked == "eco" : #récupération du montant des facturse
        res = cursor.execute("SELECT type_fact, montant, date_fact  FROM Facture;") #interroge la base de donnée
    else : 
        return {"MEssage":"Erreur d'URL"}
    res = res.fetchall()
    conn.close()

    #####Echelle de temps : un an, chaque mois
    #pas de disjonction de cas car on récupère direct le deuxième élément de res, soit "montant" soit "conso" en fct de la précédente disjonciton 
    if periode == "an" :
        consoElec = [0]*12
        consoEau = [0]*12
        consoDechets = [0]*12
        consoCopro =[0]*12
        mois = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        print(res)
        for i in res:
            date_obj = datetime.strptime(i[2], "%Y-%m-%d %H:%M:%S") 
            print(i[2])
            if date_obj.year == 2024:
                moisFacture = date_obj.month-1 #récupéraition du mois de la facture
                if i[0] == "électricité" :
                    consoElec[moisFacture] += i[1] 
                elif i[0] == "eau" : 
                    consoEau[moisFacture] += i[1] 
                elif i[0] == "déchets" :
                    consoDechets[moisFacture] += i[1] 
                elif i[0] == "copropriété" :
                    consoCopro[moisFacture] += i[1] 
                else :
                    return {"Message":"erreur1", "i[0]":i[0],"moisFacture":moisFacture, "res":res}
        print(consoElec)

        # Tableaux des éconoomies réalisées pour chaque type de facture
        if asked == "eco" :
            ecoElec = [0]*12
            ecoEau = [0]*12
            ecoDechets = [0]*12
            ecoCopro = [0]*12

            for i in range(0,12) : 
                # pourcentage d'augmentation pour les montnats qui auraient été appliqué sans ecorep
                augmentation = random.uniform(1.05, 1.20)

                ecoElec[i] = int(consoElec[i]*augmentation)
                ecoEau[i] = int(consoEau[i]*augmentation)
                ecoDechets[i] = int(consoDechets[i]*augmentation)
                ecoCopro[i] = int(consoCopro[i]*augmentation)
            
            #retourne pour chaque type de facture le montant et du montant qui auraient été sans ecorep
            return templates.TemplateResponse("./eco.html", {"request": request, "consoElec":consoElec, "consoEau":consoEau, "consoDechets":consoDechets, "consoCopro":consoCopro, "labels":mois, "ecoElec":ecoElec, "ecoEau":ecoEau, "ecoDechets":ecoDechets, "ecoCopro":ecoCopro})

        #retourne pour chaque type de facture la de conso
        return templates.TemplateResponse("./conso.html", {"request": request, "consoElec":consoElec, "consoEau":consoEau, "consoDechets":consoDechets, "consoCopro":consoCopro, "labels":mois})
        
    ###Echelle de temps : deux ans, chaque annéé
    elif periode == "deuxAns":
        consoElec = [0]*2
        consoEau = [0]*2
        consoDechets = [0]*2
        consoCopro =[0]*2
        annee = [2023, 2024] 
        for i in res:
            date_obj = datetime.strptime(i[2], "%Y-%m-%d %H:%M:%S") 
            if date_obj.year > 2023 or date_obj.year == 2023: #pas de facture antéirieure à 2023 
                anFacture = date_obj.year #récupéation de l'annee de la facture
                print(anFacture)
                if i[0] == "électricité" :
                    consoElec[anFacture-2024] += i[1] 
                elif i[0] == "eau" : 
                    consoEau[anFacture-2024] += i[1] 
                elif i[0] == "déchets" :
                    consoDechets[anFacture-2024] += i[1] 
                elif i[0] == "copropriété" :
                    consoCopro[anFacture-2024] += i[1] 
                else :
                    print(i)
                    print(i[0])
                    return {"Message":"erreur2", "consoElec":consoElec}

        # Tableau  conoomies réalisées pour chaque type de facture
        if asked == "eco" :
            ecoElec = [0]*2
            ecoEau = [0]*2
            ecoDechets = [0]*2
            ecoCopro = [0]*2

            for i in range(0,2) : 
                # pourcentage d'augmentation pour les montnats qui auraient été appliqué sans ecorep
                augmentation = random.uniform(1.05, 1.20)

                ecoElec[i] = int(consoElec[i]*augmentation)
                ecoEau[i] = int(consoEau[i]*augmentation)
                ecoDechets[i] = int(consoDechets[i]*augmentation)
                ecoCopro[i] = int(consoCopro[i]*augmentation)

            #retourne pour chaque type de facture le montant et du montant qui auraient été sans ecorep
            return templates.TemplateResponse("./eco.html", {"request": request, "consoElec":consoElec, "consoEau":consoEau, "consoDechets":consoDechets, "consoCopro":consoCopro, "labels":annee,"ecoElec":ecoElec, "ecoEau":ecoEau, "ecoDechets":ecoDechets, "ecoCopro":ecoCopro})
        
        #retourne pour chaque type de facture la de conso
        return templates.TemplateResponse("./conso.html", {"request": request, "consoElec":consoElec, "consoEau":consoEau, "consoDechets":consoDechets, "consoCopro":consoCopro, "labels":annee})

   
################## LOGEMENT 
@app.post("/creerLogement")
async def creerLogement(adresse : str, telephone : str):
    conn = sqlite3.connect("./app/logement.db") #connexion crée avec la db
    cursor = conn.cursor() #curseur crée dans la db
    cursor.execute("INSERT INTO Logement (adresse, telephone) VALUES (?, ?)", (adresse, telephone)) #requête sql à éxecuter
    conn.commit() #envoyer la requête
    ip_logement = cursor.lastrowid 
    
    #  répérer les infos du logement qui vient d'être crée
    res = cursor.execute("SELECT ip, adresse, date_insertion, telephone FROM Logement WHERE ip = ?", (ip_logement,))
    logement = res.fetchone() #récupéré les éléments de LA ligne intéréssée sous forme de liste
    if logement is None:
        conn.close()
        return {"Erreur": "Le logement n'a pas été trouvé dans la base de données après l'insertion"}
    
    conn.close()
    return {"message":"logement crée", "ip_logement":logement[0], "adresse":logement[1], "date_insertion":logement[2], "telephone":logement[3]}
 
@app.get("/getLogement/adresse")
async def getlogement_adresse(adresse : str) :
    conn = sqlite3.connect("./app/logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT * FROM Logement WHERE adresse = ?",(adresse,) ) #interroge la base de donnée
    res = res.fetchall()
    conn.close()
    return {"res" : res}
    
@app.get("/getLogement/telephone")
async def getlogement_telehone(telephone : str) :
    conn = sqlite3.connect("./app/logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT * FROM Logement WHERE telephone = ?",(telephone,) ) #interroge la base de donnée
    res = res.fetchall()
    conn.close()
    return {"res" : res}

@app.get("/getLogement/ip")
async def getlogement_ip(ip : int) :
    conn = sqlite3.connect("./app/logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT * FROM Logement WHERE ip = ?",(ip,) ) #interroge la base de donnée
    res = res.fetchall()
    conn.close()
    return {"res" : res}

####################### Facture
@app.post("/creerFacture")
async def creerFacture(montant : int, type_fact : str, conso:str, unite, idLogement : int):
    conn = sqlite3.connect("./app/logement.db") #connexion crée avec la db
    cursor = conn.cursor() #curseur crée dans la db
    cursor.execute("INSERT INTO Facture (montant, type_fact, conso, unite, idLogement) VALUES (?, ?, ?, ?, ?)", (montant, type_fact, conso, unite, idLogement)) #requête sql à éxecuter
    conn.commit() #envoyer la requête
    id_facture = cursor.lastrowid 
    
    #  répérer les infos du logement qui vient d'être crée
    res = cursor.execute("SELECT id, montant, date_fact, type_fact, conso, unite, idLogement FROM Facture WHERE id = ?", (id_facture,))
    facture = res.fetchone() #récupéré les éléments de LA ligne intéréssée sous forme de liste
    if facture is None:
        conn.close()
        return {"Erreur": "La facture n'a pas été trouvé dans la base de données après l'insertion"}
    
    conn.close()
    return {"message":"facture crée", "id":facture[0], "montant":facture[1], "date_fact":facture[2], "type_fact":facture[3], "conso":facture[4], "unite":facture[5], "idLogement":facture[6]}

@app.get("/getFacture/id")
async def getfacture_id(id : int) :
    conn = sqlite3.connect("./app/logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT * FROM Facture WHERE id = ?",(id,) ) #interroge la base de donnée
    res = res.fetchall()
    conn.close()
    return {"res" : res}

@app.get("/getFacture/montant")
async def getfacture_montant(montant : int) :
    conn = sqlite3.connect("./app/logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT * FROM Facture WHERE montant = ?",(montant,) ) #interroge la base de donnée
    res = res.fetchall()
    conn.close()
    return {"res" : res}

@app.get("/getFacture/date_fact") #type date_fact ????????
async def getfacture_date_fact(date_fact : str) :
    conn = sqlite3.connect("./app/logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT * FROM Facture WHERE id = ?",(date_fact,) ) #interroge la base de donnée
    res = res.fetchall()
    conn.close()
    return {"res" : res}

@app.get("/getFacture/type_fact")
async def getfacture_type_fact(type_fact : str) :
    conn = sqlite3.connect("./app/logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT * FROM Facture WHERE type_fact = ?",(type_fact,) ) #interroge la base de donnée
    res = res.fetchall()
    conn.close()
    return {"res" : res}

@app.get("/getFacture/conso")
async def getfacture_conso(conso : str) :
    conn = sqlite3.connect("./app/logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT * FROM Facture WHERE conso = ?",(conso,) ) #interroge la base de donnée
    res = res.fetchall()
    conn.close()
    return {"res" : res}

@app.get("/getFacture/idLogement")
async def getfacture_idLogement(idLogement: int) :
    conn = sqlite3.connect("./app/logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT * FROM Facture WHERE idLogement = ?",(idLogement,) ) #interroge la base de donnée
    res = res.fetchall()
    conn.close()
    return {"res" : res}


################# PIECE
@app.post("/creerPiece")
async def creerPiece(nom: str, coordx: int, coordy: int, coordz: int, idLogement: int):
    conn = sqlite3.connect("./app/logement.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Piece (nom, coordx, coordy, coordz, idLogement) VALUES (?, ?, ?, ?, ?)", (nom, coordx, coordy, coordz, idLogement))
    conn.commit()
    id_piece = cursor.lastrowid

    res = cursor.execute("SELECT id, nom, coordx, coordy, coordz, idLogement FROM Piece WHERE id = ?", (id_piece,))
    piece = res.fetchone()
    if piece is None:
        conn.close()
        return {"Erreur": "La pièce n'a pas été trouvée dans la base de données après l'insertion"}

    conn.close()
    return {"message": "pièce créée", "id_piece": piece[0], "nom": piece[1], "coordx": piece[2], "coordy": piece[3], "coordz": piece[4], "idLogement": piece[5]}

@app.get("/getPiece/idLogement") #obtenir les informations des pièces du logement n°idLogment
async def getPiece_idLogement(idLogement: int):
    conn = sqlite3.connect("./app/logement.db")
    cursor = conn.cursor()
    res = cursor.execute("SELECT * FROM Piece WHERE idLogement = ?", (idLogement,))
    res = res.fetchall()
    conn.close()
    return {"res": res}

################## CAPTEUR_ACTIO
@app.get("/getCapteurs")
async def getCapteurs(request:Request):
    conn = sqlite3.connect("./app/logement.db")
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    res = cursor.execute("SELECT id, ref_commerce, date_insertion, port_comm, idType, idPiece FROM Capteur_actio")
    res = res.fetchall()
    mesures={}
    unites={}
    for i in res :
        mesure = cursor.execute("SELECT valeur FROM Mesure WHERE id = ?",(i['id'],))
        mesure = mesure.fetchone()
        mesures[i['id']]=mesure['valeur']
        unite = cursor.execute("SELECT unite FROM Type_capteur_actio WHERE id = ?",(i['idType'],))
        unite = unite.fetchone()
        unites[i['id']]=unite['unite']
        print(mesure)
        
    conn.close()
    print(mesures)
    return templates.TemplateResponse("./tempsreel.html", {"request": request, "res":res, "mesures":mesures, "unites":unites})


@app.post("/creerCapteurActio")
async def creerCapteurActio(ref_commerce: str, port_comm: int, idType: int, idPiece: int):
    conn = sqlite3.connect("./app/logement.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Capteur_actio (ref_commerce, port_comm, idType, idPiece) VALUES (?, ?, ?, ?)",(ref_commerce, port_comm, idType, idPiece))
    conn.commit()
    id_capteur = cursor.lastrowid

    res = cursor.execute("SELECT id, ref_commerce, date_insertion, port_comm, idType, idPiece FROM Capteur_actio WHERE id = ?",(id_capteur,))
    capteur = res.fetchone()
    if capteur is None:
        conn.close()
        return {"Erreur": "Le capteur/actionneur n'a pas été trouvé dans la base de données après l'insertion"}

    conn.close()
    return {"message": "capteur/actionneur créé", "id_capteur": capteur[0], "ref_commerce": capteur[1], "date_insertion": capteur[2], "port_comm": capteur[3], "idType": capteur[4], "idPiece": capteur[5]}


# # Créer capteur VIA FORM
@app.get("/getCapteurActiForm")
async def getCapteurActioForm(request: Request):
    return templates.TemplateResponse("configurations.html", {"request": request})

def ajoutMesureRand(idCapteur_i : int) :
    if idCapteur_i == 1 : 
        valeur_i = random.randint(-60,60)
    elif idCapteur_i == 2 :
        valeur_i = random.randint(0,100)
    elif idCapteur_i == 3 :
        valeur_i = random.randint(0,200)  
    elif idCapteur_i == 4 : 
        valeur_i = random.randint(0,500)
    else : 
        valeur_i = random.randint(0,1)
    
    return valeur_i


@app.post("/creerCapteurActioForm")
# nom des param identiques à ceux dans le html : name=""
async def creerCapteurActioForm( request: Request, ref_commerce: str = Form(...),port_comm: int = Form(...),idType: int = Form(...),idPiece: int = Form(...)):
    print("Dans creerCapteurActioForm")
    conn = sqlite3.connect("./app/logement.db")
    print("Dans conexion sqlite")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Capteur_actio (ref_commerce, port_comm, idType, idPiece) VALUES (?, ?, ?, ?)",
        (ref_commerce, port_comm, idType, idPiece)
    )
    conn.commit()
    print("Après insert into")

    # Retourner infos capteur crée
    id_capteur = cursor.lastrowid
    # res = cursor.execute("SELECT id, ref_commerce, date_insertion, port_comm, idType, idPiece FROM Capteur_actio WHERE id = ?", (id_capteur,))
    # capteur = res.fetchone()
    # if capteur is None:
    #     conn.close()
    #     return {"Erreur": "Le capteur/actionneur n'a pas été trouvé dans la base de données après l'insertion"}

    # Ajouter une mesure random
    mesure = ajoutMesureRand(id_capteur)
    cursor.execute("INSERT INTO Mesure (valeur, idCapteur) VALUES (?, ?)",(mesure, id_capteur))
    conn.commit()
    conn.close()
    return templates.TemplateResponse("configurations.html", {"request": request})


@app.get("/getCapteurActio/idCapteur")
async def getCapteurActio_idCapteur(idCapteur: int):
    conn = sqlite3.connect("./app/logement.db")
    cursor = conn.cursor()
    res = cursor.execute("SELECT * FROM Capteur_actio WHERE id = ?", (idCapteur,))
    res = res.fetchall()
    conn.close()
    return {"res": res}

################## TYPE_CAPTEUR_ACTIO 
@app.post("/creerTypeCapteurActio")
async def creerTypeCapteurActio(unite: str, val_min: int, val_max: int):
    conn = sqlite3.connect("./app/logement.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Type_capteur_actio (unite, val_min, val_max) VALUES (?, ?, ?)",(unite, val_min, val_max))
    conn.commit()
    id_type = cursor.lastrowid

    res = cursor.execute("SELECT id, unite, val_min, val_max FROM Type_capteur_actio WHERE id = ?",(id_type,))
    type_capteur = res.fetchone()
    if type_capteur is None:
        conn.close()
        return {"Erreur": "Le type de capteur/actionneur n'a pas été trouvé après l'insertion"}

    conn.close()
    return {"message": "type capteur/actionneur créé", "id_type": type_capteur[0], "unite": type_capteur[1], "val_min": type_capteur[2],"val_max": type_capteur[3]}

@app.get("/getTypeCapteurActio/id") #obtenir infos du type d'un capteur connaissant son numéro d'id
async def getTypeCapteurActio_id(id: int):
    conn = sqlite3.connect("./app/logement.db")
    cursor = conn.cursor()
    res = cursor.execute("SELECT * FROM Capteur_actio WHERE idPiece = ?", (id,))
    res = res.fetchall()
    conn.close()
    return {"res": res}

################## MESURE 
@app.post("/creerMesure")
async def creerMesure(valeur: int, idCapteur: int):
    conn = sqlite3.connect("./app/logement.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Mesure (valeur, idCapteur) VALUES (?, ?)",(valeur, idCapteur))
    conn.commit()
    id_mesure = cursor.lastrowid

    res = cursor.execute("SELECT id, valeur, date_insertion, idCapteur FROM Mesure WHERE id = ?",(id_mesure,))
    mesure = res.fetchone()
    if mesure is None:
        conn.close()
        return {"Erreur": "La mesure n'a pas été trouvée après l'insertion"}

    conn.close()
    return {"message": "mesure créée", "id_mesure": mesure[0], "valeur": mesure[1], "date_insertion": mesure[2], "idCapteur": mesure[3]}

@app.get("/getMesure/idCapteur") #Mesure obtenue en fonction du capteur n° idCpateur considéré
async def getMesure_idCapteur(idCapteur: int):
    conn = sqlite3.connect("./app/logement.db")
    cursor = conn.cursor()
    res = cursor.execute("SELECT * FROM Mesure WHERE idCapteur = ?", (idCapteur,))
    res = res.fetchall()
    conn.close()
    return {"res": res}

