
import os
import sqlite3
import smtplib
import ssl

from email.message import EmailMessage
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash

# Charger les variables du fichier .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")


# Création de la base de données
def creer_base():
    connexion = sqlite3.connect("messages.db")

    connexion.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    connexion.commit()
    connexion.close()


# Envoyer un e-mail avec Brevo
def envoyer_email(nom, email_client, message_client):

    serveur = os.getenv("BREVO_SMTP_SERVER")
    port = int(os.getenv("BREVO_SMTP_PORT", "587"))
    login = os.getenv("BREVO_SMTP_LOGIN")
    mot_de_passe = os.getenv("BREVO_SMTP_PASSWORD")
    expediteur = os.getenv("BREVO_SENDER_EMAIL")
    destinataire = os.getenv("HOTMAIL_DESTINATION")

    if not all([serveur, login, mot_de_passe, expediteur, destinataire]):
        raise ValueError("Configuration SMTP incomplète.")

    email = EmailMessage()
    email["Subject"] = "Nouveau message - Café Lbeldia"
    email["From"] = expediteur
    email["To"] = destinataire
    email["Reply-To"] = email_client

    email.set_content(f"""
Nouveau message reçu depuis le site Café Lbeldia.

Nom : {nom}
E-mail : {email_client}       

Message :
{message_client}
""")

    contexte = ssl.create_default_context()

    with smtplib.SMTP(serveur, port) as smtp:
        smtp.starttls(context=contexte)
        smtp.login(login, mot_de_passe)
        smtp.send_message(email)


# Page d'accueil
@app.route("/")
def accueil():
    return "Bienvenue chez Café Lbeldia !"


# Page Contact
@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        nom = request.form.get("nom", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not nom or not email or not message:
            flash("Veuillez remplir tous les champs.")
            return redirect(url_for("contact"))

        connexion = sqlite3.connect("messages.db")

        connexion.execute(
            "INSERT INTO messages (nom, email, message) VALUES (?, ?, ?)",
            (nom, email, message)
        )

        connexion.commit()
        connexion.close()

        try:
            envoyer_email(nom, email, message)
            flash("Merci ! Votre message a été enregistré et envoyé.")
        except Exception as erreur:
            print("Erreur d'envoi e-mail :", erreur)
            flash("Votre message est enregistré, mais la notification e-mail n'a pas pu être envoyée.")

        return redirect(url_for("contact"))

    return render_template("contact.html")


if __name__ == "__main__":
    creer_base()
    app.run(debug=True)
