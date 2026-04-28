**Prompt – Génération automatisée du Dossier d’Exploitation (DEX) pour le projet SIREINES**  
*(à copier‑colle‑r dans votre LLM : ChatGPT, Claude, Gemini, …)*  

---  

## 🎯 Objectif du prompt  

Faire rédiger à l’IA un **Dossier d’Exploitation (DEX)** complet, conforme au modèle :  

1. **Structure obligatoire** (16 sections) – voir tableau ci‑dessous.  
2. **Contenu** : informations tirées des documents fournis (code source, wiki, README, procédures de déploiement, etc.).  
3. **Personnalisation** : les champs entre `[…]` sont à remplacer / compléter par les équipes projet (ex. SLA, politiques de sauvegarde, contacts, etc.).  

---  

## 📂 Contexte projet (extraits des sources)  

| Élément | Valeur tirée des documents | À compléter si besoin |
|---|---|---|
| **Nom de l’application** | **SIREINES** | |
| **Version en prod (au 12 / 03 / 2024)** | `2.5.20 (12/03/2026)` | |
| **Environnement cible** | Production / Pré‑prod / Recette (IaaS ECO4 – Paris La Défense) | |
| **Stack technique** | Java /J2EE (Tomcat 7.0 + JDK 8), Docker, PostgreSQL 14.1‑alpine, BIRT 4.3, Spring Framework, Struts 2, Vertigo, Talend, SonarQube, GitLab CI, Maven, FreeMarker (FTL) | |
| **SLA / SLO** | `[À définir – ex. Disponibilité 99,9 % / Temps de réponse < 2 s]` | |
| **Contacts clés** | • Vincent Letrouit – Chef de bureau – CGDD/SRI/AST2 – `Vincent.Letrouit@developpement-durable.gouv.fr`  <br>• Pascal Zemour – Chargé de mission – CGDD/SRI/AST2 – `Pascal.Zemour@developpement-durable.gouv.fr` <br>• Infocentre – CGDD/SDSED/BUN – `infocentre.bun.sdsed.cgdd@developpement-durable.gouv.fr` | |
| **Politiques de sauvegarde / restauration** | `[À définir – ex. Sauvegarde quotidienne + rétention 30 jours]` | |
| **Sécurité / conformité** | Cerbère ID : Recette 564 / Pre‑prod 546 / Prod 546  <br>Déclaration CNIL 29/09/2014 n° 1034232  <br>RGPD : Données à caractère personnel (coordonnées experts) | |
| **Matrice d’escalade** | `[À définir – ex. N‑1 : Vincent Letrouit → N‑2 : Pascal Zemour → N‑3 : DSI]` | |
| **Référentiel de version** | `gitlab-forge.din.developpement-durable.gouv.fr/snum/pnm3/produits/rh/sireines` (war `sireines‑web‑*.war`) | |
| **Documentation technique** | • Home.md (mission, acteurs) <br>• DeploiementApplicatif.md (procédures merge) <br>• LivraisonSurPosteDocker.md (Docker‑Compose) <br>• ConnexionBDD_Docker.md (psql) | |
| **Points d’attention** | • Mise à jour du war via Dockerfile (`COPY --chown=root:root sireines‑web‑*.war /tmp/ROOT.war`) <br>• Volumes Docker persistants : `sireines_db_sireines_vol`, `sireines_pgadmin_sireines_vol` <br>• Gestion des images : `sireines_app_usine_image`, `postgres:14.1‑alpine`, `dpage/pgadmin4` | |

---  

## 📋 Modèle de prompt (à copier‑colle‑r)  

````markdown
# Prompt – Génération du Dossier d’Exploitation (DEX) de SIREINES

You are an expert in IT service operation, documentation‑as‑code and ITIL/DevOps.  
Using the **project context** provided below, generate a **complete Dossier d’Exploitation (DEX)** that respects the **mandatory structure (16 sections)** defined in the reference template (see the table “Structure obligatoire du guide DEX”).

## 1️⃣ Contexte du projet (à copier‑coller tel‑quel)

**Nom de l’application** : SIREINES  
**Version actuelle en production** : 2.5.20 (12/03/2026)  
**Environnement cible** : Production / Pré‑prod / Recette – IaaS (ECO4) – Centre‑serveur ministériel Paris La Défense  
**Stack technique** : Java /J2EE (Tomcat 7.0 + JDK 8), Docker, PostgreSQL 14.1‑alpine, BIRT 4.3, Spring Framework, Struts 2, Vertigo, Talend, SonarQube, GitLab CI, Maven, FreeMarker (FTL)  
**SLA / SLO** : [À définir – ex. Disponibilité 99,9 % / Temps de réponse < 2 s]  
**Contacts clés** :  
- Vincent Letrouit – Chef de bureau – CGDD/SRI/AST2 – Vincent.Letrouit@developpement-durable.gouv.fr  
- Pascal Zemour – Chargé de mission – CGDD/SRI/AST2 – Pascal.Zemour@developpement-durable.gouv.fr  
- Infocentre – CGDD/SDSED/BUN – infocentre.bun.sdsed.cgdd@developpement-durable.gouv.fr  
**Politiques de sauvegarde / restauration** : [À définir – ex. Sauvegarde quotidienne + rétention 30 jours]  
**Sécurité & conformité** : Cerbère ID Recette 564 / Pre‑prod 546 / Prod 546 – Déclaration CNIL 29/09/2014 n° 1034232 – RGPD :Données à caractère personnel (coordonnées experts)  
**Matrice d’escalade** : [À définir – ex. N‑1 : Vincent Letrouit → N‑2 : Pascal Zemour → N‑3 : DSI]  
**Référentiel de version** : gitlab‑forge.din.developpement-durable.gouv.fr/snum/pnm3/produits/rh/sireines (war `sireines‑web‑*.war`)  
**Documentation technique disponible** : Home.md, DeploiementApplicatif.md, LivraisonSurPosteDocker.md, ConnexionBDD_Docker.md, etc.  
**Points d’attention** : mise à jour du war via Dockerfile, volumes Docker persistants (`sireines_db_sireines_vol`, `sireines_pgadmin_sireines_vol`), gestion des images (`sireines_app_usine_image`, `postgres:14.1‑alpine`, `dpage/pgadmin4`).

## 2️⃣ Consignes de rédaction

- **Format** : Markdown, respect strict du tableau de la “Structure obligatoire du guide DEX” (sections 1‑16).  
- **Style** : professionnel, orienté action, phrases courtes, verbes d’action.  
- **Icônes** : utilisez les emojis 📈 📦 🛡 🔧 📜 ⚙️ pour repérer rapidement les sections.  
- **Tableaux** : pour les contacts, matrice d’escalade, SLA, sauvegarde, etc.  
- **Liens** : insérez les URLs du wiki (ex. https://sireines.e2.rie.gouv.fr/Accueil.do) en markdown.  
- **Placeholders** : conservez les champs entre `[…]` afin que les équipes puissent les compléter rapidement.  

## 3️⃣ Structure du DEX à produire (remplacez les placeholders)

| # | Section | Contenu attendu (exemple) |
|---|---|---|
| 1 | **Généralités** | 📜 Objet, domaine d’application, audience, version du DEX. |
| 2 | **Documents applicables et de référence** | 📄 Liens vers les spécifications fonctionnelles, architecture, politiques RGPD, Cerbère, etc. |
| 3 | **Terminologie** | 📚 Glossaire (ex. SIREINES, Cerbère, BIRT, Docker‑Compose, etc.). |
| 4 | **Spécificités** | 🎯 SLA, contacts, matrice d’escalade, exigences RGPD, sauvegarde. |
| 5 | **Architecture** | 🏗 Diagramme Mermaid du flux (Tomcat ↔ PostgreSQL ↔ BIRT ↔ Docker). |
| 6 | **Serveurs** | 💻 Liste des hôtes (Bastion, serveurs Docker, IP, OS, ressources). |
| 7 | **Application** | 📦 WAR `sireines‑web‑*.war`, paramètres `application‑config.xml`, variables d’environnement (`.env`). |
| 8 | **Supervision & métrologie** | 📈 Outils (SonarQube, logs Tomcat, BIRT, métriques Docker, alertes). |
| 9 | **Sauvegarde** | 💾 Stratégie (volumes Docker, fréquence, rétention, procédure de restauration). |
|10 | **Stockage** | 📂 Volumes Docker (`sireines_db_sireines_vol`, `sireines_pgadmin_sireines_vol`). |
|11 | **Inventaire des bases** | 🗄 PostgreSQL 14.1, schéma `public`, comptes (`sireines`, `postgres`). |
|12 | **Flux inter‑applicatifs** | 🔄 Accès via reverse‑proxy, BIRT, API internes, Cerbère. |
|13 | **Plan de production** | ⏰ CRON/Docker‑Compose, fenêtres de maintenance, procédure de mise à jour du WAR. |
|14 | **Sécurisation des images** | 🛡 Scan vulnérabilités, gestion des secrets (`.env`), politique de patch. |
|15 | **Opérations courantes** | ✅ Checklist quotidienne (vérif. conteneurs, logs, alertes, BIRT). |
|16 | **Opérations récurrentes** | 📆 Rotation des mots de passe, renouvellement certificats, audits mensuels. |

## 4️⃣ Exemple de diagramme Mermaid (à insérer dans la section 5)

```mermaid
graph TB
    subgraph DockerHost["Docker Host (Paris‑La Défense)"]
    direction LR;
    Tomcat["Tomcat 7 (sireines_app_usine_container)"]
    PG["PostgreSQL 14.1 (sireines_db_usine_container)"]
    PgAdmin["pgAdmin (sireines_pgadmin_container)"]
    BIRT["BIRT 4.3 (intégré)"]
    end
    Tomcat -->|JDBC| PG;
    Tomcat -->|BIRT reports| BIRT;
    PgAdmin -->|admin UI| PG;
    classDef infra fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    class DockerHost,in
```

*(Adaptez le diagramme si des composants supplémentaires existent.)*  

## 5️⃣ Sortie attendue  

- **Un seul fichier Markdown** nommé `DEX_SIREINES.md`.  
- **Tous les champs** entre `[…]` restent à compléter par les équipes.  
- **Le diagramme Mermaid** doit être fonctionnel dans les outils supportés (VS Code, Obsidian, Confluence).  
- Le document doit être **prêt à être versionné** (Git) et publié dans le wiki interne.  

---

**À vous de jouer !** Copiez ce prompt dans votre LLM, lancez la génération, puis révisez les parties `[…]` avec les informations propres à votre organisation.  

---  

*Document généré à partir des sources : `sireines.code.filtered.md`, `sireines.code.summarized.md`, `sireines.wiki.md`, `sireines.wikisi.md`, `Home.md`, `Deploiement.*`, `Recette.*`, `Technique.*`, etc.*  