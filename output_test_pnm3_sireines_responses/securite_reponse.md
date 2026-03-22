D'après le contexte documentaire fourni, voici les mécanismes d'**authentification et d'autorisation** implémentés dans **SIREINES** :

### **1. Authentification**
- **Protocole** : **SAML 2.0** via **Cerbère** (Central Authentication Service - CAS).
  - Intégration d'un **SSO (Single Sign-On)** avec Cerbère pour une authentification unique.
  - Vérification via un **test de connexion** depuis le portail agent.
- **Gestion des sessions** :
  - Sessions **HTTP côté serveur** (implémentées avec **Struts 2**).
  - **Timeout de session** : Déconnexion automatique après **30 minutes d'inactivité**.
- **Déconnexion** :
  - Redirection vers **Cerbère** pour une déconnexion centralisée (SSO logout).

### **2. Autorisation (Contrôle d'accès)**
- **Modèle RBAC (Role-Based Access Control)** basé sur les rôles définis dans **Cerbère** :
  - **Rôles disponibles** :
    - **ADMIN** (administrateur technique)
    - **GESTIONNAIRE**
    - **RAPPORTEUR**
    - **AGENT** (mentionné dans le CCTP, mais pas dans les extraits DAT)
  - **Matrice des droits** : Documentée et vérifiée pour s'assurer que chaque rôle a les permissions appropriées.
- **Contrôles d'accès techniques** :
  - Utilisation d'annotations comme **`@Secured`** (visible dans les extraits de code comme `SeanceAffectationAction`).
  - Filtrage des sessions via **`SireinesSessionFilter`**.
  - Intégration avec **`CerbereUtil`** pour valider les droits via Cerbère.

### **3. Sécurité des mots de passe (pour les comptes techniques)**
- **Exigences pour les mots de passe administrateur** :
  - **12 caractères minimum**.
  - **Complexité** : Majuscules, minuscules, chiffres et **caractères spéciaux**.
  - Vérification par **audit de configuration**.

---
### **Synthèse des mécanismes clés**
| **Aspect**               | **Implémentation**                                                                 |
|--------------------------|------------------------------------------------------------------------------------|
| **Authentification**     | SAML 2.0 / CAS (Cerbère), SSO, sessions HTTP (Struts 2), timeout 30 min.            |
| **Autorisation**         | RBAC (rôles : Admin, Gestionnaire, Rapporteur, Agent), `@Secured`, `SireinesSessionFilter`. |
| **Déconnexion**          | Redirection SSO vers Cerbère.                                                      |
| **Sécurité des mots de passe** | Règles strictes (12+ caractères, complexité) pour les comptes techniques.      |

---
### **Références documentaires**
- **Extrait 1/2/3** : Détail technique sur SAML, Cerbère, Struts 2 et RBAC.
- **Extrait 4 (CCTP)** : Spécifications des rôles, timeout de session et complexité des mots de passe.
- **Extrait 6/7** : Mise en œuvre technique (`@Secured`, `SireinesSessionFilter`, `CerbereUtil`).