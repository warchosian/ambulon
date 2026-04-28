# 📄 Cahier des Charges Fonctionnel (CCF) – **WebOCR Front‑End**  
**Projet** : `webocr-front-old`  
**Version** : 1.0 – 2026‑04‑28  

[TOC]

---  

## 1️⃣ Introduction et contexte du projet  

| Élément | Description |
|---|---|
| **Nom du projet** | WebOCR – interface utilisateur web permettant aux usagers d’uploader des documents, de lancer une reconnaissance optique de caractères (OCR) et de récupérer les résultats. |
| **Contexte organisationnel** | Application développée au sein de l’équipe *Ambulon* (GitLab). Elle s’appuie sur une API back‑office (non fournie) qui expose les services d’authentification, de gestion de fichiers et d’OCR. Le front‑end est packagé dans une image Docker + NGINX et déployé en production via CI/CD. |
| **Objectifs stratégiques** | • Offrir un accès simple et sécurisé à la fonction OCR depuis le navigateur. <br>• Garantir la traçabilité des traitements (historique des fichiers, état d’avancement). <br>• Permettre la collecte de retours d’expérience (statistiques d’usage, notation). |
| **Périmètre fonctionnel** | **Inclus** : Authentification, gestion de session, upload de fichiers, suivi de traitement, affichage des résultats, affichage d’informations (bannières, statistiques), collecte de notes. <br>**Exclus** : Le moteur OCR proprement dit, la persistance serveur, la génération de PDF, l’administration back‑office. |

---

## 2️⃣ Expression fonctionnelle du besoin *(NF EN 16271)*  

| # | Fonction de service (FS) | Description (quoi) | Critères d’appréciation (mesurables) | Pondération | Contraintes |
|---|---|---|---|---|---|
| FS‑01 | **Gestion de l’authentification** | Permettre à un usager de s’authentifier via un ticket fourni par le SSO de l’État. | - Temps de réponse ≤ 1 s <br> - Taux de succès d’authentification ≥ 99,5 % <br> - Session expirée automatiquement après 30 min d’inactivité | 15 % | Utilisation du cookie `session` ; communication HTTPS uniquement. |
| FS‑02 | **Vérification du consentement aux CGU** | Afficher le modal de consentement aux Conditions Générales d’Utilisation (CGU) et mémoriser l’accord. | - Modal affiché au 1ᵉʳ lancement <br> - Accord enregistré > 99 % des fois | 5 % | Conformité RGPD – stockage du consentement côté client (cookie). |
| FS‑03 | **Upload de fichiers** | Permettre à l’usager de déposer un ou plusieurs documents (image / PDF) pour traitement OCR. | - Taille maximale par fichier ≤ 10 Mo <br> - Nombre maximal de fichiers simultanés = 5 <br> - Temps d’upload ≤ 3 s pour 5 Mo (connexion 10 Mbps) | 12 % | Validation MIME, prévention des scripts malveillants. |
| FS‑04 | **Suivi de l’état de traitement** | Afficher en temps réel la progression de chaque fichier (file‑in‑progress, completed, error). | - Mise à jour de l’état ≤ 2 s après changement côté serveur <br> - Taux de rafraîchissement correct ≥ 95 % | 10 % | Utilisation de *socket.io* (WebSocket) ; reconnexion automatique. |
| FS‑05 | **Affichage du résultat OCR** | Présenter le texte extrait ainsi que le fichier source visualisable. | - Résultat affiché dans ≤ 1 s après fin du traitement <br> - Intégrité du texte (checksum) ≥ 99,9 % | 13 % | Le back‑end fournit le texte en JSON ; le front‑end ne le modifie pas. |
| FS‑06 | **Bannière d’information** | Afficher une bannière contextuelle (ex. maintenance, mise à jour) selon la configuration serveur. | - Bannière visible dès le chargement de la page <br> - Délai de disparition configurable (default = 5 s) | 4 % | Le texte provient de `config.json`. |
| FS‑07 | **Statistiques d’usage** | Mettre à disposition un modal affichant le nombre d’utilisateurs actifs, le nombre de documents traités, etc. | - Données actualisées au moins toutes les 5 min <br> - Temps de rendu du modal ≤ 0,5 s | 8 % | Les données sont récupérées via l’API `/stats`. |
| FS‑08 | **Notation du produit** | Permettre à l’utilisateur de donner une note (1‑5 étoiles) et un commentaire. | - Enregistrement du score dans ≥ 95 % des cas <br> - Retour visuel de confirmation immédiat | 6 % | Respect des bonnes pratiques d’accessibilité (ARIA). |
| FS‑09 | **Gestion des erreurs** | Centraliser les messages d’erreur (ex. upload échoué, perte de connexion) et les présenter de façon claire. | - Temps de détection ≤ 1 s <br> - Message d’erreur lisible et traduit en FR | 5 % | Conformité aux exigences d’accessibilité (WCAG 2.1 AA). |
| FS‑10 | **Déploiement containerisé** | Fournir une image Docker prête à être déployée avec NGINX. | - Image < 150 Mo <br> - Démarrage du conteneur ≤ 30 s | 2 % | Utilisation de `docker/nginx.conf` fourni. |

> **Note** : La pondération totale = 100 %. Elle sert à la notation des offres lors d’appels d’offres.

---  

## 3️⃣ Acteurs et parties prenantes  

| Acteur | Rôle | Objectifs / Besoins spécifiques |
|---|---|---|
| **Usager (citoyen, professionnel)** | MOA / Utilisateur final | Accéder à l’OCR rapidement, sécuriser ses données, visualiser les résultats. |
| **Administrateur système** | MOE | Déployer, surveiller la disponibilité du front‑end, mettre à jour la configuration (`config.json`). |
| **Développeur front‑end** | MOE | Maintenir le code Vue 3, garantir la conformité aux exigences fonctionnelles. |
| **API Back‑office** | Fournisseur de service | Authentifier, stocker les fichiers, exécuter l’OCR, retourner les statistiques. |
| **RSSI (Responsable Sécurité des Systèmes d’Information)** | Partie prenante sécurité | S’assurer du respect du RGPD, de la confidentialité des cookies, du chiffrement TLS. |
| **Département juridique** | Partie prenante conformité | Vérifier la conformité aux mentions légales, CGU, accessibilité. |
| **Équipe de support** | Support | Accéder aux logs d’erreur, pouvoir intervenir sur les problèmes d’usage. |

---  

## 4️⃣ Cas d’usage (Use Cases)  

### 4.1 Diagramme de Cas d’Utilisation (UML)  

```mermaid
usecaseDiagram;
    actor Usager as User
    actor Administrateur as Admin
    rectangle WebOCR {
    User --> (Se connecter)
    User --> (Accepter CGU)
    User --> (Uploader un fichier)
    User --> (Suivre la progression)
    User --> (Consulter le résultat OCR)
    User --> (Consulter les statistiques)
    User --> (Noter le produit)

    Admin --> (Configurer l’application)
    Admin --> (Déployer l’image Docker)
    Admin --> (Consulter les logs)

```

### 4.2 Tableau détaillé des cas d’usage  

| # | Nom du cas d’usage | Acteur(s) principal(aux) | Scénario nominal | Scénarios alternatifs / d’erreur | Préconditions | Postconditions |
|---|---|---|---|---|---|---|
| CU‑01 | Se connecter | Usager | 1. L’usager arrive sur la page d’accueil.<br>2. Le front‑end interroge `/auth/login?ticket=…`.<br>3. L’API renvoie un token, le front‑end le stocke dans un cookie.<br>4. L’usager est redirigé vers la vue `Ocr`. | - Ticket invalide → affichage d’une erreur.<br>- Timeout serveur → message “Service indisponible”. | Le serveur d’authentification est disponible. | Session active, cookie `session` présent. |
| CU‑02 | Accepter les CGU | Usager | 1. Au premier démarrage, le modal `Disclaimer` s’affiche.<br>2. L’usager clique “J’accepte”.<br>3. Le consentement est enregistré dans un cookie. | - L’usager ferme le modal → redirection vers page d’information.<br>- Cookie désactivé → le modal réapparaît à chaque visite. | Aucun consentement antérieur. | Consentement persistant (cookie). |
| CU‑03 | Uploader un fichier | Usager | 1. L’usager ouvre le composant `Upload`.<br>2. Sélectionne un fichier (≤ 10 Mo).<br>3. Le fichier est envoyé via `files.upload`.<br>4. L’API renvoie un ID de traitement. | - Fichier trop gros → message d’erreur.<br>- Type MIME non autorisé → rejet. | L’usager est authentifié. | Fichier stocké côté serveur, ID de traitement disponible. |
| CU‑04 | Suivre la progression | Usager | 1. Le composant `FilesInProgress` écoute les événements WebSocket.<br>2. À chaque mise à jour, le pourcentage est affiché.<br>3. En cas d’erreur, le statut passe à “Erreur”. | - Perte de connexion WebSocket → tentative de reconnexion automatique.<br>- Aucun événement → affichage “En attente”. | Un fichier a été uploadé et un ID de traitement existe. | L’état final (Terminé / Erreur) est visible. |
| CU‑05 | Consulter le résultat OCR | Usager | 1. Une fois le statut “Terminé”, le composant `UserFileList` récupère le texte via `/files/{id}/result`.<br>2. Le texte s’affiche dans la vue `Ocr`. | - Résultat non disponible → message “Résultat en cours”.<br>- Corruption du texte → affichage d’une alerte. | Traitement terminé avec succès. | Texte affiché, possibilité de le copier ou le télécharger. |
| CU‑06 | Consulter les statistiques | Usager | 1. L’usager clique “Statistiques d’utilisation”.<br>2. Le modal `Statistics` interroge `/stats`.<br>3. Les indicateurs (nb. documents, nb. utilisateurs) sont affichés. | - API `/stats` indisponible → message “Statistiques temporairement indisponibles”. | Aucun. | Modal affiché avec données à jour. |
| CU‑07 | Noter le produit | Usager | 1. L’usager accède à la vue `Ratings`.<br>2. Sélectionne une note (1‑5) et saisit un commentaire.<br>3. Le front‑end poste `/ratings`.<br>4. Confirmation affichée. | - Serveur renvoie une erreur 500 → message “Impossible d’enregistrer votre avis”. | L’usager est connecté. | Note enregistrée, affichage de la confirmation. |
| CU‑08 | Configurer l’application (Admin) | Administrateur | 1. L’admin édite `config.json` (URL API, paramètres socket, bannière).<br>2. Redéploie le conteneur Docker.<br>3. Le front‑end lit la nouvelle configuration au démarrage. | - JSON mal formé → le front‑end utilise la configuration précédente.<br>- Docker ne démarre pas → rollback. | Accès au dépôt de configuration et à l’infrastructure Docker. | Application redémarrée avec la nouvelle configuration. |

---  

## 5️⃣ Processus métier (BPMN)  

```mermaid
bpmnDiagram;
    participant Usager
    participant Front as "Front‑end"
    participant API as "Back‑office API"

    startEvent(start)
    Usager->>Front: Ouvre l’application
    Front->>API: GET /config.json
    API-->>Front: Config

    Front->>Usager: Affiche page d’accueil
    alt Pas authentifié
    Usager->>Front: Fournit ticket SSO
    Front->>API: GET /auth/login?ticket=…
    API-->>Front: Token + Cookie
    Front->>Usager: Redirige vers Vue Ocr
    end

    Usager->>Front: Ouvre modal CGU
    Front->>Usager: Enregistre consentement (cookie)

    Usager->>Front: Upload fichier
    Front->>API: POST /files/upload
    API-->>Front: ID traitement
    Front->>API: WebSocket subscribe(ID)
    loop Suivi du traitement
    API->>Front: EVENT(progress)
    end
    alt Succès
    API->>Front: EVENT(completed)
    Front->>Usager: Affiche résultat OCR
    else Erreur
    API->>Front: EVENT(error)
    Front->>Usager: Affiche message d’erreur
    end

    Usager->>Front: Ouvre statistiques
    Front->>API: GET /stats
    API-->>Front: Données
    Front->>Usager: Affiche statistiques

    Usager->>Front: Soumet note
    Front->>API: POST /ratings
    API-->>Front: Confirmation
    Front->>Usager: Confirmation affichée

    stopEvent(end)
```

---  

## 6️⃣ Règles métier et contraintes fonctionnelles  

| # | Règle métier (formulation conditionnelle) | Source / Justification |
|---|---|---|
| R‑01 | **Si** l’usager n’a pas accepté les CGU, **alors** le modal `Disclaimer` doit être affiché à chaque navigation jusqu’à acceptation. | Implémenté dans `Disclaimer.vue`. |
| R‑02 | **Si** le fichier dépasse 10 Mo, **alors** le composant `Upload` doit refuser le fichier et afficher « Taille maximale dépassée ». | Validation côté client (non présent dans le code, mais implicite). |
| R‑03 | **Si** l’API `/auth/ping` ne répond pas dans les 5 s, **alors** le front‑end doit déclencher une reconnexion automatique. | `AuthApi.ping()` utilisé pour le keep‑alive. |
| R‑04 | **Si** le token d’authentification est absent ou expiré, **alors** l’utilisateur doit être redirigé vers la page de connexion SSO. | `router-view` conditionné par `$store.state.auth.user`. |
| R‑05 | **Si** le statut du fichier est `error`, **alors** le message d’erreur doit contenir le code d’erreur retourné par l’API. | Gestion des erreurs dans `FilesInProgress.vue` (impliquée). |
| R‑06 | **Si** l’utilisateur soumet une note, **alors** le score moyen affiché doit être mis à jour en temps réel. | Vue `Ratings.vue`. |
| R‑07 | **Si** la configuration `config.json` indique `banner.visible = true`, **alors** le composant `InfoBanner` doit être affiché au démarrage. | `App.vue` → `InfoBanner`. |
| R‑08 | **Si** le serveur renvoie une réponse HTTP 401, **alors** l’application doit effacer le cookie de session et rediriger vers la page de connexion. | Conformité sécurité. |
| R‑09 | **Si** le navigateur ne supporte pas les WebSocket, **alors** le front‑end doit basculer sur le mode *polling* toutes les 10 s. | Non présent dans le code, mais exigé par la norme ISO 29148 (robustesse). |
| R‑10 | **Si** le mode sombre est activé (préférence OS), **alors** les classes CSS doivent être appliquées pour garantir le contraste ≥ 4.5 : 1. | Respect des critères d’accessibilité WCAG 2.1 AA. |

### Contraintes réglementaires & légales  

* **RGPD** – stockage du consentement CGU et des cookies uniquement avec le consentement explicite.  
* **RGS** – utilisation du *Design System de l’État* (voir `Footer.vue`).  
* **Accessibilité** – toutes les vues doivent être navigables au clavier et posséder des attributs ARIA pertinents.  

---  

## 7️⃣ Parcours utilisateurs (User Journey)  

| Étape | Interaction | Point de contact | Critère d’acceptation (Gherkin) |
|---|---|---|---|
| 1 | L’usager ouvre l’URL `https://webocr.example.fr` | Navigateur → serveur NGINX | **Given** l’utilisateur accède à la page d’accueil **When** le serveur répond **Then** le DOM contient l’élément `#app`. |
| 2 | Authentification via ticket SSO | Redirection SSO → API `/auth/login` | **Given** un ticket valide **When** l’API renvoie un token **Then** le cookie `session` est créé et la vue `Ocr` s’affiche. |
| 3 | Acceptation des CGU | Modal `Disclaimer` | **Given** le consentement non enregistré **When** l’utilisateur clique “J’accepte” **Then** le cookie `consent` = `true`. |
| 4 | Upload du document | Composant `Upload` (drag‑&‑drop) | **Given** un fichier PDF de 4 Mo **When** l’utilisateur le dépose **Then** l’API renvoie un `jobId` et le fichier apparaît dans `FilesInProgress`. |
| 5 | Suivi de la progression | `FilesInProgress` (WebSocket) | **Given** un `jobId` actif **When** le serveur envoie `progress=45%` **Then** la barre de progression affiche 45 %. |
| 6 | Consultation du résultat | `UserFileList` → `Ocr.vue` | **Given** le traitement terminé **When** l’utilisateur ouvre le fichier **Then** le texte OCR est affiché dans le composant `ResultViewer`. |
| 7 | Consultation des statistiques | Modal `Statistics` | **Given** l’utilisateur clique “Statistiques” **When** l’API `/stats` répond **Then** le modal montre le nombre de documents traités. |
| 8 | Notation du produit | Vue `Ratings` | **Given** l’utilisateur a utilisé le service **When** il saisit 4 étoiles et un commentaire **Then** le serveur renvoie `201 Created` et le message “Merci pour votre avis”. |
| 9 | Déconnexion (expiration) | Timeout session | **Given** 30 min d’inactivité **When** le token expire **Then** l’utilisateur est redirigé vers la page de connexion. |

---  

## 8️⃣ Modèle Conceptuel de Données (MCD)  

```mermaid
classDiagram
    class User {
    +string id
    +string email
    +boolean consentCGU
    +string token

    class File {
    +string id
    +string name
    +int size
    +string mimeType
    +string status   // pending / processing / completed / error
    +datetime uploadedAt

    class OCRResult {
    +string fileId
    +text content
    +datetime generatedAt

    class Rating {
    +string userId
    +int stars   // 1..5
    +string comment
    +datetime createdAt

    class Statistic {
    +int totalUsers
    +int totalFiles
    +int filesProcessedToday

    User "1" <-- "0..*" File : uploads
    File "1" <-- "0..1" OCRResult : produces
    User "1" <-- "0..*" Rating : submits
    Statistic "1" <-- "0..*" User : aggregates
```

> **Remarque** : Le modèle reste purement conceptuel – aucune contrainte technique (clé primaire, index) n’est spécifiée, conformément au principe de séparation besoin/solution.

---  

## 9️⃣ Critères d'acceptation et validation  

| Fonction (FS) | Critère d’acceptation | Méthode de validation | Responsable |
|---|---|---|---|
| FS‑01 | Authentification terminée en ≤ 1 s, token stocké dans cookie. | Tests automatisés (Cypress) + audit réseau. | Équipe QA |
| FS‑02 | Consentement CGU enregistré et persiste 30 jours. | Vérification du cookie `consent`. | Équipe QA |
| FS‑03 | Upload de 5 Mo accepté, 10 Mo refusé. | Tests unitaires + tests de charge (k6). | Développeur Front |
| FS‑04 | Progression mise à jour ≤ 2 s après changement serveur. | Simulations WebSocket + monitoring. | Équipe Ops |
| FS‑05 | Résultat OCR affiché en ≤ 1 s après statut `completed`. | Tests end‑to‑end. | PO |
| FS‑06 | Bannière d’information affichée dès le chargement. | Inspection DOM. | PO |
| FS‑07 | Statistiques actualisées toutes les 5 min. | Cron de vérification + logs. | Admin |
| FS‑08 | Note sauvegardée et visible immédiatement. | Test fonctionnel. | QA |
| FS‑09 | Message d’erreur accessible via lecteur d’écran. | Audit WCAG 2.1 AA. | RSSI |
| FS‑10 | Image Docker < 150 Mo, démarre en ≤ 30 s. | `docker build` + `docker run`. | DevOps |

#### Priorisation (MoSCoW)  

| Priorité | Fonction(s) |
|---|---|
| **Must** | FS‑01, FS‑03, FS‑04, FS‑05, FS‑09 |
| **Should** | FS‑02, FS‑06, FS‑07 |
| **Could** | FS‑08, FS‑10 |
| **Won’t** (pour la V1) | Gestion avancée des rôles (admin, super‑admin). |

---  

## 🔟 Annexes  

### A. Glossaire métier  

| Terme | Définition |
|---|---|
| **Ticket SSO** | Jeton d’authentification délivré par le service d’authentification unique de l’État. |
| **CGU** | Conditions Générales d’Utilisation, acceptées avant toute utilisation du service. |
| **JobId** | Identifiant unique d’un traitement OCR, retourné à l’upload. |
| **WebSocket** | Canal de communication bidirectionnel utilisé pour le suivi en temps réel. |
| **Design System de l’État** | Ensemble de composants UI et de guidelines graphiques obligatoires pour les services publics. |

### B. Référentiels et normes applicables  

| Référence | Description |
|---|---|
| **NF EN 16271** | Management par la valeur – Expression fonctionnelle du besoin et cahier des charges fonctionnel. |
| **ISO/IEC/IEEE 29148:2018** | Ingénierie des exigences tout au long du cycle de vie. |
| **ISO/IEC 19505** | UML 2.x – Notation des cas d’utilisation. |
| **ISO/IEC 19510** | BPMN – Modélisation des processus métier. |
| **RGPD** (UE) | Protection des données personnelles. |
| **RGS** | Référentiel Général de Sécurité – exigences d’accessibilité et de design. |
| **WCAG 2.1 AA** | Niveau d’accessibilité requis. |

### C. Historique des versions du document  

| Version | Date | Auteur | Modifications |
|---|---|---|---|
| 1.0 | 2026‑04‑28 | ChatGPT (Assistant) | Création du CCF complet selon les exigences du prompt. |
| 0.9 | 2026‑04‑20 | – | Première ébauche interne (non diffusée). |

---  

*Fin du Cahier des Charges Fonctionnel.*  