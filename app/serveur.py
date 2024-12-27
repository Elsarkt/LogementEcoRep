from typing import Union
from fastapi import FastAPI, Request #ajout request
from app.templates.camembert import creerPage
import sqlite3
#interfaçage
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

#api météo
from contextlib import closing
from urllib.request import urlopen
import dateutil.parser
import json


app = FastAPI()

app.mount("/static", StaticFiles(directory="public"), name="public") #route crée : http://localhost:8000/public/..

templates = Jinja2Templates(directory="app/templates") #objet va chercher les templates dans le repertoire adequat

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(request, "home.html") #templateResponse crée html à partir d'un template



############### Meteo concept prévisions à afficher
@app.get("/getMeteoVille")
async def affichageMeteoCommune(ville : str, cp : int):
    MON_TOKEN = '04965bbbfb6fadabdd3e79edb27b21b78af295d90014db1c99c4b40cf9af5504'
    insee_code = 0

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
                    previsions[jour[indiceDay]] = {"Température minimum":f['tmin'], "Température maximale" : f['tmax'], "Précipitations" : f['rr10']}
                    if i ==  5 : 
                        break
                    
            return {"Ville" : city['name'], "Prévisions" : previsions }

    return {"Message" : "Requête à meteo concept non envoyée"}


################# Affichage Google Chart
@app.get("/syntheseCamembert")
async def syntheseCamembert(): #prend en paramètres des factures
    conn = sqlite3.connect("logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT type_fact, montant FROM Facture") #interroge la base de donnée
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
    liste = [["Type de Facture", "Montant"],["électricité", elec], ["eau", eau], ["déchets", dechets], ["copropriété", copro]] # Liste imbriquée avec type_fact et montant
    creerPage(liste) 
           
    return {"message": "Données générées pour Google Charts", "données": liste}


################## LOGEMENT 
@app.post("/creerLogement")
async def creerLogement(adresse : str, telephone : str):
    conn = sqlite3.connect("logement.db") #connexion crée avec la db
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
    conn = sqlite3.connect("logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT * FROM Logement WHERE adresse = ?",(adresse,) ) #interroge la base de donnée
    res = res.fetchall()
    conn.close()
    return {"res" : res}
    
@app.get("/getLogement/telephone")
async def getlogement_telehone(telephone : str) :
    conn = sqlite3.connect("logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT * FROM Logement WHERE telephone = ?",(telephone,) ) #interroge la base de donnée
    res = res.fetchall()
    conn.close()
    return {"res" : res}

@app.get("/getLogement/ip")
async def getlogement_ip(ip : int) :
    conn = sqlite3.connect("logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT * FROM Logement WHERE ip = ?",(ip,) ) #interroge la base de donnée
    res = res.fetchall()
    conn.close()
    return {"res" : res}

####################### Facture
@app.post("/creerFacture")
async def creerFacture(montant : int, type_fact : str, conso:str, idLogement : int):
    conn = sqlite3.connect("logement.db") #connexion crée avec la db
    cursor = conn.cursor() #curseur crée dans la db
    cursor.execute("INSERT INTO Facture (montant, type_fact, conso, idLogement) VALUES (?, ?, ?, ?)", (montant, type_fact, conso, idLogement)) #requête sql à éxecuter
    conn.commit() #envoyer la requête
    id_facture = cursor.lastrowid 
    
    #  répérer les infos du logement qui vient d'être crée
    res = cursor.execute("SELECT id, montant, date_fact, type_fact, conso, idLogement FROM Facture WHERE id = ?", (id_facture,))
    facture = res.fetchone() #récupéré les éléments de LA ligne intéréssée sous forme de liste
    if facture is None:
        conn.close()
        return {"Erreur": "La facture n'a pas été trouvé dans la base de données après l'insertion"}
    
    conn.close()
    return {"message":"facture crée", "id":facture[0], "montant":facture[1], "date_fact":facture[2], "type_fact":facture[3], "conso":facture[4], "idLogement":facture[5]}

@app.get("/getFacture/id")
async def getfacture_id(id : int) :
    conn = sqlite3.connect("logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT * FROM Facture WHERE id = ?",(id,) ) #interroge la base de donnée
    res = res.fetchall()
    conn.close()
    return {"res" : res}

@app.get("/getFacture/montant")
async def getfacture_montant(montant : int) :
    conn = sqlite3.connect("logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT * FROM Facture WHERE montant = ?",(montant,) ) #interroge la base de donnée
    res = res.fetchall()
    conn.close()
    return {"res" : res}

@app.get("/getFacture/date_fact") #type date_fact ????????
async def getfacture_date_fact(date_fact : str) :
    conn = sqlite3.connect("logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT * FROM Facture WHERE id = ?",(date_fact,) ) #interroge la base de donnée
    res = res.fetchall()
    conn.close()
    return {"res" : res}

@app.get("/getFacture/type_fact")
async def getfacture_type_fact(type_fact : str) :
    conn = sqlite3.connect("logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT * FROM Facture WHERE type_fact = ?",(type_fact,) ) #interroge la base de donnée
    res = res.fetchall()
    conn.close()
    return {"res" : res}

@app.get("/getFacture/conso")
async def getfacture_conso(conso : str) :
    conn = sqlite3.connect("logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT * FROM Facture WHERE conso = ?",(conso,) ) #interroge la base de donnée
    res = res.fetchall()
    conn.close()
    return {"res" : res}

@app.get("/getFacture/idLogement")
async def getfacture_idLogement(idLogement: int) :
    conn = sqlite3.connect("logement.db") 
    cursor = conn.cursor() 
    res = cursor.execute("SELECT * FROM Facture WHERE idLogement = ?",(idLogement,) ) #interroge la base de donnée
    res = res.fetchall()
    conn.close()
    return {"res" : res}


################# PIECE
@app.post("/creerPiece")
async def creerPiece(nom: str, coordx: int, coordy: int, coordz: int, idLogement: int):
    conn = sqlite3.connect("logement.db")
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
    conn = sqlite3.connect("logement.db")
    cursor = conn.cursor()
    res = cursor.execute("SELECT * FROM Piece WHERE idLogement = ?", (idLogement,))
    res = res.fetchall()
    conn.close()
    return {"res": res}

################## CAPTEUR_ACTIO
@app.post("/creerCapteurActio")
async def creerCapteurActio(ref_commerce: str, ref_piece: str, port_comm: int, idType: int, idPiece: int):
    conn = sqlite3.connect("logement.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Capteur_actio (ref_commerce, ref_piece, port_comm, idType, idPiece) VALUES (?, ?, ?, ?, ?)",(ref_commerce, ref_piece, port_comm, idType, idPiece))
    conn.commit()
    id_capteur = cursor.lastrowid

    res = cursor.execute("SELECT id, ref_commerce, ref_piece, date_insertion, port_comm, idType, idPiece FROM Capteur_actio WHERE id = ?",(id_capteur,))
    capteur = res.fetchone()
    if capteur is None:
        conn.close()
        return {"Erreur": "Le capteur/actionneur n'a pas été trouvé dans la base de données après l'insertion"}

    conn.close()
    return {"message": "capteur/actionneur créé", "id_capteur": capteur[0], "ref_commerce": capteur[1], "ref_piece": capteur[2], "date_insertion": capteur[3], "port_comm": capteur[4], "idType": capteur[5], "idPiece": capteur[6]}

@app.get("/getCapteurActio/idPiece")
async def getCapteurActio_idPiece(idPiece: int):
    conn = sqlite3.connect("logement.db")
    cursor = conn.cursor()
    res = cursor.execute("SELECT * FROM Capteur_actio WHERE idPiece = ?", (idPiece,))
    res = res.fetchall()
    conn.close()
    return {"res": res}

################## TYPE_CAPTEUR_ACTIO 
@app.post("/creerTypeCapteurActio")
async def creerTypeCapteurActio(unite: str, val_min: int, val_max: int):
    conn = sqlite3.connect("logement.db")
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
    conn = sqlite3.connect("logement.db")
    cursor = conn.cursor()
    res = cursor.execute("SELECT * FROM Capteur_actio WHERE idPiece = ?", (id,))
    res = res.fetchall()
    conn.close()
    return {"res": res}

################## MESURE 
@app.post("/creerMesure")
async def creerMesure(valeur: int, idCapteur: int):
    conn = sqlite3.connect("logement.db")
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
    conn = sqlite3.connect("logement.db")
    cursor = conn.cursor()
    res = cursor.execute("SELECT * FROM Mesure WHERE idCapteur = ?", (idCapteur,))
    res = res.fetchall()
    conn.close()
    return {"res": res}









# @app.post("/Logement")
# async def creerLogementFin(adresse : str, telephone : int):
#  logement_id = creerLogement(adresse,telephone)
#  return {"id": logement_id, **logement.dict()}





# @app.get("/Piece/{id}")

# @app.get("/Capteur_actio/{id}")

# @app.get("/Type_capteur_actio/{id}")

# @app.get("/Mesure/{id}")