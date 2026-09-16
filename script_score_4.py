#etape 4
#script qui donne l'attribut notoriété a chacun des médias de notre dataset, en se basant sur la liste de tranco

import csv

# charger SEULEMENT les 100 000 premiere lignes (hyper parametre a tester)
classement = {}
with open("data/top-1m_notoriete.csv", encoding="utf-8") as f:
    reader = csv.reader(f)
    for i, (rang, domaine) in enumerate(reader):
        if i >= 100000: 
            break
        classement[domaine] = int(rang)

print(f"{len(classement)} domaines chargés (top 100 000 seulement)")

# fonction d'attribution de notoriété
# si le domaine est dans le dictionnaire = il est dans le top 100k
def attribuer_notoriete(domaine):
    if domaine in classement:
        return "s0_connue"
    else:
        return "s1_peu_connue"

with open("data/fakenewsnet_complet_v3.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    lignes = list(reader)

for l in lignes:
    l["notoriete"] = attribuer_notoriete(l["domaine"])

with open("data/fakenewsnet_complet_v4.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=lignes[0].keys())
    writer.writeheader()
    writer.writerows(lignes)

# verif
from collections import Counter
compteur = Counter(l["notoriete"] for l in lignes)
print(compteur)