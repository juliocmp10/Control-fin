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


def data_gravacao(path):
    """Quando a cena foi gravada: metadado do celular, senão número no nome, senão data do arquivo."""
    out = json.loads(run(["ffprobe", "-v", "error", "-show_entries",
                          "format_tags:stream_tags", "-of", "json", str(path)]))
    tags = dict(out.get("format", {}).get("tags", {}))
    for s in out.get("streams", []):
        for k, v in s.get("tags", {}).items():
            tags.setdefault(k, v)
    for k in ("com.apple.quicktime.creationdate", "creation_time"):
        if tags.get(k):
            return (0, tags[k], path.name)
    digitos = "".join(re.findall(r"\d+", path.stem))
    if len(digitos) >= 8:
        return (1, digitos, path.name)
    return (2, str(path.stat().st_mtime), path.name)


def classificar_por_ordem(pasta, ordem):
    """Ignora os nomes: ordena pela hora de gravação e distribui conforme --ordem.
    ordem = "5,2,2" (5 ganchos, 2 desenv, 2 CTAs) ou "GGGGGDDCC"."""
    if re.fullmatch(r"\d+,\d+,\d+", ordem):
        g, d, c = map(int, ordem.split(","))
        seq = "G" * g + "D" * d + "C" * c
    else:
        seq = ordem.upper().replace(",", "").replace(" ", "")
        if set(seq) - set("GDC"):
            sys.exit("--ordem deve ser tipo 5,2,2 ou GGGGGDDCC")
    arquivos = sorted((f for f in pasta.iterdir() if f.suffix.lower() in VIDEO_EXT),
                      key=data_gravacao)
    if len(arquivos) != len(seq):
        sys.exit(f"Achei {len(arquivos)} vídeos na pasta, mas --ordem pede {len(seq)}.")
    cenas = {"G": [], "D": [], "C": []}
    for f, t in zip(arquivos, seq):
        cenas[t].append(f)
    return cenas


def folha_conferencia(cenas, saida):
    """Imagem com o quadro do meio de cada cena + rótulo, para conferir antes de montar."""
    tmp = saida.parent / ".thumbs"
    tmp.mkdir(exist_ok=True)
    fonte = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    fonte = f"fontfile={fonte}:" if Path(fonte).exists() else ""
    i = 0
    for t in "GDC":
        for n, f in enumerate(cenas[t], 1):
            dur = duracao(f)
            rot = f"{t}{n}  {dur:.1f}s"
            nome = re.sub(r"[^A-Za-z0-9._-]", "_", f.name)[:28]
            vf = (f"scale=360:640:force_original_aspect_ratio=decrease,"
                  f"pad=360:640:(ow-iw)/2:(oh-ih)/2,"
                  f"drawtext={fonte}text='{rot}':fontsize=40:fontcolor=white:box=1:"
                  f"boxcolor=black@0.7:boxborderw=10:x=14:y=14,"
                  f"drawtext={fonte}text='{nome}':fontsize=16:fontcolor=white:box=1:"
                  f"boxcolor=black@0.7:boxborderw=6:x=14:y=h-34")
            run(["ffmpeg", "-y", "-v", "error", "-ss", f"{dur/2:.2f}", "-i", str(f),
                 "-frames:v", "1", "-vf", vf, str(tmp / f"{i:03d}.png")])
            i += 1
    cols = min(i, 5)
    linhas = -(-i // cols)
    run(["ffmpeg", "-y", "-v", "error", "-framerate", "1", "-i", str(tmp / "%03d.png"),
         "-vf", f"tile={cols}x{linhas}:padding=6:color=white", "-frames:v", "1", str(saida)])
    shutil.rmtree(tmp)


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


def trechos_com_fala(src, pausa_max=0.20, folga_ini=0.06, folga_fim=0.10):
    """Acha os trechos com som (fala) e devolve [(ini, fim), ...] em segundos,
    alinhados aos quadros do vídeo. Pausas maiores que pausa_max são cortadas.
    Devolve None se não der para separar fala de silêncio (ex.: só música)."""
    import numpy as np
    sr, passo = 16000, 0.02
    bruto = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-map", "0:a:0", "-ac", "1",
                            "-ar", str(sr), "-f", "s16le", "-"],
                           stdout=subprocess.PIPE, check=True).stdout
    amostras = np.frombuffer(bruto, dtype=np.int16).astype(np.float32) / 32768
    n = int(sr * passo)
    if len(amostras) < n * 10:
        return None
    blocos = amostras[: len(amostras) // n * n].reshape(-1, n)
    db = 20 * np.log10(np.sqrt((blocos ** 2).mean(axis=1)) + 1e-9)
    ruido, fala = np.percentile(db, 10), np.percentile(db, 95)
    if fala - ruido < 12:          # não tem diferença clara entre fala e silêncio
        return None
    ativo = db > ruido + 0.3 * (fala - ruido)

    ini_audio = float(run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                           "stream=start_time", "-of", "default=nw=1:nk=1", str(src)]).strip() or 0)
    trechos, i = [], 0
    while i < len(ativo):
        if ativo[i]:
            j = i
            while j < len(ativo) and ativo[j]:
                j += 1
            trechos.append([i * passo, j * passo])
            i = j
        else:
            i += 1
    # junta trechos separados por pausas curtas (entre palavras)
    juntos = []
    for a, b in trechos:
        if juntos and a - juntos[-1][1] <= pausa_max:
            juntos[-1][1] = b
        else:
            juntos.append([a, b])
    juntos = [t for t in juntos if t[1] - t[0] >= 0.08]   # descarta estalos
    if not juntos:
        return None
    total = len(ativo) * passo
    finais = []
    for a, b in juntos:
        a, b = max(0, a - folga_ini), min(total, b + folga_fim)
        a = int((a + ini_audio) * FPS) / FPS                 # alinha ao quadro
        b = -(-int(round((b + ini_audio) * FPS * 1000)) // 1000) / FPS
        if finais and a <= finais[-1][1]:
            finais[-1][1] = max(finais[-1][1], b)
        else:
            finais.append([a, b])
    return finais


def normalizar(src, dst, cortar_silencio=True):
    """Deixa toda cena em 1080x1920, 30fps, H.264 + AAC estéreo, para emendar sem pulos.
    Com cortar_silencio, remove respiros e pausas (cortes secos, estilo TikTok)."""
    base = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,format=yuv420p")
    audio = tem_audio(src)
    trechos = trechos_com_fala(src) if (audio and cortar_silencio) else None
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(src)]
    if not audio:
        cmd += ["-f", "lavfi", "-i", f"anullsrc=r={AR}:cl=stereo"]
    if trechos:
        antes, depois = duracao(src), sum(b - a for a, b in trechos)
        print(f"    cortes: {len(trechos)} trecho(s), {antes:.1f}s -> {depois:.1f}s")
        sel_v = "+".join(f"between(t,{a:.4f},{b - 0.001:.4f})" for a, b in trechos)
        sel_a = "+".join(f"between(t,{a:.4f},{b:.4f})" for a, b in trechos)
        filtro = (f"[0:v:0]fps={FPS},select='{sel_v}',setpts=N/{FPS}/TB,{base}[v];"
                  f"[0:a:0]aselect='{sel_a}',asetpts=N/SR/TB,aresample={AR},"
                  f"apad=whole_dur={depois:.4f}[a]")
        # áudio e vídeo com exatamente a mesma duração (evita dessincronizar ao emendar)
        cmd += ["-filter_complex", filtro, "-map", "[v]", "-map", "[a]", "-t", f"{depois:.4f}"]
    else:
        cmd += ["-map", "0:v:0", "-map", "0:a:0" if audio else "1:a:0",
                "-vf", f"fps={FPS},{base}", "-af", "aresample=async=1,apad",
                "-shortest", "-fflags", "+shortest", "-max_interleave_delta", "0"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18",
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
    ap.add_argument("--ordem", help="ignora os nomes e usa a ordem de gravação: "
                    "5,2,2 = 5 ganchos, 2 desenv, 2 CTAs (ou GGGGGDDCC)")
    ap.add_argument("--conferir", action="store_true",
                    help="só gera conferencia.png (quadro de cada cena com rótulo) e para")
    ap.add_argument("--sem-cortes", action="store_true",
                    help="não corta silêncios (use em vídeos sem narração)")
    ap.add_argument("--nao-cortar", default="",
                    help="cenas que não devem ter silêncio cortado, ex.: D1,G3")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg não encontrado.")
    pasta = Path(args.pasta)
    cenas = classificar_por_ordem(pasta, args.ordem) if args.ordem else classificar(pasta)
    nG, nD, nC = (len(cenas[t]) for t in "GDC")
    print(f"Cenas: {nG} ganchos, {nD} desenvolvimentos, {nC} CTAs -> {nG*nD*nC} combinações")
    for t, rot in (("G", "gancho"), ("D", "desenv"), ("C", "cta")):
        for n, f in enumerate(cenas[t], 1):
            print(f"  {rot}{n}: {f.name}")
    if 0 in (nG, nD, nC):
        sys.exit("Falta pelo menos 1 cena de cada tipo.")
    if args.conferir:
        folha_conferencia(cenas, pasta / "conferencia.png")
        print(f"Conferência salva em {pasta / 'conferencia.png'}")
        return

    tmp = pasta / ".normalizadas"
    tmp.mkdir(exist_ok=True)
    norm = {}
    for t in "GDC":
        for i, f in enumerate(cenas[t]):
            rot = f"{t}{i+1}"
            cortar = not args.sem_cortes and rot not in args.nao_cortar.upper().split(",")
            dst = tmp / f"{rot}_{'cortado' if cortar else 'inteiro'}.mp4"
            if not dst.exists() or dst.stat().st_mtime < f.stat().st_mtime:
                print(f"  preparando {rot} ({f.name})...")
                normalizar(f, dst, cortar)
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
