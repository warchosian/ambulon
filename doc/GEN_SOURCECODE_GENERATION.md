Ah, je comprends beaucoup mieux maintenant ! Vous ne parlez pas de reverse engineering binaire (crack, malware, assembleur), mais d'**outils d'analyse de code source** et de **génération de documentation** pour comprendre ou documenter une base de code existante (souvent appelé "rétro-documentation" ou compréhension de code).

Voici les outils dans cette catégorie, similaires à `pydoc` et `Sphinx` :

### 1. Générateurs de Documentation (Alternatives à Sphinx/Pydoc)
Ces outils lisent le code source et les docstrings pour créer une documentation navigable.

*   **MkDocs (avec mkdocstrings)** : (Python) Très populaire actuellement. Plus simple et moderne que Sphinx. Il génère un site statique rapide à partir des fichiers Markdown et du code.
*   **Pdoc** : (Python) Une alternative légère à Sphinx. Il génère automatiquement une documentation HTML à partir des docstrings sans configuration complexe.
*   **Doxygen** : (Multi-langages : C++, Java, Python, etc.) Le standard industriel pour générer de la documentation à partir de code commenté. Très puissant pour les gros projets non-Python.
*   **JSDoc** : (JavaScript/TypeScript) L'équivalent de pydoc pour l'écosystème JS.
*   **Godoc** : (Go) Outil natif pour générer la documentation du langage Go.

### 2. Outils de Compréhension et Visualisation de Code
Ces outils aident à "reverse engineer" la logique d'un projet source en créant des graphes ou en naviguant dans les dépendances.

*   **SciTools Understand** : (Payant) C'est l'outil le plus proche du "reverse engineering" mais pour du **code source**. Il crée des graphes de flux, des cartes de dépendances, et permet de naviguer dans des millions de lignes de code pour comprendre l'architecture.
*   **Sourcegraph** : (Freemium/Open Source) Moteur de recherche de code. Permet de naviguer dans les définitions, les références et les dépendances à travers plusieurs dépôts.
*   **Pyan** : (Python) Génère des graphes d'appels (call graphs) à partir de code Python pour visualiser quelles fonctions appellent quelles autres.
*   **Code2Flow** : (Multi-langages) Transforme le code source en diagrammes de flux visuels.
*   **Gource** : (Open Source) Visualise l'historique du projet (git) sous forme d'arbre animé pour voir qui a modifié quoi et quand.

### 3. Analyse Statique et Qualité (Pour comprendre la structure)
Ces outils analysent le code pour en extraire des métriques, détecter des smells ou vérifier la conformité.

*   **SonarQube** : (Open Source/Entreprise) Analyse la qualité du code, détecte les bugs potentiels, les vulnérabilités et la "dette technique". Très utile pour auditer une base de code inconnue.
*   **Pylint / Flake8** : (Python) Analysent le code pour vérifier le respect des standards (PEP8) et détecter les erreurs potentielles.
*   **Lizard** : (Multi-langages) Analyse la complexité cyclomatique du code (pour identifier les fonctions trop complexes à maintenir).

### 4. IDE et Navigation (Outils quotidiens)
Souvent, le meilleur outil pour "reverse engineer" du code source est un IDE puissant.

*   **JetBrains (PyCharm, IntelliJ, CLion)** : Leurs fonctionnalités de "Find Usages", "Call Hierarchy" et "Structure View" sont essentielles pour comprendre un projet rapidement.
*   **Visual Studio Code** : Avec des extensions comme "Python", "C#", etc., il offre une bonne navigation de symbole.

### Résumé pour votre besoin
Si vous voulez documenter ou comprendre du code Python comme le font `pydoc` et `Sphinx` :
1.  **Pour la doc :** Utilisez **MkDocs** (plus moderne) ou **Pdoc** (plus rapide).
2.  **Pour comprendre l'architecture :** Utilisez **SciTools Understand** (si budget) ou les graphes d'appels de **PyCharm**.
3.  **Pour l'analyse qualité :** Utilisez **SonarQube**.