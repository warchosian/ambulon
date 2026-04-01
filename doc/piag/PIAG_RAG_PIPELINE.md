# Pipeline RAG PIAG - Documentation

**Version** : 3.1.0+  
**Date** : 2026-03-22

---

## Vue d'ensemble

Le `piag-rag-then-chat` est un orchestrateur qui enchaîne automatiquement les 4 étapes du workflow RAG :

1. **INIT** : Création/suppression de la collection RAG
2. **INGEST** : Upload et indexation des documents
3. **CHUNK** : Recherche sémantique (création des chunks)
4. **GENERATE** : Génération de la réponse via chat

---

## Convention de nommage systématique

À partir de seulement **3 arguments** (`--source`, `--query`, `--prompt`), tous les noms sont dérivés automatiquement :

| Argument | Valeur exemple | Dérivation |
|----------|----------------|------------|
| `--source` | `applications/PNM3_SIREINES.rag` | Collection: `PNM3_SIREINES` |
| `--query` | `"Architecture, DAT"` | Slug: `architecture_dat` |
| `--prompt` | `prompt.dat_c4model.md` | Type: `dat_c4model` |

**Résultats auto-générés** :
- **Collection** : `PNM3_SIREINES` (nom du répertoire sans `.rag`)
- **Chunks** : `piag_workplace/chunks/chunk.PNM3_SIREINES.architecture_dat.json`
- **Réponse** : `piag_workplace/responses/response.PNM3_SIREINES.dat_c4model.md`

---

## Usage

### Pipeline complet (4 étapes)

```batch
ambulon piag-rag-then-chat run ^
  --source applications/PNM3_SIREINES.rag ^
  --prompt .claude/prompts/prompt.dat_c4model.md ^
  --query "Architecture, DAT"
```

### Étapes individuelles

```batch
REM Étape 1: Initialisation
ambulon piag-rag-then-chat init --source applications/PNM3_SIREINES.rag --force

REM Étape 2: Ingestion
ambulon piag-rag-then-chat ingest --source applications/PNM3_SIREINES.rag --wait-index 60

REM Étape 3: Chunking
ambulon piag-rag-then-chat chunk ^
  --source applications/PNM3_SIREINES.rag ^
  --query "Architecture, DAT"

REM Étape 4: Génération
ambulon piag-rag-then-chat generate ^
  --source applications/PNM3_SIREINES.rag ^
  --prompt .claude/prompts/prompt.dat_c4model.md
```

---

## Options

### Commande `run` (pipeline complet)

| Option | Description | Défaut |
|--------|-------------|--------|
| `--source, -s` | Répertoire source (obligatoire) | - |
| `--prompt, -p` | Fichier prompt (obligatoire) | - |
| `--query, -q` | Requête de recherche | `"Architecture, DAT"` |
| `--extensions, -e` | Extensions à uploader | `md,pdf` |
| `--top-k, -k` | Nombre de chunks | `10` |
| `--wait-index, -w` | Attente indexation (secondes) | `60` |
| `--timeout-search` | Timeout recherche RAG | `10s` |
| `--timeout-generate` | Timeout génération | `20m` |
| `--max-retries, -r` | Nombre max de retries | `5` |
| `--retry-delay` | Délai entre retries | `1m` |
| `--force, -f` | Forcer suppression existant | `False` |

---

## Exemples avancés

### Pipeline avec prompt CCF ISO 29148

```batch
ambulon piag-rag-then-chat run ^
  --source applications/PNM3_SIREINES.rag ^
  --prompt .claude/prompts/prompt.ccf_iso29148.md ^
  --query "Exigences fonctionnelles"
```

**Fichiers générés** :
- Collection : `PNM3_SIREINES`
- Chunks : `piag_workplace/chunks/chunk.PNM3_SIREINES.exigences_fonctionnelles.json`
- Réponse : `piag_workplace/responses/response.PNM3_SIREINES.ccf_iso29148.md`

### Pipeline avec prompt CST ISO 25010

```batch
ambulon piag-rag-then-chat run ^
  --source applications/GAIA.rag ^
  --prompt .claude/prompts/prompt.cst_iso25010.md ^
  --query "Critères de qualité"
```

**Fichiers générés** :
- Collection : `GAIA`
- Chunks : `piag_workplace/chunks/chunk.GAIA.criteres_de_qualite.json`
- Réponse : `piag_workplace/responses/response.GAIA.cst_iso25010.md`

---

## Tableau de correspondance

| Répertoire source | Requête | Fichier prompt | Collection | Fichier chunks | Fichier réponse |
|-------------------|---------|----------------|------------|----------------|-----------------|
| `PNM3_SIREINES.rag` | `"Architecture, DAT"` | `prompt.dat_c4model.md` | `PNM3_SIREINES` | `chunk.PNM3_SIREINES.architecture_dat.json` | `response.PNM3_SIREINES.dat_c4model.md` |
| `PNM3_SIREINES.rag` | `"Exigences"` | `prompt.ccf_iso29148.md` | `PNM3_SIREINES` | `chunk.PNM3_SIREINES.exigences.json` | `response.PNM3_SIREINES.ccf_iso29148.md` |
| `GAIA.rag` | `"Architecture"` | `prompt.dat_archimate.md` | `GAIA` | `chunk.GAIA.architecture.json` | `response.GAIA.dat_archimate.md` |

---

## Avantages

| Avantage | Description |
|----------|-------------|
| **Minimalisme** | Seuls `--source`, `--query`, `--prompt` sont obligatoires |
| **Traçabilité** | Nom de fichier = source + requête/prompt |
| **Non-ambiguïté** | Pas de confusion entre différents runs |
| **Parallélisme** | Analyses multiples sur même source avec différentes requêtes/prompts |
| **Reproductibilité** | Métadonnées injectées dans chaque fichier |

---

## Structure des fichiers

```
ambulon/
├── applications/
│   └── PNM3_SIREINES.rag/          ← Documents sources (*.md, *.pdf)
├── .claude/
│   └── prompts/
│       └── prompt.dat_c4model.md   ← Prompt pour la génération
└── piag_workplace/                 ← Créé automatiquement
    ├── chunks/
    │   └── chunk.PNM3_SIREINES.architecture_dat.json  ← Chunks RAG
    └── responses/
        └── response.PNM3_SIREINES.dat_c4model.md      ← Réponse générée
```

---

## Métadonnées

Chaque fichier généré contient des métadonnées traçables dans l'en-tête.

---

**Auteur** : Équipe Ambulon  
**Dernière mise à jour** : 2026-03-22
curl -X POST ^
    -H "Authorization: token YOUR_GITHUB_TOKEN" ^
    -H "Content-Type: application/octet-stream" ^
    --data-binary "@dist\ambulon-3.2.0-py3-none-any.whl" ^
    "https://uploads.github.com/repos/warchosian/ambulon/releases/ID_RELEASE/assets?name=ambulon-3.2.0-py3-none-any.whl"    
