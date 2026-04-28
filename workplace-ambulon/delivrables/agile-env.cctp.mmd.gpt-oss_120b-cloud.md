# Cahier des Clauses Techniques Particulières (CCTP)  
## Projet : **agile‑env** – Environnement d’exécution Docker pour une application PHP / Apache / PostgreSQL  

> **Référence** : DCE – Lot 1 – Services d’infrastructure logicielle  
> **Date** : 27 avril 2026  
> **Version** : 1.0  

---

## 1. Objet du marché  

| Num. | Description | Référence au CCF |
|------|-------------|------------------|
| 1.1 | Fourniture d’une solution d’environnement de développement et d’intégration continue, reposant sur Docker, incluant les images applicatives PHP / Apache et PostgreSQL, ainsi que les scripts d’initialisation de la base de données. | CCF : « Déploiement d’un environnement agile‑env » |
| 1.2 | Mise à disposition de la documentation technique, des procédures d’exploitation et de la formation associée. | CCF : « Documentation et formation » |
| 1.3 | Garantir la conformité aux exigences de sécurité du Référentiel Général de Sécurité (RGS) niveau **Renforcé**, à la réglementation RGPD et aux bonnes pratiques de l’ANSSI (SSI). | CCF : « Sécurité et conformité » |
| 1.4 | Assurer la maintenance corrective, évolutive et le support technique pendant la période de garantie (24 mois). | CCF : « Maintenance et support » |

**Périmètre** :  
- Tous les artefacts listés dans l’arborescence du dépôt `agile‑env` (Dockerfiles, fichiers de configuration, scripts d’initialisation, `docker‑compose.dev.yml`).  
- Le **déploiement** sur les environnements d’intégration (dev) et de pré‑production du maître d’ouvrage.  
- L’interfaçage avec les systèmes d’authentification existants (CAS) et les bases de données de production du client.

---

## 2. Description technique détaillée  

| Niveau | Exigence | Référence |
|--------|----------|-----------|
| **2.1** | **Spécifications fonctionnelles minimales** – Le prestataire devra livrer une image Docker `agile‑env‑app` contenant : <br>• PHP 7.3 avec extensions `pdo_pgsql`, `intl` ; <br>• Apache 2.4 configuré selon le fichier `docker/conf/000‑default.conf` ; <br>• Composer installé et accessible en ligne de commande. | Dockerfile‑app |
| **2.2** | **Spécifications techniques obligatoires** – Le prestataire devra : <br>• Utiliser l’image officielle `php:7.3‑apache‑buster` comme base ; <br>• Intégrer les variables d’environnement proxy (`http_proxy`, `https_proxy`) tel que décrit dans le Dockerfile‑app ; <br>• Copier le fichier `docker/conf/000‑default.conf` dans le répertoire `/etc/apache2/sites-available/`. | Dockerfile‑app |
| **2.3** | **Spécifications techniques souhaitées** – Le prestataire pourra : <br>• Installer `yarn` et `npm` afin de permettre la compilation d’actifs front‑end ; <br>• Mettre en place un serveur de cache (Redis) en option. | Optionnel |
| **2.4** | **Spécifications techniques optionnelles** – Le prestataire pourra proposer : <br>• Un mécanisme de hot‑reload pour le code source via `docker‑compose` en mode développement ; <br>• Un tableau de bord Grafana/Prometheus pour la supervision. | Optionnel |

---

## 3. Architecture et conception  

| Item | Exigence |
|------|----------|
| **3.1** | **Contraintes architecturales** – L’ensemble des services devra être orchestré via un fichier `docker‑compose.dev.yml` respectant le schéma : <br>• Service `app` (image `agile‑env‑app`) ; <br>• Service `db` (image `postgres:11‑alpine`) ; <br>• Réseau interne nommé `agile‑net`. |
| **3.2** | **Normes et standards obligatoires** – Le prestataire devra se conformer aux standards : <br>• ISO/IEC 27001 (Sécurité de l’information) ; <br>• ISO/IEC 25010 (Qualité du logiciel) ; <br>• RFC 7230/7231 (HTTP/1.1) ; <br>• W3C HTML 5.2 (si des pages sont générées). |
| **3.3** | **Interopérabilité** – Les API exposées par l’application devront être compatibles avec le **Référentiel Général d’Interopérabilité (RGI)** : utilisation de JSON UTF‑8, respect des schémas OpenAPI 3.0. |
| **3.4** | **Frameworks autorisés** – Uniquement les composants fournis dans les images officielles Docker Hub (php, composer, postgres). Aucun composant tiers non‑documenté ne devra être introduit. |

---

## 4. Exigences de sécurité (RGS, ANSSI)

| Niveau | Exigence | Type d’obligation |
|--------|----------|--------------------|
| **4.1** | **Niveau de sécurité** – Le prestataire devra garantir le niveau **RGS Renforcé** pour l’ensemble des services (authentification forte, chiffrement, traçabilité). | Résultat |
| **4.2** | **Authentification & contrôle d’accès** – L’accès à l’interface d’administration Apache devra être protégé par **HTTP Basic** avec mots de passe stockés dans le fichier `docker/extra/app‑conf/.env` chiffrés à l’aide de **AES‑256‑GCM**. | Résultat |
| **4.3** | **Chiffrement des données** – <br>• En transit : TLS 1.3 obligatoire, certificat auto‑signé fourni ou certificat de l’autorité du maître d’ouvrage. <br>• Au repos : les volumes PostgreSQL devront être chiffrés avec **pgcrypto** ou **LUKS** au niveau du host. | Résultat |
| **4.4** | **Journalisation** – Tous les événements de sécurité (login, échec d’accès, exécution de scripts d’init) devront être consignés dans les fichiers `syslog` et `docker logs` avec le format **CEF** (Common Event Format). | Résultat |
| **4.5** | **Conformité RGPD** – Le prestataire devra : <br>• Anonymiser ou pseudonymiser les données à caractère personnel stockées dans la base de données de test. <br>• Fournir un registre des traitements (DPIA) pour les traitements réalisés dans l’environnement de développement. | Résultat |
| **4.6** | **Bonnes pratiques ANSSI** – Le prestataire devra appliquer le **Guide d’hygiène informatique** (ANSSI‑GS‑001) : mise à jour régulière des images, utilisation de l’option `--no‑cache` lors du build, suppression des packages inutiles (`apt-get clean`). | Moyen |

---

## 5. Interfaces et intégrations  

| Interface | Système cible | Protocole / Format | Modalité de recette |
|-----------|----------------|---------------------|----------------------|
| **5.1** | CAS (Central Authentication Service) – serveur existant du client | HTTP / HTTPS, tickets CAS, JSON | Vérification de l’obtention d’un ticket valide via le script `config_CAS.php`. |
| **5.2** | Base de données PostgreSQL de production (démo) | PostgreSQL 11, SSL | Test d’import/export via les scripts `initdb/*.sql` et `restore.sh`. |
| **5.3** | Outils CI/CD du client (GitLab CI) | Docker Registry, GitLab Runner | Déploiement automatisé à partir du fichier `docker‑compose.dev.yml`. |
| **5.4** | Système de supervision (optionnel) | Prometheus exposition (`/metrics`) | Validation du scraping par Prometheus. |

---

## 6. Environnements et infrastructure  

| Environnement | Caractéristiques obligatoires |
|---------------|-------------------------------|
| **6.1** Développement | Hébergement sur serveur dédié du client, OS Linux Debian 11, accès via VPN. |
| **6.2** Recette | Identique à l’environnement de développement, mais avec les variables d’environnement `APP_ENV=recette`. |
| **6.3** Production (pré‑production) | Hébergement **souverain** (data‑center français), conformité RGS Renforcé, réplication PostgreSQL en mode **Hot‑Standby**. |
| **6.4** Infrastructure réseau | Sous‑réseau `10.0.0.0/24` dédié, firewall autorisant uniquement les ports 80, 443, 5432 entre les services. |
| **6.5** Haute disponibilité | Le service `app` devra être déployé en **mode réplication** (minimum 2 réplicas) avec un load‑balancer `HAProxy` fourni par le client. |
| **6.6** PRA / PCA | Le prestataire devra fournir un **Plan de Reprise d’Activité (PRA)** détaillant la reconstruction des images et la restauration des volumes en moins de 4 heures. |

---

## 7. Qualité et conformité  

| Référentiel | Exigence |
|-------------|----------|
| **ISO 9001** | Le prestataire devra appliquer un système de management qualité certifié, avec traçabilité des livrables. |
| **ISO 25010** | Les critères de qualité du logiciel : <br>• **Fiabilité** : Taux d’erreur ≤ 0,1 % en charge normale. <br>• **Performance** : Temps de réponse HTTP ≤ 200 ms (95 % des requêtes). |
| **RGAA** (si applicables) | Les pages HTML générées devront être conformes au **niveau AA** du RGAA. |
| **Documentation** | Le code source devra être commenté selon la norme **PHPDoc** et les Dockerfiles selon la **Dockerfile Best Practices**. |
| **Maintenabilité** | Le prestataire devra fournir le code source complet (Dockerfile, scripts, `docker‑compose.yml`) sous licence **MIT** ou équivalente, avec un **README** détaillé. |

---

## 8. Documentation et formation  

| Livrable | Format | Contenu requis |
|----------|--------|----------------|
| **8.1** Dossier d’Architecture Technique (DAT) | PDF + Diagrammes UML | Schéma d’architecture, description des services, flux de données, matrice des risques. |
| **8.2** Guide d’Installation et d’Exploitation | Markdown (`README.md`) | Prérequis, procédure `docker‑compose up`, variables d’environnement, sauvegarde/restauration DB. |
| **8.3** Manuel d’Administration | PDF | Gestion des utilisateurs, mise à jour des images, supervision, procédure PRA. |
| **8.4** Documentation API (le cas échéant) | OpenAPI 3.0 (YAML) | Endpoints, schémas, exemples de requêtes. |
| **8.5** Formation | Sessions présentiel / visioconférence (2 jours) | Installation, utilisation de `docker‑compose`, bonnes pratiques de sécurité, dépannage. |
| **8.6** Support de formation | PPT + supports PDF | Slides, exercices pratiques. |

---

## 9. Tests et recette  

| Type de test | Objectif | Critère d’acceptation |
|--------------|----------|-----------------------|
| **9.1** Tests unitaires | Vérifier le bon fonctionnement des scripts PHP et des scripts d’init DB. | Couverture ≥ 80 % (outil **PHPUnit**). |
| **9.2** Tests d’intégration | Valider l’interaction `app ↔ db` et `app ↔ CAS`. | Succès de 100 % des scénarios décrits dans le **Plan de Tests d’Intégration**. |
| **9.3** Tests de charge | Simuler 200 utilisateurs simultanés via **k6**. | Temps de réponse ≤ 300 ms, taux d’erreur ≤ 0,5 %. |
| **9.4** Tests de sécurité | Scans de vulnérabilités (OWASP ZAP, Trivy). | Aucun **Critical** ou **High** non corrigé. |
| **9.5** Tests de conformité RGS | Audit interne RGS. | Niveau **Renforcé** atteint sur 100 % des critères. |
| **9.6** Recette fonctionnelle | Validation par le maître d’ouvrage sur l’environnement de pré‑production. | Validation sans réserve ou avec réserves levées dans un délai de 5 jours ouvrés. |

**Gestion des anomalies** : chaque anomalie devra être consignée dans le système de suivi (GitLab Issues) avec priorité (P1‑P4) et résolue selon les délais indiqués à la section **10.2**.

---

## 10. Maintenance et support  

| Niveau | Description | Délais (GTR / GTD) |
|--------|-------------|---------------------|
| **10.1** Support de premier niveau (hotline) | Assistance téléphonique / mail pour incidents de production. | Temps de réponse (GTR) : ≤ 30 min (P1), ≤ 2 h (P2). |
| **10.2** Support de second niveau (intervention) | Analyse et correction des défauts logiciels. | Délai de correction (GTD) : ≤ 4 h (P1), ≤ 24 h (P2), ≤ 5 jours ouvrés (P3). |
| **10.3** Maintenance corrective | Corrections de bugs détectés pendant la période de garantie. | Inclus dans le contrat pendant 24 mois. |
| **10.4** Maintenance évolutive | Ajout de nouvelles fonctionnalités ou mise à jour des dépendances (ex. PHP 8.0). | Facturation séparée, devis préalable. |
| **10.5** SLA de disponibilité | Disponibilité du service `app` : ≥ 99,9 % sur 12 mois. | Pénalité : 0,5 % du montant mensuel du lot par tranche de 0,1 % de non‑conformité. |
| **10.6** Reporting mensuel | Rapport d’incidents, indicateurs de performance, actions correctives. | Livraison au plus tard le 5 du mois suivant. |

---

## 11. Livrables et planning  

| Jalons | Livrable | Date de remise | Mode de livraison |
|--------|----------|----------------|-------------------|
| **11.1** Kick‑off projet | Cahier des charges fonctionnel (CCF) signé | 10 mai 2026 | PDF & dépôt Git |
| **11.2** Livraison des images Docker | Images `agile‑env‑app` et `agile‑env‑db` poussées sur le registre Docker privé du client | 31 mai 2026 | Registry Docker |
| **11.3** Documentation technique | DAT, guides, manuels (voir section 8) | 15 juin 2026 | PDF & GitLab Wiki |
| **11.4** Tests d’intégration et recette | Rapport de tests + validation du maître d’ouvrage | 30 juin 2026 | PDF |
| **11.5** Mise en production pré‑prévue | Environnement de pré‑production opérationnel | 15 juillet 2026 | Accès au serveur |
| **11.6** Formation utilisateurs | Sessions de formation + supports | 20 juillet 2026 | Présentiel / visioconférence |
| **11.7** Clôture du projet | Rapport de fin de projet, transfert de compétences | 31 juillet 2026 | PDF & réunion de clôture |

**Pénalités de retard** : 0,2 % du montant total du lot par jour de retard au-delà du délai d’acquisition, plafonné à 5 % du montant total.

---

## 12. Contraintes légales et réglementaires  

| Domaine | Exigence contractuelle |
|---------|------------------------|
| **12.1** Propriété intellectuelle | Tous les livrables (code source, scripts, documentation) seront cédés **exclusivement** au maître d’ouvrage, sans restriction, dès paiement complet. |
| **12.2** Licences tierces | Le prestataire devra fournir la liste exhaustive des composants tiers (ex. `composer` packages) avec leurs licences (MIT, BSD, GPL‑3.0, etc.) et garantir leur compatibilité avec la cession de droits. |
| **12.3** Protection des données (RGPD) | Le prestataire devra réaliser un **DPIA** (Data Protection Impact Assessment) et le transmettre au maître d’ouvrage avant la mise en production. |
| **12.4** Archivage | Les livrables (code, documentation, scripts d’installation) devront être archivés pendant **10 ans** au format **PDF/A** et **ZIP** chiffré (AES‑256). |
| **12.5** Conformité aux normes françaises | Le prestataire devra attester la conformité aux exigences du **Code de la commande publique** (articles L. 2151‑1 à L. 2151‑5) et au **RGS** (décret n° 2018‑1127). |
| **12.6** Sécurité des sous‑traitants | Tout sous‑traitant devra être déclaré et soumis aux mêmes exigences de sécurité et de confidentialité. |

---

## 13. Critères de sélection des offres  

| Critère | Pondération | Mode d’évaluation | Barème |
|---------|-------------|-------------------|--------|
| **13.1** Qualité technique de la solution (conformité RGS, RGPD, architecture) | 40 % | Analyse documentaire + démonstration | 0 – 20 points |
| **13.2** Planning et capacité de mise en œuvre | 20 % | Vérification du planning proposé | 0 – 10 points |
| **13.3** Coût global (TTC) | 25 % | Comparaison prix unitaires | 0 – 12,5 points |
| **13.4** Références et expérience du prestataire | 15 % | CV, projets similaires (≥ 3) | 0 – 7,5 points |
| **Total** | 100 % | | 0 – 50 points |

**Notation** : La note maximale est 50 points. Le seuil de **candidature retenue** est fixé à **30 points**. En cas d’égalité, le critère **13.1** (qualité technique) sera décisif.

---

## 14. Annexes contractuelles  

| Annexe | Contenu |
|--------|---------|
| **A** Glossaire des acronymes (RGS, RGAA, RGI, PRA, SLA, P1‑P4) | |
| **B** Références normatives (ISO 27001, ISO 25010, RFC 7230, ANSSI‑GS‑001) | |
| **C** Modèle de **Déclaration de conformité RGS** à remplir par le candidat | |
| **D** Modèle de **Plan de Tests** (unitaires, charge, sécurité) | |
| **E** Modèle de **DPIA** (Data Protection Impact Assessment) | |
| **F** Modèle de **Rapport de recette** (acceptation, réserves) | |
| **G** Modèle de **Contrat de maintenance** (SLA, pénalités) | |

---

*Ce CCTP a été rédigé conformément aux exigences du Code de la commande publique et aux référentiels de l’État (RGS, SSI, RGPD, RGI, RGAA). Il constitue le socle contractuel du lot 1 du dossier de consultation des entreprises (DCE) pour le projet **agile‑env**.*