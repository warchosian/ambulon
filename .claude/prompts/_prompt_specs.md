À partir uniquement des fichiers fournis produis un document Markdown unique intitulé :
« Spécification fonctionnelle et technique de l'application [nom-de-l'applcation] »
Ce document doit être autoporté, prêt à être rendu dans VS Code ou Obsidian (avec support PlantUML activé), sans dépendances externes, et sans aucune hypothèse ni donnée externe.
Il doit respecter les exigences suivantes :
1. Portée, domaine et périmètre
Définir clairement le domaine applicatif (archivage physique),
Préciser le contexte opérationnel (site SIT_ID = 29, base Oracle prep37),
Expliciter le périmètre fonctionnel (ce qui est inclus : versements, demandes, mouvements ; ce qui est exclu : patients, facturation, workflow avancé).
2. Structure alignée arc42 & ISO/IEC/IEEE 29148
Le document doit découpler rigoureusement :

Partie fonctionnelle :
→ Acteurs, cas d’usage, règles métier, workflows critiques.
→ Modéliser les règles complexes (ex. formatage des dates, mapping des salles) avec :
Tableaux de décision,
Diagrammes de séquence,
Formules conditionnelles,
Diagrammes en swimlane (si pertinent),
Scénarii variés pour décrire les cas d'usage les plus fréquents 

Partie technique :
→ Architecture logique et physique, modules, flux de données, dépendances, déploiements.
→ Analyse de la sécurité (données sensibles, secrets, accès).
→ Identification de la dette technique (encodage, logique en dur, etc.).
3. Qualité de la documentation
Très structuré (titres, sous-titres, sommaire cliquable),
Pédagogique (explications claires, exemples concrets),
Illustré avec de nombreux diagrammes PlantUML pertinents :
Cas d’usage,
Séquence,
Composants,
Déploiement,
États,
Classes (schéma relationnel simplifié).
4. Navigation et liens
Tous les diagrammes et sections doivent être reliés par hyperliens internes (ex. « ↩ Retour au sommaire »),
Lien externe vers la documentation arc42 (https://arc42.org) si utile,
Aucun lien brisé, aucun fichier externe requis.
5. Format de sortie
Un seul fichier .md,
Syntaxe PlantUML valide (@startuml / @enduml),
Compatible avec les extensions VS Code / Obsidian (ex. Markdown Preview Enhanced, PlantUML).