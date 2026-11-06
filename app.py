
import os
import sqlite3
import json
import smtplib
import ssl

from email.message import EmailMessage
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash


# ==================================================
# CONFIGURATION
# ==================================================

# Charger les variables du fichier .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY est absente du fichier .env")


# ==================================================
# CONNEXION À LA BASE DE DONNÉES
# ==================================================

def obtenir_connexion():
    return sqlite3.connect(
        os.path.join(os.path.dirname(__file__), "messages.db")
    )


# ==================================================
# CRÉATION DES TABLES
# ==================================================

def creer_base():
    connexion = obtenir_connexion()

    try:
        connexion.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)

        connexion.execute("""
            CREATE TABLE IF NOT EXISTS commandes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                email TEXT NOT NULL,
                articles TEXT NOT NULL,
                total REAL NOT NULL,
                message TEXT,
                date_commande TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Ajouter la colonne message si elle n'existe pas
        curseur = connexion.execute("PRAGMA table_info(commandes)")
        colonnes = [ligne[1] for ligne in curseur.fetchall()]

        if "message" not in colonnes:
            connexion.execute(
                "ALTER TABLE commandes ADD COLUMN message TEXT"
            )

        connexion.commit()

    finally:
        connexion.close()


# ==================================================
# ENVOI D'EMAIL AVEC BREVO
# ==================================================

def envoyer_email_commande(nom, email_client, commande, total, message):

    serveur = os.getenv("BREVO_SMTP_SERVER")
    port = int(os.getenv("BREVO_SMTP_PORT", "587"))
    login = os.getenv("BREVO_SMTP_LOGIN")
    mot_de_passe = os.getenv("BREVO_SMTP_PASSWORD")
    expediteur = os.getenv("BREVO_SENDER_EMAIL")
    destinataire = os.getenv("HOTMAIL_DESTINATION")

    if not all([serveur, login, mot_de_passe, expediteur, destinataire]):
        raise ValueError("Configuration SMTP incomplète.")

    email = EmailMessage()
    email["Subject"] = "Nouvelle commande - Café Lbeldia"
    email["From"] = expediteur
    email["To"] = destinataire
    email["Reply-To"] = email_client

    details = ""

    for article, informations in commande.items():
        details += (
            f"{informations['nom']} : "
            f"{informations['quantite']} x "
            f"{informations['prix']:.2f} €\n"
        )

    email.set_content(f"""
Nouvelle commande reçue depuis Café Lbeldia.

Nom : {nom}
E-mail : {email_client}

Message ou précision du client :
{message if message else "Aucune précision"}

Articles commandés :
{details}

Total : {total:.2f} €
""")

    contexte = ssl.create_default_context()

    with smtplib.SMTP(serveur, port) as smtp:
        smtp.starttls(context=contexte)
        smtp.login(login, mot_de_passe)
        smtp.send_message(email)


# ==================================================
# PAGE D'ACCUEIL
# ==================================================

@app.route("/")
def accueil():
    return render_template("index.html")


# ==================================================
# PAGE CUISINE ET COMMANDE EN LIGNE
# ==================================================

@app.route("/cuisine", methods=["GET", "POST"])
def cuisine():

    if request.method == "POST":

        nom = request.form.get("nom", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        # Prix définis côté serveur
        prix_articles = {
            "viande_pruneaux": {
                "nom": "Viande aux pruneaux",
                "prix": 12.80
            },
            "viande_legumes": {
                "nom": "Viande avec légumes et zitoun",
                "prix": 12.80
            },
            "viande_raisins": {
                "nom": "Viande aux raisins secs",
                "prix": 12.80
            },
            "couscous": {
                "nom": "Couscous",
                "prix": 10.00
            },
            "kefta": {
                "nom": "Kefta à la tomate",
                "prix": 9.60
            },
            "lehrirah": {
                "nom": "Lehrirah",
                "prix": 4.50
            },
            "coca": {
                "nom": "Coca-Cola",
                "prix": 2.50
            },
            "coca_zero": {
                "nom": "Coca-Cola zéro",
                "prix": 2.50
            },
            "fanta": {
                "nom": "Fanta",
                "prix": 2.50
            },
            "sprite": {
                "nom": "Sprite",
                "prix": 2.50
            },
            "eau_plate": {
                "nom": "Eau plate",
                "prix": 1.50
            },
            "eau_petillante": {
                "nom": "Eau pétillante",
                "prix": 1.50
            },
            "jus_orange": {
                "nom": "Jus d'orange",
                "prix": 3.50
            },
            "jus_pomme": {
                "nom": "Jus de pomme",
                "prix": 3.50
            },
            "cafe_russe": {
                "nom": "Café russe",
                "prix": 2.50
            },
            "expresso": {
                "nom": "Café expresso",
                "prix": 2.50
            },
            "the_menthe": {
                "nom": "Thé à la menthe",
                "prix": 3.50
            },
            "mhersa": {
                "nom": "Mhersa",
                "prix": 2.50
            }
        }

        commande = {}
        total = 0

        # Vérifier les quantités et calculer le total
        for identifiant, informations in prix_articles.items():

            try:
                quantite = int(request.form.get(identifiant, "0"))

            except (ValueError, TypeError):
                flash(
                    "Veuillez saisir des quantités valides.",
                    "warning"
                )
                return redirect(url_for("cuisine"))

            if quantite < 0 or quantite > 50:
                flash(
                    "Chaque quantité doit être comprise entre 0 et 50.",
                    "warning"
                )
                return redirect(url_for("cuisine"))

            if quantite > 0:
                prix = informations["prix"]

                commande[identifiant] = {
                    "nom": informations["nom"],
                    "quantite": quantite,
                    "prix": prix
                }

                total += quantite * prix

        total = round(total, 2)

        # Vérifier les informations du client
        if not nom or not email or "@" not in email:
            flash(
                "Veuillez saisir un nom et une adresse e-mail valides.",
                "warning"
            )
            return redirect(url_for("cuisine"))

        # Vérifier qu'au moins un article est sélectionné
        if not commande:
            flash(
                "Veuillez sélectionner au moins un plat ou une boisson.",
                "warning"
            )
            return redirect(url_for("cuisine"))

        # Enregistrer la commande dans SQLite
        connexion = obtenir_connexion()

        try:
            connexion.execute(
                """
                INSERT INTO commandes (nom, email, articles, total, message)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    nom,
                    email,
                    json.dumps(commande, ensure_ascii=False),
                    total,
                    message
                )
            )

            connexion.commit()

        finally:
            connexion.close()

        # Envoyer une notification par e-mail
        try:
            envoyer_email_commande(
                nom,
                email,
                commande,
                total,
                message
            )

        except Exception as erreur:
            print("Erreur d'envoi e-mail :", erreur)

            flash(
                "Votre commande est bien enregistrée, "
                "mais l'e-mail de notification n'a pas pu être envoyé.",
                "warning"
            )

            return redirect(url_for("cuisine"))

        # Confirmation de commande avec animation
        flash(
            "Votre commande a bien été enregistrée et envoyée !",
            "success"
        )

        return redirect(url_for("cuisine"))

    return render_template("cuisine-marocaine.html")


# ==================================================
# PAGE CONTACT
# ==================================================

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        nom = request.form.get("nom", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        # Vérifier les informations du formulaire
        if not nom or not email or "@" not in email or not message:
            flash(
                "Veuillez remplir correctement tous les champs.",
                "warning"
            )
            return redirect(url_for("contact"))

        # Enregistrer le message dans SQLite
        connexion = obtenir_connexion()

        try:
            connexion.execute(
                """
                INSERT INTO messages (nom, email, message)
                VALUES (?, ?, ?)
                """,
                (nom, email, message)
            )

            connexion.commit()

        finally:
            connexion.close()

        flash(
            "Merci ! Votre message a bien été envoyé.",
            "success"
        )

        return redirect(url_for("contact"))

    return render_template("contact.html")


# ==================================================
# CRÉATION DES TABLES AU DÉMARRAGE
# ==================================================

creer_base()


# ==================================================
# LANCEMENT DE L'APPLICATION
# ==================================================

if __name__ == "__main__":
    app.run(debug=True, port=5001)
