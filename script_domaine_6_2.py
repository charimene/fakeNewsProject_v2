import os
import csv

# ouvrir le fichier qu'on vient de créer
with open("data/domaines_valides.csv", encoding="utf-8") as f:
    liste = list(csv.DictReader(f))

colonnes = ["domaine_principal", "notoriete", "credibilite"]

categories = {
    "A": ("s0_connue",     "credible"),
    "B": ("s0_connue",     "peu_credible"),
    "C": ("s1_peu_connue", "credible"),
    "D": ("s1_peu_connue", "peu_credible"),
}

os.makedirs("categorie_domaine", exist_ok=True)   # creer le dossier sil existe pas

for nom, (notoriete, credibilite) in categories.items():
    selection = [d for d in liste if d["notoriete"] == notoriete and d["credibilite"] == credibilite]

    with open(f"categorie_domaine/domaines_{nom}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=colonnes)
        writer.writeheader()
        writer.writerows(selection)

    print(f"Catégorie {nom} : {len(selection)} domaines")