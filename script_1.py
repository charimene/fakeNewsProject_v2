# etape 1
import os
import json
import csv

def charger_categorie(dossier_racine, label, nom_dossier):
    lignes = []
    for nom_article in os.listdir(dossier_racine):
        chemin_json = os.path.join(dossier_racine, nom_article, 'news_article.json')
        if os.path.exists(chemin_json):
            with open(chemin_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['id'] = nom_article
                data['label'] = label
                # Nettoyage : ne garder que le premier élément de la liste authors (souvent le vrai nom)
                if isinstance(data.get('authors'), list) and len(data['authors']) > 0:
                    data['authors'] = data['authors'][0]
                else:
                    data['authors'] = None
                # On ne garde que les champs utiles (le reste comme meta_data est trop complexe pour un CSV simple)
                data_utile = {
                    'id': data.get('id'),
                    'label': data.get('label'),
                    'dossier_origine': nom_dossier,  # <-- nouvelle colonne : gossipcop_fake, gossipcop_real, politifact_fake ou politifact_real
                    'title': data.get('title'),
                    'text': data.get('text'),
                    'source': data.get('source'),
                    'authors': data.get('authors'),
                    'url': data.get('url'),
                    'publish_date': data.get('publish_date'),
                }
                lignes.append(data_utile)
    return lignes

# Charger les 4 catégories (AJUSTE LE CHEMIN selon où sont tes dossiers)
# Attention : ce repertoire FakeNewsNet_Dataset/gossipcop_fake' n'existe pas sur git 
toutes_les_lignes = []
toutes_les_lignes += charger_categorie('FakeNewsNet_Dataset/gossipcop_fake', 'fake', 'gossipcop_fake')
toutes_les_lignes += charger_categorie('FakeNewsNet_Dataset/gossipcop_real', 'real', 'gossipcop_real')
toutes_les_lignes += charger_categorie('FakeNewsNet_Dataset/politifact_fake', 'fake', 'politifact_fake')
toutes_les_lignes += charger_categorie('FakeNewsNet_Dataset/politifact_real', 'real', 'politifact_real')

print("Nombre total d'articles :", len(toutes_les_lignes))

# Récupérer toutes les colonnes possibles (certains articles peuvent avoir des champs différents)
toutes_les_colonnes = set()
for ligne in toutes_les_lignes:
    toutes_les_colonnes.update(ligne.keys())
toutes_les_colonnes = list(toutes_les_colonnes)

# Écrire le CSV
with open('data/fakenewsnet_complet.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=toutes_les_colonnes)
    writer.writeheader()
    writer.writerows(toutes_les_lignes)

print("Fichier sauvegardé : fakenewsnet_complet.csv")