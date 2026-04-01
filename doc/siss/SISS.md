Voici les **spécifications techniques** de l'application **SISS**, accompagnées des **diagrammes** disponibles dans la documentation. Ces informations sont structurées selon les principes **arc42** et illustrées avec des exemples en **PlantUML**.

---

## **1. Architecture Technique**
### **1.1 Architecture Logique**
- **Backend** : Application **Java Spring Boot** embarquée dans **Tomcat 9.0.82** (JDK 11).
- **Frontend** : Inclus dans le fichier `.war` (pas de séparation explicite avec le backend).
- **Base de données** : **PostgreSQL 13.19**.
- **Stockage** : Compatible **AWS S3** pour les pièces jointes.
- **Authentification** : **SAML2** ou **stub LDAP** (pour les tests).

---

### **1.2 Architecture Physique**
- **Environnements** :
  - **Développement** : Sources locales (fichiers `.tar.bz2` copiés dans l'image Docker).
  - **Production** : Sources téléchargées depuis **Nexus Silicom** (`nexus.sro.silicom.fr`).

---

## **2. Diagrammes Techniques**
### **2.1 Diagramme de Cas d'Usage**
```plantuml
@startuml
left to right direction
actor "Utilisateur" as User
rectangle "SISS" {
  User -- (Gérer versements)
  User -- (Consulter dossiers)
  User -- (Demander restitution)
  User -- (Recevoir notifications)
  (Gérer versements) .> (Stockage PJ) : inclut
  (Recevoir notifications) .> (Envoyer email) : inclut
}
@enduml
```

---

### **2.2 Diagramme de Séquence : Authentification en Mode TEST**
```plantuml
@startuml
actor Utilisateur
participant "SISS App" as App
database "PostgreSQL" as DB

Utilisateur -> App : POST /login (user, pwd)
App -> DB : SELECT * FROM ref_utilisateur WHERE uti_login = ?
DB --> App : Utilisateur
App -> App : Valider contre authentication.stubLdap.[user].*
App --> Utilisateur : Session créée
@enduml
```

---

### **2.3 Diagramme des Composants**
```plantuml
@startuml
package "SISS Application" {
  [Tomcat 9 + SISS.war] as app
  [PostgreSQL 13] as db
  [AWS S3] as storage
  [HEDWIGE API] as mail
}

app --> db : JDBC
app --> storage : S3 API
app --> mail : HTTPS + OAuth2
@enduml
```

---

### **2.4 Diagramme de Déploiement (Environnement Dev)**
```plantuml
@startuml
node "Host Dev" {
  node "Docker Engine" {
    artifact "siss-app" as app
    artifact "siss-db" as db
  }
}
app --> db : localhost:5432
app ..> "Local FS" : ./data, ./logs
@enduml
```

---

## **3. Détail des Composants Techniques**
### **3.1 Backend**
- **Technologie** : Java Spring Boot.
- **Serveur d'application** : Tomcat 9.0.82.
- **JDK** : Version 11.

### **3.2 Base de Données**
- **SGBD** : PostgreSQL 13.19.
- **Connexion** : JDBC.

### **3.3 Stockage**
- **Pièces jointes** : Stockées sur un système compatible **AWS S3**.
- **Configuration** : Définie par `siss.pj-stockage.mode=AWS`.

### **3.4 Authentification**
- **Mode Production** : SAML2.
- **Mode Test** : Stub LDAP (simulation locale).

### **3.5 Envoi d'E-mails**
- **Intégration** : API **HEDWIGE** (service ministériel).
- **Protocole** : HTTPS + OAuth2.

---

## **4. Dette Technique**
- **Logique en dur** :
  - URLs de l'API HEDWIGE **hardcodées**.
  - Chemins de fichiers fixes (`/app/conf`, `/app/logs`).
- **Encodage** : Aucun encodage explicite → risque d'utiliser **UTF-8** par défaut.
- **Configuration** : Mélange de `application.properties`, variables d'environnement et arguments JVM.

---

## **5. Références**
- La documentation suit les principes de **arc42** :
  - Séparation stricte entre fonctionnel et technique.
  - Documentation orientée décision.
  - Diagrammes centrés sur les besoins.

---
Si tu souhaites des détails supplémentaires sur un diagramme ou une partie spécifique, fais-le-moi savoir ! Je peux également te fournir d'autres diagrammes si nécessaire.