"""
resumo.py - consolida resultados_brutos.csv (Parte C) em tabela e grafico.

Uso:  python3 resumo.py [resultados_brutos.csv]
Gera: resumo_consolidado.csv e grafico_c1_c2.png (se matplotlib estiver instalado).
Usa apenas execucoes com Status=sucesso nas estatisticas; as falhas sao contadas e listadas.
"""
import csv
import statistics as st
import sys

arq = sys.argv[1] if len(sys.argv) > 1 else 'resultados_brutos.csv'

with open(arq, newline='') as f:
    linhas = list(csv.DictReader(f))

if not linhas:
    sys.exit('CSV vazio.')


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


conds = sorted({r['Condicao'] for r in linhas})
ok = {c: [r for r in linhas if r['Condicao'] == c and r['Status'] == 'sucesso'] for c in conds}
falhas = [r for r in linhas if r['Status'] != 'sucesso']

# (coluna, rotulo, unidade, fator de conversao)
METRICAS = [
    ('WallTime', 'Tempo de relogio (wall)', 's', 1),
    ('CpuTime', 'Tempo de CPU do processo', 's', 1),
    ('TrabS', 'Trabalho concluido por segundo', 'M iter/s', 1e-6),
    ('UsageUsec', 'cpu.stat usage_usec (delta)', 's', 1e-6),
    ('NrThrottled', 'cpu.stat nr_throttled (delta)', 'periodos', 1),
    ('ThrottledUsec', 'cpu.stat throttled_usec (delta)', 's', 1e-6),
    ('MemCurrent', 'memory.current (fim da carga)', 'MiB', 1 / 1048576),
    ('MemPeak', 'memory.peak (desde a criacao do cgroup)', 'MiB', 1 / 1048576),
    ('RssKB', 'RSS do processo (fim)', 'MiB', 1 / 1024),
    ('RssPicoKB', 'Pico de RSS do processo (VmHWM)', 'MiB', 1 / 1024),
]


def vals(c, col, fator):
    return [num(r[col]) * fator for r in ok[c] if num(r[col]) is not None]


saida = []
for c in conds:
    for col, rot, un, fat in METRICAS:
        v = vals(c, col, fat)
        if not v:
            continue
        saida.append({
            'Condicao': c, 'Metrica': rot, 'Unidade': un, 'n': len(v),
            'Mediana': st.median(v), 'Min': min(v), 'Max': max(v),
            'DesvioPadrao': st.stdev(v) if len(v) > 1 else 0.0,
            'CV_pct': (st.stdev(v) / st.mean(v) * 100) if len(v) > 1 and st.mean(v) else 0.0,
        })

with open('resumo_consolidado.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(saida[0].keys()))
    w.writeheader()
    w.writerows(saida)

# limites configurados (iguais em todas as execucoes de uma condicao?)
print('=== Limites lidos dentro do contêiner ===')
for c in conds:
    for col in ('CpuMax', 'MemMax', 'MemSwapMax', 'PidsMax'):
        vs = sorted({r[col] for r in ok[c]})
        print(f'{c} {col}: {vs}')

print('\n=== Resumo (mediana [min - max], desvio padrao, CV) ===')
for s in saida:
    print(f"{s['Condicao']} | {s['Metrica']:<42} | n={s['n']} | "
          f"{s['Mediana']:.3f} [{s['Min']:.3f} - {s['Max']:.3f}] {s['Unidade']} | "
          f"dp={s['DesvioPadrao']:.3f} | CV={s['CV_pct']:.1f}%")

if len(conds) == 2:
    a, b = conds
    wa, wb = vals(a, 'WallTime', 1), vals(b, 'WallTime', 1)
    ta, tb = vals(a, 'TrabS', 1), vals(b, 'TrabS', 1)
    if wa and wb and ta and tb:
        print(f'\nRazao das medianas de wall time {a}/{b}: {st.median(wa) / st.median(wb):.3f}')
        print(f'Razao das medianas de trabalho/s {b}/{a}: {st.median(tb) / st.median(ta):.3f}')

if falhas:
    print('\n=== Execucoes com falha (preservadas, fora das estatisticas) ===')
    for r in falhas:
        print(f"{r['Condicao']} rep {r['Repeticao']}: status={r['Status']} exit={r.get('ExitCode')}")

# grafico
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError:
    print('\nmatplotlib nao instalado: grafico nao gerado. Instale com: sudo apt install python3-matplotlib')
    sys.exit(0)

cores = {conds[0]: '#0072B2', conds[-1]: '#E69F00'}  # paleta segura para daltonismo
paineis = [
    ('WallTime', 1, 'Tempo de relogio (s)', 'Wall time (menor = melhor)'),
    ('TrabS', 1e-6, 'Milhoes de iteracoes por segundo', 'Trabalho concluido por segundo'),
    ('ThrottledUsec', 1e-6, 'Tempo throttled (s)', 'cpu.stat throttled_usec'),
]
fig, eixos = plt.subplots(1, 3, figsize=(12, 4.2))
for ax, (col, fat, ylabel, titulo) in zip(eixos, paineis):
    for i, c in enumerate(conds):
        v = vals(c, col, fat)
        if not v:
            continue
        med = st.median(v)
        ax.bar(i, med, color=cores[c], alpha=0.85, width=0.55)
        ax.vlines(i, min(v), max(v), color='#222222', lw=1.5)
        ax.scatter([i] * len(v), v, color='#222222', s=22, zorder=3)
    ax.set_xticks(range(len(conds)))
    cpus = {c: ok[c][0]['CpuMax'].split()[0] if ok[c] else '' for c in conds}
    ax.set_xticklabels([f"{c}\n(cpu.max {ok[c][0]['CpuMax']})" if ok[c] else c for c in conds], fontsize=8)
    ax.set_ylabel(ylabel)
    ax.set_title(titulo, fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    ax.set_axisbelow(True)
n = min(len(ok[c]) for c in conds)
fig.suptitle(f'C1 x C2: barra = mediana, pontos = repeticoes (n={n} por condicao), linha = min-max', fontsize=11)
fig.tight_layout()
fig.savefig('grafico_c1_c2.png', dpi=200)
print('\nGerado: resumo_consolidado.csv e grafico_c1_c2.png')
