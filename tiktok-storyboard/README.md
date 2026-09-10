# Storyboard TikTok Shop

Você joga um vídeo que já está vendendo e recebe de volta o **storyboard
completo**: o vídeo cortado em blocos de no máximo 8 segundos e, em cada bloco,
o prompt da imagem de referência, o prompt do Flow, a fala, a legenda e o som.

Existe porque o Flow gera 8s por vez. Um vídeo de 40s são 6 gerações que
precisam parecer a mesma cena — e o trabalho chato é justamente descobrir onde
cortar e qual imagem de referência usar em cada pedaço.

## O que ele resolve

| Antes | Agora |
|---|---|
| Assistir o vídeo várias vezes contando os cortes | `extrator.py` acha os cortes sozinho |
| Dar print e torcer pra ser o frame certo | Frame de referência extraído no ponto exato de cada bloco |
| Escrever prompt do zero, cena por cena | Prompt pronto, já com a fala e o som |
| Cada bloco sai com uma mão e uma mesa diferente | Bíblia visual repetida em todos os prompts |
| Anotar tudo num caderno | `storyboard.html` com botão de copiar em cada prompt |

## Instalação

Precisa de Python 3.9+.

```bash
pip install -r requirements.txt
```

Só isso — o ffmpeg vem junto no pacote `imageio-ffmpeg`, não precisa instalar
nada separado.

## Uso

### Caminho curto (com chave de API)

```bash
export ANTHROPIC_API_KEY=sk-ant-...        # Windows: setx ANTHROPIC_API_KEY sk-ant-...
python3 tudo.py video_de_referencia.mp4
```

Sai um `video_de_referencia_dossie/storyboard.html`. Abre no navegador e cada
prompt tem botão de copiar.

### Caminho sem chave de API

```bash
python3 extrator.py video_de_referencia.mp4
```

Isso gera a pasta `video_de_referencia_dossie/`. Abra um chat com o Claude e
mande:

1. o conteúdo de `briefing.md`;
2. o `mosaico.jpg`;
3. as imagens da pasta `tiras/`.

O Claude devolve o JSON. Salve como `storyboard.json` dentro da pasta e rode:

```bash
python3 montador.py video_de_referencia_dossie/
```

## O que sai na pasta

```
video_dossie/
├── storyboard.html   <- o que você vai usar no dia a dia
├── mosaico.jpg       <- mapa: todas as cenas numeradas lado a lado
├── tiras/            <- início / meio / fim de cada bloco (mostra o movimento)
├── frames/           <- os frames soltos; o "_ref" é a imagem de referência
├── dossie.json       <- tempos, cortes e transcrição
├── briefing.md       <- texto pronto pra colar no chat
└── storyboard.json   <- os prompts
```

## Como usar no Flow

1. Cole a **bíblia visual** primeiro — ela vai dentro de todo prompt. É o que
   segura a mesma mão, a mesma mesa e a mesma luz do começo ao fim.
2. Cena marcada como **nova**: gere a imagem com o `prompt_imagem`, depois use
   ela em *Frames to Video* com o `prompt_video`.
3. Cena marcada como **encadeada**: não gere imagem nova. Exporte o **último
   frame** da cena anterior e use como imagem inicial. É isso que faz o corte
   ficar invisível.
4. Junte tudo na edição, na ordem dos números.

## Ajustes do extrator

```bash
python3 extrator.py video.mp4 --limiar 0.18   # acha mais cortes (vídeo de corte suave)
python3 extrator.py video.mp4 --limiar 0.40   # acha menos (vídeo muito agitado)
python3 extrator.py video.mp4 --fixo          # ignora cortes, fatia de 8 em 8s
python3 extrator.py video.mp4 --max 6         # blocos de até 6s
python3 extrator.py video.mp4 --modelo medium # transcrição mais precisa (mais lenta)
python3 extrator.py video.mp4 --sem-audio     # pula a transcrição
```

Se o resultado vier com blocos demais, suba o `--limiar`. Se vier com blocos de
menos, desça. Vídeo de plano contínuo, sem corte nenhum: use `--fixo`.

## Detalhes que importam

- **A fala tem que caber no tempo.** Português falado roda a ~2,2 palavras por
  segundo. O storyboard conta as palavras de cada cena e marca em vermelho
  quando a fala não cabe no bloco.
- **Legenda queimada.** Todo prompt de vídeo leva `no subtitles, no captions` no
  final, porque o Veo adora queimar legenda quando ouve uma fala — e você quer
  legendar na edição, do seu jeito.
- **Sem rosto.** Os prompts são POV de primeira pessoa: só mãos, antebraço e
  produto.
- **Modele a estrutura, não o roteiro.** O storyboard traz *por que aquele vídeo
  funciona* justamente pra você copiar a lógica, não as palavras. Não reproduza
  marca, embalagem ou slogan do vídeo original.

## Limites conhecidos

- A detecção de corte erra em transição suave (fade, crossfade) e em vídeo de
  plano contínuo. Nesses casos, `--fixo` resolve.
- A transcrição depende do áudio estar limpo. Música alta por cima da voz
  atrapalha; quando isso acontece, a fala é lida das legendas na tela.
- Vídeo sem áudio nenhum funciona normal — a análise sai das imagens.
