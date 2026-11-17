#!/usr/bin/env python3
"""
Monta todas as combinações GANCHO -> DESENVOLVIMENTO -> CTA a partir de cenas soltas.

Uso básico:
    python3 montar.py cenas/fone-bluetooth

Dentro da pasta, nomeie as cenas assim (qualquer extensão de vídeo):
    gancho1.mp4  gancho2.mp4  gancho3.mp4
    desenv1.mp4  desenv2.mp4  desenv3.mp4
    cta1.mp4     cta2.mp4     cta3.mp4
(também aceita g1/d1/c1, hook1, dev1 etc. Pode ter 2, 3, 4... de cada.)

Saída: <pasta>/prontos/ com os vídeos e um plano_postagem.csv.
Com quantidades iguais de cada tipo (ex.: 3/3/3) os vídeos saem em LOTES:
cada lote usa cada gancho, cada desenvolvimento e cada CTA exatamente uma vez,
ou seja, dentro de um lote nenhuma cena se repete.
"""
import argparse
import csv
import json
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

W, H, FPS, AR = 1080, 1920, 30, 44100
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi", ".3gp"}
TIPOS = {
    "G": ("gancho", "hook", "g"),
    "D": ("desenv", "desenvolvimento", "dev", "d", "meio", "corpo"),
    "C": ("cta", "c", "final"),
}


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        sys.exit(f"\nERRO no ffmpeg:\n{' '.join(map(str, cmd))}\n{r.stderr[-2000:]}")
    return r.stdout


def tem_audio(path):
    out = run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
               "stream=index", "-of", "json", str(path)])
    return bool(json.loads(out).get("streams"))


def duracao(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=nw=1:nk=1", str(path)])
    return float(out.strip())


def classificar(pasta):
    cenas = {"G": [], "D": [], "C": []}
    for f in sorted(pasta.iterdir()):
        if f.suffix.lower() not in VIDEO_EXT:
            continue
        m = re.match(r"^([a-zA-Z]+)[ _-]*(\d+)", f.stem)
        if not m:
            print(f"  ignorando (nome fora do padrão): {f.name}")
            continue
        prefixo, num = m.group(1).lower(), int(m.group(2))
        for tipo, nomes in TIPOS.items():
            if prefixo in nomes:
                cenas[tipo].append((num, f))
                break
        else:
            print(f"  ignorando (não sei se é gancho/desenv/cta): {f.name}")
    for t in cenas:
        cenas[t] = [f for _, f in sorted(cenas[t])]
    return cenas


def normalizar(src, dst):
    """Deixa toda cena em 1080x1920, 30fps, H.264 + AAC estéreo, para emendar sem pulos."""
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps={FPS},format=yuv420p")
    audio = tem_audio(src)
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(src)]
    if not audio:
        cmd += ["-f", "lavfi", "-i", f"anullsrc=r={AR}:cl=stereo"]
    # áudio com exatamente a mesma duração do vídeo (evita dessincronizar ao emendar)
    cmd += ["-map", "0:v:0", "-map", "0:a:0" if audio else "1:a:0",
            "-vf", vf, "-af", "aresample=async=1,apad", "-shortest",
            "-fflags", "+shortest", "-max_interleave_delta", "0",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k", "-ar", str(AR), "-ac", "2",
            "-map_metadata", "-1", "-movflags", "+faststart", str(dst)]
    run(cmd)


def ordem_em_lotes(nG, nD, nC):
    """Retorna lista de lotes; cada lote é uma lista de (g, d, c) com índices base 0."""
    if nG == nD == nC:
        n = nG
        deslocs = [(a, b) for a in range(n) for b in range(n)]
        # embaralha de forma fixa para lotes vizinhos ficarem bem diferentes
        random.Random(42).shuffle(deslocs)
        return [[(g, (g + a) % n, (g + b) % n) for g in range(n)] for a, b in deslocs]
    # quantidades diferentes: lotes com um vídeo por gancho, girando D e C
    todas = [(g, d, c) for g in range(nG) for d in range(nD) for c in range(nC)]
    por_gancho = {g: [x for x in todas if x[0] == g] for g in range(nG)}
    for g in por_gancho:
        por_gancho[g].sort(key=lambda x: ((x[1] - g) % nD, (x[2] - g) % nC))
    lotes = []
    while any(por_gancho.values()):
        lotes.append([por_gancho[g].pop(0) for g in range(nG) if por_gancho[g]])
    return lotes


def montar(partes, saida, musica=None, vol_musica=0.12, so_musica=False, variar=None):
    lista = saida.with_suffix(".txt")
    lista.write_text("".join(f"file '{p.resolve()}'\n" for p in partes))
    if not musica and not variar:
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lista),
             "-c", "copy", "-map_metadata", "-1", "-movflags", "+faststart", str(saida)])
        lista.unlink()
        return

    total = sum(duracao(p) for p in partes)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lista)]
    filtros, vmap, amap = [], "0:v", "0:a"
    if variar:
        z, br, ct, sat = variar
        cw, ch = int(W / z) // 2 * 2, int(H / z) // 2 * 2
        filtros.append(f"[0:v]crop={cw}:{ch},scale={W}:{H},setsar=1,"
                       f"eq=brightness={br:.3f}:contrast={ct:.3f}:saturation={sat:.3f}[v]")
        vmap = "[v]"
    if musica:
        cmd += ["-stream_loop", "-1", "-i", str(musica)]
        if so_musica:
            filtros.append("[1:a]aresample=44100[a]")
        else:
            filtros.append(f"[1:a]volume={vol_musica}[m];[0:a][m]amix=inputs=2:duration=first:"
                           f"dropout_transition=0:normalize=0[a]")
        amap = "[a]"
    if filtros:
        cmd += ["-filter_complex", ";".join(filtros)]
    cmd += ["-map", vmap, "-map", amap]
    cmd += (["-c:v", "libx264", "-preset", "medium", "-crf", "19"] if variar else ["-c:v", "copy"])
    cmd += ["-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", "-map_metadata", "-1",
            "-movflags", "+faststart", str(saida)]
    run(cmd)
    lista.unlink()


def main():
    ap = argparse.ArgumentParser(description="Gera combinações gancho/desenvolvimento/CTA.")
    ap.add_argument("pasta", help="pasta com as cenas (gancho1, desenv1, cta1...)")
    ap.add_argument("--musica", help="arquivo de música de fundo (opcional)")
    ap.add_argument("--volume-musica", type=float, default=0.12,
                    help="volume da música por baixo da narração (padrão 0.12)")
    ap.add_argument("--so-musica", action="store_true",
                    help="tira o áudio original e deixa só a música (vídeos sem narração)")
    ap.add_argument("--variar", action="store_true",
                    help="aplica micro-variações (zoom 1-4%%, brilho/contraste/cor) em cada vídeo")
    ap.add_argument("--lotes", help="gera só esses lotes, ex.: 1,2,3 (padrão: todos)")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg não encontrado.")
    pasta = Path(args.pasta)
    cenas = classificar(pasta)
    nG, nD, nC = (len(cenas[t]) for t in "GDC")
    print(f"Cenas: {nG} ganchos, {nD} desenvolvimentos, {nC} CTAs -> {nG*nD*nC} combinações")
    if 0 in (nG, nD, nC):
        sys.exit("Falta pelo menos 1 cena de cada tipo.")

    tmp = pasta / ".normalizadas"
    tmp.mkdir(exist_ok=True)
    norm = {}
    for t in "GDC":
        for i, f in enumerate(cenas[t]):
            dst = tmp / f"{t}{i+1}.mp4"
            if not dst.exists() or dst.stat().st_mtime < f.stat().st_mtime:
                print(f"  normalizando {f.name}...")
                normalizar(f, dst)
            norm[(t, i)] = dst

    out = pasta / "prontos"
    out.mkdir(exist_ok=True)
    lotes = ordem_em_lotes(nG, nD, nC)
    filtro = {int(x) for x in args.lotes.split(",")} if args.lotes else None
    rng = random.Random(7)
    linhas = []
    for li, lote in enumerate(lotes, 1):
        for vi, (g, d, c) in enumerate(lote, 1):
            variar = None
            if args.variar:
                variar = (rng.uniform(1.01, 1.04), rng.uniform(-0.03, 0.03),
                          rng.uniform(0.97, 1.05), rng.uniform(0.95, 1.08))
            nome = f"lote{li:02d}_v{vi}_G{g+1}-D{d+1}-C{c+1}.mp4"
            dur = ""
            if filtro is None or li in filtro:
                partes = [norm[("G", g)], norm[("D", d)], norm[("C", c)]]
                print(f"  montando {nome}")
                montar(partes, out / nome, args.musica, args.volume_musica,
                       args.so_musica, variar)
                dur = round(duracao(out / nome), 1)
            linhas.append({"lote": li, "video": vi, "arquivo": nome,
                           "gancho": cenas["G"][g].name, "desenvolvimento": cenas["D"][d].name,
                           "cta": cenas["C"][c].name, "duracao_s": dur,
                           "postado": "", "views": "", "vendas": ""})

    with open(out / "plano_postagem.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    print(f"\nPronto: {len(linhas)} combinações em {len(lotes)} lotes -> {out}")


if __name__ == "__main__":
    main()
