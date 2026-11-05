
import os
import sqlite3
import json
import smtplib
import ssl

from email.message import EmailMessage
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash


# Charger les variables du fichier .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY est absente du fichier .env")


# Connexion à la base de données
def obtenir_connexion():
    return sqlite3.connect(
        os.path.join(os.path.dirname(__file__), "messages.db")
    )


# Création des tables
def creer_base():
    connexion = obtenir_connexion()

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

    connexion.commit()
    connexion.close()


# Envoyer un e-mail de confirmation interne de commande avec Brevo
def envoyer_email_commande(nom, email_client, commande, total):

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

Articles commandés :
{details}

Total : {total:.2f} €
""")

    contexte = ssl.create_default_context()

    with smtplib.SMTP(serveur, port) as smtp:
        smtp.starttls(context=contexte)
        smtp.login(login, mot_de_passe)
        smtp.send_message(email)


# Page d'accueil
@app.route("/")
def accueil():
    return render_template("index.html")


# Page Cuisine
@app.route("/cuisine")
def cuisine():
    return render_template("cuisine-marocaine.html")


# Page Commande
@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        nom = request.form.get("nom", "").strip()
        email = request.form.get("email", "").strip()

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
                "nom": "Viande avec raisins secs",
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
            }
        }

        commande = {}
        total = 0

        # Vérifier les quantités et calculer le total
        for identifiant, informations in prix_articles.items():

            try:
                quantite = int(request.form.get(identifiant, "0"))
            except (ValueError, TypeError):
                flash("Veuillez saisir des quantités valides.")
                return redirect(url_for("contact"))

            if quantite < 0 or quantite > 50:
                flash("Chaque quantité doit être comprise entre 0 et 50.")
                return redirect(url_for("contact"))

            if quantite > 0:
                prix = informations["prix"]

                commande[identifiant] = {
                    "nom": informations["nom"],
                    "quantite": quantite,
                    "prix": prix
                }

                total += quantite * prix

        total = round(total, 2)

        if not nom or not email or "@" not in email:
            flash("Veuillez saisir un nom et une adresse e-mail valides.")
            return redirect(url_for("contact"))

        if not commande:
            flash("Veuillez sélectionner au moins un plat.")
            return redirect(url_for("contact"))

        # Enregistrer la commande dans SQLite
        connexion = obtenir_connexion()

        try:
            connexion.execute(
                """
                INSERT INTO commandes (nom, email, articles, total)
                VALUES (?, ?, ?, ?)
                """,
                (nom, email, json.dumps(commande, ensure_ascii=False), total)
            )

            connexion.commit()

        finally:
            connexion.close()

        # Envoyer une notification par e-mail
        try:
            envoyer_email_commande(nom, email, commande, total)
            flash("Merci ! Votre commande a été enregistrée et envoyée.")

        except Exception as erreur:
            print("Erreur d'envoi e-mail :", erreur)
            flash("Votre commande est enregistrée, mais l'e-mail n'a pas pu être envoyé.")

        return redirect(url_for("contact"))

    return render_template("contact.html")


# Création des tables au démarrage
creer_base()


if __name__ == "__main__":
    app.run(debug=True, port=5001)
