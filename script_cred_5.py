# etape 5
# script qui donne l'attribut credibilité a chacun des médias de notre dataset, en se basant sur la liste de crédibilité

import csv
from collections import Counter

#charger la liste de crédibilité dans un dictionnaire

credibilite_dict = {}
with open("data/credibilite.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for ligne in reader:
        credibilite_dict[ligne["domain"]] = ligne["reliability_label"]

print(f"{len(credibilite_dict)} média chargés dpuis la liste de crédibilité")

def donner_credibilite(domaine):
    label = credibilite_dict.get(domaine)
    if label == "1":
        return "credible"
    else:
        return "peu_credible"

# charger le dataset fakenewsnet_complet_v4.csv
with open("data/fakenewsnet_complet_v4.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    lignes = list(reader)

for l in lignes:
    l["credibilite"] = donner_credibilite(l["domaine"])

with open("data/fakenewsnet_complet_v5.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=lignes[0].keys())
    writer.writeheader()
    writer.writerows(lignes)

#verif

compteur = Counter(l["credibilite"] for l in lignes)
print(compteur)