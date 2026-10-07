# Etape 6
# script qui va regrouper les articles selon leur catégories A,B,C,D
# catégorie A = les articles qui sont connus et qui sont crédibles
# catégorie B = les articles qui sont connus et qui sont pas crédibles
# catégorie C = les articles qui sont pas connus et qui sont crédibles
# catégorie D = les articles qui sont pas connus et qui sont pas crédibles

import csv
import os
import random

random.seed(30)
FICHIER_ENTREE = "data/fakenewsnet_complet_v5.csv"
DOSSIER_SORTIE = "data_out"
FICHIER_EXCLUSIONS = "data/sources_a_exclure.csv"

os.makedirs(DOSSIER_SORTIE, exist_ok=True)

def lire_csv(chemin):
    with open(chemin, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def ecrire_csv(chemin, lignes):
    colonnes = list(lignes[0].keys())
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        ecrivain = csv.DictWriter(f, fieldnames=colonnes)
        ecrivain.writeheader()
        ecrivain.writerows(lignes)

def charger_exclusions(chemin):
    with open(chemin, newline="", encoding="utf-8-sig") as f:
        return {r["domaine_principal"] for r in csv.DictReader(f)}

def egaliser_categories2(groupe_a, groupe_b):
    # on réduit les 2 groupes pour qu'ils aient le même nombre d'articles, en prenant le minimum des 2 tailles
    # et la meme proportions de fake/real 

    fake_a = [l for l in groupe_a if l["label"] == "fake"]
    real_a = [l for l in groupe_a if l["label"] == "real"]
    fake_b = [l for l in groupe_b if l["label"] == "fake"]
    real_b = [l for l in groupe_b if l["label"] == "real"]

    print(f"  fake : {len(fake_a)} (groupe_a), vs {len(fake_b)} (groupe_b)")
    print(f"  real : {len(real_a)} (groupe_a), vs {len(real_b)} (groupe_b)")

    nbr_fake = min(len(fake_a), len(fake_b))
    nbr_real = min(len(real_a), len(real_b))

    fake_a = random.sample(fake_a, nbr_fake)
    fake_b = random.sample(fake_b, nbr_fake)
    real_a = random.sample(real_a, nbr_real)
    real_b = random.sample(real_b, nbr_real)

    print(f" On garde {nbr_fake} fake et {nbr_real} real pour chaque groupe")

    a_egalise = fake_a + real_a
    b_egalise = fake_b + real_b

    random.shuffle(a_egalise)
    random.shuffle(b_egalise)

    return a_egalise, b_egalise

def source_de(l):
    # retourne si l'article est de gossipcop ou politifact, en se basant sur l'id de l'article
    return "gossipcop" if l["id"].startswith("gossipcop") else "politifact"


def egaliser_categories(groupe_a, groupe_b):
    # strates = toutes les combinaisons (source, label) prseentes dans nos 2 groupes
    strates = sorted({(source_de(l), l["label"]) for l in groupe_a + groupe_b})

    a_egalise = []
    b_egalise = []
    
    for s, lab in strates:
        strate_a = [l for l in groupe_a if source_de(l) == s and l["label"] == lab]
        strate_b = [l for l in groupe_b if source_de(l) == s and l["label"] == lab]

        n = min(len(strate_a), len(strate_b))
        
        a_egalise += random.sample(strate_a, n)
        b_egalise += random.sample(strate_b, n)

    random.shuffle(a_egalise)
    random.shuffle(b_egalise)

    return a_egalise, b_egalise


def echantillonner(lignes, n):
    resultat = []
    total = len(lignes)

    # on regroupe les articles par strate (source, label)
    strates = sorted({(source_de(l), l["label"]) for l in lignes})

    for s, lab in strates:
        #articles de la strate (s, lab)
        strate = [l for l in lignes if source_de(l) == s and l["label"] == lab]

        # proportion de la strate dans lignes
        proportion = len(strate) / total

        nbr_strate_n = round(proportion * n)

        resultat += random.sample(strate, nbr_strate_n)

    # on vérifie si on a exactement n articles
    if len(resultat) < n:
        print(f"Il manque {n - len(resultat)} article(s)")
        #on complete avec des articles restants
        restants = [l for l in lignes if l not in resultat]
        resultat += random.sample(restants, n - len(resultat))

    elif len(resultat) > n:
        print(f"Il y a {len(resultat) - n} article en trop")
        resultat = random.sample(resultat, n)

    print(f"Nombre final : {len(resultat)}")
    random.shuffle(resultat)

    return resultat

def echantillonner_n(lignes, n):
    strates = sorted({(source_de(l), l["label"]) for l in lignes})
    nbr_article_cellule = n // len(strates)
    reste = n % len(strates) # le nb d'articles qui reste à tirer après avoir pris un nombre égal dans chaque strate

    random.shuffle(strates)
    resultat = []

    for i, (s, lab) in enumerate(strates):

        k = nbr_article_cellule + (1 if i < reste else 0)
        cellule = [l for l in lignes if source_de(l) == s and l["label"] == lab]
        k = min(k, len(cellule)) # je veux pas depasser le nombre d'articles alloué a la cellule
        print(f"  {s} / {lab} : {len(cellule)} disponibles, on tire {k}")
        resultat += random.sample(cellule, k)

    # s'il manque des articles, on complete avec des restants au hasard
    if len(resultat) < n:
        print(f"Il manque {n - len(resultat)} article(s), on complète")
        articles_pris = {l["id"] for l in resultat}
        restants = [l for l in lignes if l["id"] not in articles_pris]
        resultat += random.sample(restants, n - len(resultat))

    random.shuffle(resultat)
    return resultat

def resumer_categories(lignes, titre):
    # affiche, pour chaque categorie A, B, C, D : nombre de sources, d'articles, proportion de fake et de real
    categories = {
        "A": ("s0_connue", "credible"),
        "B": ("s0_connue", "peu_credible"),
        "C": ("s1_peu_connue", "credible"),
        "D": ("s1_peu_connue", "peu_credible"),
    }
    print(f"--- {titre} ---")
    print("cat | sources | articles | fake | real")

    for nom, (notoriete, credibilite) in categories.items():
        cat_articles = [l for l in lignes if l["notoriete"] == notoriete and l["credibilite"] == credibilite]
        sources = {l["domaine_principal"] for l in cat_articles}
        nbr_fake = sum(1 for l in cat_articles if l["label"] == "fake")
        nbr_real = sum(1 for l in cat_articles if l["label"] == "real")
        proportion_fake = 100 * nbr_fake / len(cat_articles) if cat_articles else 0
        proportion_real = 100 * nbr_real/ len(cat_articles) if cat_articles else 0
        
        print(f" {nom}  | {len(sources):7} | {len(cat_articles):8} | {proportion_fake:5.1f} % | {proportion_real:5.1f} %")
    print()

def retirer_doublons(lignes):
    articles_uniques = {}
    for l in lignes:
        cle = (l["url"], l["title"], l["text"])
        if cle not in articles_uniques:
            articles_uniques[cle] = l 
    return list(articles_uniques.values())

def main():
    print("Lecture du fichier")
    lignes = lire_csv(FICHIER_ENTREE)
    nbr_lignes = len(lignes)
    print(f"Total d'articles : {nbr_lignes}")

    
    lignes = retirer_doublons(lignes)
    print(f"doublons retirés : {nbr_lignes - len(lignes)}")

    resumer_categories(lignes, "AVANT exclusion")

    exclus = charger_exclusions(FICHIER_EXCLUSIONS)

    lignes = [l for l in lignes if l["domaine_principal"] not in exclus and l["title"].strip() and l["text"].strip()]
    print(f"apres exclusion des sources problemes : {len(lignes)}")

    resumer_categories(lignes, "APRES exclusion")

        # (garde les prints des tailles de A, B, C, D : ils servent à décrire le corpus)

    print("Échantillon de 150 articles, tous articles valides confondus")
    echantillon = echantillonner_n(lignes, 150)
    print(f"Nombre final : {len(echantillon)}")

    from collections import Counter
    print(Counter((source_de(l), l["label"]) for l in echantillon))
    ecrire_csv(os.path.join(DOSSIER_SORTIE, "echantillon_150.csv"), echantillon)
    

if __name__ == "__main__":
    main()
