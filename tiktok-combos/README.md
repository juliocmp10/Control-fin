# Montador de combinações (TikTok Shop)

Você grava as cenas uma vez (ganchos, desenvolvimentos e CTAs) e o script monta
**todas** as combinações `gancho → desenvolvimento → CTA` como vídeos prontos para postar.

3 ganchos × 3 desenvolvimentos × 3 CTAs = **27 vídeos**.

## Como os vídeos são organizados

Os 27 saem em **9 lotes de 3**. Em cada lote, cada gancho, cada desenvolvimento e
cada CTA aparece **uma vez só**. Nenhuma cena se repete dentro de um lote:

| Lote | Vídeo 1    | Vídeo 2    | Vídeo 3    |
|------|------------|------------|------------|
| 01   | G1-D2-C1   | G2-D3-C2   | G3-D1-C3   |
| 02   | G1-D3-C1   | G2-D1-C2   | G3-D2-C3   |
| ...  | ...        | ...        | ...        |

Também é gerado `prontos/plano_postagem.csv` com colunas para anotar quando postou,
quantas views teve e quantas vendas fez. Com isso dá para ver qual **gancho** está
puxando mais views e qual **CTA** está convertendo mais.

## Como gravar as cenas

- Grave na vertical, em **1080p** (4K deixa os arquivos enormes sem ganho no TikTok).
- Cada cena deve funcionar sozinha: comece e termine com o produto parado na mão,
  sem frase cortada. Assim qualquer gancho emenda em qualquer desenvolvimento.
- Mantenha a mesma luz, o mesmo fundo e a mesma mão/roupa nas 9 cenas, para a emenda
  não ficar estranha.
- Duração sugerida: gancho de 2 a 4 s, desenvolvimento de 8 a 20 s, CTA de 3 a 6 s.

## Nomes dos arquivos

Coloque as cenas de um produto em uma pasta, por exemplo `cenas/fone-bluetooth/`:

```
gancho1.mp4  gancho2.mp4  gancho3.mp4
desenv1.mp4  desenv2.mp4  desenv3.mp4
cta1.mp4     cta2.mp4     cta3.mp4
```

`g1 / d1 / c1` também funcionam. Pode ter 2, 4 ou 5 de cada: o script calcula as
combinações sozinho.

### Corte de silêncio (automático)

Antes de montar, cada cena tem os respiros e as pausas cortados (cortes secos, estilo
TikTok), inclusive a sobra do começo e do fim. Pausas curtas entre palavras ficam.
O corte é feito uma vez por cena e vale para todas as combinações.

- `--sem-cortes`: desliga (vídeos sem narração, só música).
- `--nao-cortar D1,G3`: não corta só essas cenas (ex.: demonstração feita em silêncio).

### Sem renomear (vídeos direto do celular)

Grave sempre na mesma ordem (por exemplo: os 5 ganchos, depois os 2 desenvolvimentos,
depois os 2 CTAs) e use `--ordem`. O script ignora os nomes e ordena pela **hora de
gravação** que o celular salva dentro do vídeo:

```bash
# confere primeiro: gera conferencia.png com um quadro de cada cena e o rótulo G1, D1, C1...
python3 montar.py cenas/fone-bluetooth --ordem 5,2,2 --conferir

# se estiver certo, monta
python3 montar.py cenas/fone-bluetooth --ordem 5,2,2
```

`--ordem` também aceita a sequência por extenso, por exemplo `GGGGGDDCC`.

## Rodar

```bash
# narração original
python3 montar.py cenas/fone-bluetooth

# narração + música baixinha por baixo
python3 montar.py cenas/fone-bluetooth --musica musicas/trilha.mp3

# sem narração: troca o áudio pela música
python3 montar.py cenas/fone-bluetooth --musica musicas/trilha.mp3 --so-musica

# micro-variação em cada vídeo (zoom de 1-4%, brilho, contraste e cor)
python3 montar.py cenas/fone-bluetooth --variar

# só alguns lotes
python3 montar.py cenas/fone-bluetooth --lotes 1,2,3
```

Requer `ffmpeg` e Python 3. Os vídeos prontos ficam em `cenas/<produto>/prontos/`
e não entram no git.

## Texto na tela

Crie `textos.txt` dentro da pasta das cenas, uma linha por cena:

```
G1: O item que nunca sai da minha mochila
G2: Ela pesa 1 kg... e esse é o ponto
D1: 50.000 mAh | Display digital | 2 cabos embutidos
C1: Black Friday + frete grátis
```

O texto entra no terço de cima do vídeo (fora dos botões e da legenda do TikTok),
branco com contorno preto. `|` força a quebra de linha. Emojis não são suportados.
