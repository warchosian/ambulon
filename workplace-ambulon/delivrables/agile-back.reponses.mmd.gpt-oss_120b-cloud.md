# agile-back

[TOC]

---  

## 📖 Présentation du projet

**agile-back** est le back‑office de l’application *Agile* qui permet la création et la modification d’études stockées dans une base PostgreSQL.  
Le projet est développé en PHP avec le framework Symfony (architecture MVC) et s’intègre avec le front‑office *agile‑front*.

↩ [Retour au sommaire](#agile-back)

---  

## 🗂️ Arborescence simplifiée

```mermaid
graph TD
    A[config] --> B[packages]
    A --> C[routes]
    A --> D[bundles.php]
    A --> E[routes.yaml]
    A --> F[services.yaml]

    B --> B1[dev]
    B --> B2[prod]
    B --> B3[test]
    B --> B4[api_platform.yaml]
    B --> B5[doctrine.yaml]
    B --> B6[security.yaml]

    C --> C1[annotations.yaml]
    C --> C2[api_platform.yaml]
    C --> C3[dev]

    subgraph public;
        P1[cas] 
        P2[images]
        P3[js]
        P4[lib]
        P5[style]
        P6[index.php]
    end
    subgraph src;
        S1[Commandes]
        S2[Controller]
        S3[DataTransformer]
        S4[Dto]
        S5[Entity]
        S6[EventListeners]
        S7[EventSubscriber]
        S8[Form]
        S9[Repository]
        S10[Security]
        S11[Services]
        S12[util]
        S13[Kernel.php]
    end
    subgraph templates;
        T1[abonnements_admin]
        T2[bop_admin]
        T3[dotations_admin]
        T4[etudes]
        T5[etudes_admin]
        T6[financements]
        T7[groupes_admin]
        T8[includes]
        T9[profils_admin]
        T10[services_admin]
        T11[sousactions_admin]
        T12[themes_admin]
        T13[utilisateurs_admin]
        T14[valorisations]
        T15[base.html.twig]
        T16[base_admin.html.twig]
    end
    A -.-> public;
    A -.-> src;
    A -.-> templates
```

*Ce diagramme montre les principaux répertoires et leurs sous‑structures.*

↩ [Retour au sommaire](#agile-back)

---  

## ⚙️ Configuration principale

| Fichier | Rôle | Points clés |
|---|---|---|
| `config/packages/api_platform.yaml` | API Platform | Déclare les chemins de mapping (`src/Entity`, `src/Dto`), formats supportés (`json`, `html`, `csv`). |
| `config/packages/doctrine.yaml` | Doctrine ORM | Connexion PostgreSQL (`pdo_pgsql`), auto‑mapping des entités, paramètres de cache. |
| `config/packages/security.yaml` | Sécurité | Fournit un fournisseur `in_memory`, firewalls `dev` et `main`, contrôle d’accès via `access_control`. |
| `config/packages/nelmio_cors.yaml` | CORS | Autorise les origines définies par `CORS_ALLOW_ORIGIN`, méthodes HTTP, headers et expose les en‑têtes de pagination. |
| `config/packages/mailer.yaml` | Mailer | Utilise la DSN définie par `MAILER_DSN`. |
| `config/routes/annotations.yaml` | Routes | Charge les routes définies par annotations dans le répertoire `src/Controller`. |
| `config/routes/api_platform.yaml` | API Platform routes | Préfixe `/api` et désactive GraphQL UI. |
| `config/packages/dev/*` | Environnement de développement | Debug, monolog (niveau `debug`), Web Profiler activé. |
| `config/packages/prod/*` | Environnement de production | Monolog avec `fingers_crossed`, cache Doctrine configuré. |
| `config/packages/test/*` | Environnement de test | Base de données mock, désactivation du mailer, logs en fichier. |

↩ [Retour au sommaire](#agile-back)

---  

## 📦 Entités principales (Doctrine)

| Entité | Table | Attributs majeurs |
|---|---|---|
| `Abonnements` | `abonnements` | `utilisateur`, `ru`, `perimetre` |
| `Bop` | `bop` | `libelle_bop`, `commentaires_bop`, `sigle`, `visible` |
| `Dotations` | `dotations` | `anneedotation`, `montantdotation`, `groupe`, `bopid`, `sousActions` |
| `Etudes` | `etudes` | `titre_etude`, `zone_geographique`, `groupe`, `description`, `probleme`, `resultats`, `objectifs`, `methode` |
| `Financements` | `financements` | `sous_action`, `demandes_e`, `date_comite`, `ae_e`, `cp_e` |
| `Groupes` | `groupes` | `token`, `libelle` |
| `Profils` | `profils` | `nom`, `description` |
| `Services` | `services` | `service`, `direction`, `visible`, `region` |
| `SousActions` | `sous_actions` | `libelle`, `description` |
| `Themes` | `themes` | `theme` |
| `Territoires` | `territoires` | `territoire` |
| `Utilisateurs` | `utilisateurs` | `nom`, `prenom`, `email`, `groupe` |
| `Types` | `types` | `nom` |

> Chaque entité possède un repository dédié (`src/Repository/*Repository.php`) pour les requêtes personnalisées.

↩ [Retour au sommaire](#agile-back)

---  

## 🎛️ Contrôleurs (Symfony)

| Contrôleur | Fonction principale |
|---|---|
| `AbonnementsAdminController` | CRUD des abonnements (admin). |
| `BopAdminController` | Gestion des BOP (admin). |
| `DotationsAdminController` | CRUD des dotations. |
| `EtudesController` | Affichage et édition des études côté utilisateur. |
| `EtudesAdminController` | Administration des études. |
| `FinancementsController` | Gestion des financements. |
| `GroupesAdminController` | Administration des groupes. |
| `ProfilsAdminController` | Gestion des profils d’accès. |
| `ServicesAdminController` | Administration des services. |
| `SousActionsAdminController` | Gestion des sous‑actions. |
| `ThemesAdminController` | Administration des thèmes. |
| `UtilisateursAdminController` | Gestion des utilisateurs. |
| `ValorisationsController` | Export et visualisation des valorisations. |
| `SecurityController` | Authentification via CAS (phpCAS). |
| `ExportOdsDtoController` | Export ODS des DTO. |
| `Commandes/*Runner` | Scripts de mise à jour (cron). |

↩ [Retour au sommaire](#agile-back)

---  

## 🧩 Formulaires Symfony

Les formulaires sont définis dans `src/Form/*` et sont liés aux entités via le `data_class`.  

| Formulaire | Entité associée | Champs exposés |
|---|---|---|
| `AbonnementsType` | `Abonnements` | `utilisateur`, `ru`, `perimetre` |
| `BopType` | `Bop` | `libelle_bop`, `commentaires_bop`, `sigle`, `visible` |
| `DotationsType` | `Dotations` | `anneedotation`, `montantdotation`, `groupe`, `bopid`, `sousActions` |
| `EtudesType` | `Etudes` | `titre_etude`, `zone_geographique`, `groupe`, `description`, `probleme`, `resultats`, `objectifs`, `methode` |
| `FinancementsType` | `Financements` | `sous_action`, `demandes_e`, `date_comite`, `ae_e`, `cp_e` |
| `GroupesType` | `Groupes` | `token`, `libelle` |
| `ProfilsType` | `Profils` | `nom`, `description` |
| `ServicesType` | `Services` | `service`, `direction`, `visible`, `region` |
| `SousActionsType` | `SousActions` | `libelle`, `description` |
| `ThemesType` | `Themes` | `theme` |
| `UtilisateursType` | `Utilisateurs` | `nom`, `prenom`, `email`, `groupe` |

↩ [Retour au sommaire](#agile-back)

---  

## 📄 Templates Twig

Les vues sont organisées sous `templates/` :

| Dossier | Usage |
|---|---|
| `abonnements_admin/` | CRUD des abonnements (admin). |
| `bop_admin/` | Gestion des BOP. |
| `dotations_admin/` | Gestion des dotations. |
| `etudes/` | Formulaire et affichage des études. |
| `etudes_admin/` | Administration des études. |
| `financements/` | Gestion des financements. |
| `groupes_admin/` | Administration des groupes. |
| `includes/` | Fragments réutilisables (`identification.html`, `contexte.html`, `valorisation.html`, …). |
| `profils_admin/` | Gestion des profils. |
| `services_admin/` | Administration des services. |
| `sousactions_admin/` | Gestion des sous‑actions. |
| `themes_admin/` | Administration des thèmes. |
| `utilisateurs_admin/` | Gestion des utilisateurs. |
| `valorisations/` | Export CSV/ODS des valorisations. |
| `base.html.twig` & `base_admin.html.twig` | Layouts globaux (CSS/JS inclus). |

Exemple de fragment d’inclusion :

```twig
{% include 'includes/identification.html' %}
```

↩ [Retour au sommaire](#agile-back)

---  

## 🛠️ Services métier

| Service | Responsabilité |
|---|---|
| `SiteUpdateAbonnements` | Mise à jour des abonnements (cron). |
| `SiteUpdateAlertes` | Gestion des alertes système. |
| `SiteUpdateMailer` | Envoi d’emails (notifications). |
| `SiteUpdateMailerByProfils` | Envoi ciblé d’emails selon les profils. |
| `Valorisation` | Génération et export des valorisations (CSV/ODS). |

Ces services sont appelés depuis les contrôleurs ou via les *Commandes* Symfony (ex. `ValorisationRunner.php`).

↩ [Retour au sommaire](#agile-back)

---  

## 🔐 Authentification CAS

Le projet utilise **phpCAS** (dans `public/cas/`) :

* Le fichier `public/cas/connexionCAS.php` initialise le client CAS.
* `src/Controller/SecurityController.php` expose la route `/login` qui déclenche la redirection CAS.
* Les sessions sont gérées via PHP (`session_start()`).

Un exemple de configuration CAS (`public/cas/config_CAS.php`) définit les URL du serveur CAS et les paramètres de validation.

↩ [Retour au sommaire](#agile-back)

---  

## 📦 Déploiement & Environnements

| Environnement | Fichier de config | Particularités |
|---|---|---|
| **dev** | `config/packages/dev/*` | Monolog `debug`, Web Profiler actif, dump server. |
| **prod** | `config/packages/prod/*` | Monolog `fingers_crossed`, caches Doctrine, logs sur `stderr`. |
| **test** | `config/packages/test/*` | `swiftmailer` désactivé, `framework.test` à `true`, stockage de session mock. |

Le fichier `.env` (ou `.env.local`) doit contenir :

```
DATABASE_URL=postgresql://user:pwd@host:5432/dbname
MAILER_DSN=smtp://user:pwd@mailhost:25
CORS_ALLOW_ORIGIN=^https?://(localhost|mydomain\.com)$
```

↩ [Retour au sommaire](#agile-back)

---  

## 🧪 Tests

* **PHPUnit** est configuré via `phpunit.xml.dist`.  
* Le bootstrap `tests/bootstrap.php` charge les variables d’environnement et le autoloader.  
* Aucun test n’est fourni dans l’arborescence actuelle, mais le framework Symfony est prêt à exécuter des tests fonctionnels et unitaires.

↩ [Retour au sommaire](#agile-back)

---  

## 📚 Documentation et ressources complémentaires

| Ressource | Description |
|---|---|
| `README.md` | Présentation succincte du projet. |
| `public/cas/CAS_v135/README.md` | Documentation du client phpCAS. |
| `templates/emails/emails.html.twig` | Modèle d’email utilisé par les services de messagerie. |
| `public/images/favicons/` | Icônes de l’application. |
| `public/js/` | Scripts JavaScript (onglets, affichage détail, impression). |
| `public/style/` | Feuilles de style CSS (`agile-composants.css`, `main.css`). |

↩ [Retour au sommaire](#agile-back)

---  

## 📦 Installation rapide (Docker)

```yaml
# docker-compose.yml (exemple minimal)
version: "3.8"
services:
  php:
    image: php:8.2-fpm
    working_dir: /var/www/html
    volumes:
      - ./:/var/www/html
    environment:
      - DATABASE_URL=postgresql://agile:secret@db:5432/agile
      - MAILER_DSN=smtp://mailer:25
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./public:/var/www/html/public
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - php
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: agile
      POSTGRES_USER: agile
      POSTGRES_PASSWORD: secret
```

```bash
docker compose up -d
# Install dependencies
docker compose exec php composer install
# Run migrations
docker compose exec php php bin/console doctrine:migrations:migrate
# Accéder à l’application
open http://localhost
```

↩ [Retour au sommaire](#agile-back)

---  

## 🛡️ Points d’attention & bonnes pratiques

| Sujet | Recommandation |
|---|---|
| **Sécurité CAS** | Vérifier la configuration du certificat (`public/cas/certificat/`) et activer la validation du certificat (`$client->setCasServerCACert($certPath);`). |
| **CORS** | Restreindre `CORS_ALLOW_ORIGIN` aux domaines autorisés uniquement. |
| **Gestion des erreurs** | Activer le `web_profiler` uniquement en dev, et configurer un handler Monolog de type `errorlog` en prod. |
| **Performance** | Activer le cache Doctrine (`metadata_cache_driver`, `query_cache_driver`) en prod comme indiqué dans `config/packages/prod/doctrine.yaml`. |
| **Tests** | Ajouter des tests fonctionnels pour chaque contrôleur et des tests unitaires sur les services critiques (`Valorisation`, `SiteUpdateMailer`). |
| **Migrations** | Utiliser les migrations Doctrine (`src/Migrations/`) pour versionner les changements de schéma. |
| **Internationalisation** | Le projet ne contient pas de fichiers de traduction ; envisager d’ajouter le composant `symfony/translation` si besoin. |

↩ [Retour au sommaire](#agile-back)  