# infra-ci

Infraestrutura e CI/CD para gerenciamento de coletas de dados de redes sociais.

## Estrutura do Projeto

```
.github/workflows/
├── create_next_week_folder.yml    # Agendado: cria estrutura de pastas semanal
├── validate_csv.yml               # Trigger de PR: valida arquivos em coletas/
└── upload_to_cloudinary.yml        # Trigger de label: envia arquivos ao Cloudinary

scripts/
├── config.json                    # Configuração compartilhada (lista de plataformas)
├── data_validator/                # Scripts de validação (ver README próprio)
│   ├── pre_validate.py            # Pré-validação: estrutura e nomenclatura
│   ├── run_validation.py          # Executa validação de conteúdo nos CSVs de coleta
│   ├── validate_csv.py            # Validador principal de CSV
│   ├── schemas.py                 # Definições de schema por plataforma
│   └── data_format.py             # Funções de validação de tipos
├── cloudinary/                    # Scripts de upload para o Cloudinary
│   ├── upload.py                  # Upload de CSVs/TXTs para o Cloudinary
│   └── update_index.py            # Atualiza índice de links das coletas
└── folder_creation/
    └── create_next_week_folder.py  # Cria estrutura de pastas da próxima semana

coletas/                           # Arquivos de coleta de dados
└── semanaNN-YYYY-MM-DD_YYYY-MM-DD/
    └── {plataforma}/

coletas_index.md                   # Índice de arquivos enviados ao Cloudinary
```

## Padrão de Nomenclatura

### Pastas

| Tipo | Formato | Exemplo |
|---|---|---|
| Semana | `semana{NN}-{YYYY-MM-DD}_{YYYY-MM-DD}` | `semana05-2026-03-02_2026-03-08` |
| Plataforma | `{plataforma}` | `instagram`, `youtube` |

- **NN** — número sequencial da semana (contínuo entre meses)
- **Primeira data** — segunda-feira (início da semana)
- **Segunda data** — domingo (fim da semana)

### Arquivos Permitidos em Pastas de Plataforma

| Tipo | Formato | Exemplo |
|---|---|---|
| Coleta | `{plataforma}_{YYYY-MM-DD}_{YYYY-MM-DD}.csv` | `instagram_2026-03-02_2026-03-08.csv` |
| Registro | `registro_{plataforma}_{YYYY-MM-DD}_{YYYY-MM-DD}.csv` | `registro_instagram_2026-03-02_2026-03-08.csv` |
| Observações | `*.txt` | `observacoes.txt` |

Qualquer outro arquivo dentro de uma pasta de plataforma será **rejeitado pelo CI**.

### Plataformas

`facebook`, `instagram`, `telegram`, `tiktok`, `x`, `youtube`

Definidas em [`scripts/config.json`](scripts/config.json). Para adicionar ou remover uma plataforma, edite esse arquivo.

## Workflows de CI/CD

### Criação de Pasta Semanal

- **Trigger:** Todo domingo às 18:00 UTC (cron) + disparo manual
- **O que faz:** Cria a estrutura de pastas para a semana seguinte com subpastas para cada plataforma
- **Arquivo:** [`.github/workflows/create_next_week_folder.yml`](.github/workflows/create_next_week_folder.yml)

### Validação de Coletas

- **Trigger:** Pull requests para `main`/`master` que alterem arquivos em `coletas/`
- **Etapas:**
  1. **Pré-validação** — verifica se os arquivos seguem os padrões de nomenclatura e estão na pasta correta
  2. **Validação de conteúdo** — executa `validate_csv.py` com o parâmetro `--platform` correto para cada CSV de coleta
  3. **Comentário** — se tudo passar, comenta no PR instruindo a adicionar o label `upload`
- **Arquivo:** [`.github/workflows/validate_csv.yml`](.github/workflows/validate_csv.yml)

### Upload para Cloudinary

- **Trigger:** Label `upload` adicionado ao PR
- **Etapas:**
  1. **Upload** — envia CSVs e TXTs para o Cloudinary
  2. **Índice** — atualiza [`coletas_index.md`](coletas_index.md) com links dos arquivos enviados
  3. **Fechamento** — comenta no PR com links e fecha automaticamente
- **Arquivo:** [`.github/workflows/upload_to_cloudinary.yml`](.github/workflows/upload_to_cloudinary.yml)

> O PR **não é mergeado**. Serve apenas como gate de validação e upload. Os CSVs vão direto para o Cloudinary.

Para mais detalhes sobre os scripts de validação, consulte o [README do data_validator](scripts/data_validator/README.md).

## Como Adicionar Coletas

Consulte o [guia de contribuição](CONTRIBUTING.md) para o passo a passo completo de como subir coletas via Pull Request.

## Uso Local

### Criar pasta da próxima semana

```bash
python3 scripts/folder_creation/create_next_week_folder.py
```

### Validar um arquivo CSV

```bash
python3 scripts/data_validator/validate_csv.py <arquivo.csv> --platform <plataforma>
```

Exemplo:

```bash
python3 scripts/data_validator/validate_csv.py coletas/semana05-2026-03-02_2026-03-08/x/x_2026-03-02_2026-03-08.csv --platform x
```

Para mais opções (ignorar colunas, etc.), consulte:

```bash
python3 scripts/data_validator/validate_csv.py --help
```

## Setup do Cloudinary (para administradores)

### 1. Criar conta

1. Acesse [cloudinary.com](https://cloudinary.com) e crie uma conta (plano free: 25GB)
2. No **Dashboard**, copie: **Cloud Name**, **API Key** e **API Secret**

### 2. Configurar GitHub Secrets

No repositório, vá em **Settings > Secrets and variables > Actions** e crie:

| Secret | Valor |
|---|---|
| `CLOUDINARY_CLOUD_NAME` | Cloud Name do dashboard |
| `CLOUDINARY_API_KEY` | API Key |
| `CLOUDINARY_API_SECRET` | API Secret |

### 3. Criar label no repositório

1. Vá em **Issues > Labels > New label**
2. Nome: `upload`
3. Cor: escolha uma cor (sugestão: verde)

Após esses passos, o fluxo de upload estará funcional.