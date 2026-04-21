# Session de développement - 21 avril 2026

## Résumé des modifications

Cette session a apporté des améliorations majeures au système d'extraction WikiSI et au processus de clonage GitLab.

---

## 1. Module d'extraction WikiSI (`wikisi-extract-apps`)

### Nouveau fichier créé
- **`src/app/wikisi/commands/wikisi_extract_apps.py`** (365 lignes)
  - Commande CLI complète pour extraire les applications WikiSI désignées
  - Génère des fichiers JSON et Markdown individuels pour chaque application

### Fonctionnalités principales

#### Configuration (`config/wikisi.yaml`)
```yaml
wikisi:
  output:
    directory: "workplace-ambulon/wikisi/download"
    copy_to_rag: true
    rag_base_directory: "workplace-ambulon/gitlab"

  applications:
    extract:
      Admin EP: adminep
      Ado: ado
      AGILE: agile
      BALISE: balise
      Bulletin Officiel: bo
      CAUSALIS: causalis
      # ... 33 applications au total
```

#### Matching automatique des applications
- Script de matching créé (`temp_match_apps.py`) pour identifier les applications depuis `listeApp.txt`
- 33 applications identifiées sur 46 dans la liste PNM3
- 13 applications non trouvées (AMBULON, PARCAUTO, SIGEFOUPS, VACCINATION, etc.)

#### Options CLI
```bash
ambulon wikisi-extract-apps [OPTIONS]

--config, -c          Fichier de configuration (défaut: config/wikisi.yaml)
--output-dir, -o      Répertoire de sortie
--force, -f           Écraser les fichiers existants
--verbose, -v         Mode verbeux
--quiet, -q          Mode silencieux
```

### Résultats de l'extraction
- **66 fichiers** générés dans `workplace-ambulon/wikisi/download/`:
  - 33 fichiers `*.wikisi.json` (données complètes)
  - 33 fichiers `*.wikisi.md` (documentation formatée)

- **33 fichiers** copiés dans les répertoires RAG:
  - Structure: `workplace-ambulon/gitlab/<nom-appli>.rag/<nom-appli>.wikisi.md`
  - Exemples: `sireines.rag/sireines.wikisi.md`, `adminep.rag/adminep.wikisi.md`

---

## 2. Améliorations du format Markdown

### Ajout du champ "Nom:"
**Fichier modifié:** `src/app/wikisi/core/json_to_md_converter.py`

Avant:
```markdown
# Admin EP

**Nom complet:** Administration des établissements publics
**ID:** 507
```

Après:
```markdown
# Admin EP

**Nom:** Admin EP
**Nom complet:** Administration des établissements publics
**ID:** 507
```

### Extensions de fichiers standardisées
- `.wikisi.json` pour les données JSON
- `.wikisi.md` pour les fichiers Markdown
- Facilite l'identification des fichiers issus de WikiSI

---

## 3. Copie automatique vers RAG

### Configuration
```yaml
wikisi:
  output:
    copy_to_rag: true
    rag_base_directory: "workplace-ambulon/gitlab"
```

### Comportement
- Lors de l'extraction, chaque fichier `*.wikisi.md` est copié dans:
  ```
  workplace-ambulon/gitlab/<nom-appli>.rag/<nom-appli>.wikisi.md
  ```
- Permet d'avoir les informations WikiSI à côté des fichiers de code et wiki

### Structure créée
```
workplace-ambulon/gitlab/
├── sireines.rag/
│   ├── sireines.code.md
│   ├── sireines.wiki.md
│   └── sireines.wikisi.md          ← Nouveau!
├── adminep.rag/
│   └── adminep.wikisi.md            ← Nouveau!
└── ... (33 répertoires .rag)
```

---

## 4. Génération automatique filtered/summarized dans gitlab-clone

### Fichier modifié
**`src/app/gitlab/commands/gitlab_clone.py`** (548 lignes)

### Nouvelles options CLI
```bash
ambulon gitlab-clone [OPTIONS]

--generate-filtered true|false      Générer *.code.filtered.md (défaut: true)
--generate-summarized true|false    Générer *.code.summarized.md (défaut: true)
-E, --all-enhancements             Activer toutes les améliorations
```

### Configuration (`config/gitlab.yaml`)
```yaml
gitlab:
  automation:
    enabled: true
    generate_filtered: true      # Générer *.code.filtered.md
    generate_summarized: true    # Générer *.code.summarized.md
    code_monofile:
      enabled: true
      templates:
        - "{project}.code.md"
        - "{project}.code.html"
```

### Comportement
Lors du clonage GitLab avec `automation.enabled: true`:
1. Clone le dépôt
2. Génère `<project>.code.md` et `<project>.code.html`
3. **Si `generate_filtered: true`**: génère `<project>.code.filtered.md`
4. **Si `generate_summarized: true`**: génère `<project>.code.summarized.md`
5. Applique TOC/iTOC/augment si demandé

### Exemple de sortie
```
workplace-ambulon/gitlab/sireines.rag/
├── sireines.code.md              ← Généré par monofile
├── sireines.code.filtered.md     ← Nouveau! (version allégée)
├── sireines.code.summarized.md   ← Nouveau! (résumé LLM)
├── sireines.code.html
├── sireines.wiki.md
└── sireines.wikisi.md
```

---

## 5. Applications extraites (33 au total)

### Liste complète
1. Admin EP → `adminep`
2. Ado → `ado`
3. AGILE → `agile`
4. BALISE → `balise`
5. Bulletin Officiel → `bo`
6. CAUSALIS → `causalis`
7. DATAPOP ex Soutien Export → `datapop`
8. DPAS web → `dpasweb`
9. Formation-Écologie → `formidd`
10. GESAPP → `gesapp`
11. GTA RenoiRH → `gtarenoirh`
12. Honoré → `honore`
13. Hub RH → `hubrh`
14. LEJIS → `lejis`
15. LITIJ → `litij`
16. Méridienne → `meridienne`
17. moB → `mobilehoop`
18. OCLE → `ocle`
19. Orchidée → `orchidee`
20. ORPA → `orpa`
21. OUPS/SIGEF → `salsa_infocentre`
22. PALOME → `palome`
23. RGP Primes → `primes`
24. RIGA CISIRH → `riga2`
25. SIAM 2 → `siam2`
26. SIJ → `sij`
27. SIREINES → `sireines`
28. SISS → `siss`
29. SPEDDI → `speddi`
30. TTC → `ttc`
31. VIV@CITÉ-2 → `vivacite2`
32. Wiki SI → `wikisi`
33. Zone d'échanges → `zoneechange_legacy`

### Applications non disponibles dans WikiSI
- AMBULON
- PARCAUTO
- SIGEFOUPS
- VACCINATION

---

## 6. Fichiers de configuration mis à jour

### `config/wikisi.yaml` (137 lignes)
- Ajout de la section `applications.extract` avec les 33 applications
- Ajout de `copy_to_rag: true`
- Ajout de `rag_base_directory: "workplace-ambulon/gitlab"`

### `config/gitlab.yaml`
- Ajout de `generate_filtered: true`
- Ajout de `generate_summarized: true`

### `G:\WarchoLife\config\wikisi.yaml`
- Synchronisé avec la configuration du projet

---

## 7. Intégration CLI

### Commande ajoutée
```bash
ambulon wikisi-extract-apps
```

**Fichier modifié:** `src/app/cli/cli.py`
- Ajout du handler pour `wikisi-extract-apps`
- Documentation dans l'aide

---

## 8. Statistiques

### Fichiers créés/modifiés
- **1 nouveau fichier**: `wikisi_extract_apps.py` (365 lignes)
- **3 fichiers modifiés**:
  - `gitlab_clone.py` (+70 lignes environ)
  - `json_to_md_converter.py` (+2 lignes)
  - `cli.py` (+10 lignes)
- **2 fichiers de config mis à jour**:
  - `config/wikisi.yaml`
  - `config/gitlab.yaml`

### Données générées
- **66 fichiers** dans `workplace-ambulon/wikisi/download/`
- **33 fichiers** copiés dans les répertoires `.rag`
- **33 répertoires** `.rag` créés/mis à jour

---

## 9. Flux de travail complet

### Extraction WikiSI
```bash
# 1. Extraire les applications désignées
ambulon wikisi-extract-apps --force

# Génère automatiquement:
# - *.wikisi.json (données complètes)
# - *.wikisi.md (documentation)
# - Copie vers <app>.rag/ si copy_to_rag: true
```

### Clonage GitLab avec post-processing
```bash
# 2. Cloner les dépôts GitLab
ambulon gitlab-clone --config config/gitlab.yaml

# Génère automatiquement (si automation.enabled: true):
# - <project>.code.md
# - <project>.code.filtered.md (si generate_filtered: true)
# - <project>.code.summarized.md (si generate_summarized: true)
# - <project>.wiki.md
# - Fichiers HTML correspondants
```

### Résultat final dans chaque dossier `.rag`
```
<application>.rag/
├── <app>.code.md              # Code source complet
├── <app>.code.filtered.md     # Version allégée
├── <app>.code.summarized.md   # Résumé LLM
├── <app>.wiki.md              # Documentation wiki
└── <app>.wikisi.md            # Informations WikiSI
```

---

## 10. Commandes utiles

### Extraire uniquement certaines applications
Modifier `config/wikisi.yaml`:
```yaml
applications:
  extract:
    SIREINES: sireines
    Admin EP: adminep
```

### Désactiver la copie RAG
```yaml
output:
  copy_to_rag: false
```

### Désactiver filtered/summarized
```bash
ambulon gitlab-clone --generate-filtered false --generate-summarized false
```

Ou dans la config:
```yaml
automation:
  generate_filtered: false
  generate_summarized: false
```

---

## Conclusion

Cette session a créé un pipeline complet d'extraction et de documentation:
1. **WikiSI** → extraction des métadonnées applicatives
2. **GitLab** → extraction du code source et de la documentation
3. **Post-processing** → génération de versions filtrées et résumées
4. **Centralisation** → tous les fichiers réunis dans les dossiers `.rag`

Chaque application dispose maintenant d'un dossier `.rag` contenant:
- Sa documentation WikiSI (métadonnées, domaines, technologies)
- Son code source complet
- Une version filtrée du code (fichiers importants uniquement)
- Un résumé LLM du code
- Sa documentation wiki

Ce système facilite grandement l'analyse et la compréhension des applications du parc applicatif.
