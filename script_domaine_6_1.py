import csv
import os
from collections import Counter

F_LISTE = "data/medias_en.csv"
F_TRANCO = "data/top-1m_notoriete.csv"
F_CRED = "data/credibilite.csv"
F_EXCL = "data/sources_a_exclure.csv"
F_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "medias_en_annotes.csv") 
SEUIL = 10000  # top seuil connu 

# charger la liste et eviter les doublons
with open(F_LISTE, encoding="utf-8-sig") as f:
    lignes = list(csv.DictReader(f))

vus, uniques = set(), []
for l in lignes:
    d = l["domain"].lower().strip()
    if d and d not in vus:
        vus.add(d)
        l["domain"] = d
        uniques.append(l)
lignes = uniques
print(f"{len(lignes)} domaines uniques")

# notoriete Tranco
classement = {}
with open(F_TRANCO, encoding="utf-8") as f:
    for i, (rang, domaine) in enumerate(csv.reader(f)):
        if i >= SEUIL:
            break
        classement[domaine] = int(rang)
print(f"{len(classement)} domaines chargés (top {SEUIL})")

def attribuer_notoriete(domaine):
    domaine = domaine.lower().strip()
    parties = domaine.split(".")
    # on teste le domaine entier, puis les sous-parties
    for i in range(len(parties) - 1):
        test = ".".join(parties[i:])
        if test in classement:
            return "s0_connue", test
    return "s1_peu_connue", domaine

for l in lignes:
    n, principal = attribuer_notoriete(l["domain"])
    l["domaine_principal"] = principal
    l["notoriete"] = n

# credibilite
credibilite_dict = {}
with open(F_CRED, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        credibilite_dict[r["domain"].lower().strip()] = r["reliability_label"]

def donner_credibilite(domaine):
    label = credibilite_dict.get(domaine)
    if label == "1":
        return "credible"
    elif label == "0":
        return "mixte"
    elif label == "-1":
        return "peu_credible"
    return "non_note"

for l in lignes:
    l["credibilite"] = donner_credibilite(l["domaine_principal"])

# exclusion des domaines 
with open(F_EXCL, encoding="utf-8-sig") as f:
    exclus = {r["domaine_principal"].lower().strip() for r in csv.DictReader(f)}

avant = len(lignes)
lignes = [l for l in lignes if l["domaine_principal"] not in exclus]
print(f"{avant - len(lignes)} domaines exclus, {len(lignes)} restants")

# sauvegarde du fichier
with open(F_OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=lignes[0].keys())
    w.writeheader()
    w.writerows(lignes)
print("fichier sauvegardé :", os.path.abspath(F_OUT))

print("notoriété :", Counter(l["notoriete"] for l in lignes))
print("crédibilité :", Counter(l["credibilite"] for l in lignes))

# ---------- 4 fichiers pour 4 categories
colonnes = ["domaine_principal", "notoriete", "credibilite"]

categories = {
    "A": ("s0_connue",     "credible"),
    "B": ("s0_connue",     "peu_credible"),
    "C": ("s1_peu_connue", "credible"),
    "D": ("s1_peu_connue", "peu_credible"),
}

os.makedirs("categorie_domaine_v2", exist_ok=True)

for nom, (notoriete, credibilite) in categories.items():
    selection = [d for d in lignes if d["notoriete"] == notoriete and d["credibilite"] == credibilite]

    with open(f"categorie_domaine_v2/domaines_{nom}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=colonnes, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(selection)

    print(f"Catégorie {nom} : {len(selection)} domaines")