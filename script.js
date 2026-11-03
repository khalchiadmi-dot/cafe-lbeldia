
const boutonOuvrir = document.getElementById("ouvrir-commande");
const boutonFermer = document.getElementById("fermer-commande");
const fenetreCommande = document.getElementById("fenetre-commande");
const formulaire = document.getElementById("formulaire-commande");
const message = document.getElementById("message-commande");

// Ouvrir la fenêtre de commande
boutonOuvrir.addEventListener("click", function () {
    fenetreCommande.style.display = "block";
});

// Fermer la fenêtre de commande
boutonFermer.addEventListener("click", function () {
    fenetreCommande.style.display = "none";
});

// Vérifier le formulaire
formulaire.addEventListener("submit", function (event) {
    event.preventDefault();

    const nom = document.getElementById("nom").value.trim();
    const telephone = document.getElementById("telephone").value.trim();
    const adresse = document.getElementById("adresse").value.trim();

    const expresso = Number(document.getElementById("expresso").value);
    const cappuccino = Number(document.getElementById("cappuccino").value);
    const msemen = Number(document.getElementById("msemen").value);
    const beghrir = Number(document.getElementById("beghrir").value);

    if (expresso + cappuccino + msemen + beghrir === 0) {
        message.textContent = "Veuillez choisir au moins un article.";
        return;
    }

    message.textContent =
        "Merci " + nom + " ! Votre commande est prête à être transmise. " +
        "Téléphone : " + telephone +
        ". Adresse : " + adresse + ".";

});

// Animation du titre
const titre = document.querySelector("h1");

if (titre) {
    titre.addEventListener("mouseenter", function () {
        titre.style.color = "black";
        titre.classList.remove("rebond");
        void titre.offsetWidth;
        titre.classList.add("rebond");
    });

    titre.addEventListener("mouseleave", function () {
        titre.style.color = "";
    });
}
