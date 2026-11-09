#!/bin/bash
export ITERACOES=20000000
IMAGEM="python:3.12-slim"

echo "Iniciando testes..."
echo "Condicao,Repeticao,QntdTrabalho,CheckSum,Status,WallTime,CpuTime,TrabS,CpuMax,UsageUsec,NrThrottled,ThrottledUsec,MemCurrent,MemPeak" > resultados_brutos.csv

run_test() {
    local cond=$1
    local cpus=$2
    local rep=$3
    echo "EXECUCAO NUMERO: $3, CONDICAO: $1, LIMITE DE CPU: $2"

    saida=$(docker run --rm \
    --cpus="$cpus" \
    -m 256m --memory-swap 256m \
    --pids-limit 64 \
    -e ITERACOES="$ITERACOES" \
    -v "$PWD/carga_cpu.py:/carga_cpu.py:ro" \
    $IMAGEM python /carga_cpu.py)

    # Extrai os dados gerados pelo Python
    wall=$(echo "$saida" | grep "WALL_TIME" | cut -d'=' -f2)
    cpu=$(echo "$saida" | grep "CPU_TIME" | cut -d'=' -f2)
    trab=$(echo "$saida" | grep "TRABALHO_POR_S" | cut -d'=' -f2)
    check=$(echo "$saida" | grep "CHECK_SUM" | cut -d'=' -f2)
    qntd=$(echo "$saida" | grep "QNTD_TRABALHO" | cut -d'=' -f2)
    cpumax=$(echo "$saida" | grep "CPU_MAX" | cut -d'=' -f2)
    usage=$(echo "$saida" | grep "USAGE_USEC" | cut -d'=' -f2)
    nr_thrott=$(echo "$saida" | grep "NR_THROTTLED" | cut -d'=' -f2)
    thrott_usec=$(echo "$saida" | grep "THROTTLED_USEC" | cut -d'=' -f2)
    mem_curr=$(echo "$saida" | grep "MEM_CURRENT" | cut -d'=' -f2)
    mem_peak=$(echo "$saida" | grep "MEM_PEAK" | cut -d'=' -f2)

    if [ "$check" = "$qntd" ] && [ -n "$check" ]; then
        status="sucesso"
    else
        status="falha"
    fi

    echo "$cond,$rep,$qntd,$check,$status,$wall,$cpu,$trab,$cpumax,$usage,$nr_thrott,$thrott_usec,$mem_curr,$mem_peak" >> resultados_brutos.csv
}

for i in {1..3}; do
    run_test "C1" "0.5" "$i"
    run_test "C2" "1.0" "$i"
done

echo "Testes finalizados..."
cat resultados_brutos.csv