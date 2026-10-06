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
DOSSIER_SORTIE = "data_cat"
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


def main():
    print("Lecture du fichier")
    lignes = lire_csv(FICHIER_ENTREE)
    print(f"Total d'articles : {len(lignes)}")

    resumer_categories(lignes, "AVANT exclusion")

    exclus = charger_exclusions(FICHIER_EXCLUSIONS)
    lignes = [l for l in lignes if l["domaine_principal"] not in exclus and l["title"].strip() and l["text"].strip()]
    print(f"apres exclusion des sources problemes : {len(lignes)}")

    resumer_categories(lignes, "APRES exclusion")
    
    # Séparer les articles en catégories
    cat_a = [l for l in lignes if l["notoriete"] == "s0_connue" and l["credibilite"] == "credible"]
    cat_b = [l for l in lignes if l["notoriete"] == "s0_connue" and l["credibilite"] == "peu_credible"]
    cat_c = [l for l in lignes if l["notoriete"] == "s1_peu_connue" and l["credibilite"] == "credible"]
    cat_d = [l for l in lignes if l["notoriete"] == "s1_peu_connue" and l["credibilite"] == "peu_credible"]

    print("la taille des catégories avant égalisation :")
    print(f"Catégorie A : {len(cat_a)} articles")
    print(f"Catégorie B : {len(cat_b)} articles")
    print(f"Catégorie C : {len(cat_c)} articles")
    print(f"Catégorie D : {len(cat_d)} articles")


    # egaliser les categories en prenant le nombre min d'articles parmi les 2 categories passees en param

    print("Égalisation des catégories B et D")
    cat_b_egalise, cat_d_egalise = egaliser_categories(cat_b, cat_d)
    print(f"  -> B : {len(cat_b_egalise)} articles apres egalisation")
    print(f"  -> D : {len(cat_d_egalise)} articles apres egalisation")

    #fichiers complets
    ecrire_csv(os.path.join(DOSSIER_SORTIE, "categorie_B_egalise.csv"), cat_b_egalise)
    ecrire_csv(os.path.join(DOSSIER_SORTIE, "categorie_D_egalise.csv"), cat_d_egalise)

    print("Égalisation des catégories A et C")
    cat_a_egalise, cat_c_egalise = egaliser_categories(cat_a, cat_c)
    print(f"  -> A : {len(cat_a_egalise)} articles apres egalisation")
    print(f"  -> C : {len(cat_c_egalise)} articles apres egalisation")

    #fichiers complets
    ecrire_csv(os.path.join(DOSSIER_SORTIE, "categorie_A_egalise.csv"), cat_a_egalise)
    ecrire_csv(os.path.join(DOSSIER_SORTIE, "categorie_C_egalise.csv"), cat_c_egalise)

    #LE choix de n articles se fait ici et non sur Kaggle
    #n =150 articles par catégorie
    print("Echantillonnage de 150 articles pour B et D")

    cat_b_150 = echantillonner(cat_b_egalise, 150)
    cat_d_150 = echantillonner(cat_d_egalise, 150)

    ecrire_csv(os.path.join(DOSSIER_SORTIE, "cat_B_150.csv"),cat_b_150)

    ecrire_csv(os.path.join(DOSSIER_SORTIE, "cat_D_150.csv"),cat_d_150)


if __name__ == "__main__":
    main()
