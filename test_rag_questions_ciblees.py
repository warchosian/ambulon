#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test RAG avec questions ciblées sur des détails spécifiques à SIREINES.

Ce script teste plusieurs questions portant sur des détails impossibles
à deviner sans la documentation pour prouver l'utilité du RAG.

Usage:
    python test_rag_questions_ciblees.py
"""

import subprocess
import sys
import json
import csv
import os
from pathlib import Path
from datetime import datetime

# Forcer l'encodage UTF-8 pour Python et les sous-processus
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# Forcer l'encodage UTF-8 pour stdout et stderr (Windows compatibility)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


# Questions ciblées sur des détails spécifiques impossibles à deviner
QUESTIONS_CIBLEES = [
    {
        "id": "Q1",
        "category": "Composants Java",
        "question": "Quel est le rôle exact de la classe DossierRechercheMotsClefsAction dans SIREINES ?",
        "top_k": 5
    },
    {
        "id": "Q2",
        "category": "Vulnérabilités CVE",
        "question": "Quelles sont les vulnérabilités CVE identifiées pour le composant ExtractionsServicesImpl de SIREINES ?",
        "top_k": 7
    },
    {
        "id": "Q3",
        "category": "Configuration technique",
        "question": "Quelle version exacte d'Elasticsearch est utilisée dans SIREINES et comment est-elle configurée en mode embarqué ?",
        "top_k": 5
    },
    {
        "id": "Q4",
        "category": "Décisions architecturales",
        "question": "Pourquoi SIREINES utilise-t-il le Vertigo Framework et quelles sont ses responsabilités exactes ?",
        "top_k": 5
    },
    {
        "id": "Q5",
        "category": "Sécurité STRIDE",
        "question": "Quelles vulnérabilités STRIDE ont été identifiées pour le module CerbereUtil + SireinesSessionFilter ?",
        "top_k": 7
    },
    {
        "id": "Q6",
        "category": "ISO 25010",
        "question": "Quels sont les critères ISO 25010 spécifiques définis pour SIREINES avec leurs valeurs cibles mesurables ?",
        "top_k": 7
    },
    {
        "id": "Q7",
        "category": "Modèle C4 Level 3",
        "question": "Quels sont les composants internes détaillés du service SvcExtr dans le diagramme C4 Component de SIREINES ?",
        "top_k": 5
    },
    {
        "id": "Q8",
        "category": "Dépendances Maven",
        "question": "Quelles sont les dépendances Maven listées dans le pom.xml de sireines-web avec leurs versions exactes ?",
        "top_k": 5
    }
]


def calculate_chunk_usage(chunks_text, response_with_rag):
    """
    Calcule le taux d'utilisation effective des chunks dans la réponse.

    Vérifie si les informations des chunks sont réellement présentes dans la réponse.
    """
    if not chunks_text or not response_with_rag:
        return {
            'usage_score': 0,
            'terms_from_chunks': [],
            'terms_in_response': []
        }

    # Extraire les termes significatifs des chunks (3+ caractères, pas trop communs)
    import re

    common_words = {
        'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'ou', 'pour',
        'avec', 'dans', 'sur', 'par', 'est', 'sont', 'que', 'qui', 'this',
        'the', 'and', 'or', 'for', 'with', 'from'
    }

    # Extraire mots de 3+ caractères
    chunk_words = set(re.findall(r'\b[a-zA-Z0-9_-]{3,}\b', chunks_text.lower()))
    chunk_words = chunk_words - common_words

    # Termes techniques importants (majuscules, camelCase, versions)
    technical_terms = set(re.findall(r'\b[A-Z][a-zA-Z0-9_]*[a-z][a-zA-Z0-9_]*\b', chunks_text))
    technical_terms.update(re.findall(r'\b\d+\.\d+(?:\.\d+)?\b', chunks_text))  # Versions
    technical_terms.update(re.findall(r'\bCVE-\d+-\d+\b', chunks_text))  # CVE IDs

    all_chunk_terms = chunk_words.union(technical_terms)

    # Vérifier combien sont dans la réponse
    response_lower = response_with_rag.lower()
    terms_found = [term for term in all_chunk_terms if term.lower() in response_lower]

    usage_score = (len(terms_found) / len(all_chunk_terms) * 100) if all_chunk_terms else 0

    return {
        'usage_score': usage_score,
        'terms_from_chunks': list(all_chunk_terms)[:20],  # Top 20
        'terms_in_response': terms_found[:20]  # Top 20 trouvés
    }


def extract_metrics_from_report(report_file):
    """Extrait les métriques d'un rapport de comparaison."""
    metrics = {
        'chunks_found': 0,
        'sources': [],
        'length_without_rag': 0,
        'length_with_rag': 0,
        'terms_without_rag': [],
        'terms_with_rag': [],
        'response_without_rag': '',
        'response_with_rag': '',
        'chunks_text': '',
        'chunk_usage': {}
    }

    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extraire le nombre de chunks
        import re
        chunks_match = re.search(r'✅ (\d+) chunks trouvés', content)
        if chunks_match:
            metrics['chunks_found'] = int(chunks_match.group(1))

        # Extraire les sources
        sources_section = re.search(r'📄 Sources:\s+(.*?)(?=\n\n|\n❓)', content, re.DOTALL)
        if sources_section:
            sources_text = sources_section.group(1)
            metrics['sources'] = re.findall(r'- (.+)', sources_text)

        # Extraire les longueurs
        len_without = re.search(r'Longueur sans RAG:\s+(\d+) caractères', content)
        len_with = re.search(r'Longueur avec RAG:\s+(\d+) caractères', content)

        if len_without:
            metrics['length_without_rag'] = int(len_without.group(1))
        if len_with:
            metrics['length_with_rag'] = int(len_with.group(1))

        # Extraire les termes trouvés
        terms_without = re.search(r'- Sans RAG: (.+)', content)
        terms_with = re.search(r'- Avec RAG: (.+)', content)

        if terms_without:
            terms_text = terms_without.group(1).strip()
            if terms_text != 'Aucun':
                metrics['terms_without_rag'] = [t.strip() for t in terms_text.split(',')]

        if terms_with:
            terms_text = terms_with.group(1).strip()
            if terms_text != 'Aucun':
                metrics['terms_with_rag'] = [t.strip() for t in terms_text.split(',')]

        # Extraire les réponses complètes
        sans_rag_match = re.search(
            r'🌍 SANS CONTEXTE RAG.*?\n─+\n(.*?)\n─+',
            content,
            re.DOTALL
        )
        avec_rag_match = re.search(
            r'📚 AVEC CONTEXTE RAG.*?\n─+\n(.*?)\n─+',
            content,
            re.DOTALL
        )

        if sans_rag_match:
            metrics['response_without_rag'] = sans_rag_match.group(1).strip()
        if avec_rag_match:
            metrics['response_with_rag'] = avec_rag_match.group(1).strip()

        # Extraire le contenu des chunks (contexte documentaire)
        chunks_match = re.search(
            r'Contexte documentaire:\s*\n\n(.*?)\n\n---\n\nQuestion:',
            content,
            re.DOTALL
        )
        if chunks_match:
            metrics['chunks_text'] = chunks_match.group(1).strip()

        # Calculer l'utilisation effective des chunks
        if metrics['response_with_rag'] and metrics['chunks_text']:
            metrics['chunk_usage'] = calculate_chunk_usage(
                metrics['chunks_text'],
                metrics['response_with_rag']
            )

    except Exception as e:
        print(f"⚠️  Erreur extraction métriques: {e}")

    return metrics


def run_comparison(question_data, output_dir):
    """Lance le test de comparaison pour une question."""
    question_id = question_data["id"]
    category = question_data["category"]
    question = question_data["question"]
    top_k = question_data.get("top_k", 5)

    print("\n" + "=" * 80)
    print(f"  {question_id}: {category}")
    print("=" * 80)
    print(f"Question: {question}")
    print(f"Top-K: {top_k}")
    print()

    # Nom du fichier de sortie
    safe_id = question_id.lower()
    output_file = output_dir / f"{safe_id}_rapport.md"

    # Commande
    cmd = [
        "python", "test_compare_with_without_rag.py",
        "--question", question,
        "--top-k", str(top_k),
        "--output", str(output_file)
    ]

    # Exécution
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8',
        errors='replace'
    )

    success = result.returncode == 0

    if success:
        print(f"✅ Test réussi - Rapport: {output_file.name}")

        # Extraire les métriques
        metrics = extract_metrics_from_report(output_file)

        return {
            'success': True,
            'metrics': metrics
        }
    else:
        print(f"❌ Test échoué")
        print(result.stderr)
        return {
            'success': False,
            'metrics': None
        }


def save_results_json(results, output_dir):
    """Sauvegarde les résultats en JSON pour analyse programmatique."""
    json_file = output_dir / "resultats.json"

    json_data = {
        'timestamp': datetime.now().isoformat(),
        'collection': 'PNM3_SIREINES',
        'total_tests': len(results),
        'success_count': sum(1 for r in results if r['success']),
        'tests': []
    }

    for r in results:
        test_data = {
            'id': r['id'],
            'category': r['category'],
            'question': r['question'],
            'top_k': r['top_k'],
            'success': r['success']
        }

        if r.get('metrics'):
            m = r['metrics']
            test_data['metrics'] = {
                'chunks_found': m['chunks_found'],
                'sources_count': len(m['sources']),
                'sources': m['sources'],
                'length_without_rag': m['length_without_rag'],
                'length_with_rag': m['length_with_rag'],
                'length_difference': m['length_with_rag'] - m['length_without_rag'],
                'terms_without_rag_count': len(m['terms_without_rag']),
                'terms_with_rag_count': len(m['terms_with_rag']),
                'terms_without_rag': m['terms_without_rag'],
                'terms_with_rag': m['terms_with_rag'],
                'rag_improvement': len(m['terms_with_rag']) > len(m['terms_without_rag']),
                'chunk_usage_score': m.get('chunk_usage', {}).get('usage_score', 0),
                'chunk_usage_details': m.get('chunk_usage', {})
            }

        json_data['tests'].append(test_data)

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"📊 Résultats JSON: {json_file}")
    return json_file


def save_results_csv(results, output_dir):
    """Sauvegarde les résultats en CSV pour Excel/analyse."""
    csv_file = output_dir / "resultats.csv"

    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')

        # En-tête
        writer.writerow([
            'ID', 'Catégorie', 'Question', 'Top-K', 'Succès',
            'Chunks trouvés', 'Sources', 'Longueur sans RAG',
            'Longueur avec RAG', 'Différence', 'Termes sans RAG',
            'Termes avec RAG', 'Amélioration RAG', 'Utilisation Chunks (%)'
        ])

        # Données
        for r in results:
            row = [
                r['id'],
                r['category'],
                r['question'],
                r['top_k'],
                'OUI' if r['success'] else 'NON'
            ]

            if r.get('metrics'):
                m = r['metrics']
                chunk_usage = m.get('chunk_usage', {}).get('usage_score', 0)
                row.extend([
                    m['chunks_found'],
                    len(m['sources']),
                    m['length_without_rag'],
                    m['length_with_rag'],
                    m['length_with_rag'] - m['length_without_rag'],
                    len(m['terms_without_rag']),
                    len(m['terms_with_rag']),
                    'OUI' if len(m['terms_with_rag']) > len(m['terms_without_rag']) else 'NON',
                    f"{chunk_usage:.1f}"
                ])
            else:
                row.extend([''] * 9)

            writer.writerow(row)

    print(f"📊 Résultats CSV: {csv_file}")
    return csv_file


def create_summary_report(results, output_dir):
    """Crée un rapport synthétique de tous les tests."""
    summary_file = output_dir / "00_SYNTHESE.md"

    # Calculer les statistiques globales
    total = len(results)
    success = sum(1 for r in results if r['success'])
    success_with_metrics = [r for r in results if r['success'] and r.get('metrics')]

    avg_chunks = 0
    avg_sources = 0
    avg_length_diff = 0
    avg_terms_improvement = 0
    avg_chunk_usage = 0

    if success_with_metrics:
        avg_chunks = sum(r['metrics']['chunks_found'] for r in success_with_metrics) / len(success_with_metrics)
        avg_sources = sum(len(r['metrics']['sources']) for r in success_with_metrics) / len(success_with_metrics)
        avg_length_diff = sum(
            r['metrics']['length_with_rag'] - r['metrics']['length_without_rag']
            for r in success_with_metrics
        ) / len(success_with_metrics)
        improvements = sum(
            1 for r in success_with_metrics
            if len(r['metrics']['terms_with_rag']) > len(r['metrics']['terms_without_rag'])
        )
        avg_terms_improvement = (improvements / len(success_with_metrics)) * 100

        # Calculer l'utilisation moyenne des chunks
        chunk_usages = [
            r['metrics'].get('chunk_usage', {}).get('usage_score', 0)
            for r in success_with_metrics
        ]
        avg_chunk_usage = sum(chunk_usages) / len(chunk_usages) if chunk_usages else 0

    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# Synthèse des Tests RAG - Questions Ciblées\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Collection**: PNM3_SIREINES\n\n")
        f.write(f"**Objectif**: Tester le RAG avec des questions sur des détails spécifiques impossibles à deviner\n\n")

        # Statistiques globales
        f.write(f"## 📊 Statistiques Globales\n\n")
        f.write(f"- **Total de questions**: {total}\n")
        f.write(f"- **Tests réussis**: {success}/{total}\n")
        f.write(f"- **Taux de réussite**: {(success/total*100):.1f}%\n\n")

        # Métriques RAG
        if success_with_metrics:
            f.write(f"## 📈 Métriques RAG (Moyennes)\n\n")
            f.write(f"- **Chunks trouvés par question**: {avg_chunks:.1f}\n")
            f.write(f"- **Sources documentaires par question**: {avg_sources:.1f}\n")
            f.write(f"- **Différence de longueur (avec RAG - sans RAG)**: {avg_length_diff:+.0f} caractères\n")
            f.write(f"- **Amélioration des détails techniques**: {avg_terms_improvement:.1f}% des cas\n")
            f.write(f"- **🎯 Utilisation effective des chunks**: {avg_chunk_usage:.1f}%\n\n")

            # Explication de la métrique clé
            f.write(f"### 💡 Métrique Clé : Utilisation Effective des Chunks\n\n")
            f.write(f"Cette métrique mesure **si les informations des chunks sont réellement utilisées** ")
            f.write(f"dans la réponse générée. Elle vérifie combien de termes techniques et concepts ")
            f.write(f"présents dans les chunks se retrouvent dans la réponse avec RAG.\n\n")
            f.write(f"**Score actuel**: {avg_chunk_usage:.1f}%\n\n")

            if avg_chunk_usage >= 30:
                f.write(f"✅ Les chunks sont **bien exploités** par le modèle.\n\n")
            elif avg_chunk_usage >= 15:
                f.write(f"⚠️ Les chunks sont **partiellement utilisés**. Le modèle pourrait mieux les exploiter.\n\n")
            else:
                f.write(f"❌ Les chunks sont **peu utilisés**. Le contexte n'est pas bien intégré dans les réponses.\n\n")

            # Verdict
            f.write(f"## 🎯 Verdict\n\n")
            if avg_terms_improvement >= 70:
                f.write(f"✅ **Le RAG fonctionne très bien** : {avg_terms_improvement:.0f}% des réponses ")
                f.write(f"contiennent plus de détails techniques avec le contexte documentaire.\n\n")
            elif avg_terms_improvement >= 50:
                f.write(f"⚠️ **Le RAG fonctionne partiellement** : {avg_terms_improvement:.0f}% des réponses ")
                f.write(f"bénéficient du contexte, mais certaines questions pourraient être améliorées.\n\n")
            else:
                f.write(f"❌ **Le RAG semble peu efficace** : Seulement {avg_terms_improvement:.0f}% des réponses ")
                f.write(f"montrent une amélioration. Vérifier la qualité des documents indexés.\n\n")
        f.write("\n")

        # Liste des tests avec métriques
        f.write(f"## 📋 Détail des Tests\n\n")
        f.write(f"| ID | Catégorie | Chunks | Sources | Termes sans/avec | Utilisation | Amélioration | Rapport |\n")
        f.write(f"|---|---|---|---|---|---|---|---|\n")

        for r in results:
            if r['success'] and r.get('metrics'):
                m = r['metrics']
                chunks = f"{m['chunks_found']}"
                sources = f"{len(m['sources'])}"
                terms = f"{len(m['terms_without_rag'])}/{len(m['terms_with_rag'])}"
                usage_score = m.get('chunk_usage', {}).get('usage_score', 0)
                usage = f"{usage_score:.0f}%"
                improvement = "✅" if len(m['terms_with_rag']) > len(m['terms_without_rag']) else "⚠️"
                report_link = f"[Voir](./{r['id'].lower()}_rapport.md)"
            else:
                chunks = "-"
                sources = "-"
                terms = "-"
                usage = "-"
                improvement = "❌"
                report_link = "-"

            f.write(f"| {r['id']} | {r['category']} | {chunks} | {sources} | {terms} | {usage} | {improvement} | {report_link} |\n")

        f.write(f"\n**Légende** :\n")
        f.write(f"- **Termes** : nombre de termes techniques trouvés (sans RAG / avec RAG)\n")
        f.write(f"- **Utilisation** : % de termes des chunks effectivement utilisés dans la réponse\n\n")

        f.write(f"\n## Questions Testées\n\n")
        for r in results:
            f.write(f"### {r['id']}: {r['category']}\n\n")
            f.write(f"**Question**: {r['question']}\n\n")
            f.write(f"**Top-K**: {r['top_k']}\n\n")
            f.write(f"**Status**: {'✅ Réussi' if r['success'] else '❌ Échoué'}\n\n")
            if r['success']:
                f.write(f"**Rapport détaillé**: [{r['id'].lower()}_rapport.md](./{r['id'].lower()}_rapport.md)\n\n")
            f.write(f"---\n\n")

        # Recommandations
        f.write(f"## Recommandations\n\n")
        f.write(f"Pour chaque rapport détaillé, comparez:\n\n")
        f.write(f"1. **Précision**: La réponse avec RAG contient-elle des détails spécifiques ?\n")
        f.write(f"2. **Sources**: Les chunks proviennent-ils des bons documents ?\n")
        f.write(f"3. **Termes techniques**: Retrouve-t-on les noms de classes, CVE, versions exactes ?\n")
        f.write(f"4. **Différence**: Y a-t-il une vraie différence entre réponse avec/sans RAG ?\n\n")
        f.write(f"**Verdict attendu**: Si le RAG fonctionne bien, la réponse AVEC RAG devrait contenir\n")
        f.write(f"des détails spécifiques impossibles à deviner par le modèle seul.\n\n")

    print(f"\n📋 Rapport de synthèse créé: {summary_file}")
    return summary_file


def main():
    """Point d'entrée principal."""
    print("=" * 80)
    print("  TEST RAG - QUESTIONS CIBLÉES SUR DÉTAILS SPÉCIFIQUES")
    print("=" * 80)
    print()
    print(f"Nombre de questions: {len(QUESTIONS_CIBLEES)}")
    print(f"Collection: PNM3_SIREINES")
    print()

    # Créer le répertoire de sortie
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"tests_rag_ciblés_{timestamp}")
    output_dir.mkdir(exist_ok=True)

    print(f"📁 Répertoire de sortie: {output_dir}")
    print()

    # Lancer les tests
    results = []

    for i, question_data in enumerate(QUESTIONS_CIBLEES, 1):
        print(f"\n{'=' * 80}")
        print(f"  TEST {i}/{len(QUESTIONS_CIBLEES)}")
        print(f"{'=' * 80}")

        result = run_comparison(question_data, output_dir)

        results.append({
            'id': question_data['id'],
            'category': question_data['category'],
            'question': question_data['question'],
            'top_k': question_data['top_k'],
            'success': result['success'],
            'metrics': result.get('metrics')
        })

        # Pause entre les requêtes pour respecter le rate limit (20 req/min)
        if i < len(QUESTIONS_CIBLEES):
            import time
            print(f"\n⏸️  Pause 4s (rate limit: 20 req/min)...")
            time.sleep(4)

    # Créer les rapports d'analyse
    print("\n" + "=" * 80)
    print("  CRÉATION DES RAPPORTS D'ANALYSE")
    print("=" * 80)

    # Sauvegarde JSON
    json_file = save_results_json(results, output_dir)

    # Sauvegarde CSV
    csv_file = save_results_csv(results, output_dir)

    # Rapport de synthèse Markdown
    summary_file = create_summary_report(results, output_dir)

    # Résumé final
    print("\n" + "=" * 80)
    print("  RÉSUMÉ FINAL")
    print("=" * 80)

    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)

    print(f"\n✅ Tests réussis: {success_count}/{total_count}")
    print(f"\n📁 Répertoire: {output_dir}/")
    print(f"\n📄 Fichiers d'analyse générés:")
    print(f"   - 📋 {summary_file.name} (Rapport synthétique Markdown)")
    print(f"   - 📊 {json_file.name} (Données structurées JSON)")
    print(f"   - 📊 {csv_file.name} (Tableau Excel/CSV)")
    print(f"   - 📝 {total_count} rapports détaillés (q1_rapport.md, q2_rapport.md, ...)")

    print("\n💡 Pour analyser les résultats:")
    print(f"   - Lisez la synthèse: {summary_file}")
    print(f"   - Importez le CSV dans Excel: {csv_file}")
    print(f"   - Analysez programmatiquement: {json_file}")

    print("\n" + "=" * 80)

    return 0 if success_count == total_count else 1


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
