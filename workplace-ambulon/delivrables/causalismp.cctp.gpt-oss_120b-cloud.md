# Cahier des Clauses Techniques Particulières (CCTP)  
## Marché public – **Développement, maintenance et exploitation de l’application CausalisMP**  

*Version 1.0 – 28 avril 2026*  

---  

## 1. Objet du marché  

| N° | Description |
|---|-------------|
| 1.1 | **Fourniture, installation et mise en service** d’une application web de gestion des accidents du travail et des maladies professionnelles (nom de code **CausalisMP**). |
| 1.2 | **Maintenance évolutive et corrective** pendant une période de **douze (12) mois** à compter de la date de réception définitive. |
| 1.3 | **Exploitation** de la solution sur l’infrastructure du commanditaire (data‑center de l’État). |
| 1.4 | **Livraison** d’un dossier complet (code source, scripts de mise à jour de la base, documentation technique et fonctionnelle, procédures d’exploitation). |

> Le présent CCTP complète le Cahier des Clauses Fonctionnelles (CCF) qui décrit les exigences métier.  

---  

## 2. Description technique détaillée  

### 2.1 Spécifications fonctionnelles (référencées dans le CCF)  

| Référence | Description synthétique |
|-----------|--------------------------|
| CCF‑01 | Gestion des dossiers d’accident du travail. |
| CCF‑02 | Gestion des dossiers de maladie professionnelle. |
| CCF‑03 | Gestion des référentiels (grades, services, statuts, tâches prescrites, etc.). |
| CCF‑04 | Export des données au format OpenOffice. |
| CCF‑05 | Interface de recherche avancée (multi‑critères). |
| CCF‑06 | Gestion des droits d’accès (profil utilisateur, service). |
| CCF‑07 | Historisation et archivage des dossiers. |
| CCF‑08 | Interfaçage avec les web‑services du SI RH (sirh_causalis, sirh_referentiels). |

> Le Prestataire devra **respecter intégralement** les exigences fonctionnelles du CCF.  

### 2.2 Spécifications techniques obligatoires  

| N° | Exigence | Niveau de conformité |
|----|----------|-----------------------|
| T‑01 | Application développée en **Java 8 (ou version supérieure compatible JDK 8)**, compilable avec **Maven 3.8**. | Obligatoire |
| T‑02 | Architecture **multi‑modules Maven** : `causalismp-database`, `causalismp-deployment`, `causalismp-doc`, `causalismp-web`. | Obligatoire |
| T‑03 | Utilisation du **framework Struts 1.3.x** (Action, ActionForm, TagLib). | Obligatoire |
| T‑04 | Persistance via **Castor JDO** (mapping XML, datasource JNDI `java:comp/env/jdbc/userDScausalis`). | Obligatoire |
| T‑05 | Base de données **Oracle 12c** (ou version supérieure). Tous les scripts de migration fournis dans le module `causalismp-database`. | Obligatoire |
| T‑06 | Packaging final : **WAR** déployable sur serveur d’applications compatible **Servlet 3.1** (Tomcat 9, JBoss 7, etc.). | Obligatoire |
| T‑07 | Gestion des **logs** via **Log4j 2** (configuration `log4j.xml`). Niveau de log configurable (INFO, WARN, ERROR). | Obligatoire |
| T‑08 | **Sécurité RGS niveau basique** minimum (voir § 4). | Obligatoire |
| T‑09 | Conformité **RGPD** : chiffrement des données à caractère personnel, traçabilité des accès, droit à l’effacement. | Obligatoire |
| T‑10 | **Tests automatisés** : couverture unitaires ≥ 80 % (JaCoCo), tests d’intégration ≥ 70 %, tests fonctionnels via Selenium. | Obligatoire |
| T‑11 | **Performance** : temps de réponse moyen de l’interface utilisateur ≤ 2 s (charge 20 utilisateurs simultanés). | Obligatoire |
| T‑12 | **Accessibilité** : conformité **RGAA** niveau AA (WCAG 2.1). | Obligatoire |

### 2.3 Spécifications techniques souhaitées (souhaitables, notées)  

| N° | Exigence | Points attribués (sur 10) |
|----|----------|---------------------------|
| S‑01 | Migration progressive vers **Spring Boot** (compatibilité Struts 1). | 2 |
| S‑02 | Utilisation de **JPA/Hibernate** en remplacement de Castor JDO. | 2 |
| S‑03 | Implémentation d’une **API REST** (OpenAPI 3) en plus des services SOAP existants. | 2 |
| S‑04 | Mise en place d’un **pipeline CI/CD** (GitLab CI, SonarQube, Docker). | 2 |
| S‑05 | Support d’un **module mobile** (responsive design, PWA). | 2 |

### 2.4 Spécifications techniques optionnelles (facultatif)  

| N° | Exigence | Points attribués (sur 5) |
|----|----------|--------------------------|
| O‑01 | Intégration d’un **système de reporting BI** (ex. JasperReports). | 1 |
| O‑02 | Authentification unique via **SAML 2.0** (SSO). | 2 |
| O‑03 | **Sauvegarde incrémentale** des données en temps réel (log‑shipping). | 2 |

---  

## 3. Architecture et conception  

| Niveau | Description |
|--------|-------------|
| **3.1** | **Architecture en couches** : <br>• **Web tier** : JSP, Struts 1, TagLib custom (`StrutsOptionTag`, `PutIntoSessionTag`). <br>• **Service tier** : classes du package `i2.application.causalis.service` (ex. `GradeService`, `DomaineAffectationService`). <br>• **DAO tier** : `GenericDao<T>` et implémentations (`GradeDao`, `DossierAccidentDao`). |
| **3.2** | **Modules Maven** : chaque module génère un artefact distinct (WAR, ZIP de scripts, ZIP de sources, documentation). |
| **3.3** | **Normes et standards obligatoires** : <br>• **ISO/IEC 25010** – qualité du logiciel. <br>• **ISO 27001** – sécurité de l’information (décliné en RGS). <br>• **W3C HTML 5**, **CSS 3**, **ECMAScript 6**. |
| **3.4** | **Interopérabilité** : <br>• Conformité **RGI** – utilisation de services SOAP via WSDL fournis. <br>• Définition de contrats WS (XSD) dans le module `causalismp-web/src/main/resources/wsdl`. |
| **3.5** | **Frameworks autorisés** : Struts 1, Castor JDO, Apache Commons, Log4j 2, JUnit 5, Selenium 4. Toute introduction d’un nouveau framework doit être justifiée et validée par le maître d’ouvrage. |

---  

## 4. Exigences de sécurité (RGS, ANSSI)  

| N° | Exigence | Modalité de vérification |
|----|----------|--------------------------|
| S‑01 | Niveau **RGS basique** (authentification forte, chiffrement TLS 1.2 minimum, journalisation). | Audit de conformité RGS à la réception. |
| S‑02 | Authentification via **SSO Cerbere** (ou équivalent SAML 2.0) – gestion des profils, mots de passe conformes à la politique ANSSI (min 12 caractères, complexité). | Test d’intrusion (pentest) + revue des logs. |
| S‑03 | **Chiffrement des données en transit** (HTTPS, cipher suites recommandées : TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384). | Analyse de configuration serveur. |
| S‑04 | **Chiffrement des données au repos** : colonnes sensibles (ex. NIR, date de naissance) chiffrées AES‑256, clés stockées dans HSM ou coffre de secrets. | Revue du schéma DB et des scripts de migration. |
| S‑05 | **Journalisation** : toutes les actions critiques (connexion, création/modification/suppression de dossiers, appels WS) doivent être consignées avec horodatage, identifiant utilisateur, IP source. | Vérification du fichier `log4j.xml` et des logs d’application. |
| S‑06 | **Traçabilité & audit** : conservation des logs ≥ 365 jours, horodatage synchronisé via serveur NTP. | Inspection des procédures de sauvegarde des logs. |
| S‑07 | **RGPD** : <br>• Droit d’accès, de rectification et d’effacement (module “Gestion des droits”). <br>• Mise en place d’un registre des traitements. <br>• Notification de violation de données dans les 72 h. | Test fonctionnel sur les droits d’accès et revue du DPD. |

---  

## 5. Interfaces et intégrations  

| Interface | Type | Protocoles / Formats | Description |
|----------|------|----------------------|-------------|
| I‑01 | **Web‑service interne** – `sirh_causalis` | SOAP 1.2, WSDL fourni (`CausalisService.wsdl`). | Récupération/Envoi des données d’effectifs, grades, services. |
| I‑02 | **Web‑service interne** – `sirh_referentiels` | SOAP 1.2, WSDL fourni (`ReferentielsService.wsdl`). | Consultation des référentiels (grades, macro‑grades). |
| I‑03 | **Base de données** | JDBC 4.2 (Oracle) via JNDI `jdbc/userDScausalis`. | Persistance des dossiers, historisation. |
| I‑04 | **Export OpenOffice** | ODS (OpenDocument Spreadsheet). | Export des tableaux d’effectifs et statistiques. |
| I‑05 | **Interface utilisateur** | HTTP/HTTPS, HTML 5, CSS 3, JavaScript (ES6). | Navigation via JSPs (`index.jsp`, `dossiers.jsp`, …). |
| I‑06 | **API REST (optionnelle)** | HTTP/HTTPS, JSON, OpenAPI 3. | Fourniture d’un point d’accès moderne (facultatif, cf. § 2.3). |

> Le Prestataire devra livrer les **descripteurs WSDL** et les **schémas XSD** ainsi que les **scripts de création de la datasource JNDI** pour l’environnement de production.  

---  

## 6. Environnements et infrastructure  

| Environnement | Contenu | Contraintes |
|---------------|---------|-------------|
| **E‑01** | **Développement** – serveur dédié (VM Linux Ubuntu 22.04), JDK 8, Maven 3.8, base Oracle 12c (sandbox). | Accès limité aux développeurs, données anonymisées. |
| **E‑02** | **Intégration** – même configuration que DEV, base de données remplie de jeux de données de test. | Exécution du pipeline CI (GitLab CI). |
| **E‑03** | **Pré‑production** – clone de la production (hardware identique). | Tests de charge, validation de la sécurité, recette fonctionnelle. |
| **E‑04** | **Production** – data‑center de l’État, serveur d’applications **Tomcat 9** (ou JBoss 7) en mode **cluster actif‑passif**. <br>• **HA** : basculement < 5 min. <br>• **PRA/PCA** : sauvegarde quotidienne incrémentale + sauvegarde complète hebdomadaire, RTO ≤ 4 h, RPO ≤ 1 h. | Accès via VPN, firewall autorisant uniquement les ports **443 (HTTPS)**, **1521 (Oracle)**, **8080 (Tomcat)**. |
| **E‑05** | **Sauvegarde** – serveur de stockage LTO 6, chiffrement AES‑256. | Conservation des sauvegardes pendant **10 ans** (archivage légal). |

---  

## 7. Qualité et conformité  

| Critère | Niveau exigé | Métrique |
|---------|--------------|----------|
| **Qualité logicielle** | ISO 9001, ISO 25010 (maintenabilité, fiabilité, sécurité). | Audit qualité externe à la réception. |
| **Couverture des tests unitaires** | ≥ 80 % (JaCoCo). | Rapport de couverture dans le pipeline CI. |
| **Couverture des tests d’intégration** | ≥ 70 %. | Rapport SonarQube. |
| **Performance** | Temps moyen de réponse UI ≤ 2 s (20 utilisateurs simultanés). | Test de charge JMeter (scenario de 30 min). |
| **Disponibilité** | ≥ 99,9 % (hors fenêtres de maintenance). | Monitoring via Zabbix/Prometheus. |
| **Accessibilité** | RGAA niveau AA. | Validation à l’aide de l’outil AccessiWeb. |
| **Sécurité** | Conformité RGS basique, exigences RGPD. | Rapport d’audit de sécurité (pentest). |

---  

## 8. Documentation et formation  

| Livrable | Format | Contenu |
|----------|--------|---------|
| **Dossier d’Architecture Technique (DAT)** | PDF + source (PlantUML). | Diagrammes (class, séquence, déploiement), description des couches, flux de données. |
| **Guide d’Installation** | PDF + Markdown. | Prérequis, procédure d’installation du serveur d’applications, configuration JNDI, déploiement du WAR. |
| **Manuel Utilisateur** | PDF + HTML (WebHelp). | Navigation dans l’interface, création/modification/suppression de dossiers, export. |
| **Guide Administrateur** | PDF. | Gestion des droits, paramétrage des logs, sauvegarde/restauration, monitoring. |
| **Documentation API** | OpenAPI 3 (YAML) + PDF. | Description des services SOAP et (éventuelle) API REST. |
| **Plan de Tests** | XLSX. | Scénarios fonctionnels, jeux de données, critères d’acceptation. |
| **Rapport de Recette** | PDF. | Résultats des tests, écarts corrigés, validation finale. |
| **Formation** | Sessions présentiel ou distanciel (Webex). | • **3 jours** – Administrateurs (installation, exploitation, sauvegarde). <br>• **2 jours** – Utilisateurs fonctionnels (saisie, recherche, export). <br>• **1 jour** – Équipe de support (gestion incidents, escalades). |

---  

## 9. Tests et recette  

| Type de test | Objectif | Méthodologie | Critère d’acceptation |
|--------------|----------|---------------|-----------------------|
| **Unitaire** | Vérifier chaque classe/méthode. | JUnit 5 + Mockito. | Couverture ≥ 80 % et aucun test échoué. |
| **Intégration** | Valider l’interaction DAO‑Service‑WS. | Tests d’intégration Spring (ou JUnit + Castor). | Tous les scénarios validés, logs d’erreurs nuls. |
| **Fonctionnel** | Vérifier les exigences du CCF. | Selenium 4 (browser Chrome/Firefox). | 100 % des cas de test fonctionnels réussis. |
| **Performance** | Mesurer temps de réponse et capacité. | JMeter – 20 utilisateurs pendant 30 min. | Temps moyen ≤ 2 s, aucun dépassement de seuil de CPU > 80 % sur serveur. |
| **Sécurité** | Détecter vulnérabilités. | Pentest (OWASP ZAP) + audit code. | Aucun défaut critique, défauts majeurs corrigés. |
| **RGPD** | Vérifier droits d’accès et suppression. | Tests fonctionnels sur anonymisation, droit à l’oubli. | Conformité totale, journal des actions. |
| **Accessibilité** | Conformité RGAA. | Outil AccessiWeb. | Niveau AA atteint. |

La **recette** sera réalisée en deux temps :  
1. **Recette fonctionnelle** (validation du CCF).  
2. **Recette de conformité** (sécurité, performance, RGAA, RGPD).  

Le Prestataire devra fournir un **plan de tests** détaillé (tableau de suivi) et un **rapport de recette** signé par le maître d’ouvrage.  

---  

## 10. Maintenance et support  

| Niveau | Description | Délai d’intervention | Disponibilité |
|--------|-------------|-----------------------|--------------|
| **N1** – Support fonctionnel | Assistance sur l’utilisation (saisie, recherche, export). | **4 h** (ouverture ticket). | 7 j/24 h. |
| **N2** – Support technique | Corrections de bugs, mise à jour de composants (Struts, Castor). | **1 h** pour incidents critiques, **4 h** pour incidents majeurs. | 7 j/24 h. |
| **N3** – Support évolutif | Développement de nouvelles fonctionnalités, évolutions réglementaires. | **30 j** (planification). | Horaires ouvrés (Lun‑Ven 9h‑18h). |

### SLA (Service Level Agreement)  

| Criticité | Temps de résolution maximal |
|-----------|------------------------------|
| **Critique** (service indisponible) | 4 h |
| **Haute** (dégradation majeure) | 8 h |
| **Moyenne** (fonctionnalité non‑critique) | 24 h |
| **Basse** (question d’ordre général) | 48 h |

### Garantie  

- **Durée** : 12 mois à compter de la réception définitive.  
- **Engagement** : correction de tout défaut identifié pendant la période de garantie, sans frais supplémentaire.  

---  

## 11. Livrables et planning  

| Jalons | Date cible | Livrable(s) | Responsable |
|--------|------------|--------------|--------------|
| **J‑01** | T + 10 jours | **Kick‑off** – cahier des charges détaillé, planning détaillé. | Maître d’ouvrage + Prestataire |
| **J‑02** | T + 30 jours | **Architecture Validation** – diagrammes, choix technologiques, plan de sécurité. | Prestataire |
| **J‑03** | T + 90 jours | **Développement – Sprint 1** – modules de base (DAO, services, UI). | Prestataire |
| **J‑04** | T + 150 jours | **Développement – Sprint 2** – intégration WS, export, sécurité. | Prestataire |
| **J‑05** | T + 180 jours | **Tests unitaires & intégration** (rapports JaCoCo, Sonar). | Prestataire |
| **J‑06** | T + 210 jours | **Recette fonctionnelle** – exécution des tests fonctionnels. | Maître d’ouvrage |
| **J‑07** | T + 240 jours | **Recette de conformité** – sécurité, performance, RGAA, RGPD. | Maître d’ouvrage + Auditeur externe |
| **J‑08** | T + 260 jours | **Livraison du package final** – WAR, scripts DB, documentation, rapports de tests. | Prestataire |
| **J‑09** | T + 270 jours | **Mise en production** – déploiement, bascule, validation. | Prestataire + MOA |
| **J‑10** | T + 300 jours | **Fin de la période de garantie** – rapport de clôture. | Prestataire |

> **T** = date de notification du marché.  

### Pénalités de retard  

- **0,5 % du montant total du marché** par jour calendaire de retard au-delà du **J‑08** (livraison du package).  
- **Maximum** : **10 %** du montant total du marché.  

---  

## 12. Contraintes légales et réglementaires  

| Aspect | Exigence |
|--------|----------|
| **Propriété intellectuelle** | Toutes les sources, scripts, documentation et livrables deviennent la **propriété exclusive de l’État** dès la date de réception. Le Prestataire cède tous les droits d’exploitation, de reproduction, de modification et de diffusion, sans limitation de durée ni de territoire. |
| **Licences tierces** | Les bibliothèques tierces doivent être sous licences **compatible avec le droit public** (Apache 2.0, MIT, LGPL 2.1, BSD). Le Prestataire devra fournir la liste complète des composants et leurs licences. |
| **RGPD** | Conformité au **Règlement Général sur la Protection des Données** : registre des traitements, analyse d’impact (PIA), droits des personnes (accès, rectification, effacement). |
| **Archivage** | Conservation des dossiers d’accident et des dossiers de maladie professionnelle pendant **10 ans** conformément aux exigences de la **CNIL** et du **Code du travail**. |
| **Sécurité** | Respect du **Référentiel Général de Sécurité (RGS)** – niveau basique au minimum, avec possibilité de passer au niveau renforcé si le commanditaire le demande. |
| **Interopérabilité** | Conformité au **Référentiel Général d’Interopérabilité (RGI)** de l’État (utilisation de standards ouverts, services SOAP, XML). |
| **Accessibilité** | Conformité au **Référentiel Général d’Amélioration de l’Accessibilité (RGAA)** – niveau AA. |
| **Données de santé** | Conformité à la **déclaration CNIL** relative aux données de santé (article 9 du RGPD). |

---  

## 13. Critères de sélection des offres  

| Critère | Pondération | Sous‑critères (points) |
|---------|--------------|------------------------|
| **Qualité technique (60 %)** | 60 % du total | • **Méthodologie** (15 pts) – plan de projet, gouvernance, suivi des risques.<br>• **Conformité RGS/RGPD** (15 pts) – preuve d’audit, politique de sécurité.<br>• **Qualité du code** (10 pts) – couverture de tests, revue SonarQube.<br>• **Performance & scalabilité** (10 pts) – résultats des tests de charge.<br>• **Innovation** (10 pts) – propositions d’évolutions (ex. API REST, CI/CD). |
| **Valeur financière (40 %)** | 40 % du total | • **Prix global** (30 pts) – coût total du projet (développement, licences, maintenance).<br>• **Coût de la maintenance** (10 pts) – tarifs de support (N1/N2/N3). |
| **Total** | 100 % | **Score final** = (Qualité × 0,60) + (Valeur × 0,40). Le seuil de **réussite** est fixé à **70 points** sur 100. |

### Grille d’évaluation (exemple)  

| Niveau | Description | Points |
|--------|-------------|--------|
| **Excellent** | Réponse complète, méthodologie détaillée, conformité totale aux exigences RGS/RGPD, couverture de tests > 90 %, proposition d’évolution pertinente. | 12‑15 |
| **Satisfaisant** | Réponse conforme, méthodologie correcte, conformité partielle aux exigences, couverture de tests 80‑90 %. | 8‑11 |
| **Insuffisant** | Réponse incomplète, méthodologie floue, non‑conformité RGS/RGPD, couverture de tests < 80 %. | ≤ 7 |

---  

## 14. Annexes contractuelles  

| Annexe | Contenu |
|--------|---------|
| **A – Glossaire** | Définitions des termes techniques (ex. *WAR*, *JNDI*, *RGS*, *RGPD*, *RGAA*). |
| **B – Références normatives** | Liste des normes citées : ISO 27001, ISO 9001, ISO 25010, RGS, RGPD, RGI, RGAA, ANSSI. |
| **C – Modèle de plan de projet** | Tableau de suivi (jalons, responsables, livrables, état d’avancement). |
| **D – Modèle de tableau de suivi des anomalies** | Colonnes : ID, Description, Sévérité, Priorité, Responsable, Date de découverte, Date de correction, Statut. |
| **E – Modèle de déclaration d’incident de sécurité** | Procédure de notification à la CNIL (dans les 72 h). |
| **F – Modèle de certificat de conformité RGS** | Exemple de certificat à remettre à la réception. |
| **G – Liste des composants tiers** | Bibliothèques, versions, licences, URL de téléchargement. |
| **H – Procédure de sauvegarde / restauration** | Étapes détaillées (script `backup.sh`, plan de restauration). |

---  

*Fait à [Ville], le 28 avril 2026.*  

---  

**Fin du Cahier des Clauses Techniques Particulières**.