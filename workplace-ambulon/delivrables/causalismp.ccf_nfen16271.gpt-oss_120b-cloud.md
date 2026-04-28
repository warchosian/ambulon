# 📄 Cahier des Charges Fonctionnel (CCF) – **causalismp**  
**Projet** : Gestion des accidents du travail & des maladies professionnelles  
**Norme** : NF EN 16271 :2013 (Management par la valeur – Expression fonctionnelle du besoin)  
**Version** : 1.0 – 28 avril 2026  

---  

## 1. Présentation du projet  

| Élément | Description |
|---|---|
| **Nom du projet** | **causalismp** – Application web de saisie, suivi, analyse et export des dossiers d’accidents du travail et de maladies professionnelles. |
| **Contexte** | Le groupe **Ambulon** doit disposer d’un outil unique, inter‑opérable avec les référentiels internes (grades, services, causes, etc.) et les web‑services externes (ex. : REHUCIT). L’application remplace l’ancienne solution **ACAI** et le **cerbere‑bouchon**. |
| **Enjeux stratégiques** | 1️⃣ Garantir la conformité légale (déclaration d’accident, suivi médical). <br>2️⃣ Centraliser les référentiels RH pour éviter les doublons. <br>3️⃣ Améliorer la qualité des statistiques (taux d’accidents, répartition par cause, etc.). <br>4️⃣ Réduire les coûts de maintenance grâce à une architecture modulaire (Maven multi‑module, Struts 1, Castor JDO). |
| **Objectifs** | - Saisir et clôturer les dossiers d’accident et de maladie. <br>- Gérer les référentiels (grades, services, causes, etc.). <br>- Produire des exportations (OpenOffice, CSV) et des rapports statistiques. <br>- Synchroniser automatiquement les tables de référence avec les web‑services externes. <br>- Respecter les exigences de sécurité (RGPD, authentification, journalisation). |
| **Périmètre fonctionnel** | **Inclus** : <br>• Interface web (JSP + Struts) <br>• Gestion des dossiers (création, édition, validation, impression) <br>• Gestion des référentiels (CRUD limité à la lecture + import) <br>• Export & statistiques <br>• Synchronisation (grades ↔ transcodage) <br>• Authentification / gestion de session <br>• Gestion des logs et de la traçabilité <br>**Exclus** : <br>• Gestion des paies (hors scope) <br>• Modules de formation ou de suivi médical détaillé (hors scope). |

---  

## 2. Analyse de la valeur  

| Fonction de service (FS) | Type | Description | Critères de performance (exemples) |
|---|---|---|---|
| **FS‑01** – Saisie d’un dossier d’accident | **FP** (Fonction Principale) | Permet à un utilisateur habilité de créer, modifier et clôturer un dossier d’accident du travail. | • Temps de saisie ≤ 5 min par dossier.<br>• Validation obligatoire de tous les champs obligatoires.<br>• Enregistrement persistant avec accusé de réception. |
| **FS‑02** – Saisie d’un dossier de maladie professionnelle | **FP** | Identique à FS‑01 mais pour les dossiers de maladie. | Même critères que FS‑01. |
| **FS‑03** – Consultation / recherche de dossiers | **FC** (Fonction Contraint) | L’utilisateur doit pouvoir rechercher par critère (date, service, grade, cause, etc.). | • Temps de réponse ≤ 2 s pour < 10 000 dossiers.<br>• Recherche multi‑critères (AND/OR). |
| **FS‑04** – Gestion des référentiels (grades, services, causes, …) | **FC** | Lecture (et mise à jour ponctuelle) des tables de référence utilisées dans les dossiers. | • Disponibilité ≥ 99,5 % (lecture).<br>• Mise à jour batch ≤ 30 min (hors heures de production). |
| **FS‑05** – Export des dossiers / données | **FC** | Générer des fichiers OpenOffice, CSV ou PDF pour archivage ou transmission. | • Export complet ≤ 10 s pour 500 dossiers.<br>• Conformité du format aux exigences du client (ex. : libellé exact). |
| **FS‑06** – Production de statistiques & indicateurs | **FC** | Calculer taux d’accidents, répartition par cause, tranche d’âge, etc. | • Calcul en temps réel ≤ 5 s après sélection d’une période.<br>• Export possible des graphiques (PNG, SVG). |
| **FS‑07** – Synchronisation des référentiels externes | **FC** | Mettre à jour les grades et le transcodage via les web‑services REHUCIT. | • Synchronisation complète ≤ 15 min.<br>• Détection d’anomalies et journalisation. |
| **FS‑08** – Authentification & gestion de session | **FC** | Authentifier les utilisateurs via le composant **Cerbere** et assurer la sécurité de la session. | • Authentification < 2 s.<br>• Timeout session 30 min d’inactivité.<br>• Conformité RGPD (gestion du consentement). |
| **FS‑09** – Gestion des logs & traçabilité | **FC** | Enregistrer chaque action critique (création, modification, suppression, export). | • Conservation ≥ 2 ans.<br>• Recherche de logs ≤ 3 s. |
| **FS‑10** – Interface ergonomique & navigation | **FC** | Fournir une UI claire, compatible avec les navigateurs courants (IE 11+, Chrome, Firefox, Edge). | • Taux de satisfaction utilisateur ≥ 80 % (enquête).<br>• Aucun écran bloquant (bugs majeurs). |

> **Analyse de la valeur** : Les fonctions **FP** (FS‑01 & FS‑02) sont essentielles car elles justifient l’existence du produit. Toutes les **FC** sont contraintes imposées par le contexte réglementaire, les exigences de performance et les besoins des parties prenantes.  

---  

## 3. Expression fonctionnelle du besoin  

### 3.1. Hiérarchie des besoins  

| Identifiant | Niveau | Description (QUOI) | Critère d’appréciation | Niveau d’importance |
|---|---|---|---|---|
| **B‑01** | Système | Saisir, stocker et clôturer les dossiers d’accident du travail. | ✅ Chaque dossier comporte les champs obligatoires (date, service, grade, cause, etc.) et génère un numéro unique. | Obligatoire |
| **B‑02** | Système | Saisir, stocker et clôturer les dossiers de maladie professionnelle. | ✅ Même exigences que B‑01, avec champ « type de maladie ». | Obligatoire |
| **B‑03** | Sous‑système | Recherche avancée de dossiers (multi‑critères). | ✅ Temps de réponse ≤ 2 s, résultats paginés (max 30 lignes). | Obligatoire |
| **B‑04** | Sous‑système | Consultation détaillée d’un dossier (lecture‑seule). | ✅ Affichage complet, mise en forme conforme à la charte. | Obligatoire |
| **B‑05** | Sous‑système | Gestion (lecture) des référentiels : grades, services, causes environnementales, humaines, matérielles, organisationnelles, etc. | ✅ Les tables sont accessibles en < 0,1 s, les libellés sont à jour. | Obligatoire |
| **B‑06** | Élément | Export des dossiers au format OpenOffice (ODT) ou CSV. | ✅ Export complet, encodage UTF‑8, structure conforme aux modèles fournis. | Souhaitable |
| **B‑07** | Élément | Génération de rapports statistiques (taux d’accidents, répartition par cause, tranche d’âge, etc.). | ✅ Calcul < 5 s, graphiques exportables (PNG/SVG). | Souhaitable |
| **B‑08** | Élément | Synchronisation des grades et du transcodage avec le web‑service REHUCIT. | ✅ Synchronisation réussie > 95 % des enregistrements, logs d’erreurs. | Souhaitable |
| **B‑09** | Élément | Authentification via le composant **Cerbere** et gestion de session sécurisée. | ✅ Authentification < 2 s, session timeout 30 min, conformité RGPD. | Obligatoire |
| **B‑10** | Élément | Journalisation détaillée de toutes les actions critiques. | ✅ Logs conservés 2 ans, recherche de logs ≤ 3 s. | Obligatoire |
| **B‑11** | Élément | Interface web ergonomique, compatible avec les navigateurs standards. | ✅ Tests UI validés sur IE 11+, Chrome ≥ 90, Firefox ≥ 88, Edge ≥ 90. | Obligatoire |
| **B‑12** | Élément | Gestion des droits d’accès (rôles : manager, développeur, rapporteur, lecteur). | ✅ Accès aux écrans et fonctions selon le rôle, auditabilité. | Obligatoire |
| **B‑13** | Élément | Pagination des listes (paramétrable via `project.properties`). | ✅ Max 30 lignes par page, paramètre modifiable sans redeploiement. | Souhaitable |
| **B‑14** | Élément | Gestion des erreurs utilisateurs (messages d’avertissement clairs). | ✅ Utilisation du composant `ActionWarning` affiché en haut de chaque page. | Obligatoire |
| **B‑15** | Élément | Déploiement sous forme de WAR (Maven ‑ module `causalismp‑web`). | ✅ Build Maven réussi, artefact WAR < 50 Mo, dépendance `StubWS.jar` déclarée. | Obligatoire |

> **Notation** : *Obligatoire* = critère de conformité, *Souhaitable* = amélioration de la valeur, *Optionnel* = fonctionnalité future.  

---  

## 4. Caractérisation des besoins  

| Fonction (FS) | Critère d’appréciation | Niveau d’importance | Flexibilité | Contraintes |
|---|---|---|---|---|
| FS‑01 (Saisie accident) | Tous les champs requis remplis, génération d’un ID unique, validation de cohérence (ex. : date ≤ aujourd’hui). | Obligatoire | **Fixe** (réglementation) | RGPD, archivage ≥ 5 ans, conformité ISO 9001. |
| FS‑02 (Saisie maladie) | Même critères que FS‑01 + type maladie conforme à la nomenclature. | Obligatoire | **Fixe** | Nomenclature fournie par le service santé. |
| FS‑03 (Recherche) | Temps de réponse ≤ 2 s, pagination ≤ 30 lignes, filtres sauvegardables. | Obligatoire | **Négociable** (limite pagination) | Indexation DB (Oracle). |
| FS‑04 (Référentiels) | Lecture en < 0,1 s, mise à jour batch nocturne. | Obligatoire | **Négociable** (heure de mise à jour) | Cohérence avec les web‑services externes. |
| FS‑05 (Export) | Export complet, format conforme, pas de perte de caractères Unicode. | Souhaitable | **Négociable** (format additionnel CSV) | Taille maximale du fichier < 200 Mo. |
| FS‑06 (Statistiques) | Calcul < 5 s, graphiques exportables, filtres temporels. | Souhaitable | **Négociable** (type de graphiques) | Respect des seuils légaux de déclaration. |
| FS‑07 (Synchronisation) | Taux de réussite ≥ 95 %, logs détaillés, exécution planifiée. | Souhaitable | **Fixe** (périodicité) | Accès aux WS REHUCIT (certificat SSL). |
| FS‑08 (Auth) | Authentification < 2 s, session timeout 30 min, double‑facteur optionnel. | Obligatoire | **Négociable** (2FA) | Conformité RGPD, stockage hashé des mots‑de‑passe. |
| FS‑09 (Logs) | Conservation 2 ans, recherche par utilisateur/date/action. | Obligatoire | **Fixe** | Sécurisation des logs (intégrité SHA‑256). |
| FS‑10 (UI) | Compatibilité navigateurs, taux de satisfaction ≥ 80 %. | Obligatoire | **Négociable** (thème couleur) | Respect du design corporate. |
| FS‑11 (Droits) | Gestion fine des rôles, auditabilité des modifications de droits. | Obligatoire | **Fixe** | Aucun accès admin via URL directe. |
| FS‑12 (Pagination) | Paramètre `pagination.max` modifiable via `project.properties`. | Souhaitable | **Négociable** | Redémarrage serveur requis. |
| FS‑13 (Avertissements) | Messages affichés via `ActionWarning`, persistance d’un tableau d’avertissements. | Obligatoire | **Fixe** | Aucun message bloquant l’envoi du formulaire. |
| FS‑14 (Déploiement) | Build Maven réussi, artefact WAR < 50 Mo, manifeste contenant `StubWS.jar`. | Obligatoire | **Fixe** | Environnement d’exécution Java 8+. |

---  

## 5. Validation de l’expression du besoin  

| Étape | Méthode | Participants | Résultat attendu | Traçabilité |
|---|---|---|---|---|
| 5.1 | Atelier de cadrage (2 jours) | Managers (Adrien, Anthony B., Anthony M., Antoine, Christian, Jeanne, Julien, Nicolas) | Confirmation du périmètre fonctionnel & des priorités. | Compte‑rendu → ID B‑01 à B‑15. |
| 5.2 | Validation des fiches de besoins | Développeurs (Grégoire, Hervé, Maxime, Pascal F., Vincent) | Accord sur la faisabilité technique (Struts 1, Castor JDO). | Matrice de correspondance besoin ↔ fonction. |
| 5.3 | Revue RGPD & sécurité | Rapporteurs (Chantal, Christophe, Erwan, Farmin, Florent, Geoffrey, Khalid, Michel, Pascal B., Patrick, Redouane, Sarah, Thierry) | Validation de la conformité (consentement, logs, chiffrement). | Checklist conformité → annexes. |
| 5.4 | Validation finale du CCF | Tous les membres + **Jenkins robot** (CI) | Signature du CCF (PDF signé) et archivage dans le dépôt `causalismp-doc`. | Version 1.0 du CCF (date, signataires). |
| 5.5 | Traçabilité automatisée | CI / CD (GitLab CI) → génération du rapport `sonar‑project.properties`. | Chaque exigence possède un ticket JIRA lié. | Lien JIRA ↔ ID B‑xx dans le backlog. |

---  

## 6. Scénarios d’usage  

| Type | Scénario | Description | Étapes clés | Critères de réussite |
|---|---|---|---|---|
| **Nominal** | **SN‑01** – Saisie d’un accident | Un manager crée un nouveau dossier d’accident. | 1. Authentification<br>2. Sélection du menu “Accident”<br>3. Remplissage du formulaire (date, service, grade, cause, description)<br>4. Validation → génération du numéro de dossier<br>5. Confirmation affichée & log créé | Dossier créé, ID unique, log “ACCIDENT_CREATE”. |
| **Nominal** | **SN‑02** – Export des dossiers | Un rapporteur exporte les dossiers du mois précédent au format ODT. | 1. Authentification<br>2. Accès à “Export”<br>3. Sélection de la période<br>4. Choix du format ODT<br>5. Lancement de l’export → téléchargement du fichier | Fichier ODT conforme, taille < 200 Mo, log “EXPORT”. |
| **Erreur** | **SE‑01** – Date d’accident future | L’utilisateur saisit une date postérieure à aujourd’hui. | 1. Saisie du formulaire<br>2. Validation côté serveur (date ≤ aujourd’hui)<br>3. Retour d’un message d’erreur via `ActionWarning` | Message “La date ne peut être postérieure à aujourd’hui.” affiché, aucune sauvegarde. |
| **Erreur** | **SE‑02** – Web‑service indisponible | La synchronisation des grades échoue (WS hors‑ligne). | 1. Lancement du batch de synchronisation<br>2. Tentative d’appel WS → timeout<br>3. Enregistrement d’une erreur dans les logs<br>4. Notification à l’administrateur | Log “SYNC_GRADE_ERROR”, aucune modification des tables. |
| **Limite** | **SL‑01** – Chargement de 10 000 dossiers | L’administrateur demande la liste complète sans pagination. | 1. Requête de recherche sans pagination<br>2. Temps de réponse mesuré | Temps ≤ 10 s, aucun dépassement de mémoire (GC < 5 %). |
| **Limite** | **SL‑02** – Export massif (500 000 dossiers) | Export CSV de tous les dossiers historiques. | 1. Sélection du format CSV<br>2. Lancement de l’export<br>3. Découpage en fichiers de 100 000 lignes | Chaque fichier < 200 Mo, export complet, log “EXPORT_BULK”. |

---  

## 7. Parties prenantes (Stakeholders)  

| Partie prenante | Rôle | Besoins spécifiques | Impact sur la valeur |
|---|---|---|---|
| **Managers** (Adrien, Anthony B., Anthony M., Antoine, Christian, Jeanne, Julien, Nicolas) | Décideurs, utilisateurs finaux | Saisie fiable, suivi complet, accès aux statistiques, export pour reporting. | **Valeur élevée** – garantissent la pertinence métier. |
| **Développeurs** (Grégoire, Hervé, Maxime, Pascal F., Vincent) | Réalisation technique | Architecture modulaire, documentation, tests unitaires, CI/CD. | **Valeur technique** – assurent la maintenabilité. |
| **Rapporteurs** (Chantal, Christophe, Erwan, Farmin, Florent, Geoffrey, Khalid, Michel, Pascal B., Patrick, Redouane, Sarah, Thierry) | Contrôle conformité, audit | Traçabilité, logs, conformité RGPD, export des rapports. | **Valeur de conformité** – requis légalement. |
| **Utilisateurs finaux** (agents, services RH) | Saisie & consultation | Interface intuitive, temps de saisie réduit, assistance (aide en ligne). | **Valeur opérationnelle** – satisfaction et adoption. |
| **Équipe Sécurité / DPO** | Sécurité des données | Chiffrement, journalisation, gestion des droits. | **Valeur de risque** – minimise les incidents. |
| **Intégrateur (CI/CD)** (Jenkins robot) | Automatisation | Build reproductible, tests, déploiement. | **Valeur de productivité** – accélère les releases. |
| **Prestataire WS REHUCIT** | Fournisseur de données externes | Disponibilité du service, format de réponse stable. | **Valeur d’interopérabilité** – garantit la synchronisation. |

---  

## 8. Contraintes et environnement  

| Domaine | Contraintes |
|---|---|
| **Organisationnel** | - Respect du **processus de validation** décrit en §5.<br>- Livrables archivés dans `causalismp-doc` (PDF du CCF signé). |
| **Réglementaire** | - **RGPD** (gestion du consentement, droit à l’oubli).<br>- **Déclaration d’accident du travail** (articles L. 441‑1 et suivants du Code du travail). |
| **Technique** | - **Serveur d’application** : Tomcat 9 (ou JBoss 7) avec JDK 8.<br>- **Base** : Oracle 12c (ou supérieur) via JNDI `jdbc/userDScausalis`.<br>- **Persistance** : Castor JDO (`database.xml`, `mapping.xml`).<br>- **Web‑services** : appel HTTPS avec certificat client (REHUCIT).<br>- **Déploiement** : WAR produit par le module `causalismp-web` (Maven). |
| **Temporel** | - **Phase de test** : 8 semaines après le début du développement.<br>- **Mise en production** : avant le 31 mai 2026 (respect du planning de la PIC). |
| **Budgétaire** | - **Coût maximum** du développement : 120 k €.<br>- **Coût d’exploitation** : < 5 k €/mois (hébergement, licences). |
| **Qualité** | - **SonarQube** : quality‑gate **PASS** (bugs = 0, vulnérabilités ≤ 2, couverture ≥ 80 %).<br>- **Tests unitaires** : 80 % de couverture minimum.<br>- **Tests fonctionnels** : scénario nominal + scénarios d’erreur + charge. |

---  

## 9. Critères de sélection et pondération (pour appel d’offres)  

| Critère | Sous‑critère | Pondération | Modalité de notation |
|---|---|---|---|
| **C1 – Fonctionnalités** | Couverture des besoins B‑01 à B‑15 | 30 % | 0‑5 pts par besoin satisfait (exigence obligatoire = 5 pts). |
| **C2 – Performance** | Temps de réponse (< 2 s), export (< 10 s), synchronisation (< 15 min) | 20 % | Mesure en environnement de test (benchmark). |
| **C3 – Sécurité & conformité** | RGPD, journalisation, authentification Cerbere | 15 % | Audit (check‑list) + tests d’intrusion. |
| **C4 – Qualité du code** | SonarQube quality‑gate, couverture tests, maintenabilité | 15 % | Score Sonar (bugs, vulnérabilités, couverture). |
| **C5 – Coût** | Prix total (licences, services externes) | 10 % | Analyse du devis. |
| **C6 – Délai** | Planning de livraison (max 12 semaines) | 5 % | Respect du planning proposé. |
| **C7 – Support & évolution** | Maintenance 1 an, évolutivité (Java 8+, modularité) | 5 % | Contrat de support. |

> **Notation finale** = Σ (pondération × note). Le soumissionnaire dépassant **80 %** est considéré comme **admissible**.  

---  

## 10. Glossaire et acronymes  

| Acronyme | Signification |
|---|---|
| **CCF** | Cahier des Charges Fonctionnel |
| **NF EN 16271** | Norme française de management par la valeur – Expression fonctionnelle du besoin |
| **FP** | Fonction Principale |
| **FC** | Fonction Contraint |
| **WS** | Web Service |
| **RGPD** | Règlement Général sur la Protection des Données |
| **JDO** | Java Data Objects (Castor) |
| **JSP** | JavaServer Pages |
| **JDK** | Java Development Kit |
| **CI/CD** | Continuous Integration / Continuous Deployment |
| **POC** | Proof of Concept |
| **OCR** | Optical Character Recognition (non utilisé ici, mentionné dans les exigences éventuelles) |
| **DAO** | Data Access Object |
| **DTO** | Data Transfer Object |
| **UI** | User Interface |
| **UX** | User Experience |
| **ODT** | OpenDocument Text (format OpenOffice) |
| **CSV** | Comma‑Separated Values |
| **PDF** | Portable Document Format |
| **Jenkins** | Serveur d’intégration continue (automatisation des builds) |
| **Cerbere** | Composant d’authentification interne (gestion des sessions) |
| **REHUCIT** | Web‑service externe de transcodage des grades (exemple) |
| **Maven** | Outil de gestion de projet et de dépendances Java |
| **SonarQube** | Plate‑forme d’analyse de la qualité du code |
| **JPA** | Java Persistence API (alternative future à Castor) |
| **ISO 9001** | Norme de management de la qualité (référence pour la traçabilité) |
| **ISO 27001** | Norme de sécurité de l’information (référence pour les logs) |
| **JNDI** | Java Naming and Directory Interface (lookup datasource) |
| **CRUD** | Create, Read, Update, Delete (opérations de base) |
| **REST** | Representational State Transfer (type d’API, non utilisé ici) |
| **HTTPS** | HyperText Transfer Protocol Secure (protocole sécurisé) |
| **2FA** | Two‑Factor Authentication (authentification à deux facteurs) |
| **PDF** | Portable Document Format |
| **ODT** | OpenDocument Text (format d’export) |
| **CSV** | Comma‑Separated Values (format d’export) |
| **API** | Application Programming Interface |
| **JPA** | Java Persistence API (potentiel futur remplacement de Castor) |
| **JDBC** | Java Database Connectivity |
| **JAR** | Java ARchive (ex. : `StubWS.jar`) |
| **WAR** | Web Application Archive (artefact final) |
| **IDE** | Integrated Development Environment |
| **CI** | Continuous Integration |
| **CD** | Continuous Deployment |
| **GIT** | Système de contrôle de version distribué |
| **POC** | Proof of Concept |
| **ODT** | OpenDocument Text (format d’export) |
| **CSV** | Comma‑Separated Values (format d’export) |
| **PDF** | Portable Document Format (format d’export) |
| **UI** | User Interface |
| **UX** | User Experience |

---  

## 11. Annexes (références)  

1. **Arborescence du code source** – Document `causalismp.code.filtered.md` (extraits des packages `dao`, `service`, `metiers`, `ws`, `taglib`, `tool`).  
2. **Documentation technique** – `causalismp-doc/assembly.xml` (packaging des docs).  
3. **Scripts de migration DB** – `causalismp-database/script/*.sql`.  
4. **Fichier de configuration Castor** – `causalismp-web/src/main/resources/database.xml`.  
5. **Manifeste du WAR** – `causalismp-web/src/main/webapp/META-INF/MANIFEST.MF`.  
6. **Fichier de version** – `causalismp-web/src/main/resources/version.properties`.  

---  

*Ce CCF a été rédigé conformément à la norme NF EN 16271 :2013, en s’appuyant sur l’analyse du code source et de la documentation fournie.*  