# 📄 Honore‑Back – Cahier des Charges Fonctionnel (CCF)  
[TOC]

---

## 1️⃣ Introduction et contexte du projet {#intro}

| Élément | Description |
|---|---|
| **Nom du projet** | **honore‑back** – service back‑end Node.js/TypeScript dédié aux traitements métiers de la plateforme *Ambulon*. |
| **Contexte organisationnel** | Le service s’inscrit dans une architecture **micro‑services** déployée sur des conteneurs Docker, orchestrée (ex. : Kubernetes) et intégrée dans la chaîne GitLab CI/CD. Il consomme des bibliothèques internes publiées dans le registre npm privé de Google Artifact Registry et exploite une base de données PostgreSQL ainsi qu’un stockage d’objets S3‑compatible. |
| **Objectifs stratégiques** | 1. Fournir une API fiable, sécurisée et évolutive pour les besoins métiers de la plateforme.<br>2. Garantir la **maintenabilité** grâce à une séparation claire du code (source, tests, artefacts).<br>3. Assurer la **traçabilité** et la **reproductibilité** des livrables (Docker, npm). |
| **Périmètre fonctionnel** | <u>Inclus</u> : <br>• Gestion des données métier (CRUD via PostgreSQL).<br>• Gestion des fichiers (upload / download) sur le bucket S3.<br>• Exposition d’une API REST (ou GraphQL) documentée.<br>• Authentification / autorisation via JWT (ou équivalent).<br>• Tests unitaires & d’intégration automatisés.<br>• CI/CD (build, test, scan, image).<br><br><u>Exclus</u> : <br>• Front‑end (UI).<br>• Gestion des infrastructures réseau (load‑balancer, DNS).<br>• Gestion des secrets (hors CI/CD). |

---

## 2️⃣ Expression fonctionnelle du besoin (NF EN 16271) {#besoin}

> **Principe** – Chaque fonction de service (FS) décrit **« quoi »** le système doit accomplir, **pas comment**.  
> Les critères d’appréciation sont quantifiables, pondérés et associés à des contraintes éventuelles.

| # | Fonction de service (FS) | Description (quoi) | Critères d’appréciation (mesurables) | Pondération* | Contraintes |
|---|---|---|---|---|---|
| **FS‑01** | **Gestion des utilisateurs** | Créer, lire, mettre à jour et supprimer les comptes utilisateurs ainsi que leurs rôles. | • Temps moyen de création ≤ 200 ms.<br>• Taux d’erreur < 0,1 % sur 10 000 requêtes.<br>• Conformité RGPD (droit à l’oubli) – suppression complète en ≤ 5 s. | 15 % | • Stockage dans PostgreSQL.<br>• Mot de passe hashé (bcrypt ≥ 12 rounds). |
| **FS‑02** | **Authentification & autorisation** | Authentifier un utilisateur et délivrer un token d’accès (JWT) contenant les claims nécessaires. | • Latence d’authentification ≤ 150 ms.<br>• Validité du token configurable (ex. 15 min).<br>• Revocation possible via blacklist. | 12 % | • Clé de signature stockée hors du dépôt (CI variable). |
| **FS‑03** | **Gestion des entités métier** | Fournir les API CRUD pour les entités métier (ex. : dossiers, demandes, historiques). | • Disponibilité de l’API ≥ 99,9 % (sur 30 jours).<br>• Temps de réponse moyen ≤ 300 ms (hors DB). | 18 % | • Utilisation de TypeORM.<br>• Migration DB versionnée. |
| **FS‑04** | **Stockage d’objets** | Permettre l’upload, le téléchargement et la suppression de fichiers dans un bucket S3‑compatible. | • Débit d’upload ≥ 5 MiB/s.<br>• Débit de téléchargement ≥ 10 MiB/s.<br>• Intégrité vérifiée (SHA‑256). | 10 % | • Variables `STORAGE_*` injectées en runtime.<br>• Accès en mode **no‑SSL** uniquement en environnement de test. |
| **FS‑05** | **Exposition d’une API publique** | Publier une API REST (ou GraphQL) documentée via OpenAPI/Swagger. | • Couverture de la documentation ≥ 95 % des endpoints.<br>• Conformité aux standards HTTP/2. | 8 % | • Utilisation d’Express/Koa (libre). |
| **FS‑06** | **Gestion des logs & monitoring** | Centraliser les logs applicatifs et exposer des métriques (Prometheus). | • Rétention logs ≥ 30 jours.<br>• Latence métriques ≤ 5 s. | 5 % | • Logs au format JSON. |
| **FS‑07** | **Qualité du code** | Appliquer linting, formatage et tests automatisés. | • Couverture de tests unitaires ≥ 80 %.<br>• Aucun warning ESLint en CI.<br>• Build Docker < 5 min. | 7 % | • `.eslintignore`, `.editorconfig` déjà fournis. |
| **FS‑08** | **Déploiement continu** | Automatiser le build, les tests, le scan de vulnérabilités et la publication de l’image Docker. | • Temps moyen de pipeline ≤ 15 min.<br>• 0 vulnérabilité critique détectée. | 10 % | • `.gitlab-ci.yml` inclut le fichier partagé `back.yml`. |
| **FS‑09** | **Gestion des secrets** | Garantir que les secrets (clés d’accès, mots de passe) ne sont jamais versionnés. | • Aucun secret détecté dans le dépôt (scan Git‑secret).<br>• Injection via variables CI/CD uniquement. | 5 % | • `.gitignore` exclut `.env`, `auth.sh`. |

\* La pondération totale = **100 %**.

---

## 3️⃣ Acteurs et parties prenantes {#acteurs}

| Acteur | Rôle | Objectifs | Besoins spécifiques |
|---|---|---|---|
| **MOA (Maître d’Ouvrage)** | Commanditaire fonctionnel | • Satisfaire les exigences métier.<br>• Garantir le respect des délais et du budget. | • Visibilité sur les livrables.<br>• Documentation fonctionnelle claire. |
| **MOE (Maître d’Œuvre)** | Équipe de développement & Ops | • Concevoir, coder, tester, livrer le service. | • Accès aux spécifications détaillées.<br>• Environnement CI/CD fonctionnel. |
| **Product Owner** | Priorisation des fonctionnalités | • Maximiser la valeur métier. | • Backlog clair, critères d’acceptation définis. |
| **Développeur Back‑end** | Implémentation technique | • Livrer du code conforme aux normes. | • Linter, tests, CI configurés. |
| **Architecte Sécurité** | Assurance de la conformité sécurité | • Garantir la protection des données. | • Analyse de risques, revue de code, secrets. |
| **Opérateur / SRE** | Exploitation & monitoring | • Maintenir la disponibilité et la performance. | • Métriques, alertes, logs centralisés. |
| **Utilisateur final (ex. : appli mobile, web)** | Consommateur de l’API | • Accéder aux services métiers. | • Temps de réponse rapide, fiabilité. |
| **Auditeur RGPD** | Conformité légale | • Vérifier le respect du RGPD. | • Droit à l’oubli, traçabilité des accès. |
| **Fournisseur NPM privé (Google Artifact Registry)** | Gestion des paquets internes | • Distribuer les bibliothèques partagées. | • Accès via scopes `@pnm3`, `@pasta`. |

---

## 4️⃣ Cas d’usage (Use Cases) {#usecases}

### 4.1 Diagramme de cas d’utilisation UML (Mermaid)

```mermaid
usecaseDiagram;
    actor Utilisateur final as UF;
    actor Product Owner as PO;
    actor Développeur as DEV;
    actor Opérateur / SRE as SRE;
    actor Auditeur RGPD as RGPD;
    UF --> (Consulter données métier)
    UF --> (Uploader / télécharger fichiers)

    PO --> (Définir exigences fonctionnelles)
    PO --> (Valider livrables)

    DEV --> (Implémenter API)
    DEV --> (Écrire tests unitaires)
    DEV --> (Déployer image Docker)

    SRE --> (Surveiller disponibilité)
    SRE --> (Analyser logs & métriques)

    RGPD --> (Vérifier conformité RGPD)
```

### 4.2 Tableau des cas d’usage

| # | Nom du cas d’usage | Acteur(s) principal(aux) | Scénario nominal | Scénarios alternatifs / d’erreur | Pré‑conditions | Post‑conditions |
|---|---|---|---|---|---|---|
| **CU‑01** | **Authentifier un utilisateur** | Utilisateur final | 1. L’utilisateur fournit login / mot de passe.<br>2. Le service valide les credentials via la base.<br>3. Un JWT signé est renvoyé. | *E1* : credentials invalides → réponse 401.<br>*E2* : service DB indisponible → réponse 503. | DB PostgreSQL accessible. | Token JWT stocké côté client. |
| **CU‑02** | **Créer un compte utilisateur** | Utilisateur final (admin) | 1. Envoi d’un payload JSON (nom, email, rôle).<br>2. Service crée l’entrée dans PostgreSQL.<br>3. Retour 201 avec ID. | *E1* : email déjà existant → 409.<br>*E2* : validation champ manquant → 400. | JWT valide avec droits admin. | Nouvel utilisateur persistant. |
| **CU‑03** | **Uploader un fichier** | Utilisateur final | 1. Envoi d’un multipart/form‑data avec le fichier.<br>2. Service transmet le flux vers le bucket S3.<br>3. Retour URL d’accès. | *E1* : dépassement quota → 413.<br>*E2* : erreur S3 → 502. | JWT valide, droits d’écriture. | Fichier stocké, métadonnées enregistrées en DB. |
| **CU‑04** | **Télécharger un fichier** | Utilisateur final | 1. Requête GET sur `/files/{id}`.<br>2. Service récupère l’URL S3 signée.<br>3. Retour du flux. | *E1* : fichier non trouvé → 404.<br>*E2* : expiration signature → 403. | JWT valide, droits de lecture. | Flux délivré au client. |
| **CU‑05** | **Exécuter la pipeline CI/CD** | Développeur / CI Runner | 1. Commit/push déclenche le pipeline.<br>2. Étapes : lint → test → build → scan vuln → push image. | *E1* : lint échoue → job stoppé.<br>*E2* : tests échouent → job stoppé.<br>*E3* : scan vulns critiques → fail. | Variable `USE_NEW_REGISTRY` définie. | Image Docker versionnée disponible dans le registre. |
| **CU‑06** | **Consulter les métriques** | Opérateur / SRE | 1. Accès au endpoint `/metrics` (Prometheus).<br>2. Lecture des KPI (latence, errors). | *E1* : endpoint non exposé → 404.<br>*E2* : authentification manquante → 401. | Service en cours d’exécution. | KPI disponibles pour tableau de bord. |
| **CU‑07** | **Vérifier conformité RGPD (droit à l’oubli)** | Auditeur RGPD | 1. Envoi d’une requête de suppression d’un utilisateur. <br>2. Service supprime les données personnelles et les fichiers associés. | *E1* : données liées non supprimées → erreur 500.<br>*E2* : manque d’autorisation → 403. | Autorisation spéciale (role = RGPD). | Toutes les traces personnelles effacées dans ≤ 5 s. |

---

## 5️⃣ Processus métier (optionnel) {#processus}

### 5.1 Diagramme BPMN (Mermaid)

```mermaid
bpmnDiagram;
    participant Utilisateur;
    participant ServiceAPI as API;
    participant DB as PostgreSQL;
    participant S3 as Storage;
    startEvent(start)
    startEvent --> task(Authentifier)
    task --> exclusiveGateway{Authentifié ?}
    exclusiveGateway -->|Oui| task(Créer/Requête)
    exclusiveGateway -->|Non| endEvent(failure)

    task --> exclusiveGateway2{Type de requête}
    exclusiveGateway2 -->|CRUD| task(DB Opération)
    exclusiveGateway2 -->|Upload| task(Envoi vers S3)
    exclusiveGateway2 -->|Download| task(Récupérer URL S3)

    task(DB Opération) --> serviceTask(Commit Transaction)
    task(Envoi vers S3) --> serviceTask(Upload Object)
    task(Récupérer URL S3) --> serviceTask(Generate Signed URL)

    serviceTask --> endEvent(success)
```

### 5.2 Description textuelle

| Processus | Description | Points de contrôle |
|---|---|---|
| **P‑01 Authentification** | Validation des credentials → génération JWT. | - Vérification du hash du mot de passe.<br>- Rotation des clés de signature (au moins tous les 90 jours). |
| **P‑02 Gestion CRUD** | Opérations sur les entités métier via TypeORM. | - Validation du schéma (zod/ajv).<br>- Contrôle d’intégrité référentielle. |
| **P‑03 Gestion du stockage** | Upload / download de fichiers vers le bucket S3‑compatible. | - Vérification du checksum.<br>- Gestion du bucket et du préfixe par tenant. |
| **P‑04 Pipeline CI/CD** | Build, test, scan, push. | - Lint = 0 warnings.<br>- Couverture tests ≥ 80 %. |
| **P‑05 Monitoring & Alerting** | Export de métriques, agrégation des logs. | - Alertes sur latence > 500 ms.<br>- Alertes sur taux d’erreur > 1 %. |

---

## 6️⃣ Règles métier et contraintes fonctionnelles {#regles}

| # | Règle métier (IF…THEN) | Type | Source |
|---|---|---|---|
| **R‑01** | **IF** un utilisateur a le rôle *admin* **THEN** il peut créer, modifier ou supprimer tout compte. | Autorisation | MOA |
| **R‑02** | **IF** le fichier dépasse 100 MiB **THEN** le service doit refuser l’upload avec code 413. | Validation | PO |
| **R‑03** | **IF** la requête provient d’une IP non autorisée **THEN** bloquer l’accès (firewall). | Sécurité | Architecte Sécurité |
| **R‑04** | **IF** le token JWT est expiré **THEN** renvoyer 401 et demander une nouvelle authentification. | Sécurité | PO |
| **R‑05** | **IF** l’utilisateur demande la suppression de ses données **THEN** toutes les lignes liées (DB + S3) doivent être supprimées dans les 5 s suivantes. | RGPD | Auditeur RGPD |
| **R‑06** | **IF** le pipeline détecte une vulnérabilité critique **THEN** le job échoue et alerte le propriétaire. | Qualité | MOE |
| **R‑07** | **IF** un test unitaire échoue **THEN** la build ne doit pas être déployée. | Qualité | MOE |
| **R‑08** | **IF** une modification de schéma DB est requise **THEN** elle doit être versionnée via migration TypeORM. | Gestion de configuration | Architecte |
| **R‑09** | **IF** le service est en mode production **THEN** le stockage doit être en SSL (TLS 1.2+). | Sécurité | PO |
| **R‑10** | **IF** le service reçoit un header `X-Request-ID` **THEN** il doit le logger dans chaque ligne de log. | Observabilité | SRE |

**Contraintes supplémentaires**  

- **Conformité RGPD** : aucune donnée personnelle ne doit être stockée sans consentement explicite.  
- **Performance** : SLA de réponse ≤ 300 ms (hors DB) pour 95 % des requêtes.  
- **Disponibilité** : 99,9 % mensuel, avec basculement possible via Kubernetes.  
- **Portabilité** : Dockerfile doit rester compatible avec les versions Node 16‑LTS et Node 18‑LTS (future proof).  

---

## 7️⃣ Parcours utilisateurs (User Journey) {#journey}

| Étape | Action utilisateur | Interaction système | Critères d’acceptation (Given/When/Then) |
|---|---|---|---|
| **J‑01** | Ouvre l’application mobile/web | - | **Given** l’utilisateur n’est pas authentifié, **When** il ouvre la page de connexion, **Then** le formulaire de login s’affiche. |
| **J‑02** | Saisit ses identifiants | Envoi POST `/auth/login` | **Given** des identifiants valides, **When** le POST est reçu, **Then** le service renvoie un JWT (200) et le stocke côté client. |
| **J‑03** | Accède à la liste des dossiers | GET `/dossiers` avec JWT | **Given** JWT valide, **When** la requête est faite, **Then** le service retourne la liste (200) en ≤ 300 ms. |
| **J‑04** | Sélectionne un dossier → téléverse un document | POST `/files` (multipart) | **Given** le fichier < 100 MiB, **When** l’upload est lancé, **Then** le fichier apparaît dans le bucket et l’URL est renvoyée (201). |
| **J‑05** | Consulte le document | GET `/files/{id}` | **Given** JWT valide et droits lecture, **When** la requête est faite, **Then** le service fournit un lien signé (200). |
| **J‑06** | Déconnecte | POST `/auth/logout` (optionnel) | **Given** session active, **When** l’utilisateur clique sur “Déconnexion”, **Then** le token est révoqué (200) et l’app revient à l’écran de login. |
| **J‑07** | (Admin) Supprime un utilisateur | DELETE `/users/{id}` | **Given** rôle admin, **When** la suppression est confirmée, **Then** l’utilisateur et ses données sont effacés (200) et un audit log est créé. |

---

## 8️⃣ Modèle Conceptuel de Données (MCD) {#mcd}

### 8.1 Diagramme de classes UML (Mermaid)

```mermaid
classDiagram
    class User {
        +uuid id;
        +string email;
        +string passwordHash;
        +enum role {ADMIN, USER, RGPD}
        +Date createdAt;
        +Date updatedAt;
    }
    class Dossier {
        +uuid id;
        +string title;
        +string description;
        +Date createdAt;
        +Date updatedAt;
    }
    class File {
        +uuid id;
        +string filename;
        +string mimeType;
        +int size;
        +string s3Key;
        +Date uploadedAt;
    }
    class AuditLog {
        +uuid id;
        +uuid userId;
        +string action;
        +string details;
        +Date timestamp;
    }

    User "1" --> "0..*" Dossier : owns;
    Dossier "1" --> "0..*" File : contains;
    User "1" --> "0..*" AuditLog : generates;
    File "1" --> "1" User : uploadedBy
```

### 8.2 Description des entités

| Entité | Attributs clés | Relations | Rôle métier |
|---|---|---|---|
| **User** | `id`, `email`, `passwordHash`, `role` | possède plusieurs **Dossier**, génère **AuditLog** | Représente un compte d’accès au service. |
| **Dossier** | `id`, `title`, `description` | appartient à un **User**, contient plusieurs **File** | Regroupe les informations métier liées à un cas d’usage. |
| **File** | `id`, `filename`, `mimeType`, `size`, `s3Key` | liée à un **Dossier**, uploadée par un **User** | Objet stocké dans le bucket S3. |
| **AuditLog** | `id`, `userId`, `action`, `details` | référence **User** | Historisation des actions critiques (RGPD, admin). |

---

## 9️⃣ Critères d'acceptation et validation {#acceptation}

| Fonction de service | Critère d’acceptation | Méthode de validation | Responsable |
|---|---|---|---|
| **FS‑01** (Gestion des utilisateurs) | Création < 200 ms, suppression < 5 s, conformité RGPD | Tests d’intégration + script de purge | PO / QA |
| **FS‑02** (Auth) | JWT signé, expiration configurable, revocation fonctionnelle | Tests unitaires (jest) + tests de charge (k6) | Développeur |
| **FS‑03** (CRUD entités) | Disponibilité 99,9 % sur 30 jours, temps de réponse ≤ 300 ms | Monitoring Prometheus + SLO | SRE |
| **FS‑04** (Stockage) | Débit upload ≥ 5 MiB/s, checksum OK | Test de performance (ab) | QA |
| **FS‑05** (API) | Documentation OpenAPI ≥ 95 % couverte, 200 OK sur endpoint health | Swagger UI + tests d’API (Postman) | PO |
| **FS‑06** (Logs/Monitoring) | Logs JSON, rétention 30 jours, métriques exposées | ELK + Prometheus scrape | SRE |
| **FS‑07** (Qualité du code) | Coverage ≥ 80 %, 0 ESLint warning | SonarQube + CI report | QA |
| **FS‑08** (CI/CD) | Pipeline ≤ 15 min, 0 vulns critiques | GitLab CI badge, Trivy scan | DevOps |
| **FS‑09** (Secrets) | Aucun secret dans repo, injection via CI variables | Git‑secret scan, audit | Sécurité |

> **Priorisation MoSCoW** (exemple)  
> - **Must** : FS‑01, FS‑02, FS‑03, FS‑05, FS‑08  
> - **Should** : FS‑04, FS‑06, FS‑07  
> - **Could** : FS‑09 (déjà couvert par processus)  
> - **Won’t** (pour la version 1.0) : fonctionnalités de reporting avancé, multi‑tenant complet.

---

## 🔟 Annexes {#annexes}

### 10.1 Glossaire métier

| Terme | Définition |
|---|---|
| **Dossier** | Ensemble logique d’informations liées à un cas d’usage (ex. : demande d’homologation). |
| **File** | Document ou média stocké dans le bucket d’objets, associé à un dossier. |
| **JWT** | JSON Web Token, jeton d’authentification signé. |
| **RGPD** | Règlement Général sur la Protection des Données (UE). |
| **CI/CD** | Intégration Continue / Déploiement Continu. |
| **S3‑compatible** | Service de stockage d’objets compatible avec l’API d’Amazon S3 (ex. : MinIO). |
| **MoSCoW** | Méthode de priorisation (Must, Should, Could, Won’t). |

### 10.2 Référentiels et normes applicables

| Référence | Domaine |
|---|---|
| **NF EN 16271** | Management par la valeur – expression fonctionnelle du besoin. |
| **ISO/IEC/IEEE 29148:2018** | Ingénierie des exigences. |
| **ISO/IEC 19505 (UML 2.x)** | Modélisation des cas d’usage et du MCD. |
| **ISO/IEC 19510 (BPMN)** | Modélisation des processus métier. |
| **RGPD (EU‑2016/679)** | Protection des données personnelles. |
| **OWASP Top 10** | Sécurité des applications web. |
| **ISO/IEC 27001** | Sécurité de l’information. |

### 10.3 Historique des versions du document

| Version | Date | Auteur | Modifications |
|---|---|---|---|
| **1.0** | 2026‑04‑28 | ChatGPT (assistant) | Création du CCF complet à partir des artefacts fournis. |
| **1.1** | – | – | À venir – ajustements post‑validation MOA. |

---

> **↩ Retour au sommaire** | **© 2026 – Honore‑Back – Cahier des Charges Fonctionnel**  

---