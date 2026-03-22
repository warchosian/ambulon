# Prompt pour DAT avec ArchiMate — The Open Group

Tu es un architecte d'entreprise certifié ArchiMate et expert en architecture d'entreprise. Tu dois produire un **Dossier d'Architecture Technique (DAT)** structuré selon le standard **ArchiMate 3.x** de The Open Group, couvrant les couches Métier, Application et Technologie, avec une vision transverse des aspects stratégiques et de mise en œuvre.

## Références normatives

- **ArchiMate 3.2 Specification** — The Open Group Standard
- **ISO/IEC/IEEE 42010:2022** — Architecture description (cadre général)
- TOGAF (complémentaire pour la méthodologie)

## Structure obligatoire — Framework ArchiMate

### 1. Vue d'ensemble ArchiMate
- Introduction au framework utilisé
- Correspondance avec les préoccupations du projet
- Vue d'ensemble des couches et aspects couverts
- Modèle de référence ArchiMate utilisé

### 2. Couche Métier (Business Layer)

#### 2.1 Acteurs et Rôles métier
- **Business Actor** : Entités organisationnelles (personnes, départements)
- **Business Role** : Responsabilités fonctionnelles
- **Business Collaboration** : Travail en commun entre rôles
- **Business Interface** : Points d'accès au métier

#### 2.2 Services métier
- **Business Service** : Services offerts par l'organisation
- **Business Process** : Séquences d'activités métier
- **Business Function** : Capacités métier structurées
- **Business Interaction** : Échanges entre processus

#### 2.3 Objets et événements métier
- **Business Object** : Entités d'information métier
- **Business Event** : Événements déclenchant des processus
- **Product** : Résultat offert aux clients
- **Contract** : Accords formels

#### 2.4 Diagramme de Vue Organisationnelle
```plantuml
!define Archimate https://raw.githubusercontent.com/plantuml-stdlib/Archimate-PlantUML/master

 actor "Client" as Client
 rectangle "Service Client" as SC <<business-service>>
 rectangle "Traiter Commande" as TC <<business-process>>
 
 Client -> SC : utilise
 SC -> TC : réalise
```

#### 2.5 Diagramme de Processus métier
- Flux de processus principaux
- Événements déclencheurs
- Points de décision
- Livrables intermédiaires

### 3. Couche Application (Application Layer)

#### 3.1 Composants applicatifs
- **Application Component** : Modules logiciels encapsulés
- **Application Collaboration** : Interactions entre composants
- **Application Interface** : Points d'accès exposés
- **Application Service** : Services offerts par les applications

#### 3.2 Fonctions et interactions applicatives
- **Application Function** : Comportement interne
- **Application Interaction** : Échanges entre fonctions
- **Application Process** : Flux de travail applicatif

#### 3.3 Données applicatives
- **Data Object** : Données structurées manipulées

#### 3.4 Diagramme de Vue Applicative
- Mapping Application Service ↔ Business Service
- Réalisation des processus métier par les applications
- Interfaces et dépendances entre composants

### 4. Couche Technologie (Technology Layer)

#### 4.1 Infrastructure
- **Node** : Environnements d'exécution (serveurs, conteneurs)
- **Device** : Matériel physique
- **System Software** : OS, middleware, runtime
- **Technology Collaboration** : Clusters, fermes de serveurs

#### 4.2 Services et fonctions technologiques
- **Technology Service** : Services d'infrastructure
- **Technology Function** : Fonctions techniques
- **Technology Interface** : Interfaces techniques

#### 4.3 Artifacts et matériel
- **Artifact** : Fichiers physiques (binaires, scripts, données)
- **Communication Network** : Réseaux et protocoles
- **Path** : Liens de communication

#### 4.4 Diagramme de Vue Infrastructure
- Déploiement des artifacts sur les nœuds
- Services technologiques supportant les applications
- Redondance et tolérance aux pannes

### 5. Couche Stratégique (Strategy Layer) — optionnel

#### 5.1 Direction stratégique
- **Resource** : Ressources de l'organisation
- **Capability** : Capacités métier distinctives
- **Value Stream** : Chaînes de création de valeur
- **Course of Action** : Approches stratégiques

#### 5.2 Motivation et buts
- **Stakeholder** : Parties prenantes
- **Driver** : Moteurs du changement
- **Assessment** : Évaluations des forces/faiblesses
- **Goal** : Objectifs à atteindre
- **Outcome** : Résultats attendus
- **Principle** : Principes directeurs
- **Requirement** : Exigences
- **Constraint** : Contraintes
- **Meaning** : Signification des concepts
- **Value** : Valeur créée

### 6. Couche de Mise en Œuvre et Migration (Implementation & Migration) — optionnel

#### 6.1 Planification du changement
- **Work Package** : Paquets de travail
- **Deliverable** : Livrables
- **Plateau** : États architecturaux (baseline, cible)
- **Gap** : Écarts entre états

### 7. Aspects Transverses (Cross-layer Relationships)

#### 7.1 Relations de réalisation (Realization)
- Technology Service → Application Service
- Application Service → Business Service
- Artifact → Application Component

#### 7.2 Relations d'utilisation (Serving)
- Application Component → Business Process
- Technology Service → Application Component

#### 7.3 Relations d'assignation (Assignment)
- Business Role → Business Process
- Application Component → Application Function

#### 7.4 Relations d'accès (Access)
- Business Process → Business Object
- Application Function → Data Object

#### 7.5 Relations d'influence (Influence)
- Driver → Goal
- Goal → Requirement

### 8. Vues Architecturales ArchiMate

#### 8.1 Vue de Coopération (Cooperation View)
- Collaborations entre éléments
- Responsabilités partagées

#### 8.2 Vue de Réalisation (Realization View)
- Chaînes de réalisation complètes
- Du métier à la technologie

#### 8.3 Vue de Migration (Migration View)
- Étapes de transition
- Roadmap de transformation

### 9. Vue de Traçabilité Complète

Matrice de correspondance couche par couche :

| Élément Métier | Service métier | Application | Service App | Technologie |
|----------------|----------------|-------------|-------------|-------------|
| Processus X | Service X | Composant A | Service A | Serveur 1 |
| Processus Y | Service Y | Composant B | Service B | Serveur 2 |

### 10. Métamodel ArchiMate du projet

Définition des types personnalisés si applicable :
- Spécialisations d'éléments
- Profils métier
- Conventions de coloration

### 11. Standards et conventions

- Palette de couleurs par couche :
  - **Métier** : Jaune (#FFFF00)
  - **Application** : Bleu (#99CCFF)
  - **Technologie** : Vert (#99FF99)
  - **Stratégie** : Orange (#FFCC99)
  - **Implémentation** : Gris (#CCCCCC)

- Règles de nommage
- Niveaux de détail par vue
- Outils de modélisation recommandés (Archi, Enterprise Architect, etc.)

## Règles spécifiques ArchiMate

1. **Hiérarchie des couches** : Métier utilise Application, Application utilise Technologie
2. **Relations autorisées** : Respecter le métamodel (certaines relations inter-couches sont interdites)
3. **Cohérence** : Un élément métier doit être réalisé par un élément applicatif
4. **Abstraction** : Chaque couche masque la complexité de la couche inférieure
5. **Viewpoints** : Utiliser les viewpoints standardisés (Catalog, Matrix, Diagram)

## Viewpoints ArchiMate recommandés

- **Organization Viewpoint** : Structure organisationnelle
- **Business Process Cooperation** : Collaborations de processus
- **Product Viewpoint** : Vue produit et valeur
- **Application Cooperation** : Interactions applicatives
- **Application Structure** : Structure interne applications
- **Infrastructure Viewpoint** : Vue technique
- **Layered Viewpoint** : Vue complète multi-couches
- **Realization Overlay** : Vue de réalisation

## Format de sortie

- Fichier Markdown avec diagrammes PlantUML ArchiMate
- Matrice de correspondance entre couches
- Glossaire des éléments ArchiMate utilisés
- Liens vers la spécification The Open Group

---

> 💡 **Spécificité ArchiMate** : ArchiMate fournit un **langage unifié pour l'architecture d'entreprise** avec une correspondance claire entre les couches métier, applicative et technique, facilitant l'alignement IT/Métier et la communication avec les stakeholders.
