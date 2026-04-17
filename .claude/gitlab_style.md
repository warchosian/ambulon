## 📄 Exemple de traitement PIAG


# 🤖 Ambulon - PIAG RAG CLI

Documentation des commandes pour gérer les collections RAG via l'outil `ambulon`.

> 📌 **Plateforme** : GitLab | **OS** : Windows | **Environnement** : Conda `ambulon`

---

## 🔍 Lister les collections RAG

```bash
ambulon piag-rag-collection-list
```

<details>
<summary>👉 Voir le résultat</summary>

> <code>
> G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\ambulon\Lib\site-packages\requests\__init__.py:113: RequestsDependencyWarning
> Config resolved: G:\WarchoLife\config\piag.yaml
>
> Collections RAG récupérées avec succès :
> - PNM3_AMBULON (ID: CcjDvYhcIL1r9oG5)
> - PNM3_FORMIDD (ID: CHzOAB3896m0u0Er)
> - PNM3_LAMBDA (ID: CzvttXSD5Cx8SWPh)
> - PNM3_SIREINES (ID: CGrvE2oatf01bV0C)
>
> Résumé: 4 collection(s)
> </code>
</details>

---

## ➕ Créer une collection RAG

```bash
ambulon piag-rag-create ^
  --collection-name PNM3_SIREINES ^
  --description "Documentation complète SIREINES : DAT, C4, Composants, Wiki" ^
  --directory applications/PNM3_SIREINES.rag ^
  --extensions md,pdf
```

<details>
<summary>👉 Voir le résultat</summary>

> <code>
> ============================================================
> CRÉATION DE RAG
> ============================================================
> Collection: PNM3_SIREINES
> Fichiers trouvés: 5
>
> [1/2] Création de la collection... ✓ (ID: CnWq88KElFhzYRcz)
>
> [2/2] Téléversement des documents...
>   [  1/  5] sireines.cctp.md                                        ✓
>   [  2/  5] sireines.code.md                                        ✓
>   [  3/  5] sireines.components.md                                  ✓
>   [  4/  5] sireines.dat_c4model.md                                 ✓
>   [  5/  5] sireines.wiki.md                                        ✓
>
> RÉCAPITULATIF
> Collection: PNM3_SIREINES | ID: CnWq88KElFhzYRcz | Documents: 5
> </code>
</details>

---

## 🔎 Rechercher dans une collection

```bash
ambulon piag-rag-search ^
  --collection-name PNM3_SIREINES ^
  --query "Architecture, DAT" ^
  --top-k 10 ^
  --timeout 10s ^
  -o piag_workplace/chunks/chunk.PNM3_SIREINES.dat_c4model.json
```

<details>
<summary>👉 Voir le résultat (succès)</summary>

> <code>
> [INFO] Recherche RAG en cours dans 1 collection(s)...
> [INFO] Recherche terminée.
>
> ✅ Résultats sauvegardés dans: piag_workplace/chunks/chunk.PNM3_SIREINES.dat_c4model.json
>    10 chunk(s) récupéré(s)
> </code>
</details>

---

## 💬 Interroger le RAG avec contexte

```bash
ambulon piag-chat-query ^
  --question-file .claude/prompts/prompt.dat_c4model.md ^
  --chunks piag_workplace/chunks/chunk.PNM3_SIREINES.dat_c4model.json ^
  --timeout 20m ^
  --max-retries 5 ^
  --retry-delay 1m ^
  -o piag_workplace/responses/response.PNM3_SIREINES.dat_c4model.md
```

<details>
<summary>👉 Voir le résultat (avec retries)</summary>

> <code>
> [INFO] Chargement des chunks... 10 chunks chargés
> [INFO] Appel de l'API PIAG...
> [WARNING] ❌ Erreur (tentative 1/5): 504 Gateway Timeout
> [INFO] ⏳ Nouvelle tentative dans 60s...
> [WARNING] ❌ Erreur (tentative 2/5): 504 Gateway Timeout
> [INFO] ⏳ Nouvelle tentative dans 60s...
> [INFO] ✅ Succès à la tentative 5/5
> [INFO] Réponse sauvegardée dans: response.PNM3_SIREINES.dat_c4model.md
> </code>
</details>

---

## 🗑️ Supprimer une collection

```bash
ambulon piag-rag-collection-rm --collection-name PNM3_SIREINES
```

<details>
<summary>👉 Voir le résultat</summary>

> <code>
> ⚠️ ATTENTION: 2 collections trouvées avec le nom 'PNM3_SIREINES':
>    1. ID: CGrvE2oatf01bV0C
>    2. ID: CnWq88KElFhzYRcz
>
> Voulez-vous vraiment supprimer ? (oui/non): oui
> Collection supprimée avec succès
> </code>
</details>

---

## 📚 Référence rapide

| Commande | Description |
|----------|-------------|
| `piag-rag-collection-list` | Lister les collections |
| `piag-rag-create` | Créer une collection |
| `piag-rag-search` | Rechercher des chunks |
| `piag-chat-query` | Interroger avec contexte |
| `piag-rag-collection-rm` | Supprimer une collection |

---

## ⚠️ Dépannage courant

| Erreur | Solution |
|--------|----------|
| `NameResolutionError` | Vérifiez VPN et DNS |
| `504 Gateway Timeout` | L'outil retente automatiquement |
| Collections dupliquées | Utilisez `--collection-id <ID>` |
| `No such file or directory` | Créez le dossier de sortie |





