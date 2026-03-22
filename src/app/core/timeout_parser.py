#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de parsing des valeurs de timeout avec unités.

Permet d'accepter des valeurs comme :
- 10000 (millisecondes par défaut)
- 10000ms (millisecondes explicites)
- 10s (secondes)
- 2m (minutes)
"""
import re


def parse_timeout(value) -> int:
    """
    Parse une valeur de timeout avec suffixe optionnel et retourne les millisecondes.

    Args:
        value: Valeur du timeout (int, str)
            - int: millisecondes directement
            - str: nombre + suffixe optionnel (ms, s, m)

    Returns:
        int: Timeout en millisecondes

    Raises:
        ValueError: Si le format est invalide

    Examples:
        >>> parse_timeout(10000)
        10000
        >>> parse_timeout("10000")
        10000
        >>> parse_timeout("10000ms")
        10000
        >>> parse_timeout("10s")
        10000
        >>> parse_timeout("2m")
        120000
    """
    # Si c'est déjà un int, retourner tel quel
    if isinstance(value, int):
        return value

    # Convertir en string si nécessaire
    value_str = str(value).strip().lower()

    # Pattern: nombre + suffixe optionnel (ms, s, m)
    pattern = r'^(\d+(?:\.\d+)?)(ms|s|m)?$'
    match = re.match(pattern, value_str)

    if not match:
        raise ValueError(
            f"Format de timeout invalide: '{value}'. "
            f"Utilisez un nombre optionnellement suivi de 'ms', 's' ou 'm'. "
            f"Exemples: 10000, 10000ms, 10s, 2m"
        )

    number_str, unit = match.groups()
    number = float(number_str)

    # Conversion en millisecondes selon l'unité
    if unit is None or unit == 'ms':
        # Millisecondes (par défaut)
        timeout_ms = int(number)
    elif unit == 's':
        # Secondes → millisecondes
        timeout_ms = int(number * 1000)
    elif unit == 'm':
        # Minutes → millisecondes
        timeout_ms = int(number * 60 * 1000)
    else:
        raise ValueError(f"Unité inconnue: '{unit}'. Utilisez 'ms', 's' ou 'm'.")

    return timeout_ms


def format_timeout(timeout_ms: int) -> str:
    """
    Formate un timeout en millisecondes en format lisible.

    Args:
        timeout_ms: Timeout en millisecondes

    Returns:
        str: Format lisible avec unités

    Examples:
        >>> format_timeout(10000)
        '10000ms = 10s'
        >>> format_timeout(60000)
        '60000ms = 60s = 1m'
        >>> format_timeout(120000)
        '120000ms = 120s = 2m'
    """
    parts = [f"{timeout_ms}ms"]

    # Ajouter les secondes si >= 1s
    if timeout_ms >= 1000:
        seconds = timeout_ms // 1000
        parts.append(f"{seconds}s")

    # Ajouter les minutes si >= 1m
    if timeout_ms >= 60000:
        minutes = timeout_ms // 60000
        parts.append(f"{minutes}m")

    return " = ".join(parts)
