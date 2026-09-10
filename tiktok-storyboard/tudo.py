#!/usr/bin/env python3
"""
Atalho: video -> dossie -> analise -> storyboard.html, num comando so.

    python3 tudo.py video.mp4

Precisa da ANTHROPIC_API_KEY. Sem ela, rode o extrator.py sozinho e mande
o briefing.md junto com as imagens num chat com o Claude.
"""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


def etapa(titulo: str, args: list[str]) -> None:
    print(f"\n{'=' * 62}\n {titulo}\n{'=' * 62}")
    if subprocess.run([sys.executable, *args]).returncode != 0:
        sys.exit(f"\nParou em: {titulo}")


def principal() -> None:
    if len(sys.argv) < 2:
        sys.exit("uso: python3 tudo.py video.mp4 [outros argumentos do extrator]")

    video = Path(sys.argv[1]).expanduser().resolve()
    if not video.exists():
        sys.exit(f"Video nao encontrado: {video}")

    pasta = video.with_name(video.stem + "_dossie")
    etapa("1/3  Cortando o video em blocos",
          [str(RAIZ / "extrator.py"), str(video), "-o", str(pasta), *sys.argv[2:]])
    etapa("2/3  Escrevendo os prompts", [str(RAIZ / "analisador.py"), str(pasta)])
    etapa("3/3  Montando o storyboard", [str(RAIZ / "montador.py"), str(pasta)])

    print(f"\n>> Abra: {pasta / 'storyboard.html'}\n")


if __name__ == "__main__":
    principal()
