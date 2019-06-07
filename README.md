# Portail captif Cr@ns

Ce portail minimaliste permet aux utilisateurs de s'identifier sur un HotSpot WiFi.

Leurs adresses MAC sont capturées, et injectée dans une ipset
qui leur donne accès à internet.

## Histoire

Ce projet a initialement été forké à partir de [re2o](https://gitlab.federez.net/federez/re2o) par [chirac](https://gitlab.crans.org/detraz).

Il a été repris en 2019 par [erdnaxe](https://gitlab.crans.org/erdnaxe) pour l'améliorer.

# Installation

Il peut être souhaitable d'installer la base de données sur un serveur
séparé du serveur web en production.

## Installation du serveur web

On installe les dépendances par APT :

```bash
apt install python3-django python3-dateutil python3-django-reversion python3-pip
```

Ensuite on installe les dépendances restantes avec pip :

```bash
pip3 install django-bootstrap3 django-macaddress
```

On clone le projet dans `/var/www/portail_captif` par exemple.

Ensuite, il faut créer le fichier settings_local.py dans le sous dossier portail_captif,
un settings_local.example.py est présent.
En particulier, il est nécessaire de générer des identifiants pour le ldap
et des identifiants pour le sql (cf ci-dessous), à mettre dans settings_local.py

## Installation de la base de données

### Pour PostgreSQL

On installe `psycopg2` sur le serveur web.

Puis on installe `postgresql` sur le serveur de base de données et on le configure.

### Pour MySQL

On installe `python3-mysqldb` et `mysql-client sur le serveur web.

Puis on installe `mysql-server` sur le serveur de base de données et on le configure.

On crée la base de données et un utilisateur,

```SQL
CREATE DATABASE portail_captif;
CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON portail_captif.* TO 'newuser'@'localhost';
FLUSH PRIVILEGES;
```

### Configuration initiale

Normalement à cette étape, le ldap et la bdd sql sont configurées correctement.

Il faut alors lancer dans le dépot portail_captif
'''python3 manage.py migrate''' qui va migrer la base de données.

#### Démarrer le site web

Il faut utiliser un moteur pour servir le site web. Nginx ou apache2 sont recommandés.
Pour apache2 :
 * apt install apache2
 * apt install libapache2-mod-wsgi-py3 (pour le module wsgi)

portail_captif/wsgi.py permet de fonctionner avec apache2 en production

Pour nginx :
 * apt install nginx
 * apt install gunicorn3

Utilisez alors un site nginx qui proxifie vers une socket gunicorn. Ensuite, utilisez les fichier portail_captif.service et portail_captif.socket avec systemd pour lancer le sous process gunicorn, présents dans portail_captif/ . 

## Licence

Ce projet est sous [licence GPL](LICENSE) parce que l'on croît au développement ouvert.
La licence GPL implique des droits et des devoirs.
Veuillez vous référer au fichier de licence pour plus d'informations.