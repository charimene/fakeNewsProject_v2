# Etape 6
# script qui va regrouper les articles selon leur catégories A,B,C,D
# catégorie A = les articles qui sont connus et qui sont crédibles
# catégorie B = les articles qui sont connus et qui sont pas crédibles
# catégorie C = les articles qui sont pas connus et qui sont crédibles
# catégorie D = les articles qui sont pas connus et qui sont pas crédibles

import csv
import os
import random
import re  

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


def source_de(l):
    # retourne si l'article est de gossipcop ou politifact, en se basant sur l'id de l'article
    return "gossipcop" if l["id"].startswith("gossipcop") else "politifact"


def titre_est_la_source(l):
    titre = l["title"].strip().lower()
    return titre == l["domaine"].lower() or titre == l["domaine_principal"].lower()


#focntion qui remplace le nom du domaine ou domaine_principal par le mot neutre "media"
def remplacer_domaine(texte, l):
    for nom in (l["domaine"], l["domaine_principal"]):
        texte = texte.replace(nom, "media")
    return texte


def nettoyer_titre(l):
    titre = l["title"].strip()
    sep = r"[\-\|:–—]"

    for nom in (l["domaine"], l["domaine_principal"]):
        n = re.escape(nom)
        titre = re.sub(rf"^\s*{n}\s*{sep}?\s*", "", titre, flags=re.IGNORECASE)   # au début : on retire
        titre = re.sub(rf"\s*{sep}?\s*{n}\s*$", "", titre, flags=re.IGNORECASE)   # à la fin : on retire
        titre = re.sub(rf"\s*{n}\s*", " media ", titre, flags=re.IGNORECASE)      # au milieu : on remplace

    return re.sub(r"\s+", " ", titre).strip()


def echantillonner_n(lignes, n):
    strates = sorted({(source_de(l), l["label"]) for l in lignes})
    nbr_article_cellule = n // len(strates)
    reste = n % len(strates) # le nb d'articles qui reste a tirer apres avoir pris un nombre egal dans chaque strate

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

    lignes = [l for l in lignes if l["domaine_principal"] not in exclus 
              and l["title"].strip() 
              and l["text"].strip() 
              and not titre_est_la_source(l)]
    
    print(f"apres exclusion des sources problemes : {len(lignes)}")

    resumer_categories(lignes, "APRES exclusion")

    domaines = sorted({l["domaine_principal"] for l in lignes if l["domaine_principal"] != "inconnu"})
    ecrire_csv(os.path.join(DOSSIER_SORTIE, "domaines_valides.csv"), [{"domaine_principal": d} for d in domaines])
    

    print("Échantillon de 150 articles, tous articles valides confondus")
    echantillon = echantillonner_n(lignes, 150)
    print(f"Nombre final : {len(echantillon)}")

    for l in echantillon:
        l["title_original"] = l["title"]                    # copie de l'original
        l["text_original"] = l["text"]
        l["title"] = nettoyer_titre(l)                      # ecrase title par la version nettoyee
        l["text"] = remplacer_domaine(l["text"], l)         # ecrase text par la version nettoyeee

    from collections import Counter
    print(Counter((source_de(l), l["label"]) for l in echantillon))
    ecrire_csv(os.path.join(DOSSIER_SORTIE, "echantillon_150.csv"), echantillon)
    

if __name__ == "__main__":
    main()
