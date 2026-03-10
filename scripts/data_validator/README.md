# Data Validator

Scripts de validação de arquivos de coleta de dados de redes sociais.

## Scripts

| Script | Descrição |
|---|---|
| `pre_validate.py` | Valida estrutura e nomenclatura dos arquivos |
| `run_validation.py` | Executa validação de conteúdo nos CSVs de coleta |
| `validate_csv.py` | Validador principal — verifica colunas e tipos contra os schemas |
| `schemas.py` | Definições de schema por plataforma |
| `data_format.py` | Funções de validação de tipos (UUID, timestamp, URL, etc.) |

## Uso

### Validar um CSV manualmente

```bash
python validate_csv.py <arquivo.csv> --platform <plataforma>
```

Exemplo:

```bash
python validate_csv.py coletas/semana05-2026-03-02_2026-03-08/x/x_2026-03-02_2026-03-08.csv --platform x
```

### Parâmetros

- `--platform`, `-p` — plataforma do schema (obrigatório). Valores: `x`, `instagram`, `youtube`, `facebook`, `tiktok`, `telegram`
- `--ignore`, `-i` — ignora uma coluna durante a validação. Para ignorar múltiplas colunas: `-i coluna1 -i coluna2`
- `--help` — exibe ajuda

### Consultar ajuda

```bash
python validate_csv.py --help
```

## Arquivos Permitidos em Pastas de Plataforma

| Tipo | Padrão | Exemplo |
|---|---|---|
| Coleta | `{plataforma}_{YYYY-MM-DD}_{YYYY-MM-DD}.csv` | `instagram_2026-03-02_2026-03-08.csv` |
| Registro | `registro_{plataforma}_{YYYY-MM-DD}_{YYYY-MM-DD}.csv` | `registro_instagram_2026-03-02_2026-03-08.csv` |
| Observações | `*.txt` | `observacoes.txt` |

Qualquer outro arquivo dentro de uma pasta de plataforma será rejeitado pelo CI.

## Pipeline CI

O workflow `validate_csv.yml` executa automaticamente em PRs que alteram arquivos em `coletas/`:

1. **Pre-validate** — verifica nomes de arquivos e pastas
2. **Validate CSV content** — valida conteúdo dos CSVs de coleta contra os schemas
3. **Upload para Google Drive** — envia os arquivos via rclone (só roda se a validação passar)
4. **Fechamento do PR** — PR é fechado automaticamente

> Os CSVs nunca são mergeados no `main`. O PR serve apenas como gate de validação.

## Observações

O script diferencia entre **erros** (críticos, falham o CI) e **avisos** (informativos). É possível que o script emita avisos mesmo quando o CSV estiver correto.

Em caso de dúvidas, entre em contato pelo grupo dos alunos ou escreva para carlos.ssantos@ufabc.edu.br.
