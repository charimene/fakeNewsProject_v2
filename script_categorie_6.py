# Etape 6
# script qui va regrouper les articles selon leur catégories A,B,C,D
# catégorie A = les articles qui sont connus et qui sont crédibles
# catégorie B = les articles qui sont connus et qui sont pas crédibles
# catégorie C = les articles qui sont pas connus et qui sont crédibles
# catégorie D = les articles qui sont pas connus et qui sont pas crédibles

import csv
import os
import random

FICHIER_ENTREE = "data/fakenewsnet_complet_v5.csv"
DOSSIER_SORTIE = "data_cat"

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

def egaliser_categories(groupe_a, groupe_b):
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

def main():
    print("Lecture du fichier")
    lignes = lire_csv(FICHIER_ENTREE)
    print(f"Total d'articles : {len(lignes)}")

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

    # Écrire les articles dans les fichiers correspondants
    # with open(os.path.join(DOSSIER_SORTIE, "categorie_A.csv"), "w", newline="", encoding="utf-8") as f:
    #     writer = csv.DictWriter(f, fieldnames=lignes[0].keys())
    #     writer.writeheader()
    #     writer.writerows(cat_a)

    # with open(os.path.join(DOSSIER_SORTIE, "categorie_B.csv"), "w", newline="", encoding="utf-8") as f:
    #     writer = csv.DictWriter(f, fieldnames=lignes[0].keys())
    #     writer.writeheader()
    #     writer.writerows(cat_b)

    # with open(os.path.join(DOSSIER_SORTIE, "categorie_C.csv"), "w", newline="", encoding="utf-8") as f:
    #     writer = csv.DictWriter(f, fieldnames=lignes[0].keys())
    #     writer.writeheader()
    #     writer.writerows(cat_c)

    # with open(os.path.join(DOSSIER_SORTIE, "categorie_D.csv"), "w", newline="", encoding="utf-8") as f:
    #     writer = csv.DictWriter(f, fieldnames=lignes[0].keys())
    #     writer.writeheader()
    #     writer.writerows(cat_d)

    # egaliser les catégories en prenant le nombre min d'articles parmi les 2 catégories passées en param

    print("Égalisation des catégories B et D")
    cat_b_egalise, cat_d_egalise = egaliser_categories(cat_b, cat_d)
    print(f"  -> B : {len(cat_b_egalise)} articles apres egalisation")
    print(f"  -> D : {len(cat_d_egalise)} articles apres egalisation")

    ecrire_csv(os.path.join(DOSSIER_SORTIE, "categorie_B_egalise.csv"), cat_b_egalise)
    ecrire_csv(os.path.join(DOSSIER_SORTIE, "categorie_D_egalise.csv"), cat_d_egalise)

if __name__ == "__main__":
    main()
