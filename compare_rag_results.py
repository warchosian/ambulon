#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de comparaison des résultats RAG avant/après amélioration des sources.

Compare deux exécutions de test_rag_questions_ciblees.py pour détecter les progrès.

Usage:
    python compare_rag_results.py --before tests_rag_ciblés_20260321_110814 --after tests_rag_ciblés_NOUVEAU
    python compare_rag_results.py --auto  # Détecte automatiquement les 2 derniers
"""

import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# Forcer l'encodage UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def find_test_directories():
    """Trouve les répertoires de tests RAG, triés par date."""
    current_dir = Path.cwd()
    test_dirs = sorted(
        current_dir.glob("tests_rag_ciblés_*"),
        key=lambda p: p.name,
        reverse=True
    )
    return test_dirs


def load_results(test_dir):
    """Charge les résultats d'un test."""
    results_file = test_dir / "resultats.json"

    if not results_file.exists():
        raise FileNotFoundError(f"Fichier non trouvé: {results_file}")

    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


def extract_sources_list(test):
    """Extrait la liste des sources d'un test."""
    if 'metrics' in test and 'sources' in test['metrics']:
        return test['metrics']['sources']
    return []


def extract_unique_sources(results):
    """Extrait toutes les sources uniques utilisées."""
    all_sources = set()
    for test in results['tests']:
        all_sources.update(extract_sources_list(test))
    return sorted(all_sources)


def compare_metrics(before, after):
    """Compare les métriques entre deux exécutions."""

    # Métriques globales
    comparison = {
        'timestamp_before': before['timestamp'],
        'timestamp_after': after['timestamp'],
        'total_tests': {
            'before': before['total_tests'],
            'after': after['total_tests'],
            'delta': after['total_tests'] - before['total_tests']
        },
        'success_count': {
            'before': before['success_count'],
            'after': after['success_count'],
            'delta': after['success_count'] - before['success_count']
        },
        'questions': []
    }

    # Métriques par question
    before_tests = {t['id']: t for t in before['tests']}
    after_tests = {t['id']: t for t in after['tests']}

    for qid in sorted(before_tests.keys()):
        if qid not in after_tests:
            continue

        before_test = before_tests[qid]
        after_test = after_tests[qid]

        before_metrics = before_test.get('metrics', {})
        after_metrics = after_test.get('metrics', {})

        question_comparison = {
            'id': qid,
            'category': before_test['category'],
            'question': before_test['question'],
            'chunks_found': {
                'before': before_metrics.get('chunks_found', 0),
                'after': after_metrics.get('chunks_found', 0),
                'delta': after_metrics.get('chunks_found', 0) - before_metrics.get('chunks_found', 0)
            },
            'sources_count': {
                'before': before_metrics.get('sources_count', 0),
                'after': after_metrics.get('sources_count', 0),
                'delta': after_metrics.get('sources_count', 0) - before_metrics.get('sources_count', 0)
            },
            'sources_before': extract_sources_list(before_test),
            'sources_after': extract_sources_list(after_test),
            'new_sources': list(set(extract_sources_list(after_test)) - set(extract_sources_list(before_test))),
            'lost_sources': list(set(extract_sources_list(before_test)) - set(extract_sources_list(after_test))),
            'length_with_rag': {
                'before': before_metrics.get('length_with_rag', 0),
                'after': after_metrics.get('length_with_rag', 0),
                'delta': after_metrics.get('length_with_rag', 0) - before_metrics.get('length_with_rag', 0)
            },
            'terms_with_rag_count': {
                'before': before_metrics.get('terms_with_rag_count', 0),
                'after': after_metrics.get('terms_with_rag_count', 0),
                'delta': after_metrics.get('terms_with_rag_count', 0) - before_metrics.get('terms_with_rag_count', 0)
            },
            'chunk_usage_score': {
                'before': before_metrics.get('chunk_usage_score', 0),
                'after': after_metrics.get('chunk_usage_score', 0),
                'delta': after_metrics.get('chunk_usage_score', 0) - before_metrics.get('chunk_usage_score', 0)
            },
            'rag_improvement': {
                'before': before_metrics.get('rag_improvement', False),
                'after': after_metrics.get('rag_improvement', False)
            }
        }

        comparison['questions'].append(question_comparison)

    # Sources documentaires
    comparison['sources'] = {
        'before': extract_unique_sources(before),
        'after': extract_unique_sources(after),
        'new': list(set(extract_unique_sources(after)) - set(extract_unique_sources(before))),
        'removed': list(set(extract_unique_sources(before)) - set(extract_unique_sources(after))),
        'count_before': len(extract_unique_sources(before)),
        'count_after': len(extract_unique_sources(after))
    }

    return comparison


def generate_markdown_report(comparison, output_file):
    """Génère un rapport Markdown de comparaison."""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Rapport de Comparaison RAG : Avant/Après Amélioration des Sources\n\n")

        f.write(f"**Date de comparaison** : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Dates des tests
        f.write("## 📅 Tests Comparés\n\n")
        f.write(f"- **AVANT** : {comparison['timestamp_before']}\n")
        f.write(f"- **APRÈS** : {comparison['timestamp_after']}\n\n")

        f.write("---\n\n")

        # Métriques globales
        f.write("## 📊 Métriques Globales\n\n")

        f.write("| Métrique | Avant | Après | Évolution |\n")
        f.write("|----------|-------|-------|----------|\n")

        total_delta = comparison['total_tests']['delta']
        total_icon = "➡️" if total_delta == 0 else ("✅" if total_delta > 0 else "⚠️")
        f.write(f"| **Questions testées** | {comparison['total_tests']['before']} | {comparison['total_tests']['after']} | {total_icon} {total_delta:+d} |\n")

        success_delta = comparison['success_count']['delta']
        success_icon = "➡️" if success_delta == 0 else ("✅" if success_delta > 0 else "❌")
        f.write(f"| **Tests réussis** | {comparison['success_count']['before']} | {comparison['success_count']['after']} | {success_icon} {success_delta:+d} |\n")

        f.write("\n")

        # Sources documentaires
        f.write("## 📚 Sources Documentaires\n\n")

        sources_delta = comparison['sources']['count_after'] - comparison['sources']['count_before']
        sources_icon = "➡️" if sources_delta == 0 else ("✅" if sources_delta > 0 else "⚠️")

        f.write(f"**Nombre de sources** : {comparison['sources']['count_before']} → {comparison['sources']['count_after']} ({sources_icon} {sources_delta:+d})\n\n")

        if comparison['sources']['new']:
            f.write(f"### ✅ Nouvelles Sources ({len(comparison['sources']['new'])})\n\n")
            for source in comparison['sources']['new']:
                f.write(f"- {source}\n")
            f.write("\n")

        if comparison['sources']['removed']:
            f.write(f"### ❌ Sources Supprimées ({len(comparison['sources']['removed'])})\n\n")
            for source in comparison['sources']['removed']:
                f.write(f"- {source}\n")
            f.write("\n")

        f.write("---\n\n")

        # Détail par question
        f.write("## 📋 Comparaison Détaillée par Question\n\n")

        for q in comparison['questions']:
            f.write(f"### {q['id']}: {q['category']}\n\n")
            f.write(f"**Question** : {q['question']}\n\n")

            # Tableau de métriques
            f.write("| Métrique | Avant | Après | Évolution |\n")
            f.write("|----------|-------|-------|----------|\n")

            chunks_delta = q['chunks_found']['delta']
            chunks_icon = "➡️" if chunks_delta == 0 else ("✅" if chunks_delta > 0 else "⚠️")
            f.write(f"| Chunks trouvés | {q['chunks_found']['before']} | {q['chunks_found']['after']} | {chunks_icon} {chunks_delta:+d} |\n")

            sources_delta = q['sources_count']['delta']
            sources_icon = "➡️" if sources_delta == 0 else ("✅" if sources_delta > 0 else "⚠️")
            f.write(f"| Sources utilisées | {q['sources_count']['before']} | {q['sources_count']['after']} | {sources_icon} {sources_delta:+d} |\n")

            length_delta = q['length_with_rag']['delta']
            length_icon = "➡️" if length_delta == 0 else ("📝" if length_delta > 0 else "📉")
            f.write(f"| Longueur réponse | {q['length_with_rag']['before']} | {q['length_with_rag']['after']} | {length_icon} {length_delta:+d} |\n")

            terms_delta = q['terms_with_rag_count']['delta']
            terms_icon = "➡️" if terms_delta == 0 else ("✅" if terms_delta > 0 else "⚠️")
            f.write(f"| Termes techniques | {q['terms_with_rag_count']['before']} | {q['terms_with_rag_count']['after']} | {terms_icon} {terms_delta:+d} |\n")

            usage_delta = q['chunk_usage_score']['delta']
            usage_icon = "➡️" if usage_delta == 0 else ("✅" if usage_delta > 0 else "⚠️")
            f.write(f"| Utilisation chunks | {q['chunk_usage_score']['before']:.1f}% | {q['chunk_usage_score']['after']:.1f}% | {usage_icon} {usage_delta:+.1f}% |\n")

            f.write("\n")

            # Nouvelles sources pour cette question
            if q['new_sources']:
                f.write(f"**✅ Nouvelles sources** ({len(q['new_sources'])}) :\n")
                for source in q['new_sources']:
                    f.write(f"- {source}\n")
                f.write("\n")

            # Sources perdues
            if q['lost_sources']:
                f.write(f"**❌ Sources perdues** ({len(q['lost_sources'])}) :\n")
                for source in q['lost_sources']:
                    f.write(f"- {source}\n")
                f.write("\n")

            f.write("---\n\n")

        # Synthèse des progrès
        f.write("## 🎯 Synthèse des Progrès\n\n")

        # Compter les améliorations
        chunks_improved = sum(1 for q in comparison['questions'] if q['chunks_found']['delta'] > 0)
        sources_improved = sum(1 for q in comparison['questions'] if q['sources_count']['delta'] > 0)
        terms_improved = sum(1 for q in comparison['questions'] if q['terms_with_rag_count']['delta'] > 0)
        usage_improved = sum(1 for q in comparison['questions'] if q['chunk_usage_score']['delta'] > 0)

        total_questions = len(comparison['questions'])

        f.write(f"### Nombre de questions améliorées (sur {total_questions})\n\n")
        f.write(f"- **Chunks trouvés** : {chunks_improved}/{total_questions} questions ({chunks_improved/total_questions*100:.0f}%)\n")
        f.write(f"- **Sources utilisées** : {sources_improved}/{total_questions} questions ({sources_improved/total_questions*100:.0f}%)\n")
        f.write(f"- **Termes techniques** : {terms_improved}/{total_questions} questions ({terms_improved/total_questions*100:.0f}%)\n")
        f.write(f"- **Utilisation chunks** : {usage_improved}/{total_questions} questions ({usage_improved/total_questions*100:.0f}%)\n")
        f.write("\n")

        # Calcul du score de progrès global
        progress_score = (chunks_improved + sources_improved + terms_improved + usage_improved) / (4 * total_questions) * 100

        f.write(f"### 📊 Score de Progrès Global : {progress_score:.0f}%\n\n")

        if progress_score >= 75:
            f.write("✅ **Amélioration MAJEURE** : Les nouvelles sources ont significativement amélioré la qualité du RAG.\n\n")
        elif progress_score >= 50:
            f.write("✅ **Amélioration NOTABLE** : Les nouvelles sources ont apporté des bénéfices clairs.\n\n")
        elif progress_score >= 25:
            f.write("⚠️ **Amélioration MODÉRÉE** : Les nouvelles sources ont un impact limité.\n\n")
        else:
            f.write("❌ **Peu ou pas d'amélioration** : Les nouvelles sources n'ont pas amélioré les résultats de manière significative.\n\n")

        # Recommandations
        f.write("## 💡 Recommandations\n\n")

        if comparison['sources']['new']:
            f.write("### Sources Ajoutées\n\n")
            f.write("Les nouvelles sources suivantes ont été intégrées :\n")
            for source in comparison['sources']['new']:
                # Compter dans combien de questions elles apparaissent
                usage_count = sum(1 for q in comparison['questions'] if source in q['sources_after'])
                f.write(f"- `{source}` (utilisée dans {usage_count} question(s))\n")
            f.write("\n")

        if progress_score < 50:
            f.write("### Actions Suggérées\n\n")
            f.write("Pour améliorer davantage les résultats :\n\n")
            f.write("1. **Enrichir les sources existantes** avec plus de détails techniques\n")
            f.write("2. **Ajouter des exemples concrets** (code, configurations, CVE)\n")
            f.write("3. **Structurer les documents** avec des sections claires et des titres explicites\n")
            f.write("4. **Inclure des métadonnées** (versions, dates, références)\n")
            f.write("5. **Vérifier la couverture** de tous les sujets posés dans les questions\n")
            f.write("\n")

        f.write("---\n\n")
        f.write(f"**Rapport généré le** : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Compare deux résultats de tests RAG pour détecter les progrès"
    )
    parser.add_argument(
        '--before',
        type=Path,
        help="Répertoire du test AVANT amélioration"
    )
    parser.add_argument(
        '--after',
        type=Path,
        help="Répertoire du test APRÈS amélioration"
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help="Détecte automatiquement les 2 derniers répertoires de tests"
    )
    parser.add_argument(
        '--output',
        type=Path,
        help="Fichier de sortie pour le rapport (défaut: COMPARAISON_RAG.md)"
    )

    args = parser.parse_args()

    # Détection automatique
    if args.auto or (not args.before and not args.after):
        print("🔍 Détection automatique des répertoires de tests...")
        test_dirs = find_test_directories()

        if len(test_dirs) < 2:
            print("❌ Erreur: Il faut au moins 2 répertoires de tests")
            print("   Trouvés:", [str(d) for d in test_dirs])
            return 1

        args.after = test_dirs[0]  # Le plus récent
        args.before = test_dirs[1]  # Le second plus récent

        print(f"✅ AVANT  : {args.before}")
        print(f"✅ APRÈS  : {args.after}")
        print()

    # Validation
    if not args.before or not args.after:
        print("❌ Erreur: Spécifiez --before et --after, ou utilisez --auto")
        return 1

    if not args.before.exists():
        print(f"❌ Erreur: Répertoire non trouvé: {args.before}")
        return 1

    if not args.after.exists():
        print(f"❌ Erreur: Répertoire non trouvé: {args.after}")
        return 1

    # Fichier de sortie
    if not args.output:
        args.output = Path.cwd() / "COMPARAISON_RAG.md"

    print("=" * 80)
    print("  COMPARAISON DES RÉSULTATS RAG")
    print("=" * 80)
    print()

    # Chargement des résultats
    print("📂 Chargement des résultats...")
    try:
        before = load_results(args.before)
        after = load_results(args.after)
        print(f"   ✅ AVANT : {before['total_tests']} tests")
        print(f"   ✅ APRÈS : {after['total_tests']} tests")
        print()
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
        return 1

    # Comparaison
    print("📊 Analyse comparative...")
    comparison = compare_metrics(before, after)

    # Affichage rapide
    print(f"   Sources: {comparison['sources']['count_before']} → {comparison['sources']['count_after']}")
    print(f"   Nouvelles sources: {len(comparison['sources']['new'])}")
    print()

    # Génération du rapport
    print("📝 Génération du rapport...")
    generate_markdown_report(comparison, args.output)

    print(f"   ✅ Rapport: {args.output}")
    print()

    # Résumé
    chunks_improved = sum(1 for q in comparison['questions'] if q['chunks_found']['delta'] > 0)
    sources_improved = sum(1 for q in comparison['questions'] if q['sources_count']['delta'] > 0)
    total = len(comparison['questions'])

    progress_score = (chunks_improved + sources_improved) / (2 * total) * 100

    print("=" * 80)
    print("  RÉSUMÉ")
    print("=" * 80)
    print(f"Questions améliorées (chunks) : {chunks_improved}/{total}")
    print(f"Questions améliorées (sources): {sources_improved}/{total}")
    print(f"Score de progrès global       : {progress_score:.0f}%")
    print()

    if progress_score >= 50:
        print("✅ Les nouvelles sources ont amélioré les résultats !")
    else:
        print("⚠️  Impact limité des nouvelles sources")

    print("=" * 80)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏸️  Interrompu par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
