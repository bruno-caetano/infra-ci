# infra-ci

Infraestrutura e CI/CD para gerenciamento de coletas de dados de redes sociais.

## Estrutura do Projeto

```
.github/workflows/
├── create_next_week_folder.yml   # Agendado: cria estrutura de pastas semanal
└── validate_csv.yml              # Trigger de PR: valida, envia para Drive e fecha PR

scripts/
├── config.json                   # Configuração compartilhada (lista de plataformas)
├── data_validator/               # Scripts de validação (ver README próprio)
│   ├── pre_validate.py           # Pré-validação: estrutura e nomenclatura
│   ├── run_validation.py         # Executa validação de conteúdo nos CSVs de coleta
│   ├── validate_csv.py           # Validador principal de CSV
│   ├── schemas.py                # Definições de schema por plataforma
│   ├── data_format.py            # Funções de validação de tipos
│   └── testdata/                 # Arquivos CSV de teste
├── upload_to_drive.py            # Upload de coletas para o Google Drive
└── folder_creation/
    └── create_next_week_folder.py  # Cria estrutura de pastas da próxima semana

coletas/                          # Arquivos de coleta de dados
└── semanaNN-YYYY-MM-DD_YYYY-MM-DD/
    └── {plataforma}/
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
- **O que faz:** Cria a estrutura de pastas para a semana seguinte com subpastas para cada plataforma. Remove automaticamente pastas de semanas antigas que estão vazias (mantém as últimas 2).
- **Arquivo:** [`.github/workflows/create_next_week_folder.yml`](.github/workflows/create_next_week_folder.yml)

### Validação e Upload de Coletas

- **Trigger:** Pull requests para `main`/`master` que alterem arquivos em `coletas/`
- **Etapas:**
  1. **Pré-validação** — verifica se os arquivos seguem os padrões de nomenclatura e estão na pasta correta
  2. **Validação de conteúdo** — executa `validate_csv.py` com o parâmetro `--platform` correto para cada CSV de coleta
  3. **Upload para Google Drive** — envia os CSVs e TXTs via rclone (só roda se a validação passar)
  4. **Fechamento do PR** — PR é fechado automaticamente com comentário de sucesso
- **Arquivo:** [`.github/workflows/validate_csv.yml`](.github/workflows/validate_csv.yml)

> Os CSVs **nunca são mergeados** no `main`. O PR serve apenas como gate de validação. Após o upload para o Drive, o PR é fechado automaticamente.

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

## Setup do Google Drive (para administradores)

O workflow de upload utiliza uma Service Account do Google para enviar arquivos ao Drive via script Python (`scripts/upload_to_drive.py`). Siga os passos abaixo para configurar do zero.

### 1. Criar projeto no Google Cloud

1. Acesse [console.cloud.google.com](https://console.cloud.google.com)
2. Crie um novo projeto (ou use um existente)
3. Vá em **APIs & Services > Enable APIs** e habilite a **Google Drive API**

### 2. Criar Service Account

1. Vá em **IAM & Admin > Service Accounts > Create Service Account**
2. Nome: `gdrive-ci` (ou o que preferir)
3. Não é necessário atribuir roles
4. Na service account criada, vá em **Keys > Add Key > Create new key > JSON**
5. Vai baixar um arquivo `.json` — este é o arquivo de credenciais

### 3. Compartilhar pasta do Google Drive

1. No arquivo JSON, copie o valor do campo `client_email` (ex: `gdrive-ci@projeto.iam.gserviceaccount.com`)
2. No Google Drive, crie (ou abra) a pasta destino das coletas
3. Compartilhe a pasta com o email da Service Account com permissão de **Editor**
4. Copie o **ID da pasta** da URL:
   ```
   https://drive.google.com/drive/folders/XXXXXXXXXXXXXXXXXXXXX
                                          ^^^^^^^^^^^^^^^^^^^^^ este ID
   ```

### 4. Configurar GitHub Secrets

No repositório, vá em **Settings > Secrets and variables > Actions** e crie dois secrets:

| Secret | Valor |
|---|---|
| `GDRIVE_SA_CREDENTIALS` | Conteúdo **inteiro** do arquivo JSON da Service Account |
| `GDRIVE_FOLDER_ID` | ID da pasta do Google Drive (copiado no passo 3) |

Após esses passos, o workflow vai enviar automaticamente os CSVs validados para a pasta do Google Drive.
