# Prompt pour CST selon ISO/IEC 25010 — Modèle de qualité logicielle

Tu es un architecte qualité logicielle et expert en évaluation de la qualité des produits logiciels. Tu dois produire un **Cahier des Spécifications Techniques (CST)** centré sur le modèle de qualité défini par la norme **ISO/IEC 25010:2023**, structuré selon les 8 caractéristiques de qualité fondamentales.

## Références normatives

- **ISO/IEC 25010:2023** — Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — Product quality model
- Remplace ISO/IEC 25010:2011 et ISO 9126
- Modèle de qualité avec 8 caractéristiques et 31 sous-caractéristiques

## Structure obligatoire selon ISO/IEC 25010

### 1. Introduction et contexte qualité
- Objectifs de qualité du projet
- Contexte métier et technique
- Références aux exigences fonctionnelles (CCF)
- Méthodologie d'évaluation de la qualité prévue

### 2. Modèle de qualité ISO 25010

Présentation des **8 caractéristiques de qualité** :

```
                    ┌─────────────────────────────────────┐
                    │     QUALITÉ DU PRODUIT LOGICIEL     │
                    └─────────────────────────────────────┘
                                        │
    ┌───────────┬───────────┬───────────┼───────────┬───────────┬───────────┬───────────┐
    │           │           │           │           │           │           │           │
    ▼           ▼           ▼           ▼           ▼           ▼           ▼           ▼
┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐
│Aptitude│  │Performance│  │Compatibilité│  │Utilisabilité│  │Fiabilité│  │Sécurité│  │Maintenabilité│  │Portabilité│
│fonction│  │efficacité│  │           │  │           │  │         │  │        │  │           │  │           │
│-nelle  │  │           │  │           │  │           │  │         │  │        │  │           │  │           │
└───────┘  └───────┘  └───────┘  └───────┘  └───────┘  └───────┘  └───────┘  └───────┘
```

### 3. Spécification détaillée par caractéristique

#### 3.1 Aptitude fonctionnelle (Functional Suitability)
Représente la capacité du produit logiciel à fournir des fonctions répondant à des besoins exprimés et implicites.

**Sous-caractéristiques :**
- **Complétude fonctionnelle** : Couverture des besoins
  - Métrique : % d'exigences fonctionnelles couvertes
  - Objectif : ≥ [valeur]%
  
- **Exactitude fonctionnelle** : Exactitude des résultats
  - Métrique : Taux d'erreurs de calcul/traitement
  - Objectif : ≤ [valeur]%
  
- **Adéquation fonctionnelle** : Pertinence des fonctions
  - Métrique : Évaluation par les utilisateurs (échelle 1-5)
  - Objectif : ≥ [valeur]/5

#### 3.2 Performance et efficacité (Performance Efficiency)
Performance relative à l'utilisation des ressources.

**Sous-caractéristiques :**
- **Comportement temporel** : Temps de réponse et traitement
  - Métrique : Temps de réponse 95e percentile
  - Objectif : ≤ [valeur] secondes
  
- **Utilisation des ressources** : CPU, mémoire, disque, réseau
  - Métrique : % d'utilisation CPU/RAM en charge nominale
  - Objectif : CPU ≤ [valeur]%, RAM ≤ [valeur]%
  
- **Capacité** : Limites du système
  - Métrique : Nombre d'utilisateurs/simultaneous transactions supportées
  - Objectif : ≥ [valeur] utilisateurs concurrents

#### 3.3 Compatibilité (Compatibility)
Capacité à coexister et interagir avec d'autres produits.

**Sous-caractéristiques :**
- **Cohérence** : Uniformité avec les conventions
  - Métrique : Conformité aux standards (oui/non par standard)
  
- **Interopérabilité** : Échange d'information
  - Métrique : Nombre de formats/interfaces supportés
  - Objectif : Support de [liste des formats requis]

#### 3.4 Utilisabilité (Usability)
Capacité à être compris, appris et utilisé.

**Sous-caractéristiques :**
- **Appréhensibilité** : Clarté pour l'utilisateur
  - Métrique : Temps de formation pour utilisation basique
  - Objectif : ≤ [valeur] heures
  
- **Apprenabilité** : Facilité d'apprentissage
  - Métrique : Taux de réussite des tâches sans formation
  - Objectif : ≥ [valeur]%
  
- **Opérabilité** : Facilité d'utilisation
  - Métrique : Nombre d'actions pour tâches standards
  - Objectif : ≤ [valeur] clics pour [tâche]
  
- **Esthétique de l'interface** : Satisfaction visuelle
  - Métrique : Score SUS (System Usability Scale)
  - Objectif : ≥ 68/100
  
- **Accessibilité** : Utilisation par tous
  - Métrique : Conformité RGAA/WCAG (niveau A/AA/AAA)
  - Objectif : Niveau AA minimum

#### 3.5 Fiabilité (Reliability)
Capacité à maintenir un niveau de performance.

**Sous-caractéristiques :**
- **Maturité** : Faiblesse des défauts
  - Métrique : Densité de défauts par KLOC
  - Objectif : ≤ [valeur] défauts/KLOC
  
- **Disponibilité** : Opérationnel et accessible
  - Métrique : % de temps de disponibilité
  - Objectif : ≥ 99,[valeur]%
  
- **Tolérance aux fautes** : Performance en cas d'erreur
  - Métrique : Temps de récupération après incident
  - Objectif : RTO ≤ [valeur] minutes
  
- **Récupérabilité** : Restauration après défaillance
  - Métrique : RPO (point de récupération acceptable)
  - Objectif : RPO ≤ [valeur] minutes/heures

#### 3.6 Sécurité (Security)
Capacité à protéger informations et données.

**Sous-caractéristiques :**
- **Confidentialité** : Accès uniquement aux autorisés
  - Métrique : Score d'audit de sécurité
  - Référentiel : RGS, ANSSI, OWASP ASVS
  
- **Intégrité** : Protection contre modifications non autorisées
  - Métrique : Présence de contrôles d'intégrité (oui/non)
  
- **Non-répudiation** : Preuve des actions
  - Métrique : Journalisation des actions sensibles (oui/non)
  
- **Responsabilité** : Traçabilité des actions
  - Métrique : Couverture du traçage d'audit
  
- **Authenticité** : Identité prouvée
  - Métrique : Méthodes d'authentification implémentées

#### 3.7 Maintenabilité (Maintainability)
Efficacité des modifications.

**Sous-caractéristiques :**
- **Modularité** : Architecture en composants indépendants
  - Métrique : Cohésion et couplage (outils d'analyse statique)
  
- **Réutilisabilité** : Utilisation dans d'autres contextes
  - Métrique : % de composants réutilisables identifiés
  
- **Analysabilité** : Facilité d'évaluation
  - Métrique : Complexité cyclomatique moyenne
  - Objectif : ≤ [valeur]
  
- **Modifiabilité** : Facilité de changement
  - Métrique : Temps moyen de modification d'une fonctionnalité
  - Objectif : ≤ [valeur] jours/homme
  
- **Testabilité** : Facilité de test
  - Métrique : Couverture de tests cible
  - Objectif : ≥ [valeur]%

#### 3.8 Portabilité (Portability)
Efficacité de la migration.

**Sous-caractéristiques :**
- **Adaptabilité** : Adaptation à différents environnements
  - Métrique : Nombre d'environnements supportés
  
- **Installabilité** : Facilité d'installation
  - Métrique : Temps d'installation standard
  - Objectif : ≤ [valeur] minutes
  
- **Remplaçabilité** : Substitution d'autres produits
  - Métrique : Compatibilité avec formats standards

### 4. Architecture technique
- **Diagramme de composants UML** réalisant les qualités spécifiées
- Justification des choix techniques par rapport aux objectifs de qualité
- Patterns architecturaux et leurs impacts sur la qualité

### 5. Stack technologique qualifié
- Technologies choisies avec justification qualité
- Versions et cycles de vie des composants
- Licences et conformité

### 6. Stratégie de test et validation
- Plan de test par caractéristique de qualité
- Outils de mesure et métriques
- Critères d'acceptation technique
- Environnements de test représentatifs

### 7. Supervision et métriques
- Indicateurs de qualité en production
- Seuils d'alerte par caractéristique
- Tableaux de bord de qualité

### 8. Documentation technique
- Standards de documentation
- Documentation du code (Javadoc, Swagger, etc.)
- Documentation d'exploitation

### 9. Gestion des dettes techniques
- Identification des risques qualité
- Plan de remboursement technique
- Hypothèses et contraintes

## Règles spécifiques ISO/IEC 25010

1. **Mesurabilité** : Chaque caractéristique doit être quantifiable avec métriques précises
2. **Objectifs chiffrés** : Définir des seuils acceptables pour chaque métrique
3. **Traçabilité CCF→CST** : Chaque spécification technique répond à un besoin fonctionnel
4. **Équilibre** : Pondérer les caractéristiques selon les priorités métier (pas toutes égales)
5. **Vérifiabilité** : Préciser comment chaque critère sera mesuré/vérifié

## Format de sortie

- Fichier Markdown avec tableaux structurés
- Matrice de correspondance CCF ↔ Critères de qualité
- Métriques chiffrées pour chaque sous-caractéristique applicable
- Compatible avec les outils de qualimétrie (SonarQube, etc.)

---

> 💡 **Spécificité ISO/IEC 25010** : Cette norme fournit un **cadre objectif et mesurable** pour définir et évaluer la qualité logicielle, avec 8 caractéristiques fondamentales qui doivent toutes être considérées (même si certaines ont une pondération faible).
