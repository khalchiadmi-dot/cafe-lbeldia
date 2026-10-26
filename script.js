
document.getElementById("ouvrir-commande").addEventListener("click", function () {
    alert("Bienvenue au Café Lbeldia ! ☕\n\n" +
          "Notre menu :\n" +
          "☕ Café expresso\n" +
          "🥛 Café au lait\n" +
          "☕ Cappuccino\n" +
          "🇷🇺 Café russe\n" +
          "🥞 Mhersa\n\n" +
          "🍯 Lemlawi\n" +
          "🥞 Ftour rbaté\n" +
          "🥞 Beghrir\n" +
          "🍪 Ke3b legzal\n" +
          "🍩 Chfenj\n\n" +
          "Bon appétit !");
});

const boutonOuvrir = document.getElementById("ouvrir-commande");
const boutonFermer = document.getElementById("fermer-commande");
const fenetreCommande = document.getElementById("fenetre-commande");
const formulaire = document.getElementById("formulaire-commande");
const message = document.getElementById("message-commande");

// Ouvrir la fenêtre
boutonOuvrir.addEventListener("click", function () {
    fenetreCommande.style.display = "block";
});

// Fermer la fenêtre
boutonFermer.addEventListener("click", function () {
    fenetreCommande.style.display = "none";
});

// Traiter le formulaire
formulaire.addEventListener("submit", function (event) {
    event.preventDefault();

    const nom = document.getElementById("nom").value;
    const telephone = document.getElementById("telephone").value;
    const adresse = document.getElementById("adresse").value;

    const expresso = Number(document.getElementById("expresso").value);
    const cappuccino = Number(document.getElementById("cappuccino").value);
    const msemen = Number(document.getElementById("msemen").value);
    const beghrir = Number(document.getElementById("beghrir").value);

    if (expresso + cappuccino + msemen + beghrir === 0) {
        message.textContent = "Veuillez choisir au moins un article.";
        return;
    }

    message.textContent =
        "Merci " + nom + " ! Votre commande est préparée. " +
        "Téléphone : " + telephone +
        ". Adresse : " + adresse +
        ". Vous pourrez ensuite transmettre votre commande au café.";
});
