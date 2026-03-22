@echo off
chcp 65001 >nul
echo ==========================================
echo Commit: gitlab-clone utilise md2interactive
echo ==========================================
echo.

echo [1/3] Ajout des modifications...
git add src/app/gitlab/core/monofile.py
echo.

echo [2/3] Commit avec message conventionnel...
git commit -m "refactor(gitlab): utiliser md2interactive au lieu de md2html-diagrams

Le workflow gitlab-clone genere maintenant des HTML interactifs
complets (avec TOC, backlinks et interactivite) au lieu de
simples fichiers HTML.

- Modifie generate_code_monofile() pour utiliser md_to_interactive_html()
- Modifie generate_wiki_monofile() pour utiliser md_to_interactive_html()
- Les fichiers produits: <repo>-interactive.html (au lieu de .html simple)"

echo.
echo [3/3] Push sur la branche courante...
git push
echo.

echo ==========================================
echo Statut git actuel :
echo ==========================================
git status
git log --oneline -3
echo.
pause
