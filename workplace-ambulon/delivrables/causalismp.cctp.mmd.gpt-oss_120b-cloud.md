# Cahier des Clauses Techniques Particulières (CCTP)  
## Projet **causalismp** – Gestion des accidents du travail et des maladies professionnelles  

*Version 1.0 – 28 avril 2026*  

---

## 1. Objet du marché  

| N° | Description |
|---|-------------|
| 1.1 | Le présent marché a pour objet la **fourniture, l’installation, la mise en service et le maintien** d’une solution logicielle de gestion des accidents du travail et des maladies professionnelles (ci‑après “la Solution”). |
| 1.2 | La Solution devra couvrir l’ensemble des processus fonctionnels détaillés dans le Cahier des Clauses Fonctionnelles (CCF) fourni séparément. |
| 1.3 | Le périmètre technique comprend : <br>• Le développement et la personnalisation du code source Java (Struts 1, Castor JDO). <br>• L’intégration à la base de données Oracle existante. <br>• Le packaging (Maven multi‑modules, génération des artefacts WAR, ZIP de sources et scripts). <br>• Le déploiement sur l’infrastructure du maître‑d’ouvrage (MOA) et le transfert de compétences. |

---

## 2. Description technique détaillée  

### 2.1 Spécifications fonctionnelles minimales (extraits du CCF)  

| Fonction | Description | Niveau d’obligation |
|----------|-------------|--------------------|
| Gestion des dossiers accident | Création, modification, validation, archivage des dossiers d’accident professionnel. | Obligation de résultat – le système doit garantir **une traçabilité à 100 %** de chaque modification (horodatage, utilisateur). |
| Gestion des dossiers maladie | Même niveau de fonctionnalité que ci‑dessus pour les maladies professionnelles. | Obligation de résultat. |
| Statistiques & reporting | Tableaux de bord, export au format OpenOffice et CSV, calcul de taux d’incidence. | Obligation de moyen – le prestataire devra mettre en œuvre les indicateurs requis. |
| Gestion des référentiels (grades, services, statuts, etc.) | Interface de consultation et de mise à jour via les services `ReferenceService<T>`. | Obligation de résultat – les référentiels doivent être **synchronisés quotidiennement** avec les web‑services externes (ex. Rehucit). |
| Authentification / autorisation | Authentification unique via le composant **Cerbere**, contrôle d’accès basé sur les profils (admin, utilisateur, lecteur). | Obligation de résultat – le système doit **refuser tout accès non autorisé**. |
| Conformité RGPD | Gestion du consentement, droit d’accès, droit à l’oubli, conservation minimale des données à caractère personnel. | Obligation de résultat – mise en œuvre du registre des traitements. |

### 2.2 Spécifications techniques obligatoires  

| Élément | Exigence | Justification |
|---------|----------|----------------|
| **Langage** | Java ≥ 1.8, compatible avec Struts 1.x et Castor JDO. | Conformité au code existant. |
| **Framework web** | Struts 1 (Action, ActionForm, TagLib). | Utilisé dans le socle actuel. |
| **Persistance** | Castor JDO avec mapping XML (`database.xml`, `mapping.xml`). | Respect du modèle de données actuel. |
| **Base de données** | Oracle 12c ou supérieur, datasource JNDI `java:comp/env/jdbc/userDScausalis`. | Cohérence avec les scripts fournis. |
| **Gestion de configuration** | Maven 3.8+, modules : `causalismp-database`, `causalismp-deployment`, `causalismp-doc`, `causalismp-web`. | Garantie d’un build reproductible. |
| **Packaging** | WAR pour le module `causalismp-web` ; ZIP (scripts DB, sources, documentation) via les descripteurs *assembly*. | Conformité aux livrables attendus. |
| **Journalisation** | Log4j 2 ≥ 2.17, fichier `log4j.xml` fourni. | Traçabilité des événements. |
| **Sécurité transport** | TLS 1.2 minimum, certificat serveur fourni par le MOA. | Conformité au RGS (niveau basique). |
| **Encodage** | UTF‑8 pour toutes les ressources texte et les bases de données. | Interopérabilité et conformité RGAA. |
| **Tests automatisés** | JUnit 5, couverture de code ≥ 80 % (SonarQube). | Qualité logicielle. |

### 2.3 Spécifications techniques souhaitées  

| Élément | Description | Niveau de priorité |
|---------|-------------|--------------------|
| Migration vers Struts 2 ou Spring MVC. | Amélioration de la maintenabilité. | Souhaitable (note : non contractuel). |
| Passage à JPA/Hibernate. | Simplification du mapping. | Souhaitable. |
| Déploiement sur environnement cloud souverain (OVH Public Cloud). | Flexibilité d’infrastructure. | Souhaitable. |

### 2.4 Spécifications techniques optionnelles  

| Élément | Description |
|---------|-------------|
| Mise à disposition d’une API RESTful d’accès aux référentiels. |
| Intégration d’un moteur de recherche full‑text (ElasticSearch). |

---

## 3. Architecture et conception  

| Niveau | Description |
|--------|-------------|
| **3.1** | **Architecture en couches** : <br>• **Web** (Struts 1, JSP) <br>• **Service** (interfaces `*Service`, implémentations, logique métier) <br>• **DAO** (Castor JDO, `*Dao`) <br>• **Modèle** (beans POJO, `TablesReferences`). |
| **3.2** | **Modularité Maven** – chaque module possède son propre `pom.xml` et ses dépendances. |
| **3.3** | **Normes** – respect des standards ISO 27001 (sécurité de l’information), ISO 25010 (qualité du logiciel) et W3C (HTML 4.01 strict, CSS 2.1). |
| **3.4** | **Interopérabilité** – les services externes sont appelés via SOAP (WS Client) et les échanges utilisent le format XML défini dans `WSConstants`. |
| **3.5** | **Patrons autorisés** – DAO, Service, Singleton (`MTPoolConnexion`), Factory (`WSClient*`). |
| **3.6** | **Contraintes** – aucune dépendance externe non répertoriée, le WAR doit être déployable sur un serveur d’applications Java EE 7 (ex. WildFly, Tomcat 9). |

---

## 4. Exigences de sécurité (RGS, ANSSI)  

| Référence | Exigence | Niveau | Modalité de vérification |
|-----------|----------|--------|--------------------------|
| **4.1** | Authentification forte via le composant **Cerbere** (login/password, verrous après 5 tentatives). | **Obligation de résultat** | Test d’intrusion (pentest) – aucune authentification contournable. |
| **4.2** | Contrôle d’accès granulaire (profil admin, lecteur, contributeur). | **Obligation de résultat** | Revue des filtres Struts (`ActionServlet`) et des règles `struts-config.xml`. |
| **4.3** | Chiffrement des données en transit – TLS 1.2 minimum, certificats X.509. | **Obligation de résultat** | Analyse des traces réseau (Wireshark) – aucun flux HTTP en clair. |
| **4.4** | Chiffrement des données sensibles au repos (colonnes `DATENASISS`, `NUMERO_SECURITE_SOCIAL`). Utilisation d’AES‑256 via Transparent Data Encryption (Oracle). | **Obligation de moyen** | Vérification de la configuration TDE sur le SGBD. |
| **4.5** | Journalisation de toutes les actions critiques (création/modification de dossiers, accès aux référentiels). | **Obligation de résultat** | Vérification du fichier `log4j.xml` et des logs générés. |
| **4.6** | Conservation des journaux de sécurité pendant **180 jours**. | **Obligation de moyen** | Vérification du mécanisme de rotation des logs. |
| **4.7** | Conformité RGPD – registre des traitements, droit d’accès, droit à l’oubli, notification des violations. | **Obligation de résultat** | Audit RGPD – production du registre et des procédures. |
| **4.8** | Tests de vulnérabilité (OWASP Top 10) avant chaque mise en production. | **Obligation de moyen** | Rapport de scan (Nessus, ZAP). |

---

## 5. Interfaces et intégrations  

| Interface | Protocole | Format | Direction | Description |
|----------|-----------|--------|------------|-------------|
| **WS Grade** | SOAP 1.2 | XML (XSD `Grade.xsd`) | Entrante (synchronisation) | Le service `TranscodageGradeService` récupère les grades depuis le système Rehucit. |
| **WS Service** | SOAP 1.2 | XML | Entrante | Récupération des services (structures organisationnelles). |
| **Base de données** | JDBC (JNDI) | SQL | Bidirectionnelle | Accès via Castor JDO. |
| **Export OpenOffice** | HTTP (GET) | ODS | Sortante | Génération de rapports via `FichierOpenOffice`. |
| **Portail métier** (optionnel) | REST 2.0 | JSON | Sortante | API d’exposition des référentiels (option). |

*Toutes les interfaces devront être décrites dans un cahier d’interface détaillé (Annexe A).*

---

## 6. Environnements et infrastructure  

| Environnement | Description | Configuration minimale |
|---------------|-------------|------------------------|
| **Développement** | Serveur local du prestataire. | JDK 1.8, Maven 3.8, Oracle XE, Tomcat 9. |
| **Tests fonctionnels** | Plateforme de recette du MOA. | Identique à la production (Oracle 12c, TLS 1.2). |
| **Pré‑production** | Clone de la production, usage pour les tests de charge. | CPU 8 cœurs, RAM 16 GiB, stockage 200 GiB. |
| **Production** | Hébergement on‑premise dans le datacenter du MOA. | Serveur d’applications Java EE 7, Oracle 12c RAC, réseau segmenté, HA (cluster 2 nœuds). |
| **Contraintes d’hébergement** | **Souveraineté des données** – les données doivent rester sur le territoire français. | Utilisation d’un serveur situé en France métropolitaine. |
| **Haute disponibilité** | Architecture en **cluster** avec bascule automatique (PRA/PCA). | Taux de disponibilité **≥ 99,9 %** sur l’année. |
| **Réseau** | Pare‑feu perimétrique, DMZ, VLAN dédié aux bases de données. | Filtrage des ports 80/443 (web) et 1521 (Oracle). |

---

## 7. Qualité et conformité  

| Référentiel | Exigence | Métrique |
|-------------|----------|----------|
| **ISO 9001** | Processus de développement maîtrisé (planification, revue, validation). | Audits internes trimestriels. |
| **ISO 25010** | Qualités du logiciel – fiabilité, maintenabilité, performance. | **Fiabilité** : MTBF ≥ 500 h. <br>**Performance** : temps de réponse < 2 s pour 95 % des requêtes. |
| **ISO 27001** | Gestion de la sécurité de l’information. | Tableau de bord mensuel des incidents. |
| **RGAA** | Accessibilité – niveau AA. | 100 % des pages conformes aux critères WCAG 2.1 AA. |
| **SonarQube** | Qualité du code. | **Score global ≥ A**, **bugs ≤ 5**, **vulnérabilités ≤ 3**, **coverage ≥ 80 %**. |

---

## 8. Documentation et formation  

| Livrable | Contenu | Format |
|----------|----------|--------|
| **Guide d’installation** | Prérequis serveur, procédure de déploiement du WAR, configuration JNDI, paramétrage TLS. | PDF + HTML. |
| **Manuel d’utilisation** | Fonctionnalités utilisateurs, droits d’accès, procédures d’export. | PDF. |
| **Guide d’administration** | Gestion des référentiels, paramétrage Cerbere, journalisation, sauvegarde DB. | PDF. |
| **Documentation technique** | Architecture, diagrammes UML, description des services web, scripts SQL de migration. | PDF + Doxygen (HTML). |
| **Formation** | 2 jours de formation présentielle (ou visio) – 1 j. utilisateurs, 1 j. administrateurs. | Supports PPT, exercices pratiques. |
| **Support** | Accès à la plateforme de tickets (Jira) – SLA indiqué à l’article 10. | Web. |

---

## 9. Tests et recette  

| Type de test | Objectif | Critères d’acceptation |
|--------------|----------|-----------------------|
| **Tests unitaires** | Vérifier chaque classe Java (DAO, Service, Utilitaires). | Couverture code ≥ 80 % (SonarQube). |
| **Tests d’intégration** | Interaction DAO‑DB, services‑WS. | 100 % des scénarios validés, aucune erreur de connexion. |
| **Tests fonctionnels** | Parcours complet des écrans Struts (création, modification, suppression). | 100 % des cas d’usage du CCF exécutés avec succès. |
| **Tests de charge** | Simuler 200 utilisateurs simultanés (peak). | Temps moyen de réponse < 2 s, pas de perte de données. |
| **Tests de sécurité** | Scan OWASP Top 10, tests d’intrusion. | Aucun critère de gravité > 3 (selon CVSS). |
| **Recette fonctionnelle** | Validation par le MOA sur l’environnement de test. | **Acceptation sans réserves** ou **liste de réserves** (max 5 points). |
| **Recette de performance** | Validation des SLA de disponibilité et de temps de réponse. | Conformité aux exigences de l’article 6. |
| **Gestion des anomalies** | Enregistrement dans JIRA, correction avant mise en production. | Tous les défauts critiques (severity 1/2) corrigés. |

---

## 10. Maintenance et support  

| Niveau | Engagement | Délai | Modalité |
|--------|-------------|--------|----------|
| **Support fonctionnel** | Hotline (téléphone + mail) – 8 h / 24 h, 7 j/7. | Temps de première réponse ≤ 30 min. |
| **Support technique** | Intervention sur site ou à distance selon criticité. | **GTR** (Goal Time to Resolve) ≤ 4 h pour incidents de sévérité 1, ≤ 8 h pour sévérité 2. |
| **Mise à jour corrective** | Correctifs de bugs et mises à jour de sécurité. | Livraison dans un délai de **15 jours ouvrés** après validation de la demande. |
| **Maintenance évolutive** | Ajout de nouvelles fonctionnalités (ex. API REST). | Planifiée sur le **carnet d’évolution** (hors contrat). |
| **Disponibilité du service** | **SLA** : disponibilité ≥ 99,9 % (hors fenêtres de maintenance). | Rapport mensuel de disponibilité fourni au MOA. |
| **Garantie** | **12 mois** à compter de la date de mise en production. | Couverture des défauts de conception et de conformité. |

---

## 11. Livrables et planning  

| N° | Livrable | Format | Date cible (Jalon) |
|----|----------|--------|-------------------|
| **L‑1** | Code source complet (Maven multi‑module) | Archive ZIP (sources) | **S‑01** – 30 jours après signature du marché |
| **L‑2** | Artefact WAR (`causalismp-web.war`) | Fichier WAR | **S‑02** – 45 jours |
| **L‑3** | Scripts de migration DB (ZIP) | Archive ZIP | **S‑02** |
| **L‑4** | Documentation (installation, utilisateur, admin, technique) | PDF + HTML | **S‑03** – 60 jours |
| **L‑5** | Jeux de tests automatisés (JUnit, scripts Selenium) | Répertoire `src/test` | **S‑03** |
| **L‑6** | Rapport de conformité sécurité (pentest, audit RGPD) | PDF | **S‑04** – 70 jours |
| **L‑7** | Procédures de bascule (PRA/PCA) | PDF | **S‑04** |
| **L‑8** | Formation utilisateurs (2 j) + supports | PPT, vidéos | **S‑05** – 80 jours |
| **L‑9** | Rapport de recette fonctionnelle signé | PDF | **S‑06** – 90 jours |
| **L‑10** | Mise en production du WAR sur l’environnement de production | Déploiement | **S‑07** – 100 jours |
| **L‑11** | Rapport de clôture de projet | PDF | **S‑08** – 110 jours |

*Les dates sont indicatives et pourront être ajustées par avenant signé par les deux parties.*

---

## 12. Contraintes légales et réglementaires  

| Domaine | Exigence | Référence |
|---------|----------|------------|
| **Propriété intellectuelle** | Le code source, la documentation et les livrables restent la **propriété exclusive du maître‑d’ouvrage**. Le prestataire cède tous les droits d’exploitation, de modification et de distribution. | Code de la commande publique – Art. L. 211‑1. |
| **Licences** | Tous les composants tiers (Struts 1, Castor, Log4j, JUnit, etc.) doivent être fournis sous licences compatibles **OSS** (Apache‑2.0, LGPL, etc.). Le prestataire devra fournir la **liste exhaustive** des licences. | RGI – Référentiel Général d’Interopérabilité. |
| **Protection des données (RGPD)** | Mise en place d’un registre des traitements, chiffrement des données sensibles, droits d’accès, droit à l’effacement, notification à la CNIL en cas de violation. | RGPD Art. 5, 32, 33. |
| **Archivage** | Les dossiers d’accidents et de maladies doivent être conservés **minimum 10 ans** conformément au Code du travail. | Code du travail – Art. L. 412‑1. |
| **Conservation des logs** | Journaux de sécurité conservés **180 jours**. | ANSSI – Référentiel de sécurité. |
| **Accessibilité (RGAA)** | Tous les écrans doivent respecter le niveau **AA** du RGAA. | Référentiel Général d’Amélioration de l’Accessibilité. |
| **Sécurité** | Conformité au **RGS** (niveau basique) et aux recommandations de l’**ANSSI** (CIS Benchmarks). | RGS, ANSSI. |

---

## 13. Critères de sélection des offres  

| Critère | Pondération | Modalité d’évaluation |
|---------|--------------|-----------------------|
| **Pertinence technique** (conformité aux exigences du CCTP, architecture, sécurité) | **60 %** | Grille d’évaluation : Excellent (≥ 90 pts), Satisfaisant (70‑89 pts), Insuffisant (< 70 pts). |
| **Prix** (coût global du projet – licences, prestation, maintenance) | **30 %** | Analyse du prix unitaire et du coût total de possession (TCO). |
| **Qualité du support et du planning** (délais, SLA, disponibilité) | **10 %** | Comparaison des engagements de support et du planning proposé. |

*Le score final sera calculé sur 100 points. Le lot avec le score le plus élevé sera retenu, sous réserve du respect du critère d’éligibilité (absence de conflit d’intérêts, capacité financière).*

---

## 14. Annexes contractuelles  

| Annexe | Contenu |
|--------|---------|
| **A – Cahier d’interface détaillé** | Description des points d’entrée/sortie (WS, DB, fichiers). |
| **B – Glossaire** | Définitions des termes métiers (accident, maladie professionnelle, grade, etc.). |
| **C – Références normatives** | Liste des normes citées (ISO 9001, ISO 27001, RGS, RGAA, RGPD). |
| **D – Modèle de déclaration de conformité RGPD** | Tableau à remplir par le prestataire. |
| **E – Modèle de rapport de test** | Structure du rapport de recette fonctionnelle et de performance. |
| **F – Tableau de bord de suivi projet** | Indicateurs de suivi (avancement, risques, livrables). |
| **G – Modèle de contrat de cession de droits** | Formulaire de cession de propriété intellectuelle. |

---

*Fait à [Ville], le 28 avril 2026*  

*Le présent CCTP constitue le document contractuel de référence entre le maître‑d’ouvrage et le futur prestataire. Tout avenant devra être signé par les deux parties.*