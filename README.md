# Gestion des inscriptions au car de l’EMSP

Application d’administration Django en français : import CSV/Google Sheets, classement, filtres, indicateurs et export CSV. Les fiches sont réservées aux comptes connectés. Les modifications locales ne sont pas renvoyées vers Google Sheets.

## Installation (Windows PowerShell)

1. Ouvrir PowerShell dans C:\xampp\htdocs\car.
2. Exécuter : py -m venv .venv
3. Exécuter : .\.venv\Scripts\Activate.ps1
4. Exécuter : python -m pip install -r requirements.txt
5. Exécuter : Copy-Item .env.example .env
6. Exécuter : python manage.py migrate
7. Exécuter : python manage.py createsuperuser
8. Exécuter : python manage.py runserver

Ouvrez http://127.0.0.1:8000/ puis connectez-vous avec le compte créé. Les noms des licences et filières se gèrent dans Paramètres (/admin/). Les niveaux Licence 1 et Licence 2 et leurs filières sont créés automatiquement par la migration initiale. GARE est disponible uniquement pour Licence 2.

## Google Sheets

Créez un compte de service Google, partagez la feuille avec son adresse e-mail, gardez le JSON de clé hors du dépôt, puis renseignez dans .env les variables GOOGLE_SHEET_ID, GOOGLE_WORKSHEET_NAME et GOOGLE_SERVICE_ACCOUNT_FILE. L’application lit la première ligne comme en-têtes. Les colonnes reconnues comprennent Nom, Prénom(s), Commune, Niveau/Licence, Filière, Classe/Groupe, souhait de prendre le car, Horodatage et Téléphone. Aucun secret n’est envoyé au navigateur. Le CSV sert de solution de repli.

## Import et classement

L’import associe les lignes à une clé calculée depuis nom, prénom, commune, niveau et filière; réimporter la même ligne met à jour l’étudiant. Une réponse Oui ne renseigne jamais le paiement. Les niveaux et filières inconnus restent sans classement et sont marqués à vérifier. Le CSV exporte les résultats filtrés de la liste.

## Déploiement

Définissez DJANGO_SECRET_KEY, DJANGO_DEBUG=False et DJANGO_ALLOWED_HOSTS et configurez HTTPS. SQLite convient au développement. Pour PostgreSQL, renseignez DATABASE_URL. Ne commitez jamais .env ni le fichier JSON du compte de service.

## Périmètre de cette première version

Inclus : authentification, dashboard, gestion des étudiants, filtres, listes par licence, analyse des communes, pagination, export CSV, import CSV/Sheets et historique des imports. Paiements, zones de ramassage, export Excel et remontée des changements vers Sheets restent à développer.
