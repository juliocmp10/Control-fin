#!/usr/bin/env python3
"""
Analisador - manda o dossie (mosaico + tiras + transcricao) pro Claude e
recebe o storyboard.json com os prompts de cada cena.

Precisa da variavel de ambiente ANTHROPIC_API_KEY.

Uso:
    python3 analisador.py saida/
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
import re
import sys
import time
from pathlib import Path

API = "https://api.anthropic.com/v1/messages"
MODELO_PADRAO = os.environ.get("ANTHROPIC_MODEL", "claude-opus-5")


def imagem_para_bloco(caminho: Path, largura_max: int = 900) -> dict | None:
    """Le a imagem, encolhe se precisar e devolve no formato da API."""
    if not caminho.exists():
        return None
    dados = caminho.read_bytes()
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(dados))
        if im.width > largura_max:
            altura = int(im.height * largura_max / im.width)
            im = im.convert("RGB").resize((largura_max, altura), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=82)
            dados = buf.getvalue()
    except Exception:
        pass  # sem Pillow, manda como esta
    return {
        "type": "image",
        "source": {"type": "base64", "media_type": "image/jpeg",
                   "data": base64.b64encode(dados).decode()},
    }


def monta_conteudo(pasta: Path, dossie: dict, instrucoes: str) -> list[dict]:
    conteudo: list[dict] = [{
        "type": "text",
        "text": (
            f"{instrucoes}\n\n---\n\n# DOSSIE\n\n"
            f"- Arquivo: {dossie['video']}\n"
            f"- Duracao: {dossie['duracao']:.1f}s\n"
            f"- Resolucao: {dossie['largura']}x{dossie['altura']}\n"
            f"- Blocos: {len(dossie['blocos'])}\n\n"
            "A seguir vem o mosaico geral e, depois, a tira de cada bloco "
            "(inicio / meio / fim) com os tempos e a fala transcrita."
        ),
    }]

    mosaico = imagem_para_bloco(pasta / "mosaico.jpg", largura_max=1400)
    if mosaico:
        conteudo += [{"type": "text", "text": "\n## Mosaico geral (todas as cenas numeradas)"}, mosaico]

    for b in dossie["blocos"]:
        cabecalho = (
            f"\n## BLOCO {b['n']:02d}  |  {b['inicio']:.1f}s -> {b['fim']:.1f}s  "
            f"({b['duracao']:.1f}s)\n"
            f"Fala transcrita: {b['fala'] or '(sem fala)'}"
        )
        conteudo.append({"type": "text", "text": cabecalho})
        tira = imagem_para_bloco(pasta / b["tira"]) if b.get("tira") else None
        if tira:
            conteudo.append(tira)

    conteudo.append({
        "type": "text",
        "text": (f"\n---\n\nGere agora o storyboard das {len(dossie['blocos'])} cenas. "
                 "Responda somente o JSON do schema, sem nenhum texto antes ou depois."),
    })
    return conteudo


def chama_api(chave: str, modelo: str, conteudo: list[dict], tentativas: int = 4) -> str:
    import requests

    corpo = {
        "model": modelo,
        "max_tokens": 16000,
        "messages": [{"role": "user", "content": conteudo}],
    }
    cabecalhos = {
        "x-api-key": chave,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    espera = 4
    for tentativa in range(1, tentativas + 1):
        resposta = requests.post(API, headers=cabecalhos, json=corpo, timeout=600)
        if resposta.status_code == 200:
            return "".join(
                p.get("text", "") for p in resposta.json().get("content", [])
                if p.get("type") == "text"
            )
        if resposta.status_code in (429, 500, 502, 503, 529) and tentativa < tentativas:
            print(f"  ! API respondeu {resposta.status_code}; tentando de novo em {espera}s")
            time.sleep(espera)
            espera *= 2
            continue
        sys.exit(f"API falhou ({resposta.status_code}): {resposta.text[:400]}")
    sys.exit("API nao respondeu depois de varias tentativas.")


def extrai_json(texto: str) -> dict:
    cerca = re.search(r"```(?:json)?\s*(.+?)```", texto, re.S)
    bruto = cerca.group(1) if cerca else texto
    inicio, fim = bruto.find("{"), bruto.rfind("}")
    if inicio == -1 or fim == -1:
        sys.exit(f"A resposta nao trouxe JSON:\n{texto[:600]}")
    return json.loads(bruto[inicio:fim + 1])


def confere(storyboard: dict, dossie: dict) -> None:
    """Avisos uteis - nao interrompe, so aponta o que revisar."""
    cenas, blocos = storyboard.get("cenas", []), dossie["blocos"]
    if len(cenas) != len(blocos):
        print(f"  ! a analise trouxe {len(cenas)} cenas para {len(blocos)} blocos - confira.")

    for c in cenas:
        dur = float(c.get("duracao") or 0)
        if dur > 8.05:
            print(f"  ! cena {c.get('n')} tem {dur:.1f}s - o Flow so gera 8s.")
        palavras = len(str(c.get("fala", "")).split())
        if palavras > round(max(dur, 1) * 2.2):
            print(f"  ! cena {c.get('n')}: {palavras} palavras em {dur:.1f}s - a fala vai cortar.")
        if not c.get("prompt_video"):
            print(f"  ! cena {c.get('n')} sem prompt_video.")

    fixo = (storyboard.get("biblia_visual") or {}).get("trecho_fixo", "")
    if fixo:
        faltando = [c.get("n") for c in cenas if fixo[:40] not in str(c.get("prompt_video", ""))]
        if faltando:
            print(f"  ! biblia visual ausente nos prompts das cenas {faltando} - risco de quebrar a continuidade.")


def principal() -> None:
    p = argparse.ArgumentParser(description="Gera o storyboard chamando a API do Claude.")
    p.add_argument("pasta", help="pasta do dossie")
    p.add_argument("--modelo", default=MODELO_PADRAO, help=f"modelo (padrao {MODELO_PADRAO})")
    p.add_argument("-o", "--saida", default=None, help="json de saida (padrao: <pasta>/storyboard.json)")
    args = p.parse_args()

    chave = os.environ.get("ANTHROPIC_API_KEY")
    if not chave:
        sys.exit("Falta a ANTHROPIC_API_KEY.\n"
                 "  Linux/Mac: export ANTHROPIC_API_KEY=sk-ant-...\n"
                 "  Windows:   setx ANTHROPIC_API_KEY sk-ant-...\n"
                 "Sem chave, use o modo manual: mande briefing.md + mosaico.jpg + tiras/ no chat.")

    pasta = Path(args.pasta).expanduser().resolve()
    arq = pasta / "dossie.json"
    if not arq.exists():
        sys.exit(f"Nao encontrei {arq} - rode o extrator.py primeiro.")

    dossie = json.loads(arq.read_text(encoding="utf-8"))
    raiz = Path(__file__).resolve().parent
    instrucoes = (raiz / "prompts" / "analise.md").read_text(encoding="utf-8")

    print(f">> Analisando {len(dossie['blocos'])} blocos com {args.modelo}...")
    conteudo = monta_conteudo(pasta, dossie, instrucoes)
    imagens = sum(1 for c in conteudo if c.get("type") == "image")
    print(f"   enviando {imagens} imagens")

    resposta = chama_api(chave, args.modelo, conteudo)
    storyboard = extrai_json(resposta)
    confere(storyboard, dossie)

    destino = Path(args.saida).expanduser().resolve() if args.saida else pasta / "storyboard.json"
    destino.write_text(json.dumps(storyboard, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n== {destino}  ({len(storyboard.get('cenas', []))} cenas)")
    print(f"   agora rode:  python3 montador.py {pasta}")


if __name__ == "__main__":
    principal()
