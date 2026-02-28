#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import io

# Force UTF-8 encoding for stdout on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def format_tokens(tokens):
    """Formate les tokens en k pour les milliers"""
    if tokens >= 1000:
        return f"{tokens/1000:.1f}k"
    return str(tokens)

try:
    data = json.load(sys.stdin)
    model = data.get('model', {}).get('display_name', 'Unknown')

    # Context window info
    context_window = data.get('context_window', {})
    pct = int(context_window.get('used_percentage', 0) or 0)
    tokens_in = context_window.get('total_input_tokens', 0) or 0
    tokens_out = context_window.get('total_output_tokens', 0) or 0
    context_size = context_window.get('context_window_size', 0) or 0

    # Current context usage
    current_usage = context_window.get('current_usage', {}) or {}
    current_input = current_usage.get('input_tokens', 0) or 0
    cache_read = current_usage.get('cache_read_input_tokens', 0) or 0
    cache_write = current_usage.get('cache_creation_input_tokens', 0) or 0

    # Cost info
    cost = data.get('cost', {}).get('total_cost_usd', 0) or 0
    duration_ms = data.get('cost', {}).get('total_duration_ms', 0) or 0

    # Calcul des tokens restants
    total_tokens = tokens_in + tokens_out
    remaining_tokens = context_size - total_tokens if context_size > 0 else 0

    # Calcul de l'économie grâce au cache (cache read coûte 10x moins cher)
    # Prix approximatif : input normal ~$3/M, cache read ~$0.30/M
    cache_savings = (cache_read / 1_000_000) * 2.7 if cache_read > 0 else 0

    # Barre de progression (20 caractères)
    filled = pct * 20 // 100
    bar = '█' * filled + '░' * (20 - filled)

    # Temps écoulé
    mins = duration_ms // 60000
    secs = (duration_ms % 60000) // 1000

    # Format des tokens
    in_fmt = format_tokens(tokens_in)
    out_fmt = format_tokens(tokens_out)
    total_fmt = format_tokens(total_tokens)
    context_fmt = format_tokens(context_size)
    remaining_fmt = format_tokens(remaining_tokens)
    current_context_fmt = format_tokens(current_input)
    cache_read_fmt = format_tokens(cache_read)
    cache_write_fmt = format_tokens(cache_write)

    # Construction de l'affichage
    status = f"🤖 {model} │ {bar} {pct}% │ 📊 {total_fmt}/{context_fmt}"
    status += f" │ 📦 Left: {remaining_fmt}"
    status += f" │ 💾 Context: {current_context_fmt}"
    status += f" │ 📥 {in_fmt} 📤 {out_fmt}"

    # Ajout des stats de cache si disponibles
    if cache_read > 0 or cache_write > 0:
        status += f" │ ⚡ Cache: {cache_read_fmt}R {cache_write_fmt}W"
        if cache_savings > 0.0001:
            status += f" 💸 Saved: ${cache_savings:.4f}"

    status += f" │ 💰 ${cost:.4f} │ ⏱️ {mins}m{secs:02d}s"

    print(status)
except Exception as e:
    print(f"⚠️  Erreur statusLine: {e}")
