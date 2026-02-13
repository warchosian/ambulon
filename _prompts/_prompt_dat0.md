Tu es un expert en architecture logicielle. À partir des principes du modèle **Arc42**, tu dois produire un **Dossier d’Architecture Technique (DAT)** complet, clair, orienté utilisateurs et adapté à toute application logicielle.

Le document doit suivre strictement la structure ci-dessous, avec un langage professionnel mais accessible, des sections concises et des exemples concrets là où cela est utile.

**Consignes générales :**
 - Utilise le format Markdown.
 - Chaque section doit être autoportée : pas de référence à des fichiers externes sauf si explicitement demandé.
 - Les parties liées aux **objectifs de qualité**, **parties prenantes**, **contraintes**, **contexte**, **stratégie de solution**, **sujets transverses**, **exigences de qualité**, **risques et dettes techniques** doivent être formulées de manière générique, modulable par l’utilisateur final.
 - La section **Vue Déploiement** est **standardisée** et **doit être reproduite telle quelle**, sauf pour les tableaux d’environnements qui peuvent être adaptés dynamiquement.

**Structure attendue :**

1. **Introduction et objectifs**  
    - Vue d’ensemble fonctionnelle courte + schéma C4-L1 (textuel ou Mermaid).  
    - 3 à 5 objectifs de qualité orientés utilisateur (ex: performance, sécurité, maintenabilité, accessibilité, opérabilité).

2. **Parties prenantes**  
    - Tableau avec Rôle / Contact / Attentes.

3. **Contraintes**  
    - Contraintes d’architecture (techniques, organisationnelles, réglementaires).  
    - Contraintes de sécurité selon le modèle D-I-C-T (Disponibilité, Intégrité, Confidentialité, Traçabilité).

4. **Contexte et périmètre**  
    - Contexte métier : partenaires de communication fonctionnels.  
    - Contexte technique : interfaces externes (protocole, fréquence, type).

5. **Stratégie de solution**  
    - Modèles de conception / décisions architecturales majeures.  
    - Environnement technologique (langage, framework, base de données, frontend, infra).  
    - Forge logicielle (CI/CD, outils de tests, dépôt).

6. **Vue en Briques**  
    - Vue conteneur (C4-L2) textuelle ou Mermaid.  
    - Description des conteneurs principaux.

7. **Vue Exécution**  
    - 1 à 3 scénarios critiques ou complexes illustrés (description textuelle ou diagramme de séquence).

8. **Vue Déploiement** *(section standardisée)*  
    Reproduis **exactement** ce qui suit, sauf pour le tableau "Environnements" qui peut être personnalisé :

    ```markdown
    ### Environnements
    | Environnement | Hébergement | Serveurs | Réseau | Particularités |
    |---------------|-------------|----------|--------|----------------|
    | Développement | À compléter | À compléter | À compléter | À compléter |
    | Recette       | À compléter | À compléter | À compléter | À compléter |
    | Production    | À compléter | À compléter | À compléter | À compléter |

    ### Infrastructure
    Le produit est hébergé sur le cloud interne ECO4 basé sur Openstack, dans le tenant 'pnm3' du département.  
    Le reverse-proxy Nginx du schéma ci-dessous est en fait une paire de Nginx load-balancés en frontal des produits hébergés sur le tenant.

    ```mermaid
    graph TD
        A[Nginx] -- B[Application]
        B -- C[Base de données]
        B -- D[Autres services]
    ```

    ### Supervision
    Le produit est supervisé via le système standard du GTI pour ce faire :
    - via Portainer pour la partie purement conteneurisée,
    - via la stack Prometheus/Grafana/Loki/AlertManager,
    - Le produit dispose également d'une supervision PSIN.

    ### Sauvegardes
    Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en AES-256 et déposés sur :
    - le stockage objet B3 du IaaS ministériel,
    - le stockage objet Outscale SecNumCloud (via la prestation qu'a le GTI sur le marché "Nuage Public"),
    - le stockage objet standard de Google Cloud (via la prestation qu'a le GTI sur le marché "Nuage Public").
    ```

 9. **Sujets transverses**  
    - Authentification, journalisation, monitoring, gestion des erreurs, API, etc.

 10. **Exigences de qualité**  
     - Tableau exigence / scénario de validation.

 11. **Risques et Dettes techniques**  
     - Tableau risque / impact / mesure corrective.

 12. **Annexes**  
     - Glossaire  
     - Décisions d’architecture (ADR)

 **Style attendu :**
 - Privilégie les listes, tableaux et schémas Mermaid.
 - Évite les formulations vagues : sois précis, concret, orienté action.
 - Adapte le niveau de détail au public cible (développeurs, exploitants, MOA, RSSI).

 **Important :** Ne demande **aucun fichier complémentaire**. Le document doit être **autoporteur** et **générique**, prêt à être instancié pour n’importe quelle application.

