# Parte D — Montagem somente leitura e menor privilégio (Lucas Emanuel)

Teste feito em 10/11/2026 com a imagem fixada por digest (`python@sha256:4840d514c583a4d3d8cad3940e68dee6f0f6f3635c12fcd0a3d74c21a5b93a54`). Registro bruto: `readonly.txt`. Diretório sintético: `dados_demo/texto.txt` (conteúdo: `Documento sintetico`).

## Comando

```bash
mkdir -p dados_demo
printf '%s\n' 'Documento sintetico' > dados_demo/texto.txt

docker run --rm --network none --user 65534:65534 --cap-drop ALL \
  --security-opt no-new-privileges:true \
  -v "$PWD/dados_demo:/dados:ro" "$IMAGEM_LAB" sh -c '...'
```

Não foi usado o `evidencia_ns_mount.sh` do kit de apoio; o teste seguiu os comandos do enunciado.

Dentro do contêiner o teste executa `id`, `cat /dados/texto.txt`, `touch /dados/novo.txt`, lê a linha de `/dados` em `/proc/self/mountinfo`, `CapEff` e `NoNewPrivs` de `/proc/self/status`, e faz um controle com `touch /tmp/ok`. Foi montado apenas `dados_demo`: não foram montados `/`, o diretório home, o socket do Docker nem diretórios sigilosos. Não foi usado `--privileged`, e nenhum mecanismo de segurança do sistema foi desativado.

## Resultado

| Verificação                   | Resultado observado                                                      | Leitura                                                                                                     |
| ----------------------------- | ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| Identidade                    | `uid=65534(nobody) gid=65534(nogroup)`                                   | Processo não root.                                                                                          |
| Leitura de `/dados/texto.txt` | `Documento sintetico`                                                    | Leitura permitida.                                                                                          |
| Escrita em `/dados`           | `touch: cannot touch '/dados/novo.txt': Read-only file system`, `exit=1` | Negação registrada. A mensagem é de sistema de arquivos somente leitura (EROFS), e não de permissão negada. |
| Montagem de `/dados`          | opções `ro,noatime` em `/proc/self/mountinfo`                            | A restrição está na montagem.                                                                               |
| `CapEff`                      | `0000000000000000`                                                       | Nenhuma capability efetiva (`--cap-drop ALL`).                                                              |
| `NoNewPrivs`                  | `1`                                                                      | O processo não pode ganhar privilégios (`no-new-privileges`).                                               |
| Controle: escrita em `/tmp`   | `ok em /tmp`                                                             | O contêiner não está sem escrita em geral; a negação é específica da montagem `ro`.                         |
| No host, `ls dados_demo`      | só `texto.txt`                                                           | Nenhum arquivo foi criado.                                                                                  |

## Como distinguir os mecanismos

- **Mount namespace:** dá ao contêiner a sua própria tabela de montagens; `/dados` existe só dentro dela. Isso define o que o contêiner enxerga, e não se pode escrever ou não.
- **Montagem somente leitura (`ro`):** é uma opção da montagem. O kernel recusa escrita por qualquer usuário nessa montagem com EROFS.
- **Permissões e identidade:** no `ls -l`, o arquivo do host aparece como `-rwxrwxrwx` (diretório do Windows exposto ao WSL via drvfs/9p), então as permissões **permitiriam** a escrita. A negação, portanto, vem da montagem `ro`, e não de permissão de arquivo. Um erro de permissão teria a mensagem `Permission denied`.
- **Capabilities e `no-new-privileges`:** reduzem o que o processo pode fazer mesmo com bugs ou binários setuid. Sem capabilities, o processo não tem, por exemplo, `CAP_SYS_ADMIN` para remontar `/dados` como leitura e escrita.

## Limites da evidência

A negação de escrita não prova isolamento absoluto. O diretório continua gravável a partir do host ou de outro contêiner que o monte sem `:ro`; o kernel é compartilhado, e uma falha no kernel ou no runtime poderia contornar essas barreiras. Não coletamos o perfil de AppArmor/SELinux do contêiner e não alteramos nenhuma política.

## Nota sobre privacidade do registro

A linha de montagem em `readonly.txt` continha o caminho do usuário do Windows; essa parte foi substituída por `<CAMINHO_WINDOWS>` antes da publicação. No final do arquivo foi acrescentada, depois do teste, a listagem de `dados_demo` no host (`ls -l`), que mostra apenas `texto.txt`.
