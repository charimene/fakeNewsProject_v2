# etape 2
# script qui va remplir les champs de source et d'auteur vides avec inconnu

import csv

lignes = []
with open('data/fakenewsnet_complet.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for ligne in reader:
        if not ligne['source']:  # champ vide
            ligne['source'] = 'inconnu'
        if not ligne['authors']:
            ligne['authors'] = 'inconnu'
        lignes.append(ligne)

# Sauvegarder le nouveau CSV
with open('data/fakenewsnet_complet_v2.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=lignes[0].keys())
    writer.writeheader()
    writer.writerows(lignes)

print('Fichier sauvegardé : fakenewsnet_complet_v2.csv')