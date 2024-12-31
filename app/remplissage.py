import sqlite3, random
from datetime import datetime, timedelta


def remplissage() :
    # ouverture/initialisation de la base de donnee 
    conn = sqlite3.connect('logement.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # # affichage d'une table
    # # lecture dans la base avec un select
    # c.execute('SELECT * FROM Mesure')

    # # parcourt ligne a ligne
    # for raw in c.execute('SELECT * FROM Mesure'):
        # print(raw.keys())
        # print(raw["valeur"])

    # insertion d'une donnee
    #c.execute("INSERT INTO Mesure(valeur, idCapteur) VALUES (40,2)")

    ######## Création plusieurs Mesures
    values = []
    for i in range(10): 
        idCapteur_i = random.randint(1,4) #le capteur est un des quatres initialisés
        
        #Valeurs random en fonction de plages de mesures des capteurs
        if idCapteur_i == 1 : 
            valeur_i = random.randint(-60,60)
        elif idCapteur_i == 2 :
            valeur_i = random.randint(0,100)
        elif idCapteur_i == 3 :
            valeur_i = random.randint(0,200)  
        else : 
            valeur_i = random.randint(0,500)
        
        values.append((valeur_i,idCapteur_i))     
    c.executemany('INSERT INTO Mesure(valeur, idCapteur) VALUES (?,?)', values) #ajout date ou automatique ?



    # Fonction pour adapter datetime en une chaîne compatible avec le format attendu par SQLite.
    def adapt_datetime(ts):
        return ts.strftime("%Y-%m-%d %H:%M:%S")

    # Enregistre la fonction pour que SQLite utilise cette conversion lors de l'insertion. 
    sqlite3.register_adapter(datetime, adapt_datetime)

    #######################Création de factures
    values.clear() #vide la liste pour la réutiliser
    for i in range(10): 
        type_fact_i = random.randint(1,4)
        start_date = datetime(2022, 1, 1)
        random_days = random.randint(0, 365 * 3)  # Jusqu'à 3 ans en jours
        random_time = timedelta(days=random_days, hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59))
        timestamp = start_date + random_time

        #Valeurs random en fonction de plages de mesures des capteurs
        if type_fact_i == 1 : 
            #en 20 et 80€ éléctricité, entre 40 et 500 KWH/mois, pour le logement 1, 2 ou 3
            #ne pas avoir deux facturses, de même type pour un même logement + consommation et prix à  relié
            values.append((random.randint(20,90), timestamp,"électricité",random.randint(40,500),'kWh',random.randint(1,3)))   
            
        elif type_fact_i == 2 :
            #en 20 et 40€ eau, conso entre 2000 et 20000 L/mois/logement, pour le logement 1, 2 ou 3
            values.append((random.randint(20,40), timestamp,"eau",random.randint(2000,20000),'L/mois',random.randint(1,3)))   
        elif type_fact_i == 3 :
            #en 10 et 30€ déchets, entre 25 et 100kg de déchets
            values.append((random.randint(10,30), timestamp,"déchets",random.randint(25,100),'kg',random.randint(1,3)))   
            
        else : 
            montant_i = random.randint(0,300)#en 80 et 300€ copropriété, entre 0 et 30h par mois
            values.append((random.randint(0,300), timestamp,"copropriété",random.randint(0,30),'heures',random.randint(1,3)))   
            
        # values.append((valeur_i,idCapteur_i))     
    c.executemany('INSERT INTO Facture(montant, date_fact, type_fact, conso, unite, idLogement) VALUES (?,?,?,?,?,?)', values) 

    # lecture dans la base avec un select
    # c.execute('SELECT * FROM Emprunte')
    #print c
    #print c[0]
    # print c.fetchall()

    # fermeture
    conn.commit()
    conn.close()

# Lorsque le programme est lancé, 
remplissage()    