# Architecture C4 — vscodiumbench

Diagrammes C4 décrivant l'architecture du projet `vscodiumbench`.

---

## Niveau 1 — Contexte système

```plantuml
@startuml C4_Context
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

title Contexte système — vscodiumbench

Person(dev, "Développeur", "Utilise VSCode/VSCodium\navec Claude Code")

System(vscodiumbench, "vscodiumbench", "Outillage VSCode/VSCodium :\nconversion de diagrammes,\nstatus line, scripts")

System_Ext(claude_code, "Claude Code CLI", "Assistant IA intégré\ndans le terminal VSCodium")
System_Ext(github, "GitHub", "Dépôt distant\nwarchosian/vscodiumbench")
System_Ext(conda, "Conda", "Gestionnaire d'environnement\nPython portable")

Rel(dev, vscodiumbench, "Utilise", "CLI / scripts")
Rel(dev, claude_code, "Interagit avec", "terminal")
Rel(vscodiumbench, github, "Versionné sur", "git push")
Rel(vscodiumbench, conda, "Exécuté dans", "env vscodiumbench")
Rel(claude_code, vscodiumbench, "Lit la config", ".claude/settings.json")

@enduml
```

---

## Niveau 2 — Conteneurs

```plantuml
@startuml C4_Container
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title Conteneurs — vscodiumbench

Person(dev, "Développeur")

System_Boundary(vscodiumbench, "vscodiumbench") {
    Container(cli, "vscodiumbench CLI", "Python / argparse", "Point d'entrée principal.\nDispatche vers les sous-commandes.")
    Container(md2mmd, "md2mmd", "Python", "Convertit les diagrammes\nPlantUML et DOT en Mermaid\ndans les fichiers Markdown.")
    Container(statusline, "statusline.py", "Python", "Génère la status line\ncompacte pour Claude Code.")
    ContainerDb(diagrams, "_diagrams/", "Fichiers .md", "Sources de diagrammes\net fichiers convertis .mmd.md")
    ContainerDb(claude_cfg, ".claude/", "JSON / Markdown", "Configuration Claude Code,\ndirectives, hooks, PROJECT.md")
}

System_Ext(claude_code, "Claude Code CLI")
System_Ext(vscodium, "VSCodium / Preview Mermaid")

Rel(dev, cli, "Exécute", "vscodiumbench md2mmd ...")
Rel(cli, md2mmd, "Délègue", "sys.argv")
Rel(md2mmd, diagrams, "Lit / écrit", "fichiers .md / .mmd.md")
Rel(claude_code, statusline, "Appelle", "stdin JSON → stdout")
Rel(claude_code, claude_cfg, "Lit", "settings.json")
Rel(vscodium, diagrams, "Prévisualise", "extension Mermaid")

@enduml
```

---

## Niveau 3 — Composants du module conversion

```plantuml
@startuml C4_Component
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Composants — module app.conversion

Container_Boundary(conversion, "app.conversion") {
    Component(cli_entry, "cli.py", "Python", "Dispatcher principal.\nRoute vscodiumbench <cmd>.")
    Component(md2mmd_cmd, "commands/md2mmd.py", "Python / argparse", "Commande md2mmd.\nOrchestre extraction\net conversion.")
    Component(extractor, "extract_code_blocks()", "Python / regex", "Extrait les blocs ```plantuml\net ```dot du Markdown.")
    Component(converter, "convert_diagram()", "Python", "Aiguille vers le bon\nconvertisseur selon le type.")
    Component(seq_conv, "convert_plantuml_sequence()", "Python", "Convertit les diagrammes\nde séquence PlantUML.")
    Component(class_conv, "convert_plantuml_class()", "Python", "Convertit les diagrammes\nde classe PlantUML.")
    Component(state_conv, "convert_plantuml_state()", "Python", "Convertit les diagrammes\nd'état PlantUML.")
    Component(dot_conv, "convert_dot_digraph()", "Python", "Convertit les graphes\nGraphviz/DOT.")
    Component(writer, "convert_file()", "Python / pathlib", "Lit le .md source,\napplique les conversions,\nécrit le .mmd.md.")
}

Rel(cli_entry, md2mmd_cmd, "Appelle main()")
Rel(md2mmd_cmd, writer, "Appelle")
Rel(writer, extractor, "Extrait les blocs")
Rel(writer, converter, "Convertit chaque bloc")
Rel(converter, seq_conv, "si séquence")
Rel(converter, class_conv, "si classe")
Rel(converter, state_conv, "si état")
Rel(converter, dot_conv, "si DOT/graphviz")

@enduml
```

---

## Niveau 4 — Déploiement

```plantuml
@startuml C4_Deployment
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Deployment.puml

title Déploiement — poste développeur Windows

Deployment_Node(pc, "Poste Windows", "Windows 10/11") {
    Deployment_Node(vscodium_app, "VSCodium", "Portable") {
        Container(claude_code_ext, "Claude Code CLI", "Extension / terminal intégré")
    }
    Deployment_Node(conda_env, "Conda env : vscodiumbench", "Python 3.11+\nG:\\...\\envs\\vscodiumbench") {
        Container(pkg, "vscodiumbench 0.2.0", "wheel installé\nvia pip install")
        Container(scripts, "scripts/statusline.py", "Python UTF-8")
    }
    Deployment_Node(repo, "Dépôt local Git", "G:\\...\\vscodiumbench") {
        ContainerDb(src, "src/app/", "Sources Python")
        ContainerDb(cfg, ".claude/", "Config Claude Code")
        ContainerDb(diag, "_diagrams/", "Diagrammes Markdown")
    }
}

Deployment_Node(gh, "GitHub", "Cloud") {
    ContainerDb(remote, "warchosian/vscodiumbench", "main branch\ntags v0.1.0, v0.2.0")
}

Rel(claude_code_ext, scripts, "Exécute pour status line", "stdin/stdout")
Rel(claude_code_ext, cfg, "Lit")
Rel(pkg, src, "Installé depuis")
Rel(repo, remote, "git push --follow-tags")

@enduml
```
