# Script temporaire pour patcher cli.py

with open('src/app/cli/cli.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_text = '''    print("  ambulon mcp                         Démarrer le serveur MCP")
    print("  ambulon gitlab-clone                Cloner les projets configurés")
    print("  ambulon gitlab-monofile G:\\repos\\my-project")
    print()
    print("Pour plus d'informations sur un module spécifique:")
    print("  ambulon [MODULE] --help")'''

new_text = '''    print("  ambulon mcp                         Démarrer le serveur MCP")
    print("  ambulon gitlab-clone                Cloner les projets configurés")
    print("  ambulon gitlab-monofile G:\\repos\\my-project")
    print()
    print("Exemples RAG PIAG:")
    print("  ambulon piag-rag-create --collection-name 'MonRAG' --desc 'Docs'         Collection vide")
    print("  ambulon piag-rag-create --collection-name 'MonRAG' --directory ./docs    Avec documents")
    print("  ambulon piag-rag-collection-list                                         Lister collections")
    print("  ambulon piag-rag-doc-list --collection-name 'MonRAG'                     Lister documents")
    print("  ambulon piag-rag-search --collection-name 'MonRAG' --query 'question'    Rechercher")
    print("  ambulon piag-chat-query --collection-name 'MonRAG' --query 'question'    Chat avec RAG")
    print()
    print("Pour plus d'informations sur un module spécifique:")
    print("  ambulon [MODULE] --help")'''

if old_text in content:
    content = content.replace(old_text, new_text)
    with open('src/app/cli/cli.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patch appliqué avec succès!")
else:
    print("Texte à remplacer non trouvé")
