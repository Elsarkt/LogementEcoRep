# Projet IOT : Logement ECOREP

Logement ECOREP permet de naviguer sur un site web sur lequel on peut surveiller les factures, les économies réalisées, la météo et les capteurs renseignés.

## Prérequis
Environnement de conception du projet : Ubuntu 24.04.1 LTS  

1-Créer un environnement virtuel et l'activer
```bash
python3 -m venv .venv
source .venv/Scripts/activate
```

2-Installer les dépendances python:

```bash
sudo apt install python3-pip
pip install -r requirements.txt
```

Installer curl :  
```bash
sudo apt install curl
```

Installer sqlite3 :  
```bash
sudo apt install sqlite3
```



## Architecture du projet
Ci-dessous l'oganisation des fichiers utiles au projet :  

- Répertoire courant :
    - requirements.txt contient l'ensemble des dépendances python du projet
    - Répertoires ./app/ et ./static/  

- Répertoire ./app/ : 
    - serveur.py contient le code python du serveur
    - logement.sql contient le code de la base de donnée
    - logement.db contient la base de donnée
    - remplissage.py permet d'ajouter 50 factures supplémentaires dans la base de donnée
    - templates/ contient les pages html du site web

- Répertoire ./static/ :
    - contient les fichiers .css et .js nécéssaire au style du site web

## Spécifications sur les exercices

- Exercice 1 :  
    - 1.1 : Dans ./app/logement.sql  
    - 1.2 : Dans ./app/remplissage.py, l'ajout de mesures a été commenté  
- Exercice 2 :  
    - 1.1 : voir les requêtes POST et GET en fonction de divers paramètres des tables dans ./app/serveur.py    
    La liste des commandes curl peut se trouver via http://localhost:8000/docs/  
    - 1.2 : Dans ./app/serveur.py voir la fonction syntheseCamembert(). Le module associé est dans camembert.py  
    - 1.3 : Dans ./app/serveur.py voir la fonction affichageMeteoCommune()



## Lancement du site Web
Toutes les commandes sont à lancer à la racine du projet.

1 - Activer l'environnement virtuel  
2- La base de donnée est fournie avec quelques factures mais il est conseillé de lancer le fichier remplissage.py pour simuler les graphiques sur une plus grande quantité de factures.   


```bash
python3 ./app/remplissage.py
```  
NB : pour réinitialiser la base de donnée à l'état décrit par le code logement.sql, utiliser la commande suivante :  
```bash
sqlite3 ./app/logement.db < ./app/logement.sql
```  

3 - Lancer le serveur

```bash
fastapi dev app/serveur.py 
```
4 - Consulter le site web : Copier l'URL suivante dans le navigateur :  

```
http://localhost:8000/
```

# Sources

La majorité des templates html utilisés sont issus des exemples ou documentation de bootstrap 5.3.0.  
Les parties de code générés par ia sont identiquées aux endroits concernés.  

Liens des documentations et sites utilisés :  
https://fastapi.blog/blog/posts/2023-07-19-fastapi-web-app-with-dynamic-html-template/#corehtml    
https://api.meteo-concept.com/documentation#ephemeride    
https://getbootstrap.com/docs/5.3/getting-started/introduction/    
https://fastapi.tiangolo.com/advanced/templates/#using-jinja2templates  
https://fastapitutorial.com/blog/serving-html-response-fastapi-coursefor-book/  
https://christophergs.com/tutorials/ultimate-fastapi-tutorial-pt-6-jinja-templates/  
https://www.chartjs.org/docs/latest/charts/mixed.html  
https://www.restack.io/p/fastapi-knowledge-jinja2-javascript-answer  
https://vincent.jousse.org/blog/fr/tech/le-guide-complet-du-debutant-avec-fastapi-partie-2/

