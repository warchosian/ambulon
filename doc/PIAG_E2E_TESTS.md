# Test de bout en bout du PIAG

Option 2 : Fichier de configuration

  Le test charge automatiquement depuis config/piag.yaml ou config/piag.yml si ces variables ne sont pas définies.

  🎯 Ce que le Test E2E va Faire

  Le test exécute un workflow complet :
  1. ✅ Créer une collection
  2. ✅ Mettre à jour la collection
  3. ✅ Vérifier la mise à jour
  4. ✅ Uploader un document
  5. ✅ Lister les documents
  6. ✅ Récupérer les chunks du document
  7. ✅ Rechercher dans la collection
  8. ✅ Récupérer le document par ID
  9. ✅ Supprimer le document
  10. ✅ Vérifier la suppression
  11. ✅ Supprimer la collection (cleanup)

  ⏱️ Durée Estimée

  Environ 15-30 secondes (dépend de la latence réseau vers l'API PIAG)

  ✅ config/piag.yml est COMPLET et contient :

  | Section         | Status | Contenu                                        |
  |-----------------|--------|------------------------------------------------|
  | api             | ✅     | base_url, version, timeout, max_retries        |
  | endpoints       | ✅     | Tous les endpoints définis                     |
  | project         | ✅     | project_id: "your_project_id_here"             |
  | security        | ✅     | token: "eyJhbGci..." (token JWT tronqué)       |
  | headers         | ✅     | Accept, Content-Type, User-Agent               |
  | logging         | ✅     | Configuration complète                         |
  | listing         | ✅     | Paramètres de pagination                       |
  | document/upload | ✅     | Types MIME, taille max                         |
  | chunks          | ✅     | Paramètres de récupération                     |
  | search          | ✅     | Configuration RAG                              |