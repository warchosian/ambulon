# Cahier des Charges Fonctionnel (CCF) – **Projet : causalismp**  
*(Conformément à la norme NF EN 16271 :2013 – Management par la valeur)*  

---  

## 1. Présentation du projet  

| Élément | Description |
|---------|-------------|
| **Intitulé** | **causalismp** – Gestion des accidents du travail et des maladies professionnelles. |
| **Contexte** | Le projet s’inscrit dans la modernisation du système d’information RH d’une grande entreprise française. Il reprend les besoins exprimés par les services de prévention des risques professionnels (PPR) et les services de paie/gestion du personnel. Il doit remplacer l’ancienne version 1.5 / 1.6 et le composant « cerbere‑bouchon » par un nouveau module de saisie, de suivi, de reporting et de synchronisation avec les référentiels externes (ex. : Rehucit). |
| **Objectifs stratégiques** | 1️⃣ Améliorer la traçabilité et la qualité des dossiers d’accidents et de maladies professionnelles. <br>2️⃣ Centraliser les référentiels (grades, services, causes, etc.) afin de garantir la cohérence avec les autres applications RH. <br>3️⃣ Automatiser la synchronisation avec les web‑services externes pour réduire les interventions manuelles. <br>4️⃣ Fournir des indicateurs statistiques fiables pour l’analyse de la sinistralité. |
| **Périmètre fonctionnel** | **Inclus** : <br>• Saisie, édition, validation et clôture des dossiers d’accidents et de maladies professionnelles.<br>• Gestion des référentiels (grades, services, causes, zones, etc.).<br>• Export des dossiers (format OpenOffice).<br>• Reporting statistique (par service, gravité, année, etc.).<br>• Synchronisation avec les web‑services de référence (grade ↔ transcodage).<br>• Authentification / gestion de session (via le composant Cerbere).<br>• Gestion des droits d’accès (manager, développeur, rapporteur). <br>**Exclus** : <br>• Gestion des paies (hors périmètre).<br>• Gestion des contrats de travail. <br>• Modules de formation ou de prévention non liés aux dossiers d’incidents. |
| **Livrables attendus** | • Application web (WAR) déployable sur le serveur d’applications de l’entreprise.<br>• Scripts de migration de la base de données (SQL).<br>• Documentation d’installation, d’utilisation et de paramétrage.<br>• Jeux de tests fonctionnels (scénarios d’usage, scénarios d’erreur).<br>• Rapport de conformité à la présente CCF. |

---  

## 2. Analyse de la valeur  

| Fonction de service (FS) | Type | Description fonctionnelle | Critère de performance (CP) |
|--------------------------|------|---------------------------|----------------------------|
| **FS‑01** – Saisie d’un dossier d’accident | FP (Fonction Principale) | Permettre à un utilisateur habilité de créer un nouveau dossier d’accident du travail. | Temps de saisie ≤ 15 min ; Validation obligatoire de tous les champs obligatoires ; Enregistrement sans perte de données. |
| **FS‑02** – Saisie d’un dossier de maladie professionnelle | FP | Créer un dossier de maladie professionnelle avec les mêmes exigences que FS‑01. | Idem FS‑01. |
| **FS‑03** – Consultation / recherche de dossiers | FP | Rechercher des dossiers selon critères (service, période, gravité, etc.) et les afficher sous forme de tableau paginé. | Temps de réponse ≤ 3 s pour un jeu de 10 000 dossiers ; Pagination configurable (max 30 lignes). |
| **FS‑04** – Edition et mise à jour d’un dossier | FP | Modifier les informations d’un dossier déjà créé (avant clôture). | Historisation des modifications ; Validation de cohérence (ex. : date d’accident ≤ date de clôture). |
| **FS‑05** – Clôture d’un dossier | FP | Signaler la fin du traitement d’un dossier (saisie terminée). | Verrouillage du dossier ; Notification à l’utilisateur. |
| **FS‑06** – Gestion des référentiels (grades, services, causes, etc.) | FC (Fonction Contraint) | Maintenir à jour les tables de référence utilisées dans les dossiers. | Interface d’administration ; Mise à jour sans interruption du service. |
| **FS‑07** – Export de dossiers | FC | Générer un fichier exportable (OpenOffice) contenant le contenu d’un ou plusieurs dossiers. | Export complet, format conforme à la norme interne, génération ≤ 5 s. |
| **FS‑08** – Reporting statistique | FC | Produire des indicateurs agrégés (nombre d’accidents par service, gravité, évolution annuelle, etc.). | Tableaux et graphiques actualisés quotidiennement ; Export CSV possible. |
| **FS‑09** – Synchronisation des référentiels externes | FC | Mettre à jour les référentiels internes à partir des web‑services externes (ex. : grade Rehucit). | Taux de couverture ≥ 95 % des grades ; Processus de synchronisation automatisé (planifiable). |
| **FS‑10** – Gestion des droits d’accès | FC | Définir les rôles (manager, développeur, rapporteur) et leurs permissions. | Authentification via Cerbere ; Gestion granulaire des droits (lecture, écriture, export). |
| **FS‑11** – Gestion de session / ré‑authentification | FC | Garantir la sécurité des sessions utilisateur et permettre la déconnexion/re‑authentification. | Timeout session configurable ; Invalidation complète du contexte HTTP. |

> **Notes**  
> *Les fonctions FP sont indispensables à l’existence du produit (création de dossiers). Les fonctions FC sont imposées par le cadre réglementaire, les exigences de l’entreprise ou les besoins d’exploitation.*  

---  

## 3. Expression fonctionnelle du besoin  

### 3.1 Niveau système – Besoin global  

| ID | Besoin | Description (QUOI) | Critère d’appréciation | Niveau d’importance | Flexibilité |
|----|--------|--------------------|------------------------|--------------------|------------|
| **B‑01** | Saisie d’un dossier d’accident | L’application doit permettre la création d’un nouveau dossier d’accident du travail avec l’ensemble des champs requis (date, service, grade, cause, gravité, description, etc.). | Le dossier est enregistré dans la base de données et apparaît dans les listes de recherche. | Obligatoire | Fixe |
| **B‑02** | Saisie d’un dossier de maladie professionnelle | Idem B‑01 mais pour les maladies professionnelles. | Idem B‑01. | Obligatoire | Fixe |
| **B‑03** | Recherche de dossiers | L’utilisateur doit pouvoir rechercher des dossiers selon des critères multiples (service, période, type, gravité). | Résultat affiché en moins de 3 s, pagination fonctionnelle. | Obligatoire | Négociable (nombre de critères) |
| **B‑04** | Edition d’un dossier | L’utilisateur doit pouvoir modifier les informations d’un dossier non clôturé. | Historisation des modifications, validation de cohérence. | Obligatoire | Négociable (nombre de champs éditables) |
| **B‑05** | Clôture d’un dossier | L’utilisateur doit pouvoir clôturer un dossier, le rendant non modifiable. | Dossier marqué « clôturé », verrouillage technique. | Obligatoire | Fixe |
| **B‑06** | Gestion des référentiels | L’administrateur doit pouvoir créer, mettre à jour et supprimer les référentiels (grades, services, causes, etc.). | Modifications visibles immédiatement, aucune perte de cohérence. | Obligatoire | Négociable (type de référentiels) |
| **B‑07** | Export de dossiers | L’utilisateur doit pouvoir exporter un ou plusieurs dossiers au format OpenOffice. | Fichier exporté conforme, génération ≤ 5 s. | Souhaitable | Négociable (format d’export) |
| **B‑08** | Reporting statistique | L’application doit fournir des indicateurs de sinistralité (par service, gravité, évolution). | Tableaux/graphes actualisés quotidiennement, export CSV possible. | Souhaitable | Négociable (périodicité) |
| **B‑09** | Synchronisation externe | Le système doit synchroniser les référentiels (ex. : grades) avec les web‑services externes. | ≥ 95 % de correspondance, exécution planifiable. | Obligatoire | Négociable (fréquence) |
| **B‑10** | Gestion des droits | Définir les rôles (manager, développeur, rapporteur) et leurs droits d’accès. | Accès respectant la matrice de droits, auditabilité. | Obligatoire | Fixe |
| **B‑11** | Gestion de session | L’application doit assurer la sécurité des sessions et permettre la déconnexion/re‑authentification. | Timeout configurable, session invalidée à la déconnexion. | Obligatoire | Fixe |

### 3.2 Niveau sous‑système – Besoins partiels  

| ID | Sous‑système | Besoin | Description (QUOI) | Critère d’appréciation | Niveau d’importance |
|----|--------------|--------|--------------------|------------------------|--------------------|
| **B‑01‑01** | **Interface Web** | Formulaire de saisie d’accident | Formulaire complet, champs obligatoires, validation côté client. | Tous les champs marqués « obligatoire » refusent la soumission tant qu’ils sont vides. | Obligatoire |
| **B‑01‑02** | **Interface Web** | Formulaire de saisie de maladie | Idem B‑01‑01. | Idem. | Obligatoire |
| **B‑03‑01** | **Moteur de recherche** | Filtrage multi‑critères | Requête SQL générée dynamiquement selon les critères sélectionnés. | Temps de réponse ≤ 3 s. | Obligatoire |
| **B‑04‑01** | **Interface Web** | Page d’édition de dossier | Affichage du dossier en mode édition, bouton « Enregistrer ». | Historisation des changements. | Obligatoire |
| **B‑05‑01** | **Logique métier** | Service de clôture | Marquage du dossier comme clôturé, désactivation des actions d’édition. | Verrouillage technique (impossible d’éditer). | Obligatoire |
| **B‑06‑01** | **Gestion réf.** | Administration des référentiels | Écran de gestion (liste, création, modification, suppression). | Aucun impact sur les dossiers existants. | Obligatoire |
| **B‑07‑01** | **Export** | Générateur OpenOffice | Conversion du contenu du dossier en document ODT. | Fichier ouvert sans erreur dans OpenOffice. | Souhaitable |
| **B‑08‑01** | **Statistiques** | Générateur de rapports | Agrégation des données, création de graphiques (barres, courbes). | Rapports actualisés quotidiennement. | Souhaitable |
| **B‑09‑01** | **Synchronisation** | Service de synchronisation | Appel aux WS externes, mise à jour des référentiels internes. | Taux de mise à jour ≥ 95 %. | Obligatoire |
| **B‑10‑01** | **Sécurité** | Gestion des rôles | Table de correspondance rôle → droits (lecture, écriture, export). | Journalisation des accès. | Obligatoire |
| **B‑11‑01** | **Sécurité** | Gestion de session | Timeout, invalidation, protection CSRF. | Session détruite à la déconnexion. | Obligatoire |

### 3.3 Niveau composant – Besoins élémentaires  

> **Exemple** – le besoin **B‑01‑01** se décline en plusieurs exigences élémentaires (identifiées par **C‑xx**).  

| ID | Composant | Besoin élémentaire | Description (QUOI) | Critère d’appréciation | Niveau d’importance |
|----|-----------|-------------------|--------------------|------------------------|--------------------|
| **C‑01** | Formulaire *DossierAccident* | Champ *date d’accident* | L’utilisateur saisit la date du jour de l’accident. | Format `jj/mm/aaaa`, validation côté serveur. | Obligatoire |
| **C‑02** | Formulaire *DossierAccident* | Champ *service* | Sélection du service concerné (liste déroulante). | Valeur présente dans le référentiel « Service ». | Obligatoire |
| **C‑03** | Formulaire *DossierAccident* | Champ *grade* | Sélection du grade du salarié. | Valeur présente dans le référentiel « Grade ». | Obligatoire |
| **C‑04** | Formulaire *DossierAccident* | Champ *cause* | Sélection de la cause (environnement, humaine, matérielle…). | Valeur présente dans le référentiel « Causes ». | Obligatoire |
| **C‑05** | Formulaire *DossierAccident* | Champ *gravité* | Sélection de la gravité (léger, grave, très grave…). | Valeur présente dans le référentiel « Gravité ». | Obligatoire |
| **C‑06** | Formulaire *DossierAccident* | Champ *description* | Texte libre décrivant les circonstances. | Minimum 20 caractères, aucune balise HTML. | Obligatoire |
| **C‑07** | Service *DossierAccidentService* | Validation métier | Vérifier la cohérence des données (ex. : date ≤ date du jour). | Retour d’erreur explicite en cas d’incohérence. | Obligatoire |
| **C‑08** | DAO *DossierAccidentDAO* | Persistance | Enregistrer le dossier dans la table `DOSSIER_ACCIDENT`. | Insertion réussie, ID généré. | Obligatoire |
| **C‑09** | Page *RechercheDossiers* | Pagination | Afficher les résultats 30 lignes par page. | Navigation entre pages fonctionnelle. | Obligatoire |
| **C‑10** | Service *SynchronizeService* | Trigger de synchronisation | Lancer le processus de synchronisation à la demande ou planifié. | Retour du nombre de lignes insérées. | Obligatoire |
| **C‑11** | TagLib *StrutsOptionTag* | Rendu d’options HTML | Convertir les guillemets doubles en simples pour usage JavaScript. | Aucun caractère “ " ” restant dans le rendu. | Souhaitable |
| … | … | … | … | … | … |

> **Remarque** – La liste ci‑dessus n’est pas exhaustive ; elle illustre la façon dont chaque besoin global se décline en exigences élémentaires traçables (identifiant unique).  

---  

## 4. Caractérisation des besoins  

| Fonction (FS) | Critère d’appréciation | Niveau d’importance | Flexibilité | Contraintes |
|--------------|------------------------|---------------------|-------------|-------------|
| **FS‑01** (Saisie d’un dossier d’accident) | Enregistrement complet, validation obligatoire, temps de saisie ≤ 15 min | Obligatoire | Fixe | Conformité RGPD (données personnelles) |
| **FS‑02** (Saisie d’un dossier de maladie) | Idem FS‑01 | Obligatoire | Fixe | Conformité RGPD |
| **FS‑03** (Recherche) | Temps de réponse ≤ 3 s, pagination 30 lignes | Obligatoire | Négociable (nombre de critères) | Charge serveur < 70 % CPU |
| **FS‑04** (Edition) | Historisation, cohérence des données | Obligatoire | Négociable (champs éditables) | Aucun |
| **FS‑05** (Clôture) | Verrouillage, notification | Obligatoire | Fixe | Aucun |
| **FS‑06** (Gestion référentiels) | Disponibilité 24 / 7, mise à jour sans interruption | Obligatoire | Négociable (type de référentiel) | Conformité aux référentiels externes |
| **FS‑07** (Export) | Format ODT conforme, génération ≤ 5 s | Souhaitable | Négociable (format) | Aucun |
| **FS‑08** (Reporting) | Actualisation quotidienne, export CSV | Souhaitable | Négociable (périodicité) | Aucun |
| **FS‑09** (Synchronisation) | Taux de couverture ≥ 95 % | Obligatoire | Négociable (fréquence) | Disponibilité du WS externe |
| **FS‑10** (Gestion des droits) | Matrice de droits appliquée, journalisation | Obligatoire | Fixe | Conformité aux exigences de sécurité interne |
| **FS‑11** (Gestion de session) | Timeout configurable, invalidation totale | Obligatoire | Fixe | RGPD, exigences de sécurité (CSRF, XSS) |

---  

## 5. Validation de l’expression du besoin  

| Étape | Méthode | Participants | Artefacts de traçabilité |
|-------|---------|--------------|---------------------------|
| **5.1** | Ateliers de cadrage | Managers (DESSARTRE, BOULOY, …), Développeurs (GUITTET, MARCHAL, …), Rapporteurs | Compte‑rendu d’atelier, tableau de mapping besoins ↔ fonctions |
| **5.2** | Validation fonctionnelle (UAT) | Utilisateurs finaux (gestionnaires RH, agents de prévention) | Scénarios de test, rapports d’exécution |
| **5.3** | Revue de conformité (RGPD, sécurité) | Responsable sécurité, DPO | Checklist de conformité, audit de sécurité |
| **5.4** | Validation technique (sans prescription) | Architecte, Lead développeur | Matrice de traçabilité B‑xx ↔ C‑xx ↔ Code (ex. : classe `DossierAccidentService`) |
| **5.5** | Signature du CCF | Toutes les parties prenantes | Document CCF signé (version 1.0). |

---  

## 6. Scénarios d’usage  

| Scénario | Description | Acteurs | Étapes principales | Résultat attendu |
|----------|-------------|----------|-------------------|------------------|
| **S‑01** | **Création d’un dossier d’accident** | Gestionnaire RH | 1️⃣ Accès à l’écran « Nouvel Accident ».<br>2️⃣ Remplissage des champs obligatoires.<br>3️⃣ Validation du formulaire.<br>4️⃣ Confirmation de l’enregistrement. | Dossier enregistré, visible dans la liste, ID unique généré. |
| **S‑02** | **Recherche avancée** | Analyste sinistralité | 1️⃣ Accès à la page de recherche.<br>2️⃣ Sélection de plusieurs critères (service = « Production », période = 2022, gravité = « Grave »).<br>3️⃣ Lancement de la recherche.<br>4️⃣ Consultation du tableau paginé. | Tableau affichant les dossiers correspondants, temps de réponse ≤ 3 s. |
| **S‑03** | **Edition d’un dossier avant clôture** | Gestionnaire RH | 1️⃣ Ouverture du dossier en mode édition.<br>2️⃣ Modification du champ « description ».<br>3️⃣ Enregistrement.<br>4️⃣ Vérification de l’historique. | Modification sauvegardée, trace horodatée dans l’historique. |
| **S‑04** | **Clôture d’un dossier** | Manager | 1️⃣ Sélection du bouton « Clôturer ».<br>2️⃣ Confirmation de la clôture.<br>3️⃣ Le système bloque toute modification ultérieure. | Dossier marqué « Clôturé », verrouillé, notification au créateur. |
| **S‑05** | **Export d’un dossier** | Rapporteur | 1️⃣ Sélection du dossier.<br>2️⃣ Choix du format ODT.<br>3️⃣ Génération du fichier.<br>4️⃣ Téléchargement. | Fichier ODT contenant toutes les données du dossier, ouvert sans erreur. |
| **S‑06** | **Synchronisation des grades** | Administrateur | 1️⃣ Lancement du job « Synchroniser grades ».<br>2️⃣ Appel aux WS externes.<br>3️⃣ Mise à jour des tables `GRADE` et `TRANSCODAGE_GRADE`. | ≥ 95 % des grades mis à jour, log de synchronisation disponible. |
| **S‑07** | **Gestion des droits** | Administrateur sécurité | 1️⃣ Accès à l’écran d’administration des rôles.<br>2️⃣ Attribution du rôle « Rapporteur » à un utilisateur.<br>3️⃣ Sauvegarde.<br>4️⃣ Test d’accès (lecture uniquement). | L’utilisateur ne peut que consulter les rapports, aucune modification possible. |
| **S‑08** | **Déconnexion / ré‑authentification** | Tout utilisateur | 1️⃣ Clic sur le lien « Déconnexion ».<br>2️⃣ Session invalidée.<br>3️⃣ Redirection vers la page de connexion.<br>4️⃣ Nouvelle authentification. | Session détruite, aucun résidu de données en mémoire. |

---  

## 7. Parties prenantes (Stakeholders)  

| Partie prenante | Rôle | Besoins spécifiques | Impact sur la valeur |
|------------------|------|--------------------|----------------------|
| **Managers** (DESSARTRE, BOULOY, …) | Décideurs, validation des processus | Visibilité des indicateurs de sinistralité, capacité à clôturer les dossiers. | Garantissent l’atteinte des objectifs de réduction des accidents. |
| **Développeurs** (GUITTET, MARCHAL, …) | Réalisation technique, maintenance | Documentation claire, exigences traçables, environnement de test. | Assurent la qualité et la maintenabilité du produit. |
| **Rapporteurs** (CURBET, LOUVARD, …) | Production de rapports réglementaires | Accès à l’export et aux statistiques, traçabilité des accès. | Contribuent à la conformité légale et à la communication interne. |
| **Utilisateurs finaux** (agents de prévention, gestionnaires RH) | Saisie et suivi des dossiers | Interface simple, validation de données, assistance (aide en ligne). | Satisfaction utilisateur, réduction du temps de traitement. |
| **Responsable Sécurité / DPO** | Conformité RGPD, sécurité des données | Gestion des droits, journalisation, anonymisation éventuelle. | Réduction des risques juridiques et réputationnels. |
| **Équipe d’infrastructure** | Hébergement, base de données | Disponibilité du datasource JNDI, performances serveur. | Disponibilité du service 24 / 7. |
| **Fournisseur WS externe** (ex. : Rehucit) | Fourniture des référentiels grades | Disponibilité et fiabilité du service, format des réponses. | Qualité de la synchronisation, fiabilité des données de référence. |

---  

## 8. Contraintes et environnement  

| Type | Description |
|------|-------------|
| **Organisationnelles** | - Déploiement sur les serveurs d’applications de l’entreprise (Tomcat / JBoss). <br>- Respect du processus de mise en production (CI / CD via GitLab CI). |
| **Réglementaires** | - Conformité RGPD : anonymisation, droit d’accès, journalisation. <br>- Respect des exigences de la convention collective du secteur (déclaration des accidents). |
| **Techniques** | - Base de données Oracle, datasource JNDI `java:comp/env/jdbc/userDScausalis`. <br>- Persistence gérée par Castor JDO (mapping XML). <br>- Application web Struts 1, JSP, TagLib personnalisés. <br>- Dépendance au JAR `StubWS.jar` (Web Services). |
| **Temporelles** | - Livraison initiale prévue **12 semaines** après la signature du CCF. <br>- Phase de test fonctionnel **4 semaines**. |
| **Budgétaires** | - Budget total alloué **250 k €** (développement, tests, documentation, formation). |
| **Performance** | - Temps de réponse ≤ 3 s pour les recherches sur 10 000 dossiers. <br>- Export ≤ 5 s. |
| **Sécurité** | - Authentification via le composant **Cerbere**. <br>- Gestion de session, protection CSRF, XSS. |
| **Qualité** | - Couverture de tests unitaires ≥ 80 %. <br>- Passage du **quality‑gate** SonarQube obligatoire avant mise en production. |

---  

## 9. Critères de sélection et pondération (pour l’appel d’offres)  

| Critère | Sous‑critère | Pondération | Modalité de notation |
|---------|--------------|------------|----------------------|
| **C‑01 – Fonctionnalités** | Respect de l’ensemble des besoins (B‑01 à B‑11) | 30 % | 0 – 10 pts (10 pts = conformité totale). |
| **C‑02 – Qualité du code** | Respect des bonnes pratiques (naming, modularité, tests unitaires) | 20 % | 0 – 10 pts (based on SonarQube score). |
| **C‑03 – Architecture** | Séparation des couches, évolutivité, absence de prescriptions technologiques (conformité NF EN 16271) | 15 % | 0 – 10 pts. |
| **C‑04 – Sécurité / RGPD** | Gestion des droits, journalisation, anonymisation | 15 % | 0 – 10 pts. |
| **C‑05 – Planning** | Respect du planning proposé (12 semaines) | 10 % | 0 – 10 pts (retard = pénalité). |
| **C‑06 – Coût** | Prix total TTC | 10 % | 0 – 10 pts (meilleur prix = 10 pts). |
| **Total** |  | **100 %** |  |

> **Note** : La pondération respecte les exigences de la norme NF EN 16271 (mise en avant de la valeur fonctionnelle avant les critères de prix).  

---  

## 10. Glossaire et acronymes  

| Acronyme / Terme | Définition |
|------------------|------------|
| **ACCIDENT** | Accident du travail déclaré. |
| **MALADIE** | Maladie professionnelle déclarée. |
| **PPR** | Programme de prévention des risques. |
| **RGPD** | Règlement général sur la protection des données (UE). |
| **WS** | Web Service (SOAP/REST) externe utilisé pour la synchronisation. |
| **JDO** | Java Data Objects – API de persistance (utilisée via Castor). |
| **DAO** | Data Access Object – couche d’accès aux données. |
| **UAT** | User Acceptance Test (tests d’acceptation utilisateur). |
| **CI/CD** | Continuous Integration / Continuous Delivery (GitLab CI). |
| **SonarQube** | Plateforme d’analyse de la qualité du code. |
| **Cerbere** | Composant interne de gestion d’authentification et de session. |
| **StubWS.jar** | Bibliothèque contenant les stubs des web‑services externes. |
| **ODT** | OpenDocument Text – format de fichier OpenOffice/LibreOffice. |
| **FPS** | Functional Performance Specification (spécification fonctionnelle de performance). |
| **FN‑EN‑16271** | Norme française de management par la valeur (cahier des charges fonctionnel). |
| **FP** | Fonction Principale (obligatoire à l’existence du produit). |
| **FC** | Fonction Contraint (imposée par le contexte). |
| **B‑xx** | Identifiant d’un besoin (global ou partiel). |
| **C‑xx** | Identifiant d’un besoin élémentaire (composant). |
| **PO** | Product Owner (responsable de la priorisation des besoins). |

---  

## 11. Traçabilité (exemple)  

```
B‑01  →  FS‑01  →  C‑01, C‑02, C‑03, C‑04, C‑05, C‑06, C‑07, C‑08
B‑03  →  FS‑03  →  C‑09
B‑09  →  FS‑09  →  C‑10
…
```

Chaque ligne du tableau de traçabilité lie le **besoin global** à la **fonction de service** correspondante, puis aux **exigences élémentaires** implémentées dans le code (ex. : classe `DossierAccidentService`, formulaire `DossierAccidentForm`, etc.). Cette matrice sera complétée dans le **cahier de suivi** du projet.  

---  

## 12. Annexes  

1. **Modèle de données** (schéma ER) – fourni séparément.  
2. **Matrice de droits** (rôles ↔ actions) – fournie par le service sécurité.  
3. **Calendrier prévisionnel** – Gantt détaillé (développement, tests, recette, mise en production).  
4. **Plan de formation** – sessions d’utilisation pour les gestionnaires RH.  

---  

*Ce CCF a été rédigé en conformité avec la norme NF EN 16271 :2013 et constitue le document contractuel de référence pour la réalisation du projet **causalismp**.*  