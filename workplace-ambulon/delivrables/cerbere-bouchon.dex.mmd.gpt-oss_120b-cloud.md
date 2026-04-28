# 📄 Dossier d’Exploitation (DEX) – **cerbere‑bouchon**  

> **Document établi sur les principes de la transition Build → Run et des bonnes pratiques ITIL/DevOps pour l’exploitation applicative**  

[TOC]

---  

## 1️⃣ Introduction et objectifs  

**Objet** : Document de référence garantissant la continuité, la maintenabilité et la sécurisation de l’exploitation de l’application **cerbere‑bouchon** en production.  

**Objectifs opérationnels**  

| ✅ | Objectif |
|---|----------|
| ✅ | Assurer la continuité de service |
| 📖 | Documenter les procédures de gestion courante |
| 🛠 | Faciliter le support et la résolution d’incidents |
| 🤝 | Encadrer les responsabilités (Dev / Ops / Support) |
| 🛡 | Assurer la conformité et la maîtrise des risques |
| 🔄 | Accompagner la phase de transition **Build → Run** |

---  

## 2️⃣ Contexte d’usage et périmètre  

| Élément | Valeur |
|---------|--------|
| **Type de livrable** | Standard ✅ |
| **Nature** | Document de référence 📘 |
| **Activité** | Transition Build → Run / Exploitation |
| **Quand l’utiliser** | - Avant le go‑live <br> - Formation des équipes d’exploitation <br> - Audits de conformité, PRA/PCA, revues de sécurité |
| **Cycle de vie** | Document vivant : mise à jour à chaque évolution fonctionnelle, technique ou d’infrastructure |

---  

## 3️⃣ Pré‑requis et jalons  

- [ ] Architecture technique validée et schémas à jour  
- [ ] Environnement de production stabilisé (accès, réseaux, DNS, certificats)  
- [ ] Politiques définies : sauvegarde, supervision, sécurité, SLA  
- [ ] Contacts clés identifiés (métiers, technique, support, sécurité)  
- [ ] Outillage prêt : monitoring, logging, ordonnanceur, gestion des secrets  

> ⏱ **Jalon critique** : Le DEX doit être **validé et signé** bien avant la mise en service. Aucun déploiement en production ne doit intervenir sans un DEX approuvé.  

---  

## 4️⃣ Gouvernance et rôles  

| Rôle | Profil type | Responsabilité |
|------|-------------|----------------|
| **Rédacteur principal** | Tech Lead / DevOps / Référent Prod | Rédaction, structuration, intégration des specs techniques |
| **Validateur Exploitation** | Chef d’exploitation / Responsable support | Vérification de l’opérabilité et de la complétude |
| **Validateur Sécurité/Conformité** | RSSI / DPO / Auditeur interne | Validation des procédures de sécurité, backup, conformité |
| **Mainteneur** | Équipe projet / PO technique | Mise à jour continue à chaque release ou changement d’infra |

---  

## 5️⃣ Structure détaillée du DEX  

> **À adapter** : supprimez ou fusionnez les sections qui ne s’appliquent pas à votre contexte (ex. : serveur on‑prem vs services managés).  

| N° | Section | Contenu attendu |
|---:|---------|-----------------|
| 1 | **Généralités** | Objet, domaine d’application, audience cible, version du document |
| 2 | **Documents applicables et de référence** | Normes internes, chartes, architecture, politiques sécurité |
| 3 | **Terminologie** | Glossaire technique/métier, acronymes |
| 4 | **Spécificités** | Fonctionnalités critiques, SLA/SLO, contacts clés, matrice d’escalade |
| 5 | **Architecture** | Schémas logiques/physiques, flux de données, infra prod, PRA/PCA |
| 6 | **Serveurs / Services** | Accès (SSH/RDP/Console), OS / runtime, CPU/RAM/Stockage, DNS/IP ou services managés |
| 7 | **Application** | Composants logiciels, versions, paramètres, procédures de déploiement |
| 8 | **Supervision et métrologie** | Outils de monitoring, seuils d’alerte, dashboards, métriques clés |
| 9 | **Sauvegarde** | Politique (fréquence, rétention, type), localisation, procédure de restauration |
|10| **Stockage** | Inventaire des volumes, quotas, chemins d’accès, gestion des logs |
|11| **Inventaire des bases** | Moteurs DB, versions, schémas, utilisateurs, maintenance, archivage |
|12| **Flux inter‑applicatifs** | Matrice des échanges, protocoles, ports, authentification, dépendances |
|13| **Plan de production** | Ordonnancement, tâches planifiées (cron/batch), fenêtres de maintenance |
|14| **Sécurisation des images** | Scan vulnérabilités, hardening, gestion des secrets, politiques de patching |
|15| **Opérations courantes** | Check‑lists quotidiennes, gestion des logs, erreurs connues, diagnostics |
|16| **Opérations récurrentes** | Gestion des comptes, rotation des certificats, nettoyages, audits périodiques |

---  

## 6️⃣ Diagramme Mermaid du cycle de vie DEX  

```mermaid
graph TB
    %% Styles -------------------------------------------------
    style dev fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    style ops fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    style sec fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    style maint fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    style p1  fill:#ADD8E6,stroke:#1976D2,stroke-width_2px;
    style p2  fill:#90EE90,stroke:#1976D2,stroke-width_2px;
    style p3  fill:#FFFF99,stroke:#1976D2,stroke-width_2px;
    style p4  fill:#E6E6FA,stroke:#1976D2,stroke-width_2px;
    %% Actors -------------------------------------------------
    actor dev as "Équipe Dev / Tech Lead"
    actor ops as "Équipe Ops / Support"
    actor sec as "Équipe Sécurité"
    actor maint as "Équipe Mainteneur"

    %% Phases -------------------------------------------------
    package p1["Phase 1 – Rédaction"] {
        rectangle step1["Collecte des specs & architecture"]
        rectangle step2["Rédaction des 16 sections DEX"]
    }
    package p2["Phase 2 – Validation croisée"] {
        rectangle step3["Revue technique (DevOps/Infra)"]
        rectangle step4["Validation opérabilité (Ops)"]
        rectangle step5["Validation conformité (Sécurité)"]
    }
    package p3["Phase 3 – Go‑Live & Run"] {
        rectangle step6["Signature & archivage versionné"]
        rectangle step7["Intégration runbook & supervision"]
    }
    package p4["Phase 4 – Maintenance continue"] {
        rectangle step8["Mise à jour à chaque release"]
        rectangle step9["Revue trimestrielle / post‑incident"]
    }

    %% Flows -------------------------------------------------
    dev -->|Alimente| step1;
    dev -->|Rédige| step2;
    ops -->|Vérifie| step3;
    ops -->|Valide opérabilité| step4;
    sec -->|Valide conformité| step5;
    step5 -->|Accord go‑live| step6;
    step6 -->|Déploiement| step7;
    maint -->|Met à jour| step8;
    step9 -.->|Boucle d’amélioration| step2;
    %% Notes -------------------------------------------------
    note right of step5;
        <b>Points de contrôle</b>\n- Accès complets\n- Procédures rollback\n- Matrice d’escalade testée;
    end note;
    note bottom of step9;
        <b>Règle d’or</b>\nPas de mise en prod sans DEX à jour;
    end note;
    %% Click actions (non‑fonctionnels en export) ---------------
    click p1 "javascript_void(0)" "Aller à Phase 1"
    click p2 "javascript_void(0)" "Aller à Phase 2"
    click p3 "javascript_void(0)" "Aller à Phase 3"
    click p4 "javascript_void(0)" "Aller à Phase 4"
```

---  

## 7️⃣ Conseils de rédaction et maintenance  

| Bonne pratique | À éviter |
|----------------|----------|
| Utiliser un dépôt versionné (Git / Wiki) avec historique | Stocker le DEX en pièce jointe email ou sur un partage non versionné |
| Rédiger en langage clair, orienté action | Rédiger des descriptions vagues ou purement théoriques |
| Inclure captures d’écran, chemins exacts et commandes | Laisser des placeholders `[À COMPLÉTER]` en production |
| Prévoir une revue systématique à chaque release majeure | Considérer le DEX comme « jetable » après le lancement |
| Lier le DEX aux runbooks, tickets d’incident et procédures PRA | Isoler le DEX des outils de supervision et de ticketing |

---  

## 8️⃣ Adaptations contextuelles  

| Contexte | Adaptation recommandée |
|----------|------------------------|
| **Applications Cloud / Serverless** | Remplacer la section *Serveurs* par *Services managés, IAM, Config as Code, Limits/Quotas* |
| **Secteur réglementé (Santé, Finance, Public)** | Renforcer les sections Sécurité, Traçabilité, Archivage légal, Conformité RGAA/ANSSI |
| **Legacy / Monolithe** | Insister sur la dépendance OS, les patches, la compatibilité, les procédures de reprise manuelle |
| **Microservices / Kubernetes** | Remplacer *Inventaire BDD/Serveurs* par *Clusters, Namespaces, Helm/Manifests, Observabilité (Prometheus/Grafana/Loki)* |

---  

## 9️⃣ Livrables et intégration  

| Livrable | Description |
|----------|-------------|
| **DEX versionné** | Fichier `.md` (ou export PDF) stocké dans un repo Git avec tag de version |
| **Checklist de validation** | Document signé par les parties prenantes (Dev, Ops, Sécurité) |
| **Matrice de traçabilité** | DEX ↔ Architecture ↔ Runbooks ↔ Tickets support |
| **Intégration CI/CD** | Validation automatisée de sections critiques (ex. : présence de variables d’environnement, liens de monitoring) |
| **Liens DEX dans les dashboards** | Ajout d’un bouton « Documentation » dans Grafana / Datadog → DEX |
| **Génération partielle via IaC** | Scripts Terraform/Ansible qui exportent les blocs d’infrastructure dans le DEX (ex. : listes de serveurs, bases, volumes) |

---  

## 📚 Mini‑glossaire  

| Acronyme | Signification |
|----------|----------------|
| **SLA** | Service Level Agreement – engagement de service (ex. : disponibilité 99,5 %) |
| **SLO** | Service Level Objective – objectif mesurable d’un SLA |
| **PRA** | Plan de Reprise d’Activité – procédures de continuité après sinistre |
| **PCA** | Plan de Continuité d’Activité – dispositif de maintien du service |
| **IAM** | Identity & Access Management – gestion des identités et des droits |
| **CI/CD** | Continuous Integration / Continuous Deployment – automatisation du build et du déploiement |
| **Runbook** | Document de procédures opérationnelles détaillées |
| **KPI** | Key Performance Indicator – indicateur de performance clé |
| **RTO** | Recovery Time Objective – délai maximal de remise en service |
| **RPO** | Recovery Point Objective – perte de données maximale tolérée |

---  

## 🔧 À personnaliser en 5 minutes  

1. Remplacez les blocs `[À COMPLÉTER]` par les informations réelles de votre projet (stack, contacts, SLA, etc.).  
2. Ajoutez les schémas d’architecture spécifiques (ex. : diagramme réseau, diagramme Kubernetes).  
3. Mettez à jour la **Matrice d’escalade** avec vos numéros de tickets et contacts.  
4. Validez le diagramme Mermaid avec votre outil de documentation (VS Code + Mermaid preview ou Obsidian).  
5. Commitez le fichier dans le dépôt Git du projet et créez la première **release** du DEX.  

---  

### 📎 Annexes (facultatives)  

*Vous pouvez ajouter en annexe des scripts de backup, des extraits de configuration, ou des liens vers des runbooks détaillés.*  

---  

*Fin du DEX – Version 1.0 – 2026‑04‑28*  