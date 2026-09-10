#!/usr/bin/env python3
"""
Montador - junta o dossie (frames) com o storyboard (prompts) e gera uma
pagina HTML unica, com as imagens embutidas e botao de copiar em cada prompt.

Uso:
    python3 montador.py saida/ -o storyboard.html
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import sys
from pathlib import Path

CORES = {
    "gancho": "#F43F5E", "problema": "#F59E0B", "solucao": "#38BDF8",
    "demonstracao": "#38BDF8", "demo": "#38BDF8", "prova": "#A78BFA",
    "beneficio": "#34D399", "cta": "#22C55E",
}


def embute(caminho: Path) -> str:
    if not caminho.exists():
        return ""
    return "data:image/jpeg;base64," + base64.b64encode(caminho.read_bytes()).decode()


def esc(txt) -> str:
    return html.escape(str(txt or ""))


def campo_copiavel(rotulo: str, texto: str, destaque: bool = False) -> str:
    if not texto:
        return ""
    classe = "bloco destaque" if destaque else "bloco"
    return f"""
      <div class="{classe}">
        <div class="rotulo">{esc(rotulo)}
          <button class="copiar" type="button">copiar</button>
        </div>
        <div class="texto">{esc(texto)}</div>
      </div>"""


def monta(pasta: Path, storyboard: dict, dossie: dict) -> str:
    resumo = storyboard.get("resumo", {})
    biblia = storyboard.get("biblia_visual", {})
    cenas = storyboard.get("cenas", [])
    por_n = {b["n"]: b for b in dossie.get("blocos", [])}

    cartoes = []
    for cena in cenas:
        n = cena.get("n", 0)
        bloco = por_n.get(n, {})
        frames = bloco.get("frames", {})
        img_ref = embute(pasta / frames.get("ref", "")) if frames.get("ref") else ""
        img_fim = embute(pasta / frames.get("fim", "")) if frames.get("fim") else ""

        funcao = str(cena.get("funcao", "")).lower()
        cor = CORES.get(funcao, "#64748B")
        encadeada = str(cena.get("origem", "")).startswith("encade")

        origem_html = (
            '<div class="origem encadeada">continua da cena anterior &mdash; '
            'use o <b>ultimo frame</b> dela como imagem de referencia</div>'
            if encadeada else
            '<div class="origem nova">cena nova &mdash; gere a imagem de referencia abaixo</div>'
        )

        fala = cena.get("fala", "")
        palavras = len(str(fala).split()) if fala else 0
        limite = round(float(cena.get("duracao", 8)) * 2.2)
        aperta = palavras > limite
        medidor = ""
        if fala:
            aviso = " estourou" if aperta else ""
            medidor = (f'<span class="medidor{aviso}">{palavras} palavras '
                       f'/ cabem ~{limite} em {cena.get("duracao", 0):.1f}s</span>')

        miniatura_fim = (
            f'<div class="fim"><img src="{img_fim}" alt="ultimo frame"><span>ultimo frame '
            f'&rarr; referencia da cena {n + 1}</span></div>' if img_fim else "")

        cartoes.append(f"""
    <section class="cena">
      <div class="visual">
        {'<img class="ref" src="' + img_ref + '" alt="frame de referencia">' if img_ref else '<div class="ref vazio">sem frame</div>'}
        {miniatura_fim}
      </div>
      <div class="conteudo">
        <div class="cabeca">
          <span class="numero">#{n:02d}</span>
          <span class="etiqueta" style="background:{cor}1f;color:{cor};border-color:{cor}55">{esc(cena.get('funcao',''))}</span>
          <span class="tempo">{float(cena.get('inicio',0)):.1f}s &rarr; {float(cena.get('fim',0)):.1f}s
            <b>({float(cena.get('duracao',0)):.1f}s)</b></span>
        </div>
        {origem_html}
        <p class="descricao">{esc(cena.get('descricao',''))}</p>
        {campo_copiavel('Prompt da imagem de referencia', cena.get('prompt_imagem',''))}
        {campo_copiavel('Prompt do video (Flow)', cena.get('prompt_video',''), destaque=True)}
        {campo_copiavel('Fala', fala)}
        {medidor}
        {campo_copiavel('Legenda na tela', cena.get('legenda',''))}
        {'<div class="miudo"><b>Som:</b> ' + esc(cena.get('som','')) + '</div>' if cena.get('som') else ''}
        {'<div class="miudo nota"><b>Nota:</b> ' + esc(cena.get('nota','')) + '</div>' if cena.get('nota') else ''}
      </div>
    </section>""")

    def lista(itens, classe=""):
        if not itens:
            return ""
        return f'<ul class="{classe}">' + "".join(f"<li>{esc(i)}</li>" for i in itens) + "</ul>"

    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Storyboard &mdash; {esc(dossie.get('video','video'))}</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#0F1117; color:#F1F5F9; font:15px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
         padding:24px 16px 64px; }}
  .capa {{ max-width:1100px; margin:0 auto 28px; }}
  h1 {{ font-size:26px; font-weight:800; letter-spacing:-.02em; }}
  .sub {{ color:#94A3B8; margin-top:6px; font-size:14px; }}
  .fichas {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:18px; }}
  .ficha {{ background:#171A24; border:1px solid #262B3B; border-radius:10px; padding:10px 14px; }}
  .ficha span {{ display:block; font-size:11px; text-transform:uppercase; letter-spacing:.08em; color:#64748B; }}
  .ficha b {{ font-size:15px; font-weight:600; }}
  .painel {{ max-width:1100px; margin:0 auto 28px; background:#171A24; border:1px solid #262B3B;
             border-radius:14px; padding:18px 20px; }}
  .painel h2 {{ font-size:13px; text-transform:uppercase; letter-spacing:.09em; color:#94A3B8; margin-bottom:12px; }}
  .painel ul {{ margin-left:18px; color:#CBD5E1; }}
  .painel li {{ margin:3px 0; }}
  .cena {{ max-width:1100px; margin:0 auto 20px; display:grid; grid-template-columns:260px 1fr; gap:20px;
           background:#171A24; border:1px solid #262B3B; border-radius:14px; padding:18px; }}
  .visual .ref {{ width:100%; border-radius:10px; display:block; border:1px solid #2D3148; }}
  .visual .vazio {{ aspect-ratio:9/16; display:grid; place-items:center; color:#475569; background:#0F1117; border-radius:10px; }}
  .fim {{ margin-top:10px; }}
  .fim img {{ width:76px; border-radius:6px; border:1px solid #2D3148; display:block; }}
  .fim span {{ display:block; font-size:11px; color:#64748B; margin-top:4px; }}
  .cabeca {{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:10px; }}
  .numero {{ font-size:20px; font-weight:800; }}
  .etiqueta {{ font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.07em;
               padding:3px 9px; border-radius:99px; border:1px solid; }}
  .tempo {{ font-size:12px; color:#64748B; margin-left:auto; }}
  .origem {{ font-size:12px; padding:7px 11px; border-radius:8px; margin-bottom:12px; }}
  .origem.nova {{ background:#1E293B; color:#94A3B8; }}
  .origem.encadeada {{ background:#3B2F1560; color:#FCD34D; border:1px solid #78551f; }}
  .descricao {{ color:#CBD5E1; margin-bottom:14px; }}
  .bloco {{ background:#0F1117; border:1px solid #262B3B; border-radius:10px; padding:11px 13px; margin-bottom:10px; }}
  .bloco.destaque {{ border-color:#38BDF8; box-shadow:0 0 0 1px #38bdf82e; }}
  .rotulo {{ display:flex; align-items:center; font-size:11px; text-transform:uppercase; letter-spacing:.08em;
             color:#64748B; margin-bottom:7px; }}
  .copiar {{ margin-left:auto; background:#262B3B; color:#CBD5E1; border:0; border-radius:6px;
             padding:4px 10px; font-size:11px; cursor:pointer; font-family:inherit; }}
  .copiar:hover {{ background:#38BDF8; color:#0F1117; }}
  .copiar.feito {{ background:#22C55E; color:#0F1117; }}
  .texto {{ font-family:ui-monospace,'SF Mono',Menlo,Consolas,monospace; font-size:12.5px; line-height:1.65;
            color:#E2E8F0; white-space:pre-wrap; word-break:break-word; }}
  .medidor {{ display:inline-block; font-size:11px; color:#64748B; margin:-4px 0 10px 2px; }}
  .medidor.estourou {{ color:#F43F5E; font-weight:600; }}
  .miudo {{ font-size:12.5px; color:#94A3B8; margin-top:6px; }}
  .miudo b {{ color:#CBD5E1; }}
  .nota {{ border-left:2px solid #38BDF8; padding-left:9px; }}
  @media (max-width:760px) {{
    .cena {{ grid-template-columns:1fr; }}
    .visual .ref {{ max-width:190px; }}
    .tempo {{ margin-left:0; width:100%; }}
  }}
  @media print {{
    body {{ background:#fff; color:#000; }}
    .cena,.painel,.ficha {{ background:#fff; border-color:#ccc; break-inside:avoid; }}
    .copiar {{ display:none; }}
    .texto,.descricao,.miudo {{ color:#222; }}
  }}
</style></head><body>
  <header class="capa">
    <h1>Storyboard &mdash; {esc(resumo.get('produto','video de referencia'))}</h1>
    <div class="sub">Origem: {esc(dossie.get('video',''))} &middot; {len(cenas)} cenas &middot;
      todas com no maximo 8s, prontas pro Flow</div>
    <div class="fichas">
      <div class="ficha"><span>Duracao</span><b>{float(dossie.get('duracao',0)):.1f}s</b></div>
      <div class="ficha"><span>Cenas</span><b>{len(cenas)}</b></div>
      <div class="ficha"><span>Publico</span><b>{esc(resumo.get('publico','-'))}</b></div>
      <div class="ficha"><span>Estrutura</span><b>{esc(resumo.get('estrutura','-'))}</b></div>
    </div>
  </header>

  <div class="painel">
    <h2>Biblia visual &mdash; cole isto em todo prompt</h2>
    {campo_copiavel('Trecho fixo', biblia.get('trecho_fixo',''), destaque=True)}
    <div class="miudo"><b>Maos:</b> {esc(biblia.get('maos','-'))}</div>
    <div class="miudo"><b>Ambiente:</b> {esc(biblia.get('ambiente','-'))}</div>
    <div class="miudo"><b>Luz:</b> {esc(biblia.get('luz','-'))}</div>
    <div class="miudo"><b>Camera:</b> {esc(biblia.get('camera','-'))}</div>
  </div>

  {'<div class="painel"><h2>Por que esse video funciona</h2>' + lista(resumo.get('por_que_funciona')) + '</div>' if resumo.get('por_que_funciona') else ''}
  {'<div class="painel"><h2>O que nao repetir</h2>' + lista(resumo.get('erros_a_nao_repetir')) + '</div>' if resumo.get('erros_a_nao_repetir') else ''}

  {''.join(cartoes)}

  <div class="painel">
    <h2>Fechamento</h2>
    <div class="miudo"><b>CTA:</b> {esc(storyboard.get('cta_final','-'))}</div>
    <div class="miudo"><b>Trilha:</b> {esc(storyboard.get('trilha','-'))}</div>
    {'<h2 style="margin-top:14px">Edicao</h2>' + lista(storyboard.get('edicao')) if storyboard.get('edicao') else ''}
  </div>

<script>
document.addEventListener('click', function (ev) {{
  var botao = ev.target.closest('.copiar');
  if (!botao) return;
  var texto = botao.closest('.bloco').querySelector('.texto').innerText;
  var pronto = function () {{
    botao.textContent = 'copiado!';
    botao.classList.add('feito');
    setTimeout(function () {{ botao.textContent = 'copiar'; botao.classList.remove('feito'); }}, 1400);
  }};
  if (navigator.clipboard && window.isSecureContext) {{
    navigator.clipboard.writeText(texto).then(pronto);
  }} else {{
    var area = document.createElement('textarea');
    area.value = texto; area.style.position = 'fixed'; area.style.opacity = '0';
    document.body.appendChild(area); area.select();
    try {{ document.execCommand('copy'); pronto(); }} finally {{ area.remove(); }}
  }}
}});
</script>
</body></html>"""


def principal() -> None:
    p = argparse.ArgumentParser(description="Gera o storyboard HTML a partir do dossie + prompts.")
    p.add_argument("pasta", help="pasta do dossie (a que tem dossie.json)")
    p.add_argument("-s", "--storyboard", default=None, help="storyboard.json (padrao: <pasta>/storyboard.json)")
    p.add_argument("-o", "--saida", default=None, help="html de saida (padrao: <pasta>/storyboard.html)")
    args = p.parse_args()

    pasta = Path(args.pasta).expanduser().resolve()
    arq_dossie = pasta / "dossie.json"
    arq_sb = Path(args.storyboard).expanduser() if args.storyboard else pasta / "storyboard.json"

    for arq, dica in ((arq_dossie, "rode o extrator.py primeiro"),
                      (arq_sb, "rode o analisador.py ou salve o JSON da analise aqui")):
        if not arq.exists():
            sys.exit(f"Nao encontrei {arq}\n  -> {dica}")

    dossie = json.loads(arq_dossie.read_text(encoding="utf-8"))
    storyboard = json.loads(arq_sb.read_text(encoding="utf-8"))
    if not storyboard.get("cenas"):
        sys.exit("O storyboard nao tem nenhuma cena. Confira o JSON.")

    destino = Path(args.saida).expanduser().resolve() if args.saida else pasta / "storyboard.html"
    destino.write_text(monta(pasta, storyboard, dossie), encoding="utf-8")
    tam = destino.stat().st_size / 1024
    print(f"== {destino}  ({len(storyboard['cenas'])} cenas, {tam:.0f} KB)")
    print("   abra no navegador; cada prompt tem botao de copiar.")


if __name__ == "__main__":
    principal()
