#etape 5
import csv
import os
import random

FICHIER_ENTREE = "data/fakenewsnet_complet_v4.csv"
DOSSIER_SORTIE = "data_out"

TRAIN_SET = 0.70   
VALID_SET = 0.15   
TEST_SET = 0.15 

#retourne ue liste de dictionnaire, un dictionnaire par ligne
def lire_csv(chemin):
    with open(chemin, newline="", encoding="utf-8") as f:
        lecteur = csv.DictReader(f)
        lignes = [ligne for ligne in lecteur]
    return lignes

#Ecrit une liste de dictionnaires dans un fichier csv
def ecrire_csv(chemin, lignes):
    colonnes = list(lignes[0].keys())
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        ecrivain = csv.DictWriter(f, fieldnames=colonnes)
        ecrivain.writeheader()
        ecrivain.writerows(lignes)

# print les proportions de fake et de real
def proportion_fake_real(lignes):
    total = len(lignes)
    n_fake = len([l for l in lignes if l["label"] == "fake"])
    n_real = len([l for l in lignes if l["label"] == "real"])
    pct_fake = round(100 * n_fake / total, 1)
    pct_real = round(100 * n_real / total, 1)
    return f"fake={pct_fake}% real={pct_real}%"


# egalise la taille des 2 groupes pour avoir exactement la meme taille de connu vs peu_connu
# et l meme proportion fake/real cad le meme nombre de fake dans connu que dans peu_connu , et meme chose pour real
# on veut que le nomnre de fake news dans connu soit egale au fake news dans peu connu
# et on veut que le nombre de real_news dans connu = nbr de real_news dans peu_connu
# nbr de fake_news n'est pas necessairement = nbr de real_news
# je fais ceci parce que mes donnéées ne sont pas equitables la proportion du connu est bcp plus grande 
# que celle du peu_connu, on veut eviter que la decision soit influencée par le nombre d'exemples
# groupe_a : connu
# groupe_b : peu_connu
def egaliser_deux_groupes(groupe_a, groupe_b):
    
    # separer groupe connu selon "fake" et "real" 
    fake_a = [l for l in groupe_a if l["label"] == "fake"]
    real_a = [l for l in groupe_a if l["label"] == "real"]

    # separer groupe peu_connu selon "fake" et "real" 
    fake_b = [l for l in groupe_b if l["label"] == "fake"]
    real_b = [l for l in groupe_b if l["label"] == "real"]

    print(f"    fake : {len(fake_a)} (groupe connu) vs {len(fake_b)} (groupe peu connu)")
    print(f"    real : {len(real_a)} (groupe connu) vs {len(real_b)} (groupe peu connu)")

    # chercher la taille min selon fake/real
    n_fake = min(len(fake_a), len(fake_b)) # min de fake_news 
    n_real = min(len(real_a), len(real_b)) # min de real_news

    # refaire des ensembles d'exemples 
    fake_a = random.sample(fake_a, n_fake) # fake connu
    fake_b = random.sample(fake_b, n_fake) # fake peu_connu

    real_a = random.sample(real_a, n_real) # real connu
    real_b = random.sample(real_b, n_real) # real peu_connu

    # on a la meme taille de connu et peu_connu
    print(f"on garde {n_fake} fake et {n_real} real de chaque cote")

    # assembler les 2 ensemble (fake + real) pour chaque groupe 
    a_egalise = fake_a + real_a
    b_egalise = fake_b + real_b

    # melanger
    random.shuffle(a_egalise)
    random.shuffle(b_egalise)

    return a_egalise, b_egalise

# on divise une liste de lignes en train/valid/test sets
# on separe d abord les lignes selon fake/real 
# apers on decoupe chacune des 2 listes selon les proportions 70/15/15 

def split_train_valid_test(lignes):

    # separer fake /real
    fake = [l for l in lignes if l["label"] == "fake"]
    real = [l for l in lignes if l["label"] == "real"]

    # melanger les exemples 
    random.shuffle(fake)
    random.shuffle(real)

    # calculer la taille du fake des set selon 70/15/15
    n_fake = len(fake)
    n_fake_train = int(n_fake * TRAIN_SET)
    n_fake_valid = int(n_fake * VALID_SET)
    # le reste (n_fake -n_fake_train -n_fake_valid) va dans test

    # decouper l ensemble fake en 70/15/15
    fake_train = fake[:n_fake_train]
    fake_valid = fake[n_fake_train:n_fake_train + n_fake_valid]
    fake_test = fake[n_fake_train + n_fake_valid:]

    # calculer la taille du real des set selon 70/15/15
    n_real = len(real)
    n_real_train = int(n_real * TRAIN_SET)
    n_real_valid = int(n_real * VALID_SET)

    # decouper l ensemble real en 70/15/15
    real_train = real[:n_real_train]
    real_valid = real[n_real_train:n_real_train + n_real_valid]
    real_test = real[n_real_train + n_real_valid:]

    # --- Etape 4 : recoller fake + real pour chaque sous-partie ---
    train = fake_train + real_train
    valid = fake_valid + real_valid
    test = fake_test + real_test

    random.shuffle(train)
    random.shuffle(valid)
    random.shuffle(test)

    return train, valid, test

def main():
    print("Début")
    lignes = lire_csv(FICHIER_ENTREE)

    # creer les lots connu et peu_connu
    lignes_connu = [l for l in lignes if l["S"] == "s0_connue"]
    lignes_peu_connu = [l for l in lignes if l["S"] == "s1_peu_connue"]

    print(f"  - Sources connues     : {len(lignes_connu)} articles")
    print(f"  - Sources peu connues : {len(lignes_peu_connu)} articles")

    print("\nEgalisation des lots connu / peu_connu :")
    lignes_connu, lignes_peu_connu = egaliser_deux_groupes(lignes_connu, lignes_peu_connu)
    print(f"  - Sources connu     : {len(lignes_connu)} articles apres egalisation")
    print(f"  - Sources peu_connu : {len(lignes_peu_connu)} articles apres egalisation")

    # lot mixte
    lignes_mixte = lignes_connu + lignes_peu_connu
    random.shuffle(lignes_mixte)
    print(f"\nTaille du lot mixte : {len(lignes_mixte)} articles au total")

    # dictionnaire lots 
    lots = {
        "mixte": lignes_mixte,
        "connu": lignes_connu,
        "peu_connu": lignes_peu_connu,
    }

    # separation des lots selon train/valid/test 
    for nom_lot, data in lots.items():
        train, valid, test = split_train_valid_test(data)

        chemin_train = os.path.join(DOSSIER_SORTIE, f"{nom_lot}_train.csv")
        chemin_valid = os.path.join(DOSSIER_SORTIE, f"{nom_lot}_valid.csv")
        chemin_test = os.path.join(DOSSIER_SORTIE, f"{nom_lot}_test.csv")

        ecrire_csv(chemin_train, train)
        ecrire_csv(chemin_valid, valid)
        ecrire_csv(chemin_test, test)

        print(f"\nLot '{nom_lot}' :")
        print(f"  trainSet -> {chemin_train} ({len(train)} lignes) "
              f"- {proportion_fake_real(train)}")
        print(f"  validSet -> {chemin_valid} ({len(valid)} lignes) "
              f"- {proportion_fake_real(valid)}")
        print(f"  testSet  -> {chemin_test} ({len(test)} lignes) "
              f"- {proportion_fake_real(test)}")

    print("\nTermine ! Les 9 fichiers sont prets dans le dossier 'data/'.")

if __name__ == "__main__":
    main()
