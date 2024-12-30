import sqlite3, random

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

    # insertion de plusieurs donnees
    values = []
    for i in range(3): 
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


    #Création de factures
    values.clear() #vide la liste pour la réutiliser
    for i in range(3): 
        type_fact_i = random.randint(1,4)

        #Valeurs random en fonction de plages de mesures des capteurs
        if type_fact_i == 1 : 
            #en 20 et 80€ éléctricité, entre 40 et 500 KWH/mois, pour le logement 1, 2 ou 3
            #ne pas avoir deux facturses, de même type pour un même logement + consommation et prix à  relié
            values.append((random.randint(20,90), "'02/%d/2023'" %(random.randint(1,12)),'électricité',"'%d kWh'"%random.randint(40,500),random.randint(1,3)))   
            
        elif type_fact_i == 2 :
            #en 20 et 40€ eau, conso entre 2000 et 20000 L/mois/logement, pour le logement 1, 2 ou 3
            values.append((random.randint(20,40), "'02/%d/2023'" %(random.randint(1,12)),'eau',"'%d L/jour'"%random.randint(2000,20000),random.randint(1,3)))   
        elif type_fact_i == 3 :
            #en 10 et 30€ déchets, entre 25 et 100kg de déchets
            values.append((random.randint(10,30), "'02/%d/2023'" %(random.randint(1,12)),'déchets',"'%d kg'"%random.randint(25,100),random.randint(1,3)))   
            
        else : 
            montant_i = random.randint(0,300)#en 80 et 300€ copropriété, entre 0 et 30h par mois
            values.append((random.randint(0,300), "'02/%d/2023'" %(random.randint(1,12)),'copropriété',"'%d h'"%random.randint(0,30),random.randint(1,3)))   
            
        # values.append((valeur_i,idCapteur_i))     
    c.executemany('INSERT INTO Facture(montant, date_fact, type_fact, conso, idLogement) VALUES (?,?,?,?,?)', values) 

    # lecture dans la base avec un select
    # c.execute('SELECT * FROM Emprunte')
    #print c
    #print c[0]
    # print c.fetchall()

    # fermeture
    conn.commit()
    conn.close()