# Cahier des Clauses Techniques Particulières (CCTP) – **Projet : admin_ep**

> **Document** : CCTP‑admin_ep‑v1.0  
> **Date** : 27 avril 2026  
> **Référence du marché** : [À renseigner par l’acheteur]  

---

## 1. Objet du marché  

| N° | Description |
|----|-------------|
| **1.1** | Le présent marché a pour objet la **conception, le développement, le déploiement, la recette, la mise en production et la maintenance évolutive** de l’application **admin_ep** (Administration des établissements publics) conformément aux exigences fonctionnelles décrites dans le Cahier des Clauses Fonctionnelles (CCF) joint. |
| **1.2** | La solution devra permettre : <br>• La gestion des administrateurs, gestionnaires et mandats des établissements publics du ministère de la Transition écologique et solidaire (MTES‑MCT) ; <br>• L’alimentation automatique de la base de données à partir des données du Journal officiel de la République française (JORF) ; <br>• La diffusion d’alertes de fin de mandat par courriel ; <br>• La consultation et la recherche d’informations via une interface web. |
| **1.3** | Le périmètre comprend : <br>• Le **module back‑office** (Java 8, Spring‑Boot, Struts 2, Vertigo) ; <br>• La **base de données PostgreSQL** (version 9.6.11, avec migration prévue vers PostgreSQL 15) ; <br>• Le **serveur d’application** (Tomcat 9.0.8, avec évolution prévue vers Tomcat 10) ; <br>• L’**hébergement** sur l’infrastructure ministérielle (centre‑serveur Paris La Défense – production, pré‑production, recette) ; <br>• Les **documents livrables** (code source, scripts SQL, documentation, jeux de tests, procédures d’exploitation). |

---

## 2. Description technique détaillée  

### 2.1 Spécifications fonctionnelles minimales (référencées au CCF)  

*Gestion des utilisateurs* – Authentification via **Cerbère** (SSO ministériel) ; gestion des profils (Administrateur, Gestionnaire, Lecteur).  
*Gestion des établissements* – CRUD sur les entités : `ETABLISSEMENT`, `COLLEGE`, `CHARGE`, `MINISTERE`, `DIRECTION`.  
*Gestion des mandats* – Saisie et suivi des mandats (`TYPE_MANDAT` : Titulaire / Suppléant) avec dates d’échéance et génération d’alertes.  
*Alimentation JORF* – Extraction quotidienne du flux JORF (RSS) et mise à jour automatisée des tables `ARTICLE`, `ARTICLE_ATTENTE`.  
*Statistiques* – Tableaux de bord (nombre d’établissements, mandats actifs, échéances).  

### 2.2 Spécifications techniques obligatoires  

| Référence | Exigence | Type |
|-----------|----------|------|
| **2.2.1** | La solution devra être développée en **Java 8** (minimum) et compatible **JDK 11**. | Obligation de résultat |
| **2.2.2** | Le serveur d’application devra être **Apache Tomcat 9.0.8** (ou version supérieure compatible Java 8). | Obligation de résultat |
| **2.2.3** | La base de données devra être **PostgreSQL 9.6.11** (migration obligatoire vers **PostgreSQL 15** avant la fin 2027). | Obligation de résultat |
| **2.2.4** | Le code devra être packagé sous **Maven 3.6+** avec les *poms* fournis (voir arborescence). | Obligation de résultat |
| **2.2.5** | La solution devra être **déployable** sous forme d’archive **WAR** et d’archive **ZIP** contenant les scripts SQL d’initialisation et de mise à jour (cf. `adminep-database/assembly.xml`). | Obligation de résultat |
| **2.2.6** | Le système devra garantir une **disponibilité** de **99,9 %** sur les environnements de production (mesurée sur une période glissante de 12 mois). | Obligation de résultat |
| **2.2.7** | Les temps de réponse des pages web (hors pièces jointes) ne devront pas excéder **2 s** pour 95 % des requêtes. | Obligation de résultat |
| **2.2.8** | Le code source devra être **documenté** (Javadoc) et le projet devra fournir un **Data Access Guide** (DAT) à jour. | Obligation de résultat |
| **2.2.9** | Le respect du **Référentiel Général de Sécurité (RGS) – niveau basique** est obligatoire ; le niveau renforcé devra être appliqué aux traitements contenant des données à caractère personnel. | Obligation de résultat |
| **2.2.10** | La solution devra être **conforme au RGAA 3.0** (accessibilité) pour l’ensemble des interfaces publiques. | Obligation de résultat |
| **2.2.11** | La solution devra être **compatible avec le Référentiel Général d’Interopérabilité (RGI)** – notamment les formats d’échange XML/JSON décrits dans les définitions `*.ksp`. | Obligation de résultat |
| **2.2.12** | Le chiffrement TLS 1.2 minimum devra être activé sur toutes les connexions HTTP (SNI, HSTS, Perfect Forward Secrecy). | Obligation de résultat |
| **2.2.13** | Les mots de passe utilisateurs devront être stockés avec **hash bcrypt (cost ≥ 12)**. | Obligation de résultat |
| **2.2.14** | Les logs d’accès et d’audit devront être centralisés (format : CEF) et conservés **minimum 12 mois**. | Obligation de résultat |
| **2.2.15** | Les sauvegardes de la base de données devront être réalisées **quotidiennes** et conservées **30 jours**. | Obligation de moyen |

### 2.3 Spécifications techniques souhaitées  

| Référence | Exigence |
|-----------|----------|
| **2.3.1** | Support de la **contenerisation Docker** (Dockerfile fourni dans `adminep-deployment/`) pour les environnements de test. |
| **2.3.2** | Mise à disposition d’une **API REST** (OpenAPI 3) pour les services d’alimentation JORF. |
| **2.3.3** | Utilisation de **Spring Security** pour la gestion fine des droits (RBAC). |
| **2.3.4** | Intégration d’un **outil de CI/CD** (GitLab‑CI) avec tests unitaires et d’intégration automatisés. |

### 2.4 Spécifications techniques optionnelles  

| Référence | Exigence |
|-----------|----------|
| **2.4.1** | Déploiement sur **Kubernetes** (Helm chart fourni). |
| **2.4.2** | Mise en place d’un **module de reporting** via JasperReports. |
| **2.4.3** | Intégration d’un **service d’authentification fédérée (OAuth 2.0 / OpenID Connect)** en sus du SSO Cerbère. |

---

## 3. Architecture et conception  

| Élément | Contraintes | Normes / Standards |
|---------|-------------|--------------------|
| **3.1** | Architecture **n‑tier** (présentation, métier, persistance) ; chaque couche doit être découplée via des interfaces Java. | **ISO 42010**, **Spring Boot** conventions |
| **3.2** | Les modules **`adminep-web`**, **`adminep-database`**, **`adminep-deployment`** doivent être versionnés séparément (version 1.2.3 du projet). | **Maven 3** conventions |
| **3.3** | Tous les artefacts (WAR, ZIP) doivent être signés avec la **clé GPG** de l’autorité de certification du ministère. | **ISO 19770‑2** (Gestion des actifs logiciels) |
| **3.4** | Le schéma de la base doit respecter le **modèle de données** fourni dans les fichiers `*.ksp`. | **RGI**, **SQL:2008** |
| **3.5** | Les composants UI (JSP, FTL) doivent être compatibles **HTML 5**, **CSS 3** et respecter le **RGAA 3.0**. | **W3C**, **RGAA** |
| **3.6** | Utilisation du **framework Vertigo** (Struts 2, Vega) pour la couche présentation. | **Apache Struts 2.5**, **Vertigo 4.x** |
| **3.7** | Les communications inter‑services (ex. JORF → admin_ep) doivent s’effectuer en **HTTPS** et, le cas échéant, en **JSON** ou **XML** suivant les définitions `*.ksp`. | **REST / SOAP**, **RGS** |

---

## 4. Exigences de sécurité (RGS, ANSSI)

| N° | Exigence | Niveau | Vérification |
|----|----------|--------|---------------|
| **4.1** | Authentification unique via **Cerbère** (SSO) ; le prestataire devra implémenter le **SecurityFilter** fourni (`SecurityFilter.java`). | RGS basique | Test d’intégration avec le serveur d’identité du ministère. |
| **4.2** | Toutes les communications HTTP doivent être chiffrées **TLS 1.2** minimum, avec certificats **RSA 2048** signés par l’AC du ministère. | RGS basique | Scan SSL (Qualys) – résultat ≥ A+. |
| **4.3** | Gestion des droits d’accès : chaque action (CRUD) doit être associée à un **rôle applicatif** (`RoleApplicatifEnum`). | RGS basique | Revue de code + tests unitaires. |
| **4.4** | Journalisation (audit) de toutes les opérations sensibles (login, création/modification de mandats) dans le fichier `baseadmin.log`. | RGS renforcé | Vérification des logs via le tableau de bord ELK. |
| **4.5** | Les mots de passe sont stockés avec **bcrypt (cost ≥ 12)**. | RGS basique | Analyse de la base de données (table `BASEADMIN_USER`). |
| **4.6** | Protection contre les vulnérabilités OWASP Top 10 : XSS, CSRF, SQL‑Injection, etc. | RGS renforcé | Tests d’intrusion (pentest) à chaque version majeure. |
| **4.7** | Les données à caractère personnel (ex. email des référents) sont chiffrées **au repos** (pgcrypto) et soumises à la **politique RGPD** (droit d’accès, d’oubli). | RGPD | Examen de la matrice de conformité RGPD. |
| **4.8** | La solution doit être compatible avec le **Plan de Reprise d’Activité (PRA)** : sauvegarde quotidienne, restauration en < 2 h. | RGS renforcé | Test de restauration mensuel. |
| **4.9** | Mise en place d’un **plan de continuité (PCA)** avec bascule sur le site de secours du ministère. | RGS renforcé | Validation lors des exercices de bascule. |

---

## 5. Interfaces et intégrations  

| Interface | Description | Protocole / Format | Points de recette |
|-----------|-------------|--------------------|-------------------|
| **5.1** | **Système d’authentification Cerbère** (SSO) | SAML 2.0 via le filtre `cerbere-filtre.xml` | Validation du flux SSO et du mapping des attributs. |
| **5.2** | **Flux JORF** (RSS et archives .tar.gz) | HTTPS / RSS XML + fichiers .tar.gz | Vérification du parsing JORF (`JORFExtractor.java`) et de la mise à jour de la table `ARTICLE`. |
| **5.3** | **Base de données PostgreSQL** | JDBC 4.2 (driver PostgreSQL) | Tests d’intégrité des scripts d’init (`0_createUserAndDB.sql`, `1_createSequenceAndTablesIntegration.sql`, …). |
| **5.4** | **Service de messagerie** (alerte mandat) | SMTP TLS (port 587) | Envoi de courriels de rappel – accusé de réception. |
| **5.5** | **API interne d’interrogation** (REST) – optionnel (voir 2.3.2) | HTTP / JSON (OpenAPI 3) | Tests de conformité à la spécification OpenAPI. |
| **5.6** | **Export CSV/Excel** des statistiques | MIME `text/csv` et `application/vnd.openxmlformats‑officedocument.spreadsheetml.sheet` | Vérification du format et de l’encodage UTF‑8. |

---

## 6. Environnements et infrastructure  

| Environnement | Description | Contraintes |
|---------------|-------------|-------------|
| **6.1 – Développement** | Machines locales du développeur ; Docker + Maven. | Utilisation de **Java 8** et **PostgreSQL 9.6**. |
| **6.2 – Intégration** | Serveur de test dédié (VM) – **Tomcat 9**, **PostgreSQL 9.6**. | Accès restreint aux IP de la DSI. |
| **6.3 – Pré‑production** | Centre‑serveur ministériel **Paris La Défense**, version **ACA I – Java ACA (Clusters ESXi)**. | Réplication exacte de la production (configuration, certificats). |
| **6.4 – Production** | Même infrastructure que 6.3, **Hébergement MSP**. | Disponibilité ≥ 99,9 %; sauvegarde quotidienne, PRA/PCA. |
| **6.5 – Réseau** | Accès via le **réseau interne du ministère** et via **Internet** (HTTPS). | Pare‑feu avec règles d’accès limitées aux ports 443 (HTTPS) et 22 (SSH). |
| **6.6 – Conteneurisation (optionnel)** | Dockerfile fourni dans `adminep-deployment/` ; images stockées dans le registre Docker interne. | Conformité aux exigences de sécurité du registre (signatures, scans). |

---

## 7. Qualité et conformité  

| Critère | Référence | Niveau requis |
|---------|-----------|--------------|
| **7.1** | **ISO 25010 – Qualité du produit** (fiabilité, performance, maintenabilité, sécurité) | Tous les sous‑critères doivent atteindre **≥ 4/5** lors de l’évaluation interne. |
| **7.2** | **ISO 9001 – Management qualité** (processus de développement) | Processus de suivi des anomalies (JIRA) et de gestion des changements (GitLab) documentés. |
| **7.3** | **RGAA 3.0** – Accessibilité | Score global **≥ 80 %** (audit automatisé + manuel). |
| **7.4** | **Couverture des tests unitaires** | **≥ 80 %** de lignes de code couvertes (JaCoCo). |
| **7.5** | **Analyse statique** | Aucun défaut critique (SonarQube ≥ A). |
| **7.6** | **Documentation** | DAT, Guide d’installation, Guide d’exploitation et Guide d’administration à jour (version 1.2.3). |
| **7.7** | **Performance** | Temps de réponse moyen < 2 s sous charge de 50 concurrentes (JMeter). |

---

## 8. Documentation et formation  

| Livrable | Format | Contenu attendu |
|----------|--------|-----------------|
| **8.1** | **DAT** (Data Access Technical) – PDF/HTML | Description du schéma, scripts d’initialisation, procédures de migration. |
| **8.2** | **Guide d’installation** – PDF | Prérequis, étapes de déploiement (WAR, Docker, Kubernetes). |
| **8.3** | **Guide d’exploitation** – PDF | Gestion des logs, sauvegarde/restauration, procédures PRA/PCA. |
| **8.4** | **Guide d’administration fonctionnelle** – PDF | Gestion des utilisateurs, des mandats, des alertes. |
| **8.5** | **Plan de formation** – PPT + vidéos | 2 jours de formation présentielle (ou distancielle) pour les équipes MOE/MOA. |
| **8.6** | **Référentiel de tests** – Excel | Scénarios fonctionnels, critères d’acceptation, résultats. |

---

## 9. Tests et recette  

| Type de test | Description | Critères d’acceptation |
|--------------|-------------|------------------------|
| **9.1 – Tests unitaires** | Exécution via JUnit 5, couverture ≥ 80 % | Tous les modules compilent, aucune erreur. |
| **9.2 – Tests d’intégration** | Déploiement sur l’environnement d’intégration, appels aux services JORF, base de données, SSO. | 100 % des scénarios validés. |
| **9.3 – Tests de charge** | Scénario JMeter : 50 utilisateurs simultanés pendant 30 min. | Temps de réponse moyen ≤ 2 s, aucun dépassement de 5 % d’erreurs. |
| **9.4 – Tests de sécurité** | Pentest OWASP Top 10, scan de vulnérabilités (Nessus). | Aucun résultat **critique** ou **haute**. |
| **9.5 – Tests d’acceptation (UAT)** | Validation fonctionnelle par la MOA (voir CCF). | Tous les cas d’usage validés, aucun défaut bloquant. |
| **9.6 – Recette de migration** | Exécution des scripts `update/*.sql` sur une base pré‑existante. | Succès sans perte de données, logs de migration vierges. |
| **9.7 – Recette de bascule (PRA)** | Simulation de restauration à partir des sauvegardes. | Temps de reprise ≤ 2 h, intégrité des données confirmée. |

*Gestion des anomalies* : toute anomalie détectée devra être consignée dans le suivi JIRA, classée (Bloquant, Critique, Mineur) et corrigée avant la signature de la recette.

---

## 10. Maintenance et support  

| Niveau | Service | Délai d’intervention (GTR) | Délai de correction (GTD) |
|--------|----------|----------------------------|-----------------------------|
| **10.1 – Support fonctionnel** | Hotline téléphonique (8 h / 24 h) | 4 h (hors week‑ends) | 2 jours ouvrés |
| **10.2 – Support technique** | Intervention sur le serveur (Tomcat, DB) | 2 h | 1 jour ouvré |
| **10.3 – Maintenance corrective** | Corrections de bugs de niveau bloquant | 1 h | 24 h |
| **10.4 – Maintenance évolutive** | Ajout de nouvelles fonctionnalités (ex. API REST) | Sur accord | Selon planning (délais à définir) |
| **10.5 – Garantie** | 12 mois à compter de la mise en production, incluant le support de niveau 1 et 2. | – | – |
| **10.6 – SLA globaux** | Disponibilité ≥ 99,9 % ; Temps moyen de résolution (MTTR) ≤ 4 h pour incidents critiques. | – | – |

---

## 11. Livrables et planning  

| Jalons | Date cible | Livrable |
|--------|------------|----------|
| **11.1 – Validation du CCTP** | 30 mai 2026 | CCTP signé par le maître d’ouvrage. |
| **11.2 – Livraison du prototype** | 30 septembre 2026 | Version 1.0 du WAR + scripts d’init, documentation technique. |
| **11.3 – Recette fonctionnelle** | 31 octobre 2026 | Rapport de recette signé par la MOA. |
| **11.4 – Mise en production** | 15 décembre 2026 | Déploiement sur l’infrastructure de production, transfert de la maîtrise d’ouvrage. |
| **11.5 – Fin de la période de garantie** | 15 décembre 2027 | Rapport de clôture de garantie. |
| **11.6 – Livraison de la version 2.0 (migration PostgreSQL 15 / Tomcat 10)** | 30 juin 2028 | Nouvelle version du WAR, scripts de migration, documentation mise à jour. |

**Pénalités de retard** : 0,5 % du montant du lot par jour de retard au-delà du délai contractuel, plafonné à 10 % du lot.

---

## 12. Contraintes légales et réglementaires  

| Domaine | Exigence |
|----------|----------|
| **12.1 – Propriété intellectuelle** | Le code source, la documentation et les livrables sont **cédés en totalité** à l’État (licence « public domain » ou « Cession exclusive »). |
| **12.2 – Licences tierces** | Tous les composants externes (Spring, Struts 2, Vertigo, PostgreSQL JDBC, etc.) doivent être **compatibles avec la licence GPL v2 ou supérieure** ou disposer d’une **dérogation** signée par le ministère. |
| **12.3 – Protection des données personnelles** | Conformité **RGPD** : registre des traitements, analyse d’impact (AIPD), droit d’accès, de rectification et d’effacement. |
| **12.4 – Archivage** | Les pièces justificatives (mandats, pièces jointes) doivent être archivées **au minimum 10 ans** au format PDF/A‑2b, conservées dans le référentiel d’archivage du ministère. |
| **12.5 – Sécurité des systèmes d’information** | Respect du **RGS**, du **Référentiel SSI de l’ANSSI** (ISO 27001) et des exigences du **RGI** pour les échanges inter‑systèmes. |
| **12.6 – Accessibilité** | Conformité **RGAA 3.0** pour les pages publiques et les écrans d’administration. |
| **12.7 – Obligations de résultat** | Le prestataire garantit le **respect** de l’ensemble des exigences ci‑dessus ; tout manquement constitue une faute contractuelle donnant lieu à pénalités et/ou à la résolution du marché. |

---

## 13. Critères de sélection des offres  

| Critère | Pondération | Modalité d’évaluation |
|---------|--------------|-----------------------|
| **13.1 – Conformité aux exigences fonctionnelles** (CCF) | 30 % | Analyse du tableau de correspondance fourni par le candidat. |
| **13.2 – Qualité technique** (architecture, sécurité, performances) | 25 % | Scoring sur la base du **CCTP** (respect des obligations de résultat). |
| **13.3 – Expérience du prestataire** (références similaires, projets ministériels) | 20 % | Vérification des références (minimum 3 projets comparables). |
| **13.4 – Méthodologie de gestion de projet** (agile, DevOps, CI/CD) | 15 % | Présentation du processus, livrables, planning. |
| **13.5 – Prix** | 10 % | Prix global (hors TVA) sur la période de garantie. |

**Notation** : chaque critère est noté sur 20 points ; la somme maximale est de 100 points. L’offre la mieux classée (≥ 70 points) sera retenue.

---

## 14. Annexes contractuelles  

| Annexe | Contenu |
|--------|---------|
| **14.1 – Glossaire** | Définitions des termes (RGS, RGI, RGAA, PRA, PCA, etc.). |
| **14.2 – Références normatives** | Listes complètes des normes (ISO 27001, ISO 25010, ISO 9001, RFC 2818, RFC 7525, etc.). |
| **14.3 – Modèle de tableau de correspondance CCF ↔ CCTP** | À remplir par le candidat. |
| **14.4 – Modèle de plan de formation** | Structure attendue (objectifs, durée, supports). |
| **14.5 – Modèle de registre des traitements RGPD** | À compléter par le prestataire. |
| **14.6 – Modèle de rapport de test d’intrusion** | Format et éléments attendus. |
| **14.7 – Modèle de déclaration de conformité RGS** | Formulaire à signer à la livraison. |

---  

### Signature du CCTP  

| Signataire | Fonction | Date |
|------------|-----------|------|
| **Maître d’ouvrage** | Responsable du marché | 27/04/2026 |
| **Prestataire** | Représentant légal | 27/04/2026 |

---  

*Fin du Cahier des Clauses Techniques Particulières.*  