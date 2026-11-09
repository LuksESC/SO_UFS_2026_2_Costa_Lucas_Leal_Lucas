import os, time

def ler_cpu_stats():
    stats = {}
    try:
        with open('/sys/fs/cgroup/cpu.stat', 'r') as f:
        # separa num dicionário as informacoes dentro do arquivo eba
            for linha in f:
                partes = linha.split()
                if len(partes) == 2:
                    stats[partes[0]] = int(partes[1])
    except FileNotFoundError:
        pass
    return stats

# função genérica
def ler_arquivo(caminho):
    try:
        with open(caminho, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0"
    

iteracoes = int(os.environ.get('ITERACOES', 20000000))
cpu_max = ler_arquivo('/sys/fs/cgroup/cpu.max')

# tempo inicial dos cronômetros
inicio_stats = ler_cpu_stats()
inicio_wall = time.perf_counter()
inicio_cpu = time.process_time()

# carga de trabalho
x = 0
for i in range(iteracoes):
    x += 1

# tempo final dos cronômetros
final_stats = ler_cpu_stats()
final_wall = time.perf_counter()
final_cpu = time.process_time()

# Leitura da memória exata no fim do processamento
mem_current = ler_arquivo('/sys/fs/cgroup/memory.current')
mem_peak = ler_arquivo('/sys/fs/cgroup/memory.peak')

# calculos
wall_time = final_wall - inicio_wall
cpu_time = final_cpu - inicio_cpu
trabalho_por_s = (iteracoes / wall_time) if wall_time > 0 else 0
usage_usec = final_stats.get('usage_usec', 0) - inicio_stats.get('usage_usec', 0)
nr_throttled = final_stats.get('nr_throttled', 0) - inicio_stats.get('nr_throttled', 0)
throttled_usec = final_stats.get('throttled_usec', 0) - inicio_stats.get('throttled_usec', 0)

# imprime tudo
print(f'WALL_TIME={wall_time:.4f}')
print(f'CPU_TIME={cpu_time:.4f}')
print(f'TRABALHO_POR_S={trabalho_por_s:.4f}')
print(f'QNTD_TRABALHO={iteracoes}')
print(f'CHECK_SUM={x}')
print(f"CPU_MAX={cpu_max}")
print(f"USAGE_USEC={usage_usec}")
print(f"NR_THROTTLED={nr_throttled}")
print(f"THROTTLED_USEC={throttled_usec}")
print(f"MEM_CURRENT={mem_current}")
print(f"MEM_PEAK={mem_peak}")