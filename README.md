# infra-ci

Infraestrutura e CI/CD para gerenciamento de coletas de dados de redes sociais.

## Estrutura do Projeto

```
.github/workflows/
├── create_next_week_folder.yml   # Agendado: cria estrutura de pastas semanal
└── validate_csv.yml              # Trigger de PR: valida CSVs por plataforma

scripts/
├── config.json                   # Configuração compartilhada (lista de plataformas)
├── data_validator/               # Scripts de validação de CSV
│   ├── run_validation.py         # Ponto de entrada: detecta plataforma e executa validação
│   ├── validate_csv.py            # Validador principal de CSV
│   ├── schemas.py                # Definições de schema por plataforma
│   ├── data_format.py             # Utilitários de formato de dados
│   └── testdata/                 # Arquivos CSV de teste
└── folder_creation/
    └── create_next_week_folder.py  # Cria estrutura de pastas da próxima semana

coletas/                          # Arquivos de coleta de dados
└── MM-YYYY/
    └── SemanaNN-YYYY-MM-DD_YYYY-MM-DD/
        └── {plataforma}_YYYY-MM-DD_YYYY-MM-DD/
```

## Padrão de Nomenclatura de Pastas

### Pastas de mês

Formato: `MM-YYYY`

Exemplos: `02-2026`, `03-2026`

### Pastas de semana

Formato: `Semana{NN}-{YYYY-MM-DD}_{YYYY-MM-DD}`

- `NN` — número sequencial (contínuo entre meses)
- Primeira data — segunda-feira (início da semana)
- Segunda data — domingo (fim da semana)

Exemplos: `Semana01-2026-02-02_2026-02-08`, `Semana05-2026-03-02_2026-03-08`

### Pastas de plataforma

Formato: `{plataforma}_{YYYY-MM-DD}_{YYYY-MM-DD}`

Plataformas: `facebook`, `instagram`, `telegram`, `tiktok`, `x`, `youtube`

Exemplo: `instagram_2026-03-02_2026-03-08`

## Workflows de CI/CD

### Criação de Pasta Semanal

- **Trigger:** Todo domingo às 18:00 UTC (cron) + disparo manual
- **O que faz:** Cria a estrutura de pastas para a semana seguinte com subpastas para cada plataforma
- **Arquivo:** `.github/workflows/create_next_week_folder.yml`

### Validação de CSV

- **Trigger:** Pull requests para `main`/`master` que alterem arquivos `.csv` em `coletas/`
- **O que faz:**
  1. Detecta quais CSVs foram alterados no PR
  2. Infere a plataforma pelo nome da pasta pai
  3. Executa `validatecsv.py` com o parâmetro `--platform` correto
- **Arquivo:** `.github/workflows/validate_csv.yml`

## Configuração

As plataformas são definidas em uma única fonte de verdade:

```json
// scripts/config.json
{
  "platforms": ["facebook", "instagram", "telegram", "tiktok", "x", "youtube"]
}
```

Todos os scripts leem desse arquivo. Para adicionar ou remover uma plataforma, edite `config.json`.

## Uso Local

### Criar pasta da próxima semana manualmente

```bash
python3 scripts/folder_creation/create_next_week_folder.py
```

### Validar um arquivo CSV

```bash
python3 scripts/data_validator/validate_csv.py <arquivo.csv> --platform <plataforma>
```

Exemplo:

```bash
python3 scripts/data_validator/validate_csv.py coletas/03-2026/Semana05-.../x_2026-03-02_2026-03-08/x.csv --platform x
```