# Parte C — Experimento de cgroups (Lucas Emanuel)

Comparação de trabalho fixo sob duas quotas de CPU: **C1 = 0,5 CPU** e **C2 = 1,0 CPU**, ambas com 256 MiB de RAM, RAM+swap = 256 MiB e `--pids-limit 64`, 3 repetições por condição, execuções alternadas (C1, C2, C2, C1, C1, C2).

Base: scripts da tentativa anterior de Daniel Farani (`../daniel_farani/scripts/`), adaptados nesta pasta (ver "Adaptações").

## Organização desta pasta

| Caminho                                                              | O que é                                                                                      |
| -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `carga_cpu.py`                                                       | Carga determinística: `ITERACOES` somas de 1; imprime tempos, checksum e leituras do cgroup  |
| `run_experimentos.sh`                                                | Roda as 6 execuções; grava `resultados_brutos.csv` e `brutos/`                               |
| `resumo.py`                                                          | Gera `resumo_consolidado.csv` e `grafico_c1_c2.png` a partir de `resultados_brutos.csv`      |
| `resultados_brutos.csv`, `brutos/`                                   | **Execução oficial** (N = 100.000.000): uma linha por execução e a saída bruta de cada uma   |
| `resumo_consolidado.csv`, `grafico_c1_c2.png`                        | Tabela (mediana, mín-máx, desvio, CV) e gráfico da execução oficial                          |
| `preliminares/piloto.csv`, `preliminares/brutos_piloto/`             | Piloto (N = 2.000.000) para validar o fluxo e a coleta                                       |
| `preliminares/ensaio_n100M.csv`, `preliminares/brutos_ensaio_n100M/` | Ensaio com o N final, feito antes da execução oficial (aquecimento); preservado, não apagado |

Não rode `python3 resumo.py` apontando para arquivos de `preliminares/` a partir desta pasta: o script sobrescreve `resumo_consolidado.csv` e `grafico_c1_c2.png` da execução oficial.

## Reprodução

```bash
# 1) reduzir ruído: parar outros contêineres e fechar aplicativos pesados
# 2) fixar a imagem por digest (mesma da Parte A)
export IMAGEM_LAB="python@sha256:4840d514c583a4d3d8cad3940e68dee6f0f6f3635c12fcd0a3d74c21a5b93a54"
# 3) piloto (opcional)
ITERACOES=2000000 SAIDA_CSV=piloto.csv DIR_BRUTOS=brutos_piloto bash run_experimentos.sh
# 4) execução oficial (N congelado)
ITERACOES=100000000 bash run_experimentos.sh
python3 resumo.py          # requer matplotlib (sudo apt install python3-matplotlib)
```

O script recusa rodar se `resultados_brutos.csv` ou `brutos/` já existirem (preserva tentativas). Para limpar uma execução própria, renomeie ou mova esses itens.

## Escolha da quantidade de trabalho (N)

O valor inicial sugerido no roteiro era N = 20.000.000. Na tentativa anterior, com N = 20M, a condição C2 durava ~1 s e a variação relativa entre repetições era alta (~30%); aumentamos para N = 100.000.000 (C1 ≈ 14,6 s, abaixo do limite de 60 s), validamos esse valor no ensaio, congelamos antes das seis execuções oficiais e não o alteramos depois. A tentativa com N = 20M foi preservada na pasta de Daniel Farani.

## Parâmetros de cada contêiner

`--network none --cpus <0.5|1.0> --memory 256m --memory-swap 256m --pids-limit 64`, carga montada em `/carga_cpu.py:ro`, `timeout 90` no host, `ITERACOES=100000000`. Limites confirmados dentro do contêiner em todas as execuções: `cpu.max` = `50000 100000` (C1) e `100000 100000` (C2); `memory.max` = 268435456; `memory.swap.max` = 0; `pids.max` = 64.

## Resultados (execução oficial, n = 3 por condição, medianas)

|              | Wall    | CPU do processo | Trabalho/s   | `nr_throttled` | `throttled_usec` |
| ------------ | ------- | --------------- | ------------ | -------------- | ---------------- |
| C1 (0,5 CPU) | 14,59 s | 7,31 s          | 6,85 M it/s  | 146            | 8,60 s           |
| C2 (1,0 CPU) | 6,71 s  | 6,72 s          | 14,91 M it/s | 66             | 0,59 s           |

- Razão das medianas de wall (C1/C2): 2,175. Wall ÷ tempo de CPU: ~2,0 na C1 e ~1,0 na C2 (utilização ~50% e ~100%).
- Outras rodadas, para consistência: ensaio com N = 100 M, razão 1,94; tentativa anterior (N = 20 M), razão ~2,17.
- `memory.peak` máximo de 17,8 MiB, ~7% do teto de 256 MiB: o limite de memória não foi pressionado. RSS (~9,7 MiB), `memory.current` (~5,6 a 6,1 MiB, exceto um valor de 17,7 MiB na C1 rep. 1) e `memory.peak` são métricas diferentes.

## Limitações e ameaças à validade

- Ruído do host (Windows + WSL2 em VM): as rodadas mais tardias de cada condição foram ~10% mais lentas, e os tempos de CPU variaram igualmente nas duas condições; isso indica variação de velocidade da máquina ao longo do tempo, não efeito da quota.
- `throttled_usec` tem a mesma ordem de grandeza de wall − CPU na C1 (~1,18×), mas não é igual; na C2 houve throttling (65 a 73 períodos) sem tempo extra de relógio. Mecanismo não determinado com estas amostras.
- Só 3 repetições por condição; ancestrais do cgroup não são visíveis de dentro do contêiner; medições em regime "quente" (imagem já local; a janela de medição cobre apenas o laço, não a inicialização).
- Checksum = número de iterações: verifica a quantidade de trabalho, não é um hash robusto.

## Adaptações em relação aos scripts originais

Imagem por digest; `--network none` e `timeout 90`; leitura de `memory.max`, `memory.swap.max`, `pids.max`, RSS e pico de RSS; saída bruta por execução em `brutos/`; ordem alternada; proteção contra sobrescrita; `resumo.py` novo.
