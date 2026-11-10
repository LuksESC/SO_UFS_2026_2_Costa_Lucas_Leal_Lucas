"""
carga_cpu.py - carga deterministica de CPU com trabalho fixo (Atividade 3, Parte C).

Base:
  - leitura tambem de memory.max, memory.swap.max e pids.max (confirmam os limites aplicados);
  - RSS atual (VmRSS) e pico de RSS (VmHWM) do processo, para distinguir de memory.current
    e memory.peak do cgroup;
  - arquivo ausente vira "NA" (antes virava "0", o que podia ser confundido com valor real).

O trabalho e o mesmo da versao do daniel: ITERACOES somas de 1. Se tudo correu bem,
CHECK_SUM == QNTD_TRABALHO.
"""
import os
import time

CG = '/sys/fs/cgroup/'


def ler_arquivo(caminho):
    try:
        with open(caminho, 'r') as f:
            return f.read().strip()
    except OSError:
        return 'NA'


def ler_cpu_stats():
    stats = {}
    try:
        with open(CG + 'cpu.stat', 'r') as f:
            for linha in f:
                partes = linha.split()
                if len(partes) == 2:
                    stats[partes[0]] = int(partes[1])
    except OSError:
        pass
    return stats


def ler_status_kb(campo):
    """Le VmRSS / VmHWM (em kB) de /proc/self/status."""
    try:
        with open('/proc/self/status', 'r') as f:
            for linha in f:
                if linha.startswith(campo + ':'):
                    return linha.split()[1]
    except OSError:
        pass
    return 'NA'


iteracoes = int(os.environ.get('ITERACOES', 20000000))

# limites configurados (lidos antes da carga)
cpu_max = ler_arquivo(CG + 'cpu.max')
mem_max = ler_arquivo(CG + 'memory.max')
mem_swap_max = ler_arquivo(CG + 'memory.swap.max')
pids_max = ler_arquivo(CG + 'pids.max')

inicio_stats = ler_cpu_stats()
inicio_wall = time.perf_counter()
inicio_cpu = time.process_time()

# carga de trabalho (fixa)
x = 0
for i in range(iteracoes):
    x += 1

final_stats = ler_cpu_stats()
final_wall = time.perf_counter()
final_cpu = time.process_time()

mem_current = ler_arquivo(CG + 'memory.current')
mem_peak = ler_arquivo(CG + 'memory.peak')
rss_kb = ler_status_kb('VmRSS')
rss_pico_kb = ler_status_kb('VmHWM')

wall_time = final_wall - inicio_wall
cpu_time = final_cpu - inicio_cpu
trabalho_por_s = (iteracoes / wall_time) if wall_time > 0 else 0
usage_usec = final_stats.get('usage_usec', 0) - inicio_stats.get('usage_usec', 0)
nr_throttled = final_stats.get('nr_throttled', 0) - inicio_stats.get('nr_throttled', 0)
throttled_usec = final_stats.get('throttled_usec', 0) - inicio_stats.get('throttled_usec', 0)

print(f'WALL_TIME={wall_time:.4f}')
print(f'CPU_TIME={cpu_time:.4f}')
print(f'TRABALHO_POR_S={trabalho_por_s:.4f}')
print(f'QNTD_TRABALHO={iteracoes}')
print(f'CHECK_SUM={x}')
print(f'CPU_MAX={cpu_max}')
print(f'USAGE_USEC={usage_usec}')
print(f'NR_THROTTLED={nr_throttled}')
print(f'THROTTLED_USEC={throttled_usec}')
print(f'MEM_CURRENT={mem_current}')
print(f'MEM_PEAK={mem_peak}')
print(f'MEM_MAX={mem_max}')
print(f'MEM_SWAP_MAX={mem_swap_max}')
print(f'PIDS_MAX={pids_max}')
print(f'RSS_KB={rss_kb}')
print(f'RSS_PICO_KB={rss_pico_kb}')
