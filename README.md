# Atividade 3 — Contêineres, namespaces e cgroups (Equipe Mistral)

## Estrutura do repositório

```
atividade3/
├── README.md
├── scripts/
├── parte_a/<integrante>/
├── parte_b/<integrante>/
├── parte_c/<integrante>/
└── parte_d/<integrante>/
```

## Ambiente (Parte A)

- Windows + WSL2 (Ubuntu 24.04.5 LTS) + Docker Desktop 4.45.0
- Docker engine 28.3.3, containerd 1.7.27, runc 1.2.5
- cgroup v2, driver cgroupfs
- Kernel (distro Ubuntu e daemon): `6.18.54.1-microsoft-standard-WSL2` — o mesmo, ou seja, há um único kernel compartilhado na VM do WSL2
- 12 CPUs lógicas, ~15 GiB de RAM
- Controladores disponíveis: `cpuset cpu io memory hugetlb pids rdma`

Imagem oficial `python:3.12-slim` (Docker Hub), fixada por digest. Comandos usados:

```bash
docker pull python:3.12-slim
export IMAGEM_LAB="$(docker image inspect --format '{{index .RepoDigests 0}}' python:3.12-slim)"
printf '%s\n' "$IMAGEM_LAB"
```

Digest resultante (usado em todos os experimentos, com `--network none` após o pull):

```
python@sha256:4840d514c583a4d3d8cad3940e68dee6f0f6f3635c12fcd0a3d74c21a5b93a54
```

Coleta do ambiente (data: 07/11/2026): `uname -a`, `cat /etc/os-release`, `nproc`, `free -h`, `docker version`, `docker compose version` e `docker info --format 'Cgroup={{.CgroupVersion}} Driver={{.CgroupDriver}}'`.

Evidências: `parte_a/lucas_emanuel/ambiente.txt`, `imagem_digest.txt`, `controladores.txt`.
Diagrama de camadas: `parte_a/lucas_emanuel/diagrama_camadas.png`.

## Parte B — Namespaces

Dois contêineres (`lab_a`, `lab_b`, `--network none`) com handles de namespaces PID, mount e net distintos; ambos têm `sleep` como PID 1, pois a numeração de PIDs é por namespace. Evidência: `parte_b/lucas_emanuel/namespaces.txt`.

Limite da evidência: handles diferentes mostram namespaces distintos, mas não provam isolamento absoluto; o kernel é compartilhado.

## Parte C — cgroups (limites e medições)

_A preencher._

## Parte D — Montagem somente leitura e privilégios mínimos

_A preencher._

## Vídeo

_URL: a preencher._

## Commit final

_Hash: a preencher._
