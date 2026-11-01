
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "cafe-lbeldia-cle-secrete"


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


# Page d'accueil temporaire
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

        flash("Merci ! Votre message a bien été enregistré.")

        return redirect(url_for("contact"))

    return render_template("contact.html")


if __name__ == "__main__":
    creer_base()
    app.run(debug=True)
