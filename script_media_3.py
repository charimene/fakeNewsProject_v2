# etape 3
# script qui va creer une autre colonne qui contiendrait le nom du média formaté sans le https

import csv
from urllib.parse import urlparse

lignes = []
with open('data/fakenewsnet_complet_v2.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for ligne in reader:
        url = ligne['source']
        if url == 'inconnu':
            domaine = 'inconnu'
        else:
            if not url.startswith('http'):
                url = 'http://' + url
            domaine = urlparse(url).netloc.replace('www.', '')
        ligne['domaine'] = domaine
        lignes.append(ligne)

with open('data/fakenewsnet_complet_v3.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=lignes[0].keys())
    writer.writeheader()
    writer.writerows(lignes)