-- sqlite3 bibli.db
-- .read bibli.sql

-- commandes de destruction des tables
DROP TABLE IF EXISTS Logement;
DROP TABLE IF EXISTS Facture;
DROP TABLE IF EXISTS Piece;
DROP TABLE IF EXISTS Capteur_actio;
DROP TABLE IF EXISTS Type_capteur_actio;
DROP TABLE IF EXISTS Mesure;

-- commandes de creation des tables
--Dans les commentaires associés, bien préciser le rôle de chaque table et champ.
CREATE TABLE Logement (ip INTEGER PRIMARY KEY AUTOINCREMENT, adresse TEXT NOT NULL, date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, telephone TEXT NOT NULL); 
CREATE TABLE Facture (id INTEGER PRIMARY KEY AUTOINCREMENT, montant INTEGER, date_fact TEXT DEFAULT CURRENT_TIMESTAMP, type_fact TEXT NOT NULL, conso INTEGER, unite TEXT NOT NULL, idLogement INTEGER NOT NULL, FOREIGN KEY (idLogement) REFERENCES Logement(ip));--changer montant en float
CREATE TABLE Piece (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL, coordx INTEGER, coordy INTEGER, coordz INTEGER, idLogement INTEGER NOT NULL, FOREIGN KEY (idLogement) REFERENCES Logement(ip)); --Matrice à trois dimensions?
CREATE TABLE Capteur_actio (id INTEGER PRIMARY KEY AUTOINCREMENT, ref_commerce  TEXT NOT NULL, date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, port_comm INTEGER, idType INTEGER NOT NULL, idPiece INTEGER NOT NULL, FOREIGN KEY (idType) REFERENCES Type_capteur_actio(id),  FOREIGN KEY (idPiece) REFERENCES Piece(id)); -- port_com integer ?/syntaxe foreign 
CREATE TABLE Type_capteur_actio (id INTEGER PRIMARY KEY AUTOINCREMENT, unite TEXT NOT NULL, val_min INTEGER, val_max INTEGER);
CREATE TABLE Mesure (id INTEGER PRIMARY KEY AUTOINCREMENT, valeur INTEGER, date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, idCapteur INTEGER NOT NULL, FOREIGN KEY (idCapteur) REFERENCES Capteur_actio(id));

--Création d'un logement avec 4 pièces
INSERT INTO Logement (adresse, telephone) VALUES ('4 allee de Nancy, 91300 Massy', '0123456789'); --Création d'un logement

INSERT INTO Piece (nom, coordx, coordy, coordz, idLogement) VALUES  --Création de 4 pièces
    ('1chambre',1,2,3, 1),
    ('1WC',1,4,3,1),
    ('1cuisine',2,2,3,1),
    ('1salon',1,2,3,1)
;

--Création 4  capteurs
INSERT INTO Capteur_actio (ref_commerce, port_comm, idType, idPiece) VALUES
    ('DT11',1, 1, 1), 
    ('DH12', 2, 1, 2), 
    ('SONORE', 3, 2, 3),
    ('DT35_DIST', 4, 3,4),
    ('Climatisateur', 2, 5, 3),
    ('Chauffage', 0, 5, 3) 
;

--Créer différents types de capteurs
INSERT INTO Type_capteur_actio (unite, val_min, val_max) VALUES
    ('°C', -60, 60), --température 1
    ('%',0, 100), --humidité 2
    ('dB', 0, 200), --niveau sonore 3
    ('cm', 0, 500), --distance 4
    ('Actionneur', 0, 1) --actionneur 5
;

--Création mesures
INSERT INTO Mesure(valeur, idCapteur) VALUES 
    (18, 1), --18°C température
    (20, 2), -- 20% d'humidité
    (50, 3), -- 50dB
    (200, 4), -- 50 cm
    (0, 5), --Climatisateur désactivé
    (1, 6) --Chauffage activé
;

--Création factures : chaque facture pour la catégorie considérée est mensuelle
INSERT INTO Facture(montant, date_fact, type_fact, conso, unite, idLogement) VALUES
    (40,'2024-12-01 00:00:00','électricité', 200,'kWh',1),
    (30, '2024-04-01 00:00:00', 'eau', 4000, 'L/mois',1), 
    (15,'2024-05-01 00:00:00', 'déchets', 30,'kg',1),
    (100,'2024-06-01 00:00:00', 'copropriété', 4,'heures',1),
    
    (60,'2023-10-01 00:00:00','électricité', 300,'kWh',1),
    (70, '2023-04-01 00:00:00', 'eau', 5000, 'L/mois',1), 
    (45,'2023-03-01 00:00:00', 'déchets', 70,'kg',1),
    (150,'2023-05-01 00:00:00', 'copropriété', 7,'heures',1)
;



