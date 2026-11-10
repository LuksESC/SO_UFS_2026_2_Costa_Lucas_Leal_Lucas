# Parte B — Evidências de namespaces (Lucas Emanuel)

Dois contêineres independentes da mesma imagem (`python@sha256:4840d514c583a4d3d8cad3940e68dee6f0f6f3635c12fcd0a3d74c21a5b93a54`), com nomes próprios e `--network none`, ativos durante a coleta (07/11/2026). Registro bruto: `namespaces.txt`.

## Criação e coleta

```bash
docker run -d --name lab_a --network none "$IMAGEM_LAB" sleep 600
docker run -d --name lab_b --network none "$IMAGEM_LAB" sleep 600
for C in lab_a lab_b; do
  docker inspect --format 'PID_host={{.State.Pid}}' $C
  docker exec $C sh -c 'cat /proc/1/comm'
  docker exec $C readlink /proc/1/ns/pid
  docker exec $C readlink /proc/1/ns/mnt
  docker exec $C readlink /proc/1/ns/net
done
```

O registro bruto (namespaces.txt) foi gerado por um laço equivalente a este, que acrescentou rótulos (PID_host=, ns_pid= etc.) a cada saída.

O `sleep 600` apenas mantém cada contêiner vivo durante a coleta. Não foi usado o `evidencia_ns_mount.sh` do kit de apoio (o professor orientou a desconsiderar o kit); a coleta seguiu os comandos do enunciado.

## Tabela comparativa

| Recurso                              | Handle em lab_a    | Handle em lab_b    | Iguais ou diferentes | Interpretação                                                                                                                                             |
| ------------------------------------ | ------------------ | ------------------ | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PID namespace (`/proc/1/ns/pid`)     | `pid:[4026532713]` | `pid:[4026532816]` | diferentes           | Cada contêiner tem sua própria numeração de PIDs; o primeiro processo de cada um é o PID 1 do seu namespace.                                              |
| Mount namespace (`/proc/1/ns/mnt`)   | `mnt:[4026532710]` | `mnt:[4026532813]` | diferentes           | Cada contêiner enxerga sua própria árvore de montagens (o sistema de arquivos da imagem).                                                                 |
| Network namespace (`/proc/1/ns/net`) | `net:[4026532715]` | `net:[4026532818]` | diferentes           | Pilhas de rede separadas. Os contêineres foram criados com `--network none`; não coletamos `ip addr`, então não afirmamos aqui o conteúdo das interfaces. |

Dados complementares:

|                                          | lab_a   | lab_b   |
| ---------------------------------------- | ------- | ------- |
| PID no host do daemon (`docker inspect`) | 4015    | 4058    |
| Processo PID 1 interno (`/proc/1/comm`)  | `sleep` | `sleep` |

## Como ambos têm PID 1 sem serem o mesmo processo

A numeração de PIDs é relativa ao PID namespace. Cada contêiner tem o seu, e nele o primeiro processo criado recebe o número 1. Os dois executam `sleep`, por isso ambos mostram PID 1 = `sleep`, mas são processos distintos: para o host do daemon eles aparecem com PIDs diferentes (4015 e 4058). Os identificadores `pid:[...]` diferentes confirmam que os namespaces são distintos.

## Observações e limites da evidência

- O PID do `docker inspect` pertence ao host do **daemon** (a distro `docker-desktop` dentro da VM do WSL2), e não ao `/proc` do terminal Ubuntu.
- Handles diferentes mostram que os processos estão em namespaces diferentes. Isso não prova isolamento absoluto: o kernel é compartilhado entre os contêineres e as distros (mesmo kernel `6.18.54.1-microsoft-standard-WSL2` no Ubuntu e no daemon).
- Namespaces alteram o que cada contêiner **enxerga**; não limitam o que consomem (isso é papel dos cgroups, Parte C) nem definem identidade ou permissões de acesso (usuário, capabilities e política de acesso, Parte D).
- Os contêineres desta parte foram criados sem limites de recursos; os limites foram configurados e confirmados na Parte C.
