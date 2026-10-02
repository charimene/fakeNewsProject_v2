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
def attribuer_notoriete2(domaine):
    if domaine in classement:
        return "s0_connue"
    else:
        return "s1_peu_connue"

def attribuer_notoriete(domaine):
    if domaine == "inconnu":
        return "s1_peu_connue", domaine

    #enlever les espaces et mettre en minuscule
    domaine = domaine.lower().strip()

    # Un seul point : domaine simple
    if domaine.count(".") == 1:
        if domaine in classement:
            return "s0_connue", domaine
        else:
            return "s1_peu_connue", domaine

    #plusieurs points: donc un sous-domaine
    #on test la presenece des sous-domaines dans le classement, en combianant les parties du domaine
    else:
        parties = domaine.split(".")

        for i in range(len(parties) - 1):
            domaine_test = ".".join(parties[i:])

            if domaine_test in classement:
                return "s0_connue", domaine_test
        return "s1_peu_connue", domaine

with open("data/fakenewsnet_complet_v3.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    lignes = list(reader)

for l in lignes:
    # print(l["domaine"])
    notoriete, domaine_principal = attribuer_notoriete(l["domaine"])

    l["notoriete"] = notoriete
    l["domaine_principal"] = domaine_principal

with open("data/fakenewsnet_complet_v4.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=lignes[0].keys())
    writer.writeheader()
    writer.writerows(lignes)

# verif
from collections import Counter
compteur = Counter(l["notoriete"] for l in lignes)
print(compteur)