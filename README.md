# Atividade 3 — Contêineres, namespaces e cgroups (Equipe Mistral)

Sistemas Operacionais (UFS), 2026.2. Laboratório reprodutível sobre isolamento de processos e limites de recursos em contêineres Linux.

## Estrutura do repositório

```
atividade3/
├── README.md                       ← este arquivo
├── scripts/
├── parte_a/<integrante>/           ← ambiente, digest, controladores, diagrama
├── parte_b/<integrante>/           ← namespaces (registro bruto + README com a tabela)
├── parte_c/
│   ├── daniel_farani/scripts/      ← tentativa anterior (N = 20M), preservada
│   └── lucas_emanuel/              ← execução oficial (N = 100M), preliminares/ e README
└── parte_d/<integrante>/           ← mount somente leitura e menor privilégio
```

Cada pasta de parte tem o seu `README.md` com comandos, resultados e limitações.

## Parte A — Ambiente

- Windows 10.0.26200.9711 + WSL 3.0.3.0 (distros `Ubuntu` 24.04.5 LTS e `docker-desktop`, ambas WSL2) + Docker Desktop 4.45.0
- Docker engine 28.3.3, containerd 1.7.27, runc 1.2.5, Compose v2.39.2
- cgroup v2, driver cgroupfs; controladores `cpuset cpu io memory hugetlb pids rdma`
- Kernel único e compartilhado na VM do WSL2: `6.18.54.1-microsoft-standard-WSL2` (o mesmo no Ubuntu e no daemon); 12 CPUs lógicas, ~15 GiB de RAM

Imagem oficial `python:3.12-slim` (Docker Hub), fixada por digest:

```bash
docker pull python:3.12-slim
export IMAGEM_LAB="$(docker image inspect --format '{{index .RepoDigests 0}}' python:3.12-slim)"
printf '%s\n' "$IMAGEM_LAB"
```

```
python@sha256:4840d514c583a4d3d8cad3940e68dee6f0f6f3635c12fcd0a3d74c21a5b93a54
```

Evidências: `parte_a/lucas_emanuel/ambiente.txt`, `imagem_digest.txt`, `controladores.txt`. Diagrama de camadas: `parte_a/lucas_emanuel/diagrama_camadas.png`.

## Parte B — Namespaces

Dois contêineres (`lab_a`, `lab_b`, `--network none`) da mesma imagem, com handles diferentes nos namespaces PID, mount e net; ambos têm `sleep` como PID 1, pois a numeração de PIDs é por namespace (PIDs no host do daemon: 4015 e 4058). Registro bruto e tabela comparativa em `parte_b/lucas_emanuel/` (`namespaces.txt` e `README.md`).

Limite da evidência: handles diferentes mostram namespaces distintos, mas não provam isolamento absoluto; o kernel é compartilhado.

## Parte C — cgroups (limites e medições)

Trabalho fixo de CPU (100.000.000 iterações, checksum verificado) sob duas quotas, com 256 MiB de RAM, RAM+swap = 256 MiB e `pids-limit 64`; 3 repetições por condição, alternadas. Limites confirmados dentro do contêiner (`cpu.max`, `memory.max`, `memory.swap.max`, `pids.max`).

|              | Wall (mediana) | CPU do processo | Trabalho/s   | `nr_throttled` | `throttled_usec` |
| ------------ | -------------- | --------------- | ------------ | -------------- | ---------------- |
| C1 (0,5 CPU) | 14,59 s        | 7,31 s          | 6,85 M it/s  | 146            | 8,60 s           |
| C2 (1,0 CPU) | 6,71 s         | 6,72 s          | 14,91 M it/s | 66             | 0,59 s           |

Razão das medianas de wall (C1/C2): 2,175; wall ÷ tempo de CPU ≈ 2,0 na C1 e ≈ 1,0 na C2. A variação entre rodadas vem principalmente do ruído do host (WSL2 em VM). O piloto (N = 2M), o ensaio (N = 100M) e a tentativa anterior (N = 20M) estão preservados. Detalhes, reprodução e limitações em `parte_c/lucas_emanuel/README.md`.

## Parte D — Mount somente leitura e menor privilégio

Diretório sintético montado como `/dados:ro` em um contêiner com `--user 65534:65534`, `--cap-drop ALL`, `--security-opt no-new-privileges:true` e `--network none`. A leitura funcionou; a escrita foi negada com `Read-only file system` (EROFS, e não "Permission denied"); `CapEff` zerado e `NoNewPrivs: 1`; escrita em `/tmp` funcionou como controle. Registro bruto e análise em `parte_d/lucas_emanuel/` (`readonly.txt` e `README.md`).

Limite da evidência: a negação de escrita não prova isolamento absoluto; o kernel é compartilhado.

## Vídeo

_URL: a preencher._

## Commit final

_Hash: a preencher._
