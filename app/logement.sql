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
CREATE TABLE Facture (id INTEGER PRIMARY KEY AUTOINCREMENT, montant INTEGER, date_fact TIMESTAMP DEFAULT CURRENT_TIMESTAMP, type_fact TEXT NOT NULL, conso TEXT NOT NULL, idLogement INTEGER NOT NULL, FOREIGN KEY (idLogement) REFERENCES Logement(ip));--changer montant en float
CREATE TABLE Piece (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL, coordx INTEGER, coordy INTEGER, coordz INTEGER, idLogement INTEGER NOT NULL, FOREIGN KEY (idLogement) REFERENCES Logement(ip)); --Matrice à trois dimensions?
CREATE TABLE Capteur_actio (id INTEGER PRIMARY KEY AUTOINCREMENT, ref_commerce  TEXT NOT NULL, ref_piece TEXT NOT NULL, date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, port_comm INTEGER, idType INTEGER NOT NULL, idPiece INTEGER NOT NULL, FOREIGN KEY (idType) REFERENCES Type_capteur_actio(id),  FOREIGN KEY (idPiece) REFERENCES Piece(id)); -- port_com integer ?/syntaxe foreign 
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
INSERT INTO Capteur_actio (ref_commerce, ref_piece, port_comm, idType, idPiece) VALUES
    ('capcom1', 'DT11', 1, 1, 1), 
    ('capcom2', 'DH12', 2, 1, 1), 
    ('capcom3', 'SONORE', 3, 2, 3),
    ('capcom4', 'DT35_DIST', 4, 3,4)
;

--Créer différents types de capteurs
INSERT INTO Type_capteur_actio (unite, val_min, val_max) VALUES
    ('°C', -60, 60), --température 1
    ('%',0, 100), --humidité 2
    ('dB', 0, 200), --niveau sonore 3
    ('cm', 0, 500) --distance 4
;

--Création mesures
INSERT INTO Mesure(valeur, idCapteur) VALUES 
    (20, 2), -- 20% d'humidité
    (50, 3), -- 50dB
    (200, 4) -- 50 cm
;

--Création factures : chaque facture pour la catégorie considérée est mensuelle
INSERT INTO Facture(montant, type_fact, conso, idLogement) VALUES
    (40,'électricité', '200kWh',1),
    (30, 'eau', '4000 L/mois',1), 
    (15, 'déchets', '30 kg',1),
    (100, 'entretienCopropiété', '4h',1)
;


--questions
--ip est bien foreign key de logement ?
