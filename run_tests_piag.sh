#!/bin/bash
# Script de lancement des tests E2E PIAG
# Usage: ./run_tests_piag.sh [check|all|rag|chat]

set -e

echo "================================================================================"
echo "TESTS END-TO-END API PIAG"
echo "================================================================================"
echo ""

CONFIG_FILE="config/piag.yaml"

# Déterminer l'action
ACTION="${1:-all}"

case "$ACTION" in
    check)
        echo "[1/1] Vérification de la configuration..."
        echo ""
        python3 check_piag_config.py --config "$CONFIG_FILE"
        ;;

    all)
        echo "[1/3] Vérification de la configuration..."
        echo ""
        if ! python3 check_piag_config.py --config "$CONFIG_FILE"; then
            echo ""
            echo "================================================================================"
            echo "ATTENTION: Configuration incomplète ou incorrecte"
            echo "================================================================================"
            echo ""
            read -p "Continuer quand même? (y/N) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi

        echo ""
        echo "[2/3] Lancement des tests RAG et CHAT..."
        echo ""
        python3 test_piag_all.py --config "$CONFIG_FILE"
        ;;

    rag)
        echo "[1/2] Vérification de la configuration RAG..."
        echo ""
        python3 check_piag_config.py --config "$CONFIG_FILE"

        echo ""
        echo "[2/2] Lancement du test RAG..."
        echo ""
        python3 test_piag_rag_e2e.py --config "$CONFIG_FILE"
        ;;

    chat)
        echo "[1/2] Vérification de la configuration CHAT..."
        echo ""
        python3 check_piag_config.py --config "$CONFIG_FILE"

        echo ""
        echo "[2/2] Lancement du test CHAT..."
        echo ""
        python3 test_piag_chat_e2e.py --config "$CONFIG_FILE"
        ;;

    *)
        echo "Action inconnue: $ACTION"
        echo ""
        echo "Usage: $0 [check|all|rag|chat]"
        echo ""
        echo "  check - Vérifie seulement la configuration"
        echo "  all   - Lance tous les tests (par défaut)"
        echo "  rag   - Lance uniquement les tests RAG"
        echo "  chat  - Lance uniquement les tests CHAT"
        echo ""
        exit 1
        ;;
esac

echo ""
echo "================================================================================"
echo "FIN"
echo "================================================================================"
