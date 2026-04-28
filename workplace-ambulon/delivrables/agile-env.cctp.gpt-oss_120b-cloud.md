# Cahier des Clauses Techniques Particulières (CCTP)  
**Projet : agile‑env** – Mise à disposition d’un environnement conteneurisé pour le développement et l’exploitation d’une application PHP 7.3 / PostgreSQL 11  

> **Références réglementaires appliquées** : Code de la commande publique, RGS (niveau basique), RGPD, Référentiel SSI de l’ANSSI, RGI, RGAA, ISO 9001, ISO 25010.  

---

## 1. Objet du marché  

| N° | Description |
|---|-------------|
| 1.1 | Le présent marché a pour objet la **conception, la réalisation, la livraison et le support** d’un environnement de développement et de pré‑production sous forme de conteneurs Docker, incluant : <br>• Une image Docker **PHP 7.3‑Apache‑buster** pré‑configurée (composer, extensions pdo, pdo_pgsql, intl). <br>• Une image Docker **PostgreSQL 11‑alpine** avec scripts d’initialisation. <br>• Un fichier **docker‑compose.dev.yml** permettant le déploiement automatisé des deux services ainsi que la configuration réseau. |
| 1.2 | Le marché comprend également : <br>• La rédaction de la documentation d’installation, d’exploitation et d’administration. <br>• La formation des équipes techniques du maître d’ouvrage. <br>• Le support technique pendant la période de garantie (minimum 12 mois). |
| 1.3 | Le CCTP décrit les exigences techniques et fonctionnelles. Le **Cahier des Clauses Financières (CCF)**, fourni séparément, décrit les exigences fonctionnelles et les critères de prix. |

---

## 2. Description technique détaillée  

| Niveau | Exigence |
|--------|----------|
| **2.1 Obligations minimales (impératives)** | • L’ensemble des images Docker doit être **conforme aux spécifications du Dockerfile‑app** et du **Dockerfile‑db** (voir Annexes A & B). <br>• Le conteneur PHP doit être **compatible avec PHP 7.3** et contenir les extensions **pdo, pdo_pgsql, intl**. <br>• Le conteneur PostgreSQL doit être basé sur **postgres:11‑alpine** et exécuter les scripts d’initialisation fournis dans le répertoire `initdb/`. |
| **2.2 Obligations souhaitées (souhaitables, notées)** | • Utilisation d’un **proxy d’entreprise** configurable via les variables d’environnement `http_proxy` et `https_proxy`. <br>• Installation de **yarn** et **npm** (facultatif) pour la gestion de dépendances front‑end. |
| **2.3 Obligations optionnelles (facultatives)** | • Fourniture d’une image **Node 16** en tant que service additionnel pour le build front‑end. <br>• Mise à disposition d’un **registry privé** hébergé sur le Cloud souverain (ex. OVHcloud). |

---

## 3. Architecture et conception  

| Point | Exigence |
|-------|----------|
| **3.1** | L’architecture doit être **micro‑services** : un service *app* (PHP/Apache) et un service *db* (PostgreSQL). |
| **3.2** | Les images Docker doivent être construites **déclarativement** via les Dockerfiles fournis, sans étape interactive. |
| **3.3** | Respect des standards : <br>• **Docker 20.10+**, <br>• **Compose 1.29+**, <br>• **ISO / IEC 62443‑4‑2** (sécurité des composants). |
| **3.4** | Interopérabilité : les images doivent être **conformes au Référentiel Général d’Interopérabilité (RGI)**, notamment le respect du format **OCI** et la disponibilité d’un **manifest** compatible Kubernetes (facultatif). |
| **3.5** | Frameworks autorisés : aucun framework propriétaire n’est autorisé ; seules les bibliothèques **open‑source** listées dans le fichier `composer.json` (fourni en annexe) peuvent être utilisées. |

---

## 4. Exigences de sécurité (RGS, ANSSI)  

| N° | Exigence de sécurité |
|----|----------------------|
| **4.1 Niveau de sécurité** | Le dispositif doit satisfaire le **RGS niveau basique** (authentification forte, chiffrement TLS 1.2 minimum). |
| **4.2 Authentification & contrôle d’accès** | • Les accès aux services Docker (API, registry) doivent être protégés par **authentification à deux facteurs (2FA)**. <br>• Les conteneurs doivent être exécutés avec l’utilisateur **www‑data** (UID 33) et non en root. |
| **4.3 Chiffrement** | • Toutes les communications entre *app* et *db* doivent être chiffrées via **TLS 1.2** (certificats auto‑signés ou fournis par le maître d’ouvrage). <br>• Les volumes de données persistant (PostgreSQL) doivent être chiffrés au repos (ex. LUKS). |
| **4.4 Traçabilité** | Le système doit générer des **journaux** conformes au **Référentiel SSI** : <br>• `access.log` Apache, <br>• `postgresql.log`, <br>• `docker daemon log`. <br>Les logs doivent être centralisés via **syslog** et conservés **minimum 12 mois**. |
| **4.5 RGPD** | Le prestataire devra garantir la conformité au **RGPD** pour toute donnée à caractère personnel éventuellement stockée dans la base : <br>• Mise en place d’un **DPIA** (Document d’Analyse d’Impact) avant la mise en production. <br>• Anonymisation ou pseudonymisation des champs sensibles si nécessaire. |
| **4.6 Tests de sécurité** | Avant la recette, le prestataire devra réaliser : <br>• Un **scan de vulnérabilité** (OWASP Dependency‑Check, Trivy) avec un taux de criticité maximal **0 CVE critique** et **≤ 5 CVE hautes**. <br>• Un **test d’intrusion** (pentest) externalisé, rapport à remettre au maître d’ouvrage. |

---

## 5. Interfaces et intégrations  

| Interface | Description | Protocoles / Formats |
|----------|-------------|----------------------|
| **5.1** | Communication *app* ↔ *db* | PostgreSQL 11, **TLS**, format SQL |
| **5.2** | Proxy d’entreprise (variables `http_proxy`/`https_proxy`) | HTTP/HTTPS via le proxy interne du ministère |
| **5.3** | Export des logs vers le SIEM du ministère | Syslog (RFC 5424) |
| **5.4** | Fichiers de configuration (`.env`, `config_CAS.php`, `param.ini`) | Texte UTF‑8, encodage **LF** |

*Modalités de recette* : chaque interface sera testée à l’aide de scripts d’intégration (Annexe C). Le prestataire devra fournir les jeux de tests automatisés.

---

## 6. Environnements et infrastructure  

| Environnement | Exigence |
|---------------|----------|
| **6.1 Développement** | Docker‑Compose dev doit être exécutable sur **Linux Ubuntu 20.04 LTS** ou **Windows 10** (WSL2). |
| **6.2 Recette** | Un serveur dédié **VM** (CPU 4, RAM 8 Go, disque 100 Go) hébergé dans le datacenter du ministère, réseau isolé, accès via VPN. |
| **6.3 Production** | Hébergement **on‑premise** dans le data‑center du ministère, **souveraineté** des données (pas de cloud public). |
| **6.4 Haute disponibilité** | Le service PostgreSQL doit être configuré en **replication streaming** (master‑slave) avec un **SLA disponibilité ≥ 99,9 %**. |
| **6.5 PRA/PCA** | Le prestataire devra fournir un **Plan de Reprise d’Activité (PRA)** documenté, testable en moins de **4 heures**. |
| **6.6 Réseau** | Les conteneurs doivent être placés dans un réseau Docker **isolé (bridge)**, avec des règles de pare‑feu limitant les ports à 80/443 (HTTP/HTTPS) et 5432 (PostgreSQL). |

---

## 7. Qualité et conformité  

| Critère | Niveau requis |
|---------|---------------|
| **7.1 Référentiel qualité** | Conformité ISO 9001 : 2015 et ISO 25010 (maintenabilité, sécurité, performance). |
| **7.2 Maintenabilité** | Le code source des Dockerfiles, scripts d’init et fichiers de configuration doit être **documenté** (commentaires) et versionné **Git**. |
| **7.3 Performance** | • Temps de réponse HTTP du conteneur *app* ≤ 200 ms (95 % des requêtes) sous charge de 100 RPS. <br>• Temps de connexion à la base ≤ 50 ms. |
| **7.4 Accessibilité** | Si l’application web exposée doit être accessible aux usagers publics, le respect du **RGAA 4.0** sera vérifié (niveau AA). |
| **7.5 Tests unitaires** | Couverture du code de configuration ≥ 80 % (ex. scripts Bash, Dockerfile). |

---

## 8. Documentation et formation  

| Livrable | Format | Contenu requis |
|----------|--------|----------------|
| **8.1 Manuel d’installation** | PDF + Markdown | Procédure pas à pas pour le build des images, le lancement du `docker‑compose.dev.yml`, configuration du proxy, mise en place du TLS. |
| **8.2 Manuel d’exploitation** | PDF + Markdown | Gestion des logs, mise à jour des images, sauvegarde de la base, restauration, PRA. |
| **8.3 Guide développeur** | Markdown (Git) | Variables d’environnement, points d’entrée de l’application, conventions de code. |
| **8.4 Formation** | 2 sessions de 4 h (présentiel ou visioconférence) | • Installation et configuration <br>• Gestion du cycle de vie des conteneurs <br>• Sécurité et conformité RGS. |

---

## 9. Tests et recette  

| Type de test | Objectif | Critère d’acceptation |
|--------------|----------|----------------------|
| **9.1 Tests unitaires** | Vérifier le bon fonctionnement des scripts d’initialisation et des Dockerfiles | ✅ 100 % des tests passent, couverture ≥ 80 %. |
| **9.2 Tests d’intégration** | Valider les échanges *app* ↔ *db* et la bonne prise en compte du proxy | ✅ Aucun échec, temps de réponse ≤ 200 ms. |
| **9.3 Tests de charge** | Simuler 200 RPS pendant 30 min | ✅ Aucun dépassement du seuil CPU 80 % ou mémoire 75 %. |
| **9.4 Tests de sécurité** | Scan de vulnérabilités & pentest | ✅ ≤ 5 CVE hautes, 0 CVE critiques. |
| **9.5 Recette fonctionnelle** | Validation par le maître d’ouvrage | ✅ Tous les points de la check‑list (Annexe D) validés sans réserve. |

*Gestion des anomalies* : tout défaut constaté devra être corrigé dans un délai **5 jours ouvrés** (défaut de moyen) ou **2 jours ouvrés** (défaut de résultat) suivant la gravité.

---

## 10. Maintenance et support  

| Niveau | Engagement | Délai |
|--------|------------|-------|
| **10.1 Support de niveau 1** (hotline) | Disponibilité **7 j/24 h** (hors jours fériés) | Réponse ≤ 30 min, résolution ≤ 4 h. |
| **10.2 Support de niveau 2** (intervention technique) | Intervention sur site ou à distance selon criticité | GTR ≤ 2 h (critique), ≤ 8 h (haute), ≤ 24 h (moyenne). |
| **10.3 Garantie** | **12 mois** à compter de la date de réception définitive. | Tous les correctifs de sécurité inclus. |
| **10.4 Maintenance évolutive** | Optionnelle, à négocier séparément. | – |

**SLA** : disponibilité globale de l’environnement ≥ 99,9 % sur la période de garantie.  

---

## 11. Livrables et planning  

| N° | Livrable | Format | Date de remise (estimation) | Modalité de réception |
|---|-----------|--------|------------------------------|------------------------|
| **11.1** | Dockerfile‑app (source) | texte (Dockerfile) | S‑4 semaines | dépôt Git privé du maître d’ouvrage |
| **11.2** | Dockerfile‑db (source) | texte (Dockerfile) | S‑4 semaines | même dépôt |
| **11.3** | docker‑compose.dev.yml | YAML | S‑4 semaines | même dépôt |
| **11.4** | Scripts d’initialisation (SQL, restore.sh) | texte | S‑4 semaines | même dépôt |
| **11.5** | Documentation (install, exploitation, développeur) | PDF + Markdown | S‑3 semaines | livrable numérique |
| **11.6** | Rapport de tests (unitaires, charge, sécurité) | PDF | S‑2 semaines | livrable numérique |
| **11.7** | Plan de Reprise d’Activité (PRA) | PDF | S‑2 semaines | livrable numérique |
| **11.8** | Attestation de conformité RGS & RGPD | PDF signé | S‑1 semaine | livrable numérique |
| **11.9** | Formation (supports PPT, enregistrements) | PDF + MP4 | S‑1 semaine | livrable numérique |

**Planning indicatif**  

| Phase | Durée | Date de début (est.) | Date de fin (est.) |
|-------|-------|----------------------|--------------------|
| 1️⃣ Lancement du marché | 2 semaines | 01/05/2026 | 14/05/2026 |
| 2️⃣ Développement & Dockerisation | 4 semaines | 15/05/2026 | 11/06/2026 |
| 3️⃣ Tests & validation | 2 semaines | 12/06/2026 | 25/06/2026 |
| 4️⃣ Recette fonctionnelle | 1 semaine | 26/06/2026 | 02/07/2026 |
| 5️⃣ Livraison définitive | 1 semaine | 03/07/2026 | 09/07/2026 |

**Pénalités de retard** : 0,1 % du montant total du marché par jour de retard au-delà du délai de **09/07/2026**, plafonné à 5 % du montant total.

---

## 12. Contraintes légales et réglementaires  

| Aspect | Exigence |
|--------|----------|
| **12.1 Propriété intellectuelle** | Le prestataire cède **l’intégralité des droits patrimoniaux** sur les Dockerfiles, scripts, documentation et livrables au maître d’ouvrage, sans restriction territoriale. |
| **12.2 Licences** | Tous les composants open‑source doivent être compatibles avec **licence GPL‑v3**, **MIT** ou **Apache‑2.0**. Le prestataire devra fournir la liste exhaustive des licences utilisées (Annexe E). |
| **12.3 Protection des données** | Conformité RGPD : mise en place d’un registre des traitements, chiffrement des données personnelles, notification de toute violation dans les 72 h. |
| **12.4 Archivage** | Les livrables (code, documentation, rapports) devront être archivés **au minimum 10 ans** sur le serveur d’archivage du ministère, format PDF/A‑2 ou équivalent. |
| **12.5 Sécurité** | Respect du **Référentiel Général de Sécurité (RGS) – Niveau Basique** et des bonnes pratiques de l’**ANSSI** (mise à jour des images Docker, gestion des secrets via Vault ou équivalent). |

---

## 13. Critères de sélection des offres  

| Critère | Pondération | Modalité d’évaluation |
|---------|-------------|------------------------|
| **13.1 Qualité technique du livrable** (conformité aux exigences 2‑4) | **40 %** | Grille d’évaluation (Annexe F) : 0‑5 points par exigence. |
| **13.2 Méthodologie et planning** | **20 %** | Analyse de la cohérence du planning proposé et de la capacité à respecter les jalons. |
| **13.3 Expérience du prestataire** (références similaires) | **15 %** | Vérification de 3 références sur projets publics (ANSSI, ministère). |
| **13.4 Coût** | **15 %** | Prix global hors taxes, comparatif au budget prévisionnel. |
| **13.5 Garanties de maintenance & support** | **10 %** | Niveau de SLA proposé, durée de garantie, modalités d’évolution. |

**Barème** : chaque critère sera noté sur 20 points, la note finale sera la moyenne pondérée. L’offre la mieux notée sera retenue, sous réserve de conformité juridique.

---

## 14. Annexes contractuelles  

| Annexe | Description |
|--------|-------------|
| **Annexe A** | Dockerfile‑app (version 1.0) |
| **Annexe B** | Dockerfile‑db (version 1.0) |
| **Annexe C** | Scripts de tests d’intégration (bash) |
| **Annexe D** | Check‑list de recette fonctionnelle |
| **Annexe E** | Inventaire des licences open‑source |
| **Annexe F** | Grille d’évaluation technique (notation 0‑5) |
| **Annexe G** | Glossaire des acronymes (RGS, RGI, RGAA, etc.) |
| **Annexe H** | Références normatives (ISO 9001, ISO 25010, IEC 62443, etc.) |

---  

*Fait à Paris, le 28 avril 2026*  

*Le présent CCTP constitue une partie intégrante du Dossier de Consultation des Entreprises (DCE) et devra être respecté intégralement par le titulaire du marché.*