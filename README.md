# fakeNewsProject_v2
# Grande étape 1 — Préparation et annotation des données

## Étape 1 — Construction du fichier CSV complet

Le dataset utilisé s'appelle **FakeNewsNet**. Sous sa forme originale, il se présente comme un ensemble de répertoires, et non comme un fichier CSV unique.

Pour obtenir un fichier CSV complet à partir de ces répertoires, il faut exécuter :

```
script_1.py
```

Ce script génère le fichier :

```
data/fakenewsnet_complet.csv
```
> **Note** — inutile de lancer `script_1.py`, puisque vous ne disposez pas du répertoire original du dataset. Vous trouverez directement le fichier qu'il produit en sortie dans le dossier `data/`.

## Étape 2 — Remplissage des champs vides

Pour annoter les données, les scripts suivants doivent être exécutés dans l'ordre indiqué par leur numéro.

**`script_inconnue_2.py`** remplit les champs `source` et `auteur` vides par la valeur `inconnu`.

| | |
|---|---|
| Entrée | `data/fakenewsnet_complet.csv` |
| Sortie | `data/fakenewsnet_complet_v2.csv` |

## Étape 3 — Extraction du nom du média

**`script_media_3.py`** ajoute une colonne contenant le nom du média, formaté sans le préfixe `https`.

| | |
|---|---|
| Entrée | `data/fakenewsnet_complet_v2.csv` |
| Sortie | `data/fakenewsnet_complet_v3.csv` |

## Étape 4 — Attribution de la notoriété

**`script_score_4.py`** attribue à chaque média du dataset un score de **notoriété**, en se basant sur le classement Tranco.

| | |
|---|---|
| Entrée | `data/fakenewsnet_complet_v3.csv` |
| Sortie | `data/fakenewsnet_complet_v4.csv` |

## Étape 5 — Attribution de la crédibilité

**`script_cred_5.py`** attribue à chaque média du dataset un score de **crédibilité**, à partir d'une liste de crédibilité construite à partir du travail scientifique suivant :

> Burdisso, S., Sánchez-Cortés, D., Villatoro-Tello, E., & Motlicek, P. (2024). *Reliability Estimation of News Media Sources: Birds of a Feather Flock Together*. Idiap Research Institute. Publié à NAACL 2024.

Liste de crédibilité : [huggingface.co/datasets/sergioburdisso/news_media_reliability](https://huggingface.co/datasets/sergioburdisso/news_media_reliability/tree/main)

| | |
|---|---|
| Entrée | `data/fakenewsnet_complet_v4.csv` |
| Sortie | `data/fakenewsnet_complet_v5.csv` |

## Étape 6 — Regroupement par catégorie

**`script_categorie_6.py`** regroupe les articles selon quatre catégories, définies par le croisement de la notoriété et de la crédibilité du média :

| Catégorie | Notoriété | Crédibilité |
|---|---|---|
| A | Connu | Crédible |
| B | Connu | Peu crédible |
| C | Peu connu | Crédible |
| D | Peu connu | Peu crédible |

| | |
|---|---|
| Entrée | `"data/fakenewsnet_complet_v5.csv"` |
| Sortie | Un fichier CSV par catégorie demandée, sauvegardé dans le dossier `data_cat/` |

Par défaut, ce script produit les fichiers des catégories **B** et **D**.

> **Note** — pour produire les fichiers des deux autres catégories (A et C), il suffit de relancer le `main` de `script_categorie_6.py` en précisant les catégories voulues.

Les fichiers des catégories B et D ainsi obtenus sont ensuite utilisés dans le notebook Kaggle pour la suite du travail.

---

# Grande étape 2 — Exécution des modèles sur Kaggle

Cette étape consiste à lancer les modèles de langage sur les fichiers des deux catégories (B et D) obtenus à l'étape précédente.

J'utilise deux notebooks Kaggle :

- **`fakeNewsProject`** pour l'interrogation du LLM assisté du RAG
- **`fakeNewsWithoutRAG`** pour l'interrogation du LLM seul, sans le RAG

Pour les deux notebooks, le dataset d'entrée est **`data_in`**, qui contient les deux fichiers de catégorie produits lors de l'étape d'annotation.

Les résultats obtenus sont sauvegardés dans deux autres datasets Kaggle :

- **`test_stat`** pour les résultats du modèle **Gemma**
- **`test_set_qwen`** pour les résultats du modèle **Qwen**

Ces résultats sont placés dans des datasets séparés (plutôt que dans le dossier de travail temporaire du notebook) afin de pouvoir ensuite y lancer le **test de Cochran's Q**, qui nécessite de recharger les fichiers de résultats dans une session ultérieure.

Le calcul du **test de Cochran's Q** se fait uniquement sur le notebook **`fakeNewsProject`**.

> **Prérequis avant de lancer les notebooks** : dans chaque notebook, j'utilise GPU T4 de kaggle, et Ollama ainsi que le modèle utilisé (`gemma3:4b` ou `qwen2.5:3b` selon le notebook) doivent être installés et téléchargés en début de session — voir la cellule d'installation au début de chaque notebook.
