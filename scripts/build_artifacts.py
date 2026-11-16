"""Gera graficos, relatorio PDF e apresentacao a partir dos CSVs medidos."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "output" / "figures"
PDF = ROOT / "output" / "pdf"
PRES = ROOT / "output" / "presentation"
SUMMARY = list(csv.DictReader((ROOT / "data" / "results" / "summary.csv").open(encoding="utf-8")))
DATA = {(r["instance"], r["language"], r["algorithm"]): r for r in SUMMARY}
MEMORY_SUMMARY = list(csv.DictReader((ROOT / "data" / "results" / "memory_summary.csv").open(encoding="utf-8")))
MEMORY = {(r["n"], r["language"], r["algorithm"]): r for r in MEMORY_SUMMARY}
GEOMETRIC_SUMMARY = list(csv.DictReader((ROOT / "data" / "results" / "geometric_summary.csv").open(encoding="utf-8")))
GEOMETRIC = {(r["n"], r["language"], r["algorithm"]): r for r in GEOMETRIC_SUMMARY}
LIMIT = json.loads((ROOT / "data" / "results" / "limit_60s.json").read_text(encoding="utf-8"))
SIZES = (4, 5, 6, 7, 8, 9)
MEMORY_SIZES = (6, 12, 24, 48, 96, 192)
PAPER_URL = "https://jair.org/index.php/jair/article/view/11079"
REPO_URL = "https://github.com/Gustavotorrescastro/teoria-computacao-n-rainhas"


def number(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def ms(instance: str, language: str, algorithm: str) -> float:
    return float(DATA[(instance, language, algorithm)]["mean_ms"])


def partial_mean(n: int, language: str, algorithm: str) -> float:
    names = [f"partial_n{n}"] + [f"partial_n{n}_{i}" for i in range(2, 6)]
    return sum(ms(name, language, algorithm) for name in names) / len(names)


def plot_all() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    palette = {("Python", "brute"): "#bb3e03", ("Python", "backtracking"): "#005f73",
               ("C++", "brute"): "#e9a100", ("C++", "backtracking"): "#0a9396"}
    labels = {("Python", "brute"): "Força bruta / Python", ("Python", "backtracking"): "Backtracking / Python",
              ("C++", "brute"): "Força bruta / C++", ("C++", "backtracking"): "Backtracking / C++"}
    fig, ax = plt.subplots(figsize=(8.7, 4.7), layout="constrained")
    for key, color in palette.items():
        lang, alg = key
        values = [ms(f"empty_n{n}", lang, alg) for n in SIZES]
        ax.plot(SIZES, values, marker="o", color=color, label=labels[key], linewidth=2)
    ax.set(xlabel="Tamanho n do tabuleiro", ylabel="Tempo médio (ms)", title="Tempo de execução - tabuleiro vazio")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(SIZES, [str(n) for n in SIZES])
    ax.grid(True, which="both", alpha=.23)
    ax.legend(fontsize=8, ncol=2)
    fig.savefig(FIG / "tempos_loglog.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.7, 4.2), layout="constrained")
    for language, color in (("Python", "#bb3e03"), ("C++", "#005f73")):
        ratio = [ms(f"empty_n{n}", language, "brute") / (math.factorial(n) * n) for n in SIZES]
        ax.plot(SIZES, ratio, marker="o", linewidth=2, color=color, label=language)
    ax.set(xlabel="Tamanho n", ylabel="T(n) / (n! . n), em ms", title="Razão empírica da força bruta")
    ax.set_xticks(SIZES)
    ax.grid(alpha=.23)
    ax.legend()
    fig.savefig(FIG / "razao_teorica.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.7, 4.2), layout="constrained")
    leaves = [int(DATA[(f"empty_n{n}", "Python", "brute")]["operations"]) for n in SIZES]
    attempts = [int(DATA[(f"empty_n{n}", "Python", "backtracking")]["operations"]) for n in SIZES]
    ax.plot(SIZES, leaves, marker="o", linewidth=2, color="#bb3e03", label="Permutações completas (n!)")
    ax.plot(SIZES, attempts, marker="o", linewidth=2, color="#005f73", label="Tentativas de posição no backtracking")
    ax.set(xlabel="Tamanho n", ylabel="Contagem de operações", title="Espaço de busca observado")
    ax.set_yscale("log")
    ax.set_xticks(SIZES)
    ax.grid(True, which="both", alpha=.23)
    ax.legend()
    fig.savefig(FIG / "operacoes.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.7, 4.2), layout="constrained")
    types = ("empty_n9", "partial", "complete_n9")
    names = ("Vazio", "5 parciais (média)", "Completo")
    x = list(range(3))
    width = .19
    for j, key in enumerate(palette):
        lang, alg = key
        ax.bar([v + (j - 1.5) * width for v in x],
               [partial_mean(9, lang, alg) if t == "partial" else ms(t, lang, alg) for t in types],
               width, color=palette[key], label=labels[key])
    ax.set(xlabel="Tipo de entrada (n=9)", ylabel="Tempo médio (ms)", title="Efeito de rainhas já posicionadas")
    ax.set_xticks(x, names)
    ax.set_yscale("log")
    ax.grid(axis="y", which="both", alpha=.23)
    ax.legend(fontsize=8, ncol=2)
    fig.savefig(FIG / "casos_n9.png", dpi=200)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(8.7, 4.0), layout="constrained", sharey=False)
    for ax, language in zip(axes, ("Python", "C++")):
        for algorithm, color, label in (("brute", "#bb3e03", "Força bruta"),
                                        ("backtracking", "#005f73", "Backtracking")):
            peaks = [float(MEMORY[(str(n), language, algorithm)]["mean_peak_bytes"]) / 1024
                     for n in MEMORY_SIZES]
            ax.plot(MEMORY_SIZES, peaks, marker="o", linewidth=2, color=color, label=label)
        ax.set(xlabel="Tamanho n", title=language)
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_xticks(MEMORY_SIZES, [str(n) for n in MEMORY_SIZES])
        ax.grid(True, which="both", alpha=.23)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("Pico de alocações dinâmicas (KiB)")
    fig.suptitle("Memória auxiliar medida - seis linhas livres", fontsize=12)
    fig.savefig(FIG / "memoria_alocacoes.png", dpi=200)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(8.7, 3.7), layout="constrained")
    for ax, language in zip(axes, ("Python", "C++")):
        for algorithm, color, label in (("brute", "#bb3e03", "Força bruta"),
                                        ("backtracking", "#005f73", "Backtracking")):
            measured = [float(GEOMETRIC[(str(n), language, algorithm)]["mean_ms"])
                        for n in MEMORY_SIZES]
            ax.plot(MEMORY_SIZES, measured, marker="o", linewidth=2, color=color, label=label)
        ax.set(xlabel="Tamanho n (seis linhas livres)", title=language)
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_xticks(MEMORY_SIZES, [str(n) for n in MEMORY_SIZES])
        ax.grid(True, which="both", alpha=.23)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("Tempo médio (ms)")
    fig.suptitle("Tempo em seis tamanhos geométricos", fontsize=12)
    fig.savefig(FIG / "tempos_geometricos.png", dpi=200)
    plt.close(fig)


def setup_fonts() -> None:
    fonts = Path("C:/Windows/Fonts")
    pdfmetrics.registerFont(TTFont("Arial", str(fonts / "arial.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-Bold", str(fonts / "arialbd.ttf")))
    pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold")


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleCustom", fontName="Arial-Bold", fontSize=19, leading=24,
                          textColor=colors.HexColor("#123945"), spaceAfter=14))
styles.add(ParagraphStyle(name="HeadingCustom", fontName="Arial-Bold", fontSize=13, leading=17,
                          textColor=colors.HexColor("#0b6575"), spaceBefore=14, spaceAfter=8))
styles.add(ParagraphStyle(name="SubCustom", fontName="Arial-Bold", fontSize=10, leading=14,
                          textColor=colors.HexColor("#123945"), spaceBefore=9, spaceAfter=4))
styles.add(ParagraphStyle(name="BodyCustom", fontName="Arial", fontSize=9.2, leading=13.7,
                          spaceAfter=6, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="SmallCustom", fontName="Arial", fontSize=8, leading=11,
                          spaceAfter=4, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="CaptionCustom", fontName="Arial", fontSize=8, leading=11,
                          textColor=colors.HexColor("#4f5b60"), spaceAfter=8, alignment=TA_CENTER))


def p(text: str, style: str = "BodyCustom") -> Paragraph:
    return Paragraph(text, styles[style])


def heading(text: str) -> Paragraph:
    return p(text, "HeadingCustom")


def sub(text: str) -> Paragraph:
    return p(text, "SubCustom")


def figure(name: str, caption: str, width: float = 16.6 * cm) -> list:
    from PIL import Image as PILImage
    path = FIG / name
    with PILImage.open(path) as im:
        aspect = im.height / im.width
    return [Image(str(path), width=width, height=width * aspect), p(caption, "CaptionCustom")]


def table(data: list[list[str]], widths: list[float] | None = None) -> Table:
    tab = Table([[p(str(cell), "SmallCustom") for cell in row] for row in data], colWidths=widths,
                repeatRows=1, hAlign="LEFT")
    tab.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dcebef")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f8f8")]),
        ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#cbd8db")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tab


def footer(canv: canvas.Canvas, doc: BaseDocTemplate) -> None:
    canv.saveState()
    canv.setFont("Arial", 8)
    canv.setFillColor(colors.HexColor("#617077"))
    canv.drawString(2 * cm, 1.3 * cm, "Teoria da Computação | N-rainhas")
    canv.drawRightString(A4[0] - 2 * cm, 1.3 * cm, str(doc.page))
    canv.restoreState()


def make_report() -> None:
    PDF.mkdir(parents=True, exist_ok=True)
    path = PDF / "relatorio_n_rainhas.pdf"
    doc = BaseDocTemplate(str(path), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                          topMargin=1.75 * cm, bottomMargin=1.75 * cm)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, leftPadding=0,
                  rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id="report", frames=frame, onPage=footer))
    story: list = []
    story += [p("N-rainhas: força bruta e backtracking em Python e C++", "TitleCustom"),
              p("<b>Disciplina:</b> Teoria da Computação | <b>Professor:</b> Daniel Bezerra | <b>Data:</b> 16/11/2026"),
              p("<b>Equipe:</b> Bruno Augusto; Gustavo Torres Castro; Diego Magnata; Pablo Coelho."),
              p("<b>Resumo.</b> Implementamos quatro programas para contar todas as soluções de N-rainhas, usando o mesmo conjunto de entradas em Python e C++. Em tabuleiro vazio de n=9, a força bruta levou "
                + number(ms("empty_n9", "Python", "brute")) + " ms em Python e " + number(ms("empty_n9", "C++", "brute"))
                + " ms em C++; o backtracking levou " + number(ms("empty_n9", "Python", "backtracking")) + " ms e "
                + number(ms("empty_n9", "C++", "backtracking")) + " ms, respectivamente. São 15 medições por combinação e entradas idênticas, com semente fixa."),
              heading("1. Descrição do problema e dos algoritmos"),
              p("O tabuleiro n x n recebe uma rainha por linha e por coluna; duas rainhas não podem compartilhar diagonal. Uma entrada contém n e zero ou mais rainhas já posicionadas. A saída é o número de maneiras de completar o tabuleiro. A instância vazia é o N-rainhas clássico; instâncias parciais também permitem discutir a versão de completamento."),
              sub("Algoritmo A - força bruta por permutações"),
              p("Após validar as rainhas fixas, o algoritmo distribui as colunas livres entre as linhas livres, gerando todas as m! permutações, onde m é o número de linhas livres. Somente na folha verifica todas as n diagonais, sem encerrar a varredura ao encontrar conflito, e soma uma solução se nenhuma colisão existir. Não há poda de diagonais durante a geração."),
              sub("Algoritmo B - backtracking com poda"),
              p("O algoritmo visita as linhas em ordem. Para cada coluna candidata, consulta três estruturas booleanas: colunas ocupadas, diagonais de diferença linha-coluna e diagonais de soma linha+coluna. Um conflito interrompe imediatamente o ramo. Uma configuração completa acrescenta uma solução; o retorno desfaz as marcações. As rainhas fixas restringem a única escolha da sua linha."),
              p("<b>Pseudocódigo A:</b> para cada permutação das colunas livres, formar tabuleiro; percorrer as n linhas checando diagonais; se válido, incrementar contador."),
              p("<b>Pseudocódigo B:</b> busca(linha): se linha=n, incrementar contador; senão, para cada coluna permitida na linha, se coluna e diagonais estiverem livres, marcar, chamar busca(linha+1), desmarcar."),
              heading("2. Classificação assintótica"),
              p("Na força bruta, cada uma das m! permutações custa Θ(n) para verificar diagonais. A geração também é limitada por O(m! m); como m≤n, o custo total em instâncias válidas é <b>Θ(n·m!)</b>, além da leitura/validação Θ(n). Para o tabuleiro vazio, m=n: <b>O(n·n!), Ω(n·n!) e Θ(n·n!)</b>. A memória auxiliar, incluindo a pilha recursiva, é O(n)."),
              p("No backtracking, defina A(n,P) como o número de posições candidatas efetivamente examinadas para a entrada parcial P. Cada tentativa usa O(1), mais a validação inicial Θ(n), logo o custo específico da entrada é <b>Θ(n + A(n,P))</b>. Isso dá O(n·n!) no pior limite combinatório e Ω(n) pelo processamento da entrada. A expressão Θ(n + A(n,P)) é o limite apertado; chamar Θ(n!) para toda entrada seria incorreto, pois a poda varia com P. A memória auxiliar, inclusive pilha, é O(n)."),
              heading("3. Melhor caso, pior caso e caso médio"),
              p("No cenário sem rainhas fixas, A visita exatamente n! folhas para todo n, portanto seu custo praticamente independe de haver poucas ou muitas soluções. B tenta menos posições quando conflitos diagonais surgem cedo. Uma solução completamente fixada é o caso favorável para ambos: apenas uma configuração é verificada, com custo Θ(n). O tabuleiro vazio amplia a busca e é o caso adverso observado no conjunto medido. Cinco entradas parciais aleatórias por tamanho formam o cenário médio amostral. Essa média não representa todas as configurações possíveis."),
              PageBreak()]

    story += [heading("4. Aplicabilidade prática"),
              p("Força bruta é simples, serve como referência independente de corretude e funciona para n pequeno ou para tabuleiros quase completos. Seu crescimento fatorial inviabiliza n maior. Backtracking é preferível para enumerar ou contar soluções em tamanhos moderados, porque evita expandir configurações já impossíveis. Para apenas decidir se o tabuleiro vazio tem solução, os dois métodos são desnecessários: há uma solução para n=1 e para todo n≥4; n=2 e n=3 não têm solução [1]. Para instâncias parciais grandes, técnicas de propagação de restrições e SAT podem ser mais adequadas."),
              heading("5. Simulação e metodologia experimental"),
              p("O script de geração usa semente 20261116. Para cada n=4,5,6,7,8,9 há um tabuleiro vazio, cinco tabuleiros parciais com duas rainhas não atacantes sorteadas sem condicionar à existência de solução e um tabuleiro completamente preenchido; acrescentou-se n=4 com primeira rainha na coluna 0, impossível de completar. São 43 entradas. O incremento de uma unidade em n multiplica o espaço de permutações por n; por isso seis tamanhos pequenos já cobrem um crescimento maior que geométrico de trabalho, sem impor execuções inviáveis."),
              p("Cada combinação de linguagem e algoritmo usa o mesmo arquivo de entrada. O processo lê o arquivo antes do cronômetro; cada execução temporizada inclui somente a função do algoritmo. Há três aquecimentos e 15 execuções medidas por entrada. As médias, desvios padrão, medianas e medidas brutas são salvos em CSV. A compilação C++ usa g++ 15.2.0 com -O2 -std=c++17; Python 3.13.9. Ambiente: Intel Core i7-1355U (10 núcleos, 12 threads), 23,6 GiB de RAM e Windows 11 Home Single Language 10.0.26300."),
              p("Para o bônus de memória, uma rodada separada usa n=6,12,24,48,96,192, sempre com seis linhas livres e as demais rainhas fixas em uma solução válida. Assim as quatro versões recebem exatamente a mesma entrada, mas o fatorial das linhas livres permanece viável. São 15 processos independentes por combinação. Em Python, tracemalloc mede o pico de alocações rastreadas durante a chamada; em C++, um contador de operator new mede o pico de bytes dinamicamente alocados pelas mesmas funções. Leitura, inicialização do processo e escrita da saída ficam fora da medição. As medidas não são memória residente total e não devem ser comparadas diretamente entre linguagens."),
              p("A corretude foi verificada pelas quatro implementações nas 43 entradas, por contagens conhecidas dos tabuleiros vazios e por testes automatizados de casos de borda. Todos os programas retornaram os mesmos resultados. Tempos muito curtos, sobretudo em C++ com n pequeno ou tabuleiro completo, sofrem maior ruído de relógio e escalonamento; as conclusões de desempenho se apoiam sobretudo em n≥7."),
              heading("6. Gráficos e tabelas comparativas"),
              p("A tabela apresenta média ± desvio padrão em milissegundos, com 15 repetições por célula, para entradas vazias. A coluna de soluções confirma a saída comum."),
              table([["n", "Soluções", "A / Python", "B / Python", "A / C++", "B / C++"]] + [
                  [str(n), DATA[(f"empty_n{n}", "Python", "brute")]["solutions"]] + [
                      number(ms(f"empty_n{n}", lang, alg), 3) + " ± " +
                      number(float(DATA[(f"empty_n{n}", lang, alg)]["sd_ms"]), 3)
                      for lang, alg in (("Python", "brute"), ("Python", "backtracking"),
                                        ("C++", "brute"), ("C++", "backtracking"))]
                  for n in SIZES], [1.15*cm, 1.65*cm, 3.25*cm, 3.25*cm, 3.25*cm, 3.25*cm]),
              Spacer(1, 6),
              *figure("tempos_loglog.png", "Figura 1. Escala log-log: quatro implementações sobre as mesmas entradas vazias.")]

    n = 9
    py_speedup = ms("empty_n9", "Python", "brute") / ms("empty_n9", "Python", "backtracking")
    cpp_speedup = ms("empty_n9", "C++", "brute") / ms("empty_n9", "C++", "backtracking")
    language_ratio = ms("empty_n9", "Python", "brute") / ms("empty_n9", "C++", "brute")
    story += [heading("6. Análise dos resultados (continuação)"),
              p("Para n=9, a poda foi " + number(py_speedup, 1) + " vezes mais rápida em Python e " + number(cpp_speedup, 1)
                + " vezes em C++ na média. Mantido o algoritmo A, C++ foi " + number(language_ratio, 1)
                + " vezes mais rápido que Python. Esses fatores são observações deste equipamento e desta implementação, não propriedades assintóticas das linguagens."),
              *figure("razao_teorica.png", "Figura 2. T(n)/(n!·n) da força bruta: aproxima uma constante no intervalo maior, coerente com Θ(n!·n)."),
              *figure("operacoes.png", "Figura 3. Busca: a força bruta visita n! folhas; B registra tentativas de posições. As contagens têm unidades distintas e ilustram a poda."),
              heading("6. Efeito das entradas forçadas"),
              *figure("casos_n9.png", "Figura 4. Para n=9, o tabuleiro vazio exige mais busca; a barra parcial é a média de cinco entradas; o completo exige validação curta."),
              p("O caso vazio de n=9 tem 352 soluções; o completo tem 1. As cinco entradas parciais sorteadas têm, respectivamente, 8, 12, 7, 4 e 3 soluções. Há entradas parciais insolúveis, como n=4 com rainha fixa em (0,0); as quatro implementações concordaram. Para instâncias completas, o valor minúsculo de tempo em C++ torna razões de desempenho pouco informativas."),
              PageBreak(),
              heading("6. Escala geométrica complementar"),
              p("A série controlada dobra n de 6 a 192 mantendo m=6 linhas livres; as demais rainhas vêm de uma solução válida. Cada implementação recebeu as mesmas seis entradas, com três aquecimentos e 15 repetições, totalizando 360 tempos medidos. Manter m fixo torna a força bruta viável e isola o efeito de n, sem representar o pior caso do tabuleiro vazio. O modelo teórico de A passa a Θ(n·6!)=Θ(n); em B, as posições tentadas ainda dependem das rainhas fixas."),
              p("Uma sondagem separada, com uma execução por tamanho, registrou o limite de 60 s do tabuleiro vazio na combinação limitante, força bruta em Python: n=10 levou "
                + number(float(LIMIT["observations"][0]["algorithm_seconds"]), 2)
                + " s para 3.628.800 folhas; n=11 excedeu 60 s. Essa sondagem não integra as médias de 15 repetições."),
              table([["n", "A / Python", "B / Python", "A / C++", "B / C++"]] + [
                  [str(size)] + [number(float(GEOMETRIC[(str(size), lang, alg)]["mean_ms"]), 3)
                                 for lang, alg in (("Python", "brute"), ("Python", "backtracking"),
                                                   ("C++", "brute"), ("C++", "backtracking"))]
                  for size in MEMORY_SIZES], [1.4*cm, 3.75*cm, 3.75*cm, 3.75*cm, 3.75*cm]),
              p("Tabela: tempo médio em ms para as entradas geométricas, 15 repetições por célula.", "CaptionCustom"),
              *figure("tempos_geometricos.png", "Figura 5. Tempos médios nas mesmas entradas de tamanho geométrico; seis linhas livres em cada tabuleiro."),
              PageBreak(),
              heading("6. Bônus: uso de memória"),
              p("A tabela mostra o pico médio de alocações dinâmicas, em KiB, de 15 execuções por célula. O desvio padrão foi zero para as 24 combinações, pois as entradas e os padrões de alocação são determinísticos."),
              table([["n", "A / Python", "B / Python", "A / C++", "B / C++"]] + [
                  [str(size)] + [number(float(MEMORY[(str(size), lang, alg)]["mean_peak_bytes"]) / 1024, 2)
                                 for lang, alg in (("Python", "brute"), ("Python", "backtracking"),
                                                   ("C++", "brute"), ("C++", "backtracking"))]
                  for size in MEMORY_SIZES], [1.4*cm, 3.75*cm, 3.75*cm, 3.75*cm, 3.75*cm]),
              Spacer(1, 7),
              *figure("memoria_alocacoes.png", "Figura 6. Pico de alocações dinâmicas nas entradas de memória. Os painéis têm escalas próprias; compare tendências dentro de cada linguagem."),
              p("De n=6 a 192 (32 vezes maior), o pico medido passa de 3,09 para 32,02 KiB em Python/A e de 0,18 para 2,00 KiB em C++/A. O crescimento é compatível com estruturas auxiliares O(n): tabuleiro, vetores de ocupação e conjuntos de diagonais crescem com n. Saltos e patamares em Python refletem a capacidade interna de listas e conjuntos. A pilha recursiva não é coberta integralmente por esses contadores: nas entradas medidas, a profundidade máxima atingida é 7 chamadas em A (seis linhas livres) e n+1 em B. Para o problema geral, ambas as pilhas têm limite O(n). Os dados apoiam, mas não provam, a análise assintótica."),
              PageBreak(),
              heading("7. Reflexão sobre P e NP"),
              p("É essencial definir a pergunta. A <b>decisão do N-rainhas vazio</b> - existe uma solução? - está em P: basta verificar n, pois há solução para n=1 e n≥4 e não há para n=2 ou 3 [1]. Nosso experimento, por escolha metodológica, <b>conta todas as soluções</b>, uma tarefa diferente e muito mais cara que decidir existência. Portanto, o crescimento medido não demonstra que a decisão esteja fora de P."),
              p("O problema vizinho é <b>completar N-rainhas</b>: dadas rainhas já colocadas, é possível acrescentar as restantes sem ataques? Essa versão de decisão pertence a NP, pois um tabuleiro completo pode ser verificado em tempo polinomial. Gent, Jefferson e Nightingale [1] provaram que ela é NP-completa por uma cadeia de reduções polinomiais partindo de uma variante de satisfatibilidade; também mostraram #P-completude da versão de contagem do completamento. A diferença é que as posições pré-fixadas codificam restrições arbitrárias e eliminam a resposta simples que existe no tabuleiro vazio."),
              p("O backtracking com poda é um algoritmo exato para o problema vizinho e melhora muitas entradas na prática, mas sua redução da árvore não constitui uma prova de tempo polinomial. A dificuldade teórica se refere ao pior caso de todas as instâncias parciais, não a estas 43 amostras."),
              heading("Referência"),
              p("[1] GENT, Ian P.; JEFFERSON, Christopher; NIGHTINGALE, Peter. Complexity of n-Queens Completion. <i>Journal of Artificial Intelligence Research</i>, v. 59, p. 815-848, 2017. "
                + PAPER_URL, "SmallCustom"),
              heading("Ambiente, reprodutibilidade e responsabilidades"),
              p("O código-fonte, o gerador, a medição, os testes e os gráficos estão no repositório " + REPO_URL + ". O README contém os comandos de reprodução. Arquivos de entrada e CSVs medidos acompanham o projeto."),
              p("<b>Contribuições informadas pela equipe:</b> Bruno Augusto - força bruta e justificativa assintótica; Gustavo Torres Castro - metodologia experimental, CSVs e gráficos; Diego Magnata - backtracking, testes e apresentação; Pablo Coelho - texto final, referências e apresentação. Todos os integrantes participam da revisão e devem conseguir explicar o código e a análise."),
              heading("Declaração de uso de IA"),
              p("Durante o desenvolvimento, utilizamos o <b>ChatGPT (OpenAI Codex)</b> como ferramenta de IA generativa no estudo teórico, na implementação e revisão do código, na preparação dos experimentos, na análise dos resultados e na organização do relatório e da apresentação."),
              p("A IA foi utilizada diretamente para implementar e ajustar os algoritmos em Python e C++, os scripts de geração de entradas, medição de tempo e memória, testes e gráficos. Também ajudou a entender o funcionamento de cada implementação, discutir escolhas do código, identificar possíveis erros e esclarecer as classificações de complexidade. Na etapa experimental, apoiou a compreensão das métricas, a interpretação dos gráficos e a discussão das diferenças entre Python e C++."),
              p("<b>Exemplos de consultas:</b> diferenças entre força bruta e backtracking; justificativa de O, Ω e Θ; cuidados ao comparar Python e C++; interpretação de gráficos log-log; distinção entre N-rainhas vazio e completamento; organização de uma apresentação de até sete minutos."),
              p("<b>Validação e responsabilidade:</b> As respostas e o código produzidos com auxílio da ferramenta foram analisados pela equipe. Os integrantes são responsáveis por compreender as implementações, verificar os testes e resultados apresentados e explicar as conclusões do trabalho."),
              Spacer(1, 12),
              p("Fim do relatório.", "CaptionCustom")]
    doc.build(story)
    print(f"Relatório: {path}")


def slide_title(c: canvas.Canvas, title: str, subtitle: str = "") -> None:
    w, h = landscape(A4)
    c.setFillColor(colors.HexColor("#f8fbfb"))
    c.rect(0, 0, w, h, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#0b6575"))
    c.rect(0, h - 20, w, 20, fill=1, stroke=0)
    c.setFont("Arial-Bold", 25)
    c.setFillColor(colors.HexColor("#123945"))
    c.drawString(38, h - 68, title)
    if subtitle:
        c.setFont("Arial", 11)
        c.setFillColor(colors.HexColor("#5a6a70"))
        c.drawString(39, h - 88, subtitle)


def slide_bullets(c: canvas.Canvas, lines: list[str], y: float = 465) -> None:
    c.setFillColor(colors.HexColor("#263d44"))
    c.setFont("Arial", 15)
    for line in lines:
        c.drawString(54, y, "• " + line)
        y -= 39


def make_slides() -> None:
    PRES.mkdir(parents=True, exist_ok=True)
    path = PRES / "apresentacao_n_rainhas.pdf"
    c = canvas.Canvas(str(path), pagesize=landscape(A4))
    w, h = landscape(A4)
    slide_title(c, "N-rainhas: duas buscas, duas linguagens", "Teoria da Computação | Bruno, Gustavo, Diego e Pablo")
    slide_bullets(c, ["Força bruta por permutações x backtracking com poda", "Python e C++ sobre as mesmas entradas", "15 medições por entrada e por implementação"], h-150)
    c.showPage()
    slide_title(c, "O problema e os algoritmos")
    slide_bullets(c, ["Contar tabuleiros com n rainhas sem ataques", "A: gera todas as permutações; verifica diagonais no fim", "B: corta o ramo ao detectar conflito de coluna/diagonal", "Rainhas pré-fixadas definem a variante de completamento"], h-145)
    c.showPage()
    slide_title(c, "Complexidade teórica")
    slide_bullets(c, ["A: Θ(n·n!) no tabuleiro vazio", "B: Θ(n + tentativas examinadas); limite O(n·n!)", "B reduz a busca na prática, sem mudar o pior limite provado", "Espaço auxiliar O(n) nas duas versões"], h-145)
    c.showPage()
    slide_title(c, "Experimento reproduzível")
    slide_bullets(c, ["n=4 a 9; vazio, 5 parciais aleatórias e completo", "Mesmos 43 arquivos; semente 20261116", "3 aquecimentos + 15 medições; apenas o algoritmo cronometrado", "Quatro respostas concordaram em todas as entradas"], h-145)
    c.showPage()
    slide_title(c, "Tempo medido - escala log-log")
    c.drawImage(str(FIG / "tempos_loglog.png"), 52, 30, width=w-104, height=h-135, preserveAspectRatio=True, anchor="c")
    c.showPage()
    slide_title(c, "Resultado em n=9")
    slide_bullets(c, [f"Python: poda {number(ms('empty_n9','Python','brute')/ms('empty_n9','Python','backtracking'),1)}x mais rápida",
                      f"C++: poda {number(ms('empty_n9','C++','brute')/ms('empty_n9','C++','backtracking'),1)}x mais rápida",
                      "352 soluções; 362.880 permutações completas em A", "72.378 tentativas de posição em B"], h-145)
    c.showPage()
    slide_title(c, "Bônus: memória auxiliar")
    c.drawImage(str(FIG / "memoria_alocacoes.png"), 52, 30, width=w-104, height=h-135,
                preserveAspectRatio=True, anchor="c")
    c.showPage()
    slide_title(c, "P, NP e o problema vizinho")
    slide_bullets(c, ["Decidir N-rainhas vazio está em P", "Contar soluções é outra tarefa", "Completar tabuleiro parcial é NP-completo", "Pré-posições codificam restrições arbitrárias"], h-145)
    c.setFont("Arial", 8)
    c.drawString(48, 28, "Gent, Jefferson e Nightingale, JAIR 59 (2017).")
    c.showPage()
    c.save()
    notes = PRES / "roteiro_7_minutos.md"
    notes.write_text("""# Roteiro de apresentação (até 7 minutos)

1. **0:00-0:40 - Bruno:** problema, equipe e pergunta experimental.
2. **0:40-1:40 - Bruno:** permutações e backtracking; conferir compreensão das quatro versões.
3. **1:40-2:35 - Diego:** limites assintóticos e por que a poda ajuda.
4. **2:35-3:25 - Gustavo:** entradas, semente, repetição, temporização e testes.
5. **3:25-4:25 - Gustavo:** gráfico log-log e comparação entre algoritmos e linguagens.
6. **4:25-5:10 - Diego:** números de n=9 e limites de medição.
7. **5:10-5:45 - Gustavo:** bônus de memória e ressalva sobre pilha e runtime.
8. **5:45-6:40 - Pablo:** P, NP e completamento NP-completo; fonte Gent et al. (2017).
9. **6:40-7:00 - Todos:** conclusão e transição para perguntas.

As falas são uma distribuição proposta. Cada integrante deve revisar e conseguir explicar qualquer trecho do código e da análise antes da apresentação.
""", encoding="utf-8")
    print(f"Apresentação: {path}")


def main() -> None:
    setup_fonts()
    plot_all()
    make_report()
    make_slides()


if __name__ == "__main__":
    main()
