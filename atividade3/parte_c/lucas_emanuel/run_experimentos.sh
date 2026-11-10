#!/bin/bash
#
# run_experimentos.sh - Parte C: C1 (0,5 CPU) x C2 (1,0 CPU), 3 repeticoes cada, alternadas.
# Base: versao do daniel. Adaptacoes: imagem por digest, --network none, timeout de 90 s,
# memory.max/pids.max/RSS coletados, saida bruta de cada execucao preservada em brutos/,
# ordem alternada e protecao contra sobrescrever resultados anteriores.
#
# Uso (oficial):  export IMAGEM_LAB=<digest>; bash run_experimentos.sh
# Uso (piloto):   ITERACOES=2000000 SAIDA_CSV=piloto.csv DIR_BRUTOS=brutos_piloto bash run_experimentos.sh

set -u
cd "$(dirname "$0")"

: "${IMAGEM_LAB:?Defina IMAGEM_LAB com o digest (export IMAGEM_LAB=\"\$(docker image inspect --format '{{index .RepoDigests 0}}' python:3.12-slim)\")}"
export ITERACOES="${ITERACOES:-20000000}"
SAIDA_CSV="${SAIDA_CSV:-resultados_brutos.csv}"
DIR_BRUTOS="${DIR_BRUTOS:-brutos}"

if [ -e "$SAIDA_CSV" ] || [ -e "$DIR_BRUTOS" ]; then
    echo "ERRO: $SAIDA_CSV ou $DIR_BRUTOS ja existe. Renomeie-os (tentativas anteriores devem ser preservadas) ou use outros nomes via SAIDA_CSV/DIR_BRUTOS." >&2
    exit 1
fi
mkdir -p "$DIR_BRUTOS"

echo "Condicao,Repeticao,Ordem,QntdTrabalho,CheckSum,Status,ExitCode,WallTime,CpuTime,TrabS,CpuMax,UsageUsec,NrThrottled,ThrottledUsec,MemCurrent,MemPeak,MemMax,MemSwapMax,PidsMax,RssKB,RssPicoKB" > "$SAIDA_CSV"

ORDEM=0

run_test() {
    local cond=$1 cpus=$2 rep=$3
    ORDEM=$((ORDEM + 1))
    local nome="lab_c_${cond}_${rep}"
    local bruto="$DIR_BRUTOS/${cond}_rep${rep}.txt"
    echo "[$ORDEM/6] condicao=$cond repeticao=$rep cpus=$cpus N=$ITERACOES"

    local saida rc
    saida=$(timeout 90 docker run --rm --name "$nome" \
        --network none \
        --cpus="$cpus" \
        --memory 256m --memory-swap 256m \
        --pids-limit 64 \
        -e ITERACOES="$ITERACOES" \
        -v "$PWD/carga_cpu.py:/carga_cpu.py:ro" \
        "$IMAGEM_LAB" python /carga_cpu.py 2>&1)
    rc=$?
    # se o timeout matou o cliente, garante que o conteiner nao fica para tras
    [ "$rc" -eq 124 ] && docker rm -f "$nome" > /dev/null 2>&1

    {
        echo "# data=$(date -Iseconds)"
        echo "# imagem=$IMAGEM_LAB"
        echo "# condicao=$cond repeticao=$rep ordem=$ORDEM cpus=$cpus memory=256m memory-swap=256m pids-limit=64 network=none"
        echo "# exit_code=$rc"
        echo "$saida"
    } > "$bruto"

    pega() { echo "$saida" | grep "^$1=" | head -1 | cut -d'=' -f2-; }
    local wall cpu trab check qntd cpumax usage nrt thr mcur mpeak mmax mswap pmax rss rsspk status
    wall=$(pega WALL_TIME);        cpu=$(pega CPU_TIME);          trab=$(pega TRABALHO_POR_S)
    check=$(pega CHECK_SUM);       qntd=$(pega QNTD_TRABALHO);    cpumax=$(pega CPU_MAX)
    usage=$(pega USAGE_USEC);      nrt=$(pega NR_THROTTLED);      thr=$(pega THROTTLED_USEC)
    mcur=$(pega MEM_CURRENT);      mpeak=$(pega MEM_PEAK);        mmax=$(pega MEM_MAX)
    mswap=$(pega MEM_SWAP_MAX);    pmax=$(pega PIDS_MAX)
    rss=$(pega RSS_KB);            rsspk=$(pega RSS_PICO_KB)

    if [ "$rc" -eq 0 ] && [ -n "$check" ] && [ "$check" = "$qntd" ]; then
        status="sucesso"
    else
        status="falha"
        echo "  AVISO: execucao marcada como falha (exit=$rc). Registro preservado em $bruto" >&2
    fi

    echo "$cond,$rep,$ORDEM,$qntd,$check,$status,$rc,$wall,$cpu,$trab,$cpumax,$usage,$nrt,$thr,$mcur,$mpeak,$mmax,$mswap,$pmax,$rss,$rsspk" >> "$SAIDA_CSV"
}

echo "Iniciando testes (imagem: $IMAGEM_LAB, N=$ITERACOES)..."
# ordem alternada: C1 C2 | C2 C1 | C1 C2
run_test C1 0.5 1
run_test C2 1.0 1
run_test C2 1.0 2
run_test C1 0.5 2
run_test C1 0.5 3
run_test C2 1.0 3

echo "Testes finalizados. Resultados em $SAIDA_CSV e $DIR_BRUTOS/"
cat "$SAIDA_CSV"
