#!/usr/bin/env python3
"""
Extrator de blocos - le um video de referencia e devolve o "dossie":
cenas cortadas em blocos de ate 8s, frames de referencia, tiras de
movimento, mosaico geral e transcricao da fala.

Uso:
    python3 extrator.py video.mp4 -o saida/
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------- ffmpeg ----

def ffmpeg_bin() -> str:
    """Acha o ffmpeg: primeiro o do sistema, depois o wheel do pip."""
    achado = shutil.which("ffmpeg")
    if achado:
        return achado
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    sys.exit(
        "ffmpeg nao encontrado.\n"
        "Resolva com:  pip install imageio-ffmpeg\n"
        "ou instale o ffmpeg do sistema (https://ffmpeg.org/download.html)."
    )


FFMPEG = None  # preenchido no main


def roda(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [FFMPEG, "-hide_banner", "-nostdin", *args],
        capture_output=True, text=True, errors="replace",
    )


# ----------------------------------------------------------------- probe ----

def inspeciona(video: Path) -> dict:
    """Duracao, fps e resolucao lendo o stderr do ffmpeg (dispensa ffprobe)."""
    saida = roda(["-i", str(video)]).stderr

    dados = {"duracao": 0.0, "fps": 30.0, "largura": 0, "altura": 0}

    m = re.search(r"Duration:\s*(\d+):(\d\d):(\d\d(?:\.\d+)?)", saida)
    if m:
        h, mnt, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
        dados["duracao"] = h * 3600 + mnt * 60 + s

    m = re.search(r"Stream #\d+:\d+.*?Video:.*?(\d{2,5})x(\d{2,5})", saida, re.S)
    if m:
        dados["largura"], dados["altura"] = int(m.group(1)), int(m.group(2))

    m = re.search(r"(\d+(?:\.\d+)?)\s*fps", saida)
    if m:
        dados["fps"] = float(m.group(1))

    if dados["duracao"] <= 0:
        sys.exit(f"Nao consegui ler a duracao de {video}. O arquivo esta intacto?")
    return dados


# -------------------------------------------------------- deteccao de corte -

def detecta_cortes(video: Path, limiar: float) -> list[float]:
    """Timestamps onde a imagem muda o suficiente para ser considerado corte."""
    res = roda([
        "-i", str(video),
        "-filter:v", f"select='gt(scene,{limiar})',metadata=print:file=-",
        "-an", "-sn", "-f", "null", "-",
    ])
    tempos = [float(t) for t in re.findall(r"pts_time:(\d+(?:\.\d+)?)", res.stdout)]
    return sorted(set(tempos))


def monta_blocos(cortes: list[float], duracao: float,
                 maximo: float, minimo: float) -> list[tuple[float, float]]:
    """Cortes -> blocos, respeitando o teto de 8s do Flow.

    1. junta pedaco curto demais no anterior (corte-relampago nao vira cena);
    2. parte pedaco longo demais em fatias iguais de ate `maximo`.
    """
    marcos = [0.0] + [c for c in cortes if 0.05 < c < duracao - 0.05] + [duracao]

    brutos: list[list[float]] = []
    for ini, fim in zip(marcos, marcos[1:]):
        if brutos and (fim - ini) < minimo:
            brutos[-1][1] = fim          # gruda no anterior
        else:
            brutos.append([ini, fim])

    if len(brutos) > 1 and (brutos[0][1] - brutos[0][0]) < minimo:
        brutos[1][0] = brutos[0][0]
        brutos.pop(0)

    blocos: list[tuple[float, float]] = []
    for ini, fim in brutos:
        dur = fim - ini
        if dur <= maximo + 0.35:         # tolerancia: 8.3s ainda vira 1 bloco
            blocos.append((ini, fim))
            continue
        partes = math.ceil(dur / maximo)
        passo = dur / partes
        for i in range(partes):
            blocos.append((ini + i * passo, ini + (i + 1) * passo))
    return blocos


def blocos_fixos(duracao: float, tamanho: float) -> list[tuple[float, float]]:
    """Fatiamento cego, para video de plano continuo sem corte nenhum."""
    partes = max(1, math.ceil(duracao / tamanho))
    passo = duracao / partes
    return [(i * passo, (i + 1) * passo) for i in range(partes)]


# ----------------------------------------------------------------- frames ----

def salva_frame(video: Path, t: float, destino: Path, altura: int) -> bool:
    roda([
        "-ss", f"{max(t, 0):.3f}", "-i", str(video),
        "-frames:v", "1",
        "-vf", f"scale=-2:{altura}:flags=lanczos",
        "-q:v", "2", "-y", str(destino),
    ])
    return destino.exists() and destino.stat().st_size > 0


def tc(seg: float) -> str:
    return f"{int(seg // 60)}:{seg % 60:04.1f}"


# --------------------------------------------------------------- montagem ----

def carrega_fonte(tamanho: int):
    from PIL import ImageFont
    candidatos = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for caminho in candidatos:
        if os.path.exists(caminho):
            return ImageFont.truetype(caminho, tamanho)
    try:
        return ImageFont.load_default(size=tamanho)
    except TypeError:
        return ImageFont.load_default()


def tira_de_movimento(frames: list[Path], rotulos: list[str],
                      titulo: str, destino: Path, altura: int = 460) -> None:
    """Inicio | meio | fim lado a lado - deixa o movimento da cena obvio."""
    from PIL import Image, ImageDraw

    imgs = []
    for f in frames:
        im = Image.open(f).convert("RGB")
        escala = altura / im.height
        imgs.append(im.resize((max(1, int(im.width * escala)), altura), Image.LANCZOS))

    vao, topo, pe = 8, 42, 28
    largura = sum(i.width for i in imgs) + vao * (len(imgs) + 1)
    tela = Image.new("RGB", (largura, altura + topo + pe + vao), (15, 17, 23))
    desenho = ImageDraw.Draw(tela)
    desenho.text((vao + 2, 10), titulo, font=carrega_fonte(24), fill=(241, 245, 249))

    x = vao
    fonte_p = carrega_fonte(18)
    for im, rot in zip(imgs, rotulos):
        tela.paste(im, (x, topo))
        desenho.text((x + 4, topo + altura + 5), rot, font=fonte_p, fill=(148, 163, 184))
        x += im.width + vao
    tela.save(destino, quality=88)


def mosaico(entradas: list[tuple[Path, str]], destino: Path,
            colunas: int = 5, altura: int = 380) -> None:
    """Mapa geral: um frame de referencia por cena, numerado."""
    from PIL import Image, ImageDraw

    fonte = carrega_fonte(22)
    imgs = []
    for caminho, _ in entradas:
        im = Image.open(caminho).convert("RGB")
        escala = altura / im.height
        imgs.append(im.resize((max(1, int(im.width * escala)), altura), Image.LANCZOS))

    larg_cel = max(i.width for i in imgs)
    vao, faixa = 10, 34
    linhas = math.ceil(len(imgs) / colunas)
    tela = Image.new(
        "RGB",
        (colunas * larg_cel + vao * (colunas + 1),
         linhas * (altura + faixa) + vao * (linhas + 1)),
        (15, 17, 23),
    )
    desenho = ImageDraw.Draw(tela)

    for idx, (im, (_, rotulo)) in enumerate(zip(imgs, entradas)):
        col, lin = idx % colunas, idx // colunas
        x = vao + col * (larg_cel + vao) + (larg_cel - im.width) // 2
        y = vao + lin * (altura + faixa + vao)
        tela.paste(im, (x, y))

        # encolhe o rotulo ate caber na celula, senao ele invade a vizinha
        fonte_rot = fonte
        for tam in (22, 19, 16, 13):
            fonte_rot = carrega_fonte(tam)
            if desenho.textlength(rotulo, font=fonte_rot) <= larg_cel:
                break
        desenho.text((x, y + altura + 6), rotulo, font=fonte_rot, fill=(241, 245, 249))
    tela.save(destino, quality=88)


# ------------------------------------------------------------- transcricao ---

def extrai_audio(video: Path, destino: Path) -> bool:
    roda(["-i", str(video), "-vn", "-ac", "1", "-ar", "16000", "-y", str(destino)])
    return destino.exists() and destino.stat().st_size > 1000


def transcreve(wav: Path, modelo: str, idioma: str | None) -> list[dict]:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("  ! faster-whisper nao instalado - pulando transcricao.")
        print("    (pip install faster-whisper) Sem ela, a fala sai das legendas dos frames.")
        return []

    print(f"  . transcrevendo com o modelo '{modelo}' (a primeira vez baixa o modelo)...")
    try:
        wm = WhisperModel(modelo, device="cpu", compute_type="int8")
        segmentos, info = wm.transcribe(str(wav), language=idioma, vad_filter=True)
        idioma_detectado = getattr(info, "language", idioma)
        print(f"  . idioma detectado: {idioma_detectado}")
        return [
            {"inicio": round(s.start, 2), "fim": round(s.end, 2), "texto": s.text.strip()}
            for s in segmentos if s.text.strip()
        ]
    except Exception as erro:
        print(f"  ! transcricao falhou ({erro}) - seguindo sem ela.")
        return []


def fala_do_bloco(segmentos: list[dict], ini: float, fim: float) -> str:
    """Junta o que foi dito dentro da janela do bloco (por sobreposicao)."""
    pedacos = []
    for s in segmentos:
        sobreposicao = min(fim, s["fim"]) - max(ini, s["inicio"])
        if sobreposicao > 0.25 * max(0.1, s["fim"] - s["inicio"]):
            pedacos.append(s["texto"])
    return " ".join(pedacos).strip()


# ------------------------------------------------------------------ dossie ---

def escreve_briefing(dossie: dict, pasta: Path, raiz: Path) -> None:
    """Texto pronto pra colar num chat junto com o mosaico e as tiras."""
    modelo = raiz / "prompts" / "analise.md"
    instrucoes = modelo.read_text(encoding="utf-8") if modelo.exists() else \
        "(prompts/analise.md nao encontrado)"

    linhas = [
        instrucoes,
        "\n\n---\n\n# DADOS DO VIDEO ANALISADO\n",
        f"- Arquivo: `{dossie['video']}`",
        f"- Duracao: {dossie['duracao']:.1f}s",
        f"- Resolucao: {dossie['largura']}x{dossie['altura']} @ {dossie['fps']:.0f}fps",
        f"- Blocos detectados: {len(dossie['blocos'])}\n",
        "## Blocos\n",
        "| # | Inicio | Fim | Dur | Frame de referencia | Fala transcrita |",
        "|---|--------|-----|-----|---------------------|-----------------|",
    ]
    for b in dossie["blocos"]:
        fala = (b["fala"] or "-").replace("|", "/")
        linhas.append(
            f"| {b['n']:02d} | {tc(b['inicio'])} | {tc(b['fim'])} | {b['duracao']:.1f}s "
            f"| `{b['frames']['ref']}` | {fala} |"
        )

    linhas += [
        "\n## Imagens em anexo\n",
        "- `mosaico.jpg` - todos os frames de referencia numerados (visao geral).",
        "- `tiras/bloco_NN.jpg` - inicio / meio / fim de cada bloco (mostra o movimento).",
        "\nEntregue o JSON do storyboard seguindo o schema acima.\n",
    ]
    (pasta / "briefing.md").write_text("\n".join(linhas), encoding="utf-8")


def principal() -> None:
    global FFMPEG

    p = argparse.ArgumentParser(
        description="Corta um video de referencia em blocos de ate 8s e monta o dossie.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("video", help="arquivo de video de referencia (mp4, mov...)")
    p.add_argument("-o", "--saida", default=None, help="pasta de saida (padrao: <video>_dossie)")
    p.add_argument("--max", type=float, default=8.0, help="teto do bloco em segundos (padrao 8, limite do Flow)")
    p.add_argument("--min", type=float, default=1.2, help="piso do bloco em segundos (padrao 1.2)")
    p.add_argument("--limiar", type=float, default=0.28, help="sensibilidade do corte, 0.1 a 0.6 (padrao 0.28)")
    p.add_argument("--fixo", action="store_true", help="ignora deteccao e fatia em blocos iguais")
    p.add_argument("--altura", type=int, default=1280, help="altura dos frames extraidos (padrao 1280)")
    p.add_argument("--sem-audio", action="store_true", help="pula a transcricao")
    p.add_argument("--modelo", default="small", help="modelo whisper: tiny|base|small|medium (padrao small)")
    p.add_argument("--idioma", default="pt", help="idioma da fala, ou 'auto' (padrao pt)")
    args = p.parse_args()

    FFMPEG = ffmpeg_bin()
    raiz = Path(__file__).resolve().parent
    video = Path(args.video).expanduser().resolve()
    if not video.exists():
        sys.exit(f"Video nao encontrado: {video}")

    pasta = Path(args.saida).expanduser().resolve() if args.saida \
        else video.with_name(video.stem + "_dossie")
    (pasta / "frames").mkdir(parents=True, exist_ok=True)
    (pasta / "tiras").mkdir(parents=True, exist_ok=True)

    print(f"\n>> Lendo {video.name}")
    info = inspeciona(video)
    print(f"   {info['duracao']:.1f}s | {info['largura']}x{info['altura']} | {info['fps']:.0f}fps")

    if args.fixo:
        blocos = blocos_fixos(info["duracao"], args.max)
        print(f">> Fatiamento fixo: {len(blocos)} blocos de {args.max:.1f}s")
    else:
        print(">> Detectando cortes de cena...")
        cortes = detecta_cortes(video, args.limiar)
        blocos = monta_blocos(cortes, info["duracao"], args.max, args.min)
        print(f"   {len(cortes)} cortes -> {len(blocos)} blocos de ate {args.max:.0f}s")
        if len(blocos) == 1 and info["duracao"] > args.max + 1:
            print("   ! nenhum corte encontrado; caindo pro fatiamento fixo.")
            blocos = blocos_fixos(info["duracao"], args.max)

    segmentos: list[dict] = []
    if not args.sem_audio:
        print(">> Extraindo audio...")
        wav = pasta / "audio.wav"
        if extrai_audio(video, wav):
            idioma = None if args.idioma == "auto" else args.idioma
            segmentos = transcreve(wav, args.modelo, idioma)
            print(f"   {len(segmentos)} trechos de fala")
        else:
            print("   ! video sem faixa de audio.")

    print(">> Extraindo frames...")
    registro, para_mosaico = [], []
    for i, (ini, fim) in enumerate(blocos, start=1):
        dur = fim - ini
        margem = min(0.15, dur * 0.08)
        pontos = {
            "ref": ini + margem,
            "meio": ini + dur / 2,
            "fim": max(ini + margem, fim - margem),
        }
        arquivos = {}
        for nome, t in pontos.items():
            destino = pasta / "frames" / f"bloco_{i:02d}_{nome}.jpg"
            salva_frame(video, t, destino, args.altura)
            arquivos[nome] = f"frames/{destino.name}"

        existentes = [pasta / arquivos[k] for k in ("ref", "meio", "fim")
                      if (pasta / arquivos[k]).exists()]
        tira_rel = ""
        if existentes:
            tira = pasta / "tiras" / f"bloco_{i:02d}.jpg"
            tira_de_movimento(
                existentes,
                [f"inicio {tc(ini)}", f"meio {tc(pontos['meio'])}", f"fim {tc(fim)}"][:len(existentes)],
                f"BLOCO {i:02d}  -  {tc(ini)} ate {tc(fim)}  ({dur:.1f}s)",
                tira,
            )
            tira_rel = f"tiras/{tira.name}"
            para_mosaico.append((pasta / arquivos["ref"], f"#{i:02d}  {tc(ini)} ({dur:.1f}s)"))

        registro.append({
            "n": i,
            "inicio": round(ini, 2),
            "fim": round(fim, 2),
            "duracao": round(dur, 2),
            "frames": arquivos,
            "tira": tira_rel,
            "fala": fala_do_bloco(segmentos, ini, fim),
        })
        print(f"   bloco {i:02d}  {tc(ini)} -> {tc(fim)}  ({dur:.1f}s)")

    if para_mosaico:
        print(">> Montando mosaico...")
        mosaico(para_mosaico, pasta / "mosaico.jpg")

    dossie = {
        "video": video.name,
        "duracao": round(info["duracao"], 2),
        "largura": info["largura"],
        "altura": info["altura"],
        "fps": round(info["fps"], 2),
        "transcricao": segmentos,
        "blocos": registro,
    }
    (pasta / "dossie.json").write_text(
        json.dumps(dossie, ensure_ascii=False, indent=2), encoding="utf-8")
    escreve_briefing(dossie, pasta, raiz)

    print(f"\n== Pronto: {pasta}")
    print(f"   dossie.json   {len(registro)} blocos")
    print( "   mosaico.jpg   mapa das imagens de referencia")
    print( "   tiras/        movimento de cada bloco")
    print( "   briefing.md   texto pronto pra colar no chat\n")


if __name__ == "__main__":
    principal()
