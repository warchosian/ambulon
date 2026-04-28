"""
Convertisseurs de diagrammes vers SVG.

Supporte:
- PlantUML (via Kroki ou JAR local)
- Mermaid (via Kroki)
- Graphviz/DOT (via commande dot ou Kroki)
"""

from __future__ import annotations

import base64
import logging
import os
import re
import subprocess
import tempfile
import urllib.request
import urllib.error
import zlib
from importlib.util import find_spec
from pathlib import Path
from typing import Dict, Optional, Callable

# Suppress RequestsDependencyWarning about urllib3/chardet version mismatch
import warnings

warnings.filterwarnings(
    "ignore", message="urllib3 .* or chardet .* doesn't match a supported version"
)
warnings.filterwarnings("ignore", message="doesn't match a supported version")
import requests

from .base import ConversionResult, ConversionMethod, DiagramType

logger = logging.getLogger(__name__)


# =============================================================================
# UTILITAIRES
# =============================================================================


def _java_available(min_major: int = 8) -> bool:
    """Vérifie que Java est disponible et correspond à la version minimale."""
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, timeout=10)
    except Exception:
        return False

    output = (result.stderr or b"") + (result.stdout or b"")
    text = output.decode("utf-8", errors="ignore")

    version_match = re.search(r'version "([^"]+)"', text)
    if not version_match:
        return False

    version_str = version_match.group(1)
    if version_str.startswith("1."):
        parts = version_str.split(".")
        major = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    else:
        major = (
            int(version_str.split(".")[0]) if version_str.split(".")[0].isdigit() else 0
        )

    return major >= min_major


def _kroki_module_available() -> bool:
    """Vérifie si le package kroki Python est disponible."""
    return find_spec("kroki") is not None


def _try_kroki_module_render(diagram_type: str, diagram_code: str) -> Optional[str]:
    """
    Essaie de rendre via le package kroki Python optionnel.

    Args:
        diagram_type: Type de diagramme ('plantuml', 'mermaid', etc.)
        diagram_code: Code source du diagramme

    Returns:
        Contenu SVG ou None si échec
    """
    if not _kroki_module_available():
        return None

    try:
        import kroki as kroki_module
    except Exception:
        return None

    try:
        if hasattr(kroki_module, "Kroki"):
            client = kroki_module.Kroki()
            return client.diagram(diagram_type, diagram_code, "svg")
        if hasattr(kroki_module, "Client"):
            client = kroki_module.Client()
            return client.diagram(diagram_type, diagram_code, "svg")
        if hasattr(kroki_module, "get_diagram"):
            return kroki_module.get_diagram(diagram_type, diagram_code, "svg")
    except Exception:
        return None

    return None


# =============================================================================
# PLANTUML
# =============================================================================


def convert_plantuml(
    plantuml_code: str,
    method: ConversionMethod = ConversionMethod.KROKI,
    plantuml_jar: Optional[str] = None,
    timeout: int = 30,
) -> ConversionResult:
    """
    Convertit du code PlantUML en SVG.

    Args:
        plantuml_code: Code PlantUML
        method: Méthode de conversion (KROKI, JAR, AUTO)
        plantuml_jar: Chemin vers le JAR PlantUML (pour méthode JAR)
        timeout: Timeout en secondes

    Returns:
        Résultat de la conversion
    """
    # Normalise le code
    plantuml_code = _normalize_plantuml_code(plantuml_code)

    # Détermine la méthode si AUTO
    if method == ConversionMethod.AUTO:
        jar_path = _get_plantuml_jar_path(plantuml_jar)
        if jar_path and _java_available():
            method = ConversionMethod.JAR
        else:
            method = ConversionMethod.KROKI

    # Exécute la conversion
    if method == ConversionMethod.JAR:
        return _convert_plantuml_with_jar(plantuml_code, plantuml_jar, timeout)
    else:
        return _convert_plantuml_with_kroki(plantuml_code, timeout)


def _normalize_plantuml_code(plantuml_code: str) -> str:
    """
    Normalise le code PlantUML pour la conversion.

    Supprime le nom du diagramme après @startuml pour éviter
    les problèmes de nommage de fichier.
    """
    # Supprime le nom après @startuml
    code = re.sub(r"@startuml[ \t]+\S+", "@startuml", plantuml_code, count=1)
    return code


def _get_plantuml_jar_path(cli_jar_path: Optional[str] = None) -> Optional[str]:
    """
    Détermine le chemin du JAR PlantUML.

    Priorité: CLI arg > ENV var > None
    """
    if cli_jar_path and Path(cli_jar_path).exists():
        return cli_jar_path

    env_jar = os.environ.get("PLANTUML_JAR")
    if env_jar and Path(env_jar).exists():
        return env_jar

    return None


def _convert_plantuml_with_jar(
    plantuml_code: str, jar_path: Optional[str] = None, timeout: int = 30
) -> ConversionResult:
    """
    Convertit PlantUML en utilisant le JAR local.
    """
    jar = _get_plantuml_jar_path(jar_path)

    if not jar:
        return ConversionResult(
            success=False,
            error_message="PlantUML JAR not found. Set PLANTUML_JAR env var or use --plantuml-jar",
        )

    if not _java_available():
        return ConversionResult(
            success=False, error_message="Java not available or version too old"
        )

    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".puml", delete=False, encoding="utf-8"
        ) as f:
            f.write(plantuml_code)
            temp_input = f.name

        temp_output = temp_input.replace(".puml", ".svg")

        result = subprocess.run(
            ["java", "-jar", jar, "-tsvg", temp_input],
            capture_output=True,
            timeout=timeout,
        )

        # Attend que le fichier soit écrit
        import time

        for _ in range(10):
            if Path(temp_output).exists():
                break
            time.sleep(0.1)

        # Nettoie le fichier temporaire d'entrée
        if Path(temp_input).exists():
            os.unlink(temp_input)

        if result.returncode == 0 and Path(temp_output).exists():
            with open(temp_output, "r", encoding="utf-8") as f:
                svg_content = f.read()
            os.unlink(temp_output)

            return ConversionResult(
                success=True, svg_content=svg_content, method_used="jar"
            )
        else:
            error = (
                result.stderr.decode("utf-8", errors="replace")
                if result.stderr
                else "Unknown error"
            )
            if Path(temp_output).exists():
                os.unlink(temp_output)
            return ConversionResult(
                success=False, error_message=f"PlantUML JAR failed: {error}"
            )

    except subprocess.TimeoutExpired:
        return ConversionResult(
            success=False, error_message="PlantUML JAR conversion timed out"
        )
    except Exception as e:
        return ConversionResult(success=False, error_message=f"PlantUML JAR error: {e}")


def _convert_plantuml_with_kroki(
    plantuml_code: str, timeout: int = 30
) -> ConversionResult:
    """
    Convertit PlantUML en utilisant le service Kroki.
    """
    # Essaie d'abord le module kroki si disponible
    svg = _try_kroki_module_render("plantuml", plantuml_code)
    if svg:
        return ConversionResult(
            success=True, svg_content=svg, method_used="kroki-module"
        )

    # Sinon utilise l'API HTTP directe
    try:
        compressed = zlib.compress(plantuml_code.encode("utf-8"), 9)
        encoded = base64.urlsafe_b64encode(compressed).decode("utf-8")
        url = f"https://kroki.io/plantuml/svg/{encoded}"

        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Mozilla/5.0 (Ambulon)")

        with urllib.request.urlopen(req, timeout=timeout) as response:
            svg_content = response.read().decode("utf-8")

        return ConversionResult(
            success=True, svg_content=svg_content, method_used="kroki-http"
        )

    except urllib.error.URLError as e:
        return ConversionResult(
            success=False,
            error_message=f"Kroki service unavailable: {e}. Check your internet connection or use --plantuml-method jar",
        )
    except Exception as e:
        return ConversionResult(
            success=False, error_message=f"Kroki conversion error: {e}"
        )


# =============================================================================
# MERMAID
# =============================================================================


def convert_mermaid(mermaid_code: str, timeout: int = 30) -> ConversionResult:
    """
    Convertit du code Mermaid en SVG.

    Args:
        mermaid_code: Code Mermaid
        timeout: Timeout en secondes

    Returns:
        Résultat de la conversion
    """
    # Essaie d'abord le module kroki si disponible
    svg = _try_kroki_module_render("mermaid", mermaid_code)
    if svg:
        return ConversionResult(
            success=True, svg_content=svg, method_used="kroki-module"
        )

    # Sinon utilise l'API HTTP
    try:
        compressed = zlib.compress(mermaid_code.encode("utf-8"), 9)
        encoded = base64.urlsafe_b64encode(compressed).decode("utf-8")
        url = f"https://kroki.io/mermaid/svg/{encoded}"

        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Mozilla/5.0 (Ambulon)")

        with urllib.request.urlopen(req, timeout=timeout) as response:
            svg_content = response.read().decode("utf-8")

        return ConversionResult(
            success=True, svg_content=svg_content, method_used="kroki-http"
        )

    except Exception as e:
        return ConversionResult(
            success=False, error_message=f"Mermaid conversion error: {e}"
        )


# =============================================================================
# GRAPHVIZ
# =============================================================================


def convert_graphviz(dot_code: str, timeout: int = 30) -> ConversionResult:
    """
    Convertit du code Graphviz DOT en SVG.

    Args:
        dot_code: Code DOT
        timeout: Timeout en secondes

    Returns:
        Résultat de la conversion
    """
    # Essaie d'abord la commande dot locale
    result = _convert_graphviz_with_dot(dot_code, timeout)
    if result.success:
        return result

    # Fallback sur Kroki
    return _convert_graphviz_with_kroki(dot_code, timeout)


def _convert_graphviz_with_dot(dot_code: str, timeout: int = 30) -> ConversionResult:
    """
    Convertit Graphviz en utilisant la commande dot locale.
    """
    dot_command = "dot"

    # Vérifie GRAPHVIZ_EXE
    graphviz_exe = os.environ.get("GRAPHVIZ_EXE")
    if graphviz_exe and Path(graphviz_exe).exists():
        dot_command = graphviz_exe

    try:
        result = subprocess.run(
            [dot_command, "-Tsvg"],
            input=dot_code.encode("utf-8"),
            capture_output=True,
            timeout=timeout,
        )

        if result.returncode == 0:
            return ConversionResult(
                success=True,
                svg_content=result.stdout.decode("utf-8"),
                method_used="graphviz-dot",
            )
        else:
            error = (
                result.stderr.decode("utf-8", errors="replace")
                if result.stderr
                else "Unknown error"
            )
            return ConversionResult(
                success=False, error_message=f"Graphviz failed: {error}"
            )

    except FileNotFoundError:
        return ConversionResult(
            success=False, error_message="Graphviz 'dot' command not found"
        )
    except subprocess.TimeoutExpired:
        return ConversionResult(
            success=False, error_message="Graphviz conversion timed out"
        )
    except Exception as e:
        return ConversionResult(success=False, error_message=f"Graphviz error: {e}")


def _convert_graphviz_with_kroki(dot_code: str, timeout: int = 30) -> ConversionResult:
    """
    Convertit Graphviz en utilisant le service Kroki.
    """
    try:
        url = "https://kroki.io/graphviz/svg"

        response = requests.post(
            url,
            data=dot_code.encode("utf-8"),
            headers={"Content-Type": "text/plain"},
            timeout=timeout,
        )

        if response.status_code == 200:
            return ConversionResult(
                success=True, svg_content=response.text, method_used="kroki-http"
            )
        else:
            return ConversionResult(
                success=False,
                error_message=f"Kroki returned HTTP {response.status_code}",
            )

    except Exception as e:
        return ConversionResult(
            success=False, error_message=f"Kroki Graphviz error: {e}"
        )


# =============================================================================
# DISPATCHER GÉNÉRIQUE
# =============================================================================

CONVERTERS: Dict[DiagramType, Callable] = {
    DiagramType.PLANTUML: convert_plantuml,
    DiagramType.MERMAID: convert_mermaid,
    DiagramType.GRAPHVIZ: convert_graphviz,
    DiagramType.DOT: convert_graphviz,
}


def convert_diagram(
    diagram_type: DiagramType,
    diagram_code: str,
    method: ConversionMethod = ConversionMethod.KROKI,
    plantuml_jar: Optional[str] = None,
    timeout: int = 30,
) -> ConversionResult:
    """
    Convertit un diagramme vers SVG selon son type.

    Args:
        diagram_type: Type de diagramme
        diagram_code: Code source du diagramme
        method: Méthode de conversion (pour PlantUML)
        plantuml_jar: Chemin vers le JAR PlantUML
        timeout: Timeout en secondes

    Returns:
        Résultat de la conversion
    """
    converter = CONVERTERS.get(diagram_type)

    if not converter:
        return ConversionResult(
            success=False,
            error_message=f"No converter available for diagram type: {diagram_type}",
        )

    if diagram_type == DiagramType.PLANTUML:
        return converter(diagram_code, method, plantuml_jar, timeout)
    else:
        return converter(diagram_code, timeout)
