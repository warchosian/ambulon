# Guide Complet des Prompts de Documentation

Ce guide répertorie et explique l'utilisation de tous les prompts disponibles pour la génération de documentation technique selon les normes et standards internationaux.

---

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Catalogue des prompts](#catalogue-des-prompts)
3. [Matrice de sélection](#matrice-de-sélection)
4. [Chaîne documentaire](#chaîne-documentaire)
5. [Exemples d'utilisation](#exemples-dutilisation)
6. [Bonnes pratiques](#bonnes-pratiques)

---

## Vue d'ensemble

### Types de documents couverts

| Type | Description | Normes principales |
|------|-------------|-------------------|
| **CCF** | Cahier des Charges Fonctionnel | NF EN 16271, ISO/IEC/IEEE 29148, BPMN |
| **CST** | Cahier des Spécifications Techniques | ISO/IEC 25010, ISO/IEC/IEEE 29119 |
| **DAT** | Dossier d'Architecture Technique | ISO/IEC/IEEE 42010, C4 Model, UML, ArchiMate |
| **CCTP** | Cahier des Clauses Techniques Particulières | Code de la commande publique, RGS |

### Standards normatifs couverts

- **NF EN 16271** — Management par la valeur (expression du besoin)
- **ISO/IEC/IEEE 29148** — Ingénierie des exigences
- **ISO/IEC 19510** — BPMN (modélisation des processus)
- **ISO/IEC 25010** — Qualité des produits logiciels
- **ISO/IEC/IEEE 29119** — Tests logiciels
- **ISO/IEC 19505** — UML (langage de modélisation)
- **ISO/IEC/IEEE 42010** — Description d'architecture
- **ArchiMate** — Architecture d'entreprise (The Open Group)
- **C4 Model** — Visualisation architecturale (Simon Brown)
- **ADR** — Architecture Decision Records

---

## Catalogue des prompts

### 📋 CCF — Cahier des Charges Fonctionnel

#### 1. `_prompt_ccf.md` — Vue d'ensemble
**Usage** : Découverte et choix de la norme CCF appropriée
**Contient** : Présentation des différentes normes applicables aux CCF
**Quand l'utiliser** : En phase d'initiation, pour comprendre les options disponibles

---

#### 2. `_prompt_ccf_nfen16271.md` — CCF × NF EN 16271
**Norme** : NF EN 16271:2013 — Management par la valeur
**Contexte** : Marchés publics français, approche par la valeur
**Spécificités** :
- Décomposition fonctionnelle hiérarchique
- Critères d'appréciation pondérés
- Distinction besoin/solution stricte
- Adapté aux consultations publiques

**Structure produite** :
1. Présentation du projet
2. Analyse de la valeur (fonctions de service FP/FC)
3. Expression fonctionnelle du besoin
4. Caractérisation des besoins (tableau critères/pondération)
5. Validation de l'expression du besoin
6. Scénarios d'usage
7. Parties prenantes
8. Contraintes
9. Critères de sélection et pondération
10. Glossaire

**Quand l'utiliser** :
- Projet public français
- Consultation d'entreprises (marché public)
- Besoin d'une pondération formelle des critères
- Approche "management par la valeur"

---

#### 3. `_prompt_ccf_iso29148.md` — CCF × ISO/IEC/IEEE 29148
**Norme** : ISO/IEC/IEEE 29148:2018 — Ingénierie des exigences
**Contexte** : Projets internationaux, ingénierie système rigoureuse
**Spécificités** :
- Traçabilité complète des exigences
- Attributs riches (priorité, statut, méthode de vérification)
- 7 caractéristiques des exigences (correctness, unambiguity, etc.)
- Compatible cycle de vie complet

**Structure produite** :
1. Identification et contexte
2. Description de l'écosystème
3. Exigences fonctionnelles (avec attributs ISO)
4. Exigences non-fonctionnelles (performance, interfaces, qualité, sécurité)
5. Modèle de données conceptuel
6. Modélisation des comportements (UML)
7. Attributs d'exigences détaillés
8. Traçabilité (matrice)
9. Gestion des exigences
10. Validation et vérification

**Quand l'utiliser** :
- Projet international ou multinational
- Système critique (santé, aéronautique, nucléaire)
- Besoin de traçabilité forte
- Intégration avec des outils ALM (Application Lifecycle Management)

---

#### 4. `_prompt_ccf_bpmn.md` — CCF × BPMN/ISO 19510
**Norme** : ISO/IEC 19510:2013 — Business Process Model and Notation
**Contexte** : Processus métier complexes, workflow automatisables
**Spécificités** :
- Modélisation graphique des processus
- Passerelle vers implémentation (moteurs BPMN)
- Collaboration inter-organisations
- Exécutable sur moteurs (Camunda, etc.)

**Structure produite** :
1. Introduction et contexte processus
2. Cartographie des processus
3. Modélisation BPMN détaillée (collaboration, processus, choreography)
4. Règles de gestion métier
5. Données et documents
6. Acteurs et rôles
7. Performances et indicateurs (KPIs)
8. Gestion des exceptions
9. Sous-processus et réutilisation
10. Matrice de traçabilité
11. Validation et conformité

**Quand l'utiliser** :
- Processus métier complexes à modéliser
- Préparation à l'automatisation (RPA, BPM)
- Besoin de communication visuelle forte avec le métier
- Projet avec workflow transactionnels

---

### ⚙️ CST — Cahier des Spécifications Techniques

#### 5. `_prompt_cst.md` — Vue d'ensemble
**Usage** : Découverte et choix de l'approche CST appropriée
**Contient** : Présentation des standards de qualité et de tests
**Quand l'utiliser** : En phase de conception technique

---

#### 6. `_prompt_cst_iso25010.md` — CST × ISO/IEC 25010
**Norme** : ISO/IEC 25010:2023 — Modèle de qualité des produits logiciels
**Contexte** : Définition objective des critères de qualité
**Spécificités** :
- 8 caractéristiques de qualité fondamentales
- Métriques mesurables et objectives
- Évaluation de la qualité logicielle

**Structure produite** (par caractéristique) :
1. **Aptitude fonctionnelle** : Complétude, exactitude, adéquation
2. **Performance et efficacité** : Comportement temporel, utilisation ressources, capacité
3. **Compatibilité** : Cohérence, interopérabilité
4. **Utilisabilité** : Appréhensibilité, apprenabilité, opérabilité, esthétique, accessibilité
5. **Fiabilité** : Maturité, disponibilité, tolérance aux fautes, récupérabilité
6. **Sécurité** : Confidentialité, intégrité, non-répudiation, responsabilité, authenticité
7. **Maintenabilité** : Modularité, réutilisabilité, analysabilité, modifiabilité, testabilité
8. **Portabilité** : Adaptabilité, installabilité, remplaçabilité

Pour chaque caractéristique : métriques, objectifs chiffrés, méthodes de mesure.

**Quand l'utiliser** :
- Définition de SLAs et critères d'acceptation
- Évaluation comparative de solutions
- Contrat de qualité avec un prestataire
- Amélioration continue de la qualité

---

#### 7. `_prompt_cst_iso29119.md` — CST × ISO/IEC/IEEE 29119
**Norme** : ISO/IEC/IEEE 29119 (série) — Tests logiciels
**Contexte** : Stratégie de test complète et documentée
**Spécificités** :
- Processus de test standardisés
- Techniques de test éprouvées
- Documentation formelle des tests

**Structure produite** :
1. Stratégie de test (ISO 29119-3)
2. Plan de test détaillé
3. Conception des tests (ISO 29119-4)
   - Partitionnement en classes d'équivalence
   - Tables de décision
   - Tests de transition d'états
   - Tests de scénarios
   - Couverture structurelle
4. Spécification des cas de test
5. Procédures de test
6. Gestion des anomalies (défauts)
7. Tests de régression (ISO 29119-6)
8. Tests unitaires (ISO 29119-11)
9. Automatisation des tests
10. Environnements de test
11. Rapports et métriques

**Quand l'utiliser** :
- Définition d'une stratégie de test complète
- Projets avec exigences de couverture élevées
- Certification ou homologation
- Équipes QA structurées

---

### 🏗️ DAT — Dossier d'Architecture Technique

#### 8. `_prompt_dat_iso42010.md` — DAT × ISO/IEC/IEEE 42010
**Norme** : ISO/IEC/IEEE 42010:2022 — Description d'architecture
**Contexte** : Documentation architecturale formelle, audits
**Spécificités** :
- Cadre rigoureux (stakeholders, concerns, viewpoints, views)
- Adapté aux systèmes critiques
- Compatible audits et revues formelles

**Structure produite** :
1. Introduction architecturale
2. Parties prenantes et préoccupations
3. Points de vue architecturaux (viewpoints)
4. Vues architecturales :
   - Vue Contexte
   - Vue Fonctionnelle/Métier
   - Vue Applicative/Logicielle
   - Vue Données et Information
   - Vue Technique/Infrastructure
   - Vue Intégration
   - Vue Sécurité
   - Vue Opérationnelle
5. Correspondance entre vues
6. Décisions architecturales (ADR)
7. Analyse des écarts et risques
8. Qualités et exigences NFR
9. Évolutivité et feuille de route

**Quand l'utiliser** :
- Systèmes critiques ou réglementés
- Audit d'architecture
- Architecture d'entreprise
- Documentation pour homologation

---

#### 9. `_prompt_dat_adr.md` — DAT × ADR + C4 Model
**Standards** : Architecture Decision Records + C4 Model
**Contexte** : Documentation agile, "documentation as code"
**Spécificités** :
- Léger et itératif
- Centré sur les décisions
- Visualisation C4 (Contexte, Conteneurs, Composants, Code)

**Structure produite** :
1. Introduction et vision
2. Niveau 1 — Vue Contexte (C4-L1)
3. Niveau 2 — Vue Conteneurs (C4-L2)
4. **ADRs** (Architecture Decision Records) :
   - Contexte
   - Options considérées (tableau comparatif)
   - Décision retenue
   - Conséquences (+/-)
5. Niveau 3 — Vue Composants (C4-L3)
6. Niveau 4 — Vue Code (référence)
7. Vue Exécution (scénarios)
8. Vue Déploiement (C4)
9. Sujets transverses
10. Risques et dettes techniques

**Quand l'utiliser** :
- Projets agiles/Scrum
- Équipes de développement
- Documentation vivante et évolutive
- Communication technique interne

---

#### 10. `_prompt_dat_uml.md` — DAT × UML/ISO 19505
**Norme** : ISO/IEC 19505 — Unified Modeling Language 2.x
**Contexte** : Modélisation objet complète
**Spécificités** :
- 13 types de diagrammes UML
- Couverture structurelle, comportementale, interaction

**Structure produite** :

**Vue Structurelle** :
- Diagramme de Classes
- Diagramme de Composants
- Diagramme de Déploiement
- Diagramme d'Objets (optionnel)
- Diagramme de Paquetages
- Diagramme de Structure Composite (optionnel)

**Vue Comportementale** :
- Diagramme de Cas d'Utilisation
- Diagramme d'Activités
- Diagramme d'États

**Vue d'Interaction** :
- Diagramme de Séquence
- Diagramme de Communication
- Diagramme de Vue d'Ensemble d'Interaction (optionnel)
- Diagramme de Temps (optionnel)

**Quand l'utiliser** :
- Modélisation objet rigoureuse
- Équipes familiarisées avec UML
- Génération de code depuis modèles
- Documentation technique détaillée

---

#### 11. `_prompt_dat_archimate.md` — DAT × ArchiMate
**Standard** : ArchiMate 3.x — The Open Group
**Contexte** : Architecture d'entreprise, alignement IT/Métier
**Spécificités** :
- Couches Métier, Application, Technologie
- Vue transversale et stratégique
- Communication avec les stakeholders

**Structure produite** :
1. Vue d'ensemble ArchiMate
2. **Couche Métier** : Acteurs, rôles, services, processus, fonctions, objets
3. **Couche Application** : Composants, collaborations, interfaces, services, fonctions, données
4. **Couche Technologie** : Nœuds, devices, system software, services, fonctions, artifacts
5. **Couche Stratégique** (optionnel) : Ressources, capabilities, value streams
6. **Couche Motivation** : Stakeholders, drivers, assessments, goals, outcomes
7. **Couche Implémentation** (optionnel) : Work packages, deliverables, plateaux, gaps
8. Relations transverses (realization, serving, assignment, access, influence)
9. Vues architecturales (viewpoints)
10. Métamodel du projet

**Quand l'utiliser** :
- Architecture d'entreprise (Enterprise Architecture)
- Communication MOA/MOE
- Cartographie des systèmes d'information
- Transformation digitale

---

### 📜 CCTP — Cahier des Clauses Techniques Particulières

#### 12. `_prompt_cctp.md` — CCTP Marchés publics
**Références** : Code de la commande publique, RGS, RGPD
**Contexte** : Consultation des entreprises (secteur public français)
**Spécificités** :
- Valeur contractuelle
- Référentiels de sécurité de l'État
- Conformité RGPD

**Structure produite** :
1. Objet du marché
2. Description technique détaillée
3. Architecture et conception
4. Exigences de sécurité (RGS/ANSSI)
5. Interfaces et intégrations
6. Environnements et infrastructure
7. Qualité et conformité
8. Documentation et formation
9. Tests et recette
10. Maintenance et support
11. Livrables et planning
12. Contraintes légales et réglementaires
13. Critères de sélection des offres
14. Annexes contractuelles

**Quand l'utiliser** :
- Marché public informatique
- Consultation de prestataires
- Cadre contractuel réglementé

---

## Matrice de sélection

### Par contexte de projet

| Contexte | CCF | CST | DAT |
|----------|-----|-----|-----|
| **Marché public FR** | `_ccf_nfen16271` | `_cctp` + qualité | `_iso42010` |
| **Projet international** | `_ccf_iso29148` | `_iso25010` + `_iso29119` | `_uml` ou `_archimate` |
| **Projet agile** | `_ccf_bpmn` (léger) | `_iso25010` | `_adr` + `_c4model` |
| **Système critique** | `_ccf_iso29148` | `_iso29119` (tests formels) | `_iso42010` + `_uml` |
| **Architecture d'entreprise** | — | — | `_archimate` |
| **Communication tech** | — | — | `_c4model` |

### Par phase du projet

| Phase | Document recommandé | Prompt |
|-------|---------------------|--------|
| Cadrage | CCF | Selon contexte (voir tableau ci-dessus) |
| Consultation | CCTP | `_cctp` |
| Conception | CST | `_iso25010` ou `_iso29119` |
| Architecture | DAT | Selon audience et criticité |
| Réalisation | DAT (évolutif) | `_adr` |

### Par audience cible

| Audience | Documents adaptés |
|----------|-------------------|
| **MOA / AMOA** | CCF (NF EN 16271 ou ISO 29148), ArchiMate (couche métier) |
| **Développeurs** | CST (ISO 25010), DAT (UML, C4-L2/L3) |
| **Architectes** | DAT (tous types selon besoin) |
| **RSSI / Sécurité** | CCTP (partie sécurité), DAT (Vue sécurité ISO 42010) |
| **Exploitants / Ops** | CST (déploiement), DAT (Vue déploiement C4) |
| **Auditeurs** | DAT (ISO 42010) |
| **Direction / Métier** | CCF, ArchiMate (stratégique) |

---

## Chaîne documentaire

### Traçabilité recommandée

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│     CCF     │ ───► │     CST     │ ───► │     DAT     │
│  (Besoin)   │      │ (Solution)  │      │(Structure)  │
│   QUOI ?    │      │  COMMENT ?  │      │ QUELLE ?    │
└─────────────┘      └─────────────┘      └─────────────┘
       │                    │                    │
       ▼                    ▼                    ▼
  Exigences           Spécifications       Composants
  Fonctionnelles      Techniques           Architecturaux
```

### Correspondance entre documents

| Élément CCF | Élément CST | Élément DAT |
|-------------|-------------|-------------|
| Cas d'utilisation | Diagramme de séquence | Vue Contexte (C4-L1) |
| Règle métier | Implémentation code | Composant métier |
| Exigence NFR | Métrique qualité | Decision (ADR) |
| Processus métier | API/Interfaces | Vue Conteneurs (C4-L2) |

---

## Exemples d'utilisation

### Exemple 1 : Projet public français (marché)

**Phase 1 — Expression du besoin** :
```
Utiliser : _prompt_ccf_nfen16271.md
Input : Description du projet, acteurs identifiés, contraintes
Output : CCF avec fonctions de service pondérées, critères d'appréciation
```

**Phase 2 — Consultation** :
```
Utiliser : _prompt_cctp.md
Input : CCF produit, référentiels sécurité (RGS), budget
Output : CCTP contractuel avec clauses de sécurité
```

**Phase 3 — Architecture** :
```
Utiliser : _prompt_dat_iso42010.md
Input : CCF, CCTP, choix technologiques préliminaires
Output : DAT formel avec vues architecturales complètes
```

### Exemple 2 : Projet agile interne

**Phase 1 — User Stories et processus** :
```
Utiliser : _prompt_ccf_bpmn.md (léger)
Input : Ateliers métiers, workflow identifiés
Output : CCF avec modélisation BPMN des processus critiques
```

**Phase 2 — Qualité et architecture** :
```
Utiliser : _prompt_cst_iso25010.md + _prompt_dat_adr.md
Input : Exigences fonctionnelles, stack technique choisi
Output : Critères de qualité mesurables + ADRs des décisions majeures
```

### Exemple 3 : Architecture d'entreprise

```
Utiliser : _prompt_dat_archimate.md
Input : Inventaire des applications, cartographie métier existante
Output : DAT ArchiMate avec couches Métier/Application/Technologie alignées
```

---

## Bonnes pratiques

### 1. Ordre de production

**Jamais de DAT avant CCF** : L'architecture doit répondre à des besoins identifiés.

**Séquence recommandée** :
1. CCF (expression du besoin)
2. CST (spécifications techniques)
3. DAT (architecture réalisant le CST)

### 2. Niveau de détail

| Document | Niveau | Contenu |
|----------|--------|---------|
| CCF | Abstrait | Quoi, pas comment |
| CST | Technique | Comment, avec quelle qualité |
| DAT | Structure | Organisation, composants, flux |

### 3. Maintenance

- **CCF** : Figé après validation (versionné)
- **CST** : Évolue avec les choix techniques
- **DAT** : Document vivant (ADR recommandé)

### 4. Combinaisons à éviter

- ❌ Ne pas mélanger les normes dans un même document
- ❌ Ne pas dupliquer le contenu entre CCF et CST
- ❌ Ne pas détailler le code dans le DAT (sauf vue C4-L4 si pertinent)

### 5. Outils recommandés

| Document | Outils |
|----------|--------|
| CCF BPMN | Camunda Modeler, Bizagi |
| CST Tests | JUnit, Selenium, SonarQube |
| DAT C4 | Structurizr, IcePanel, Mermaid |
| DAT UML | Enterprise Architect, Visual Paradigm |
| DAT ArchiMate | Archi, BiZZdesign |

---

## Index rapide

### Par norme ISO

| Norme | Prompts concernés |
|-------|-------------------|
| NF EN 16271 | `_ccf_nfen16271` |
| ISO/IEC/IEEE 29148 | `_ccf_iso29148` |
| ISO/IEC 19510 (BPMN) | `_ccf_bpmn` |
| ISO/IEC 25010 | `_cst_iso25010` |
| ISO/IEC/IEEE 29119 | `_cst_iso29119` |
| ISO/IEC 19505 (UML) | `_dat_uml` |
| ISO/IEC/IEEE 42010 | `_dat_iso42010` |

### Par format de sortie

Les prompts produisent tous des fichiers **Markdown (.md)** avec :
- Diagrammes **Mermaid** (sauf mention contraire)
- Tableaux structurés
- Navigation interne (TOC, liens)
- Compatible VS Code / Obsidian

---

## Ressources complémentaires

### Fichiers de référence dans `.claude/prompts/`

- `TypesDeDocumentsDAnalyse.md` — Description détaillée des types de documents
- `REGLES_MERMAID.md` — Syntaxe et règles Mermaid
- `INDEX_PROMPTS_NORMES.md` — Index matriciel complet
- `_prompt_reponses.md` — Guide de réponse

### Références externes

- [SemVer](https://semver.org/) — Versioning sémantique
- [ISO standards](https://www.iso.org/) — Normes ISO officielles
- [AFNOR](https://www.afnor.org/) — Normes françaises
- [The Open Group](https://www.opengroup.org/archimate) — ArchiMate
- [C4 Model](https://c4model.com/) — Simon Brown
- [Arc42](https://arc42.org/) — Template d'architecture

---

*Document généré automatiquement — Dernière mise à jour : 2026-03-19*
