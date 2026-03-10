# Como Adicionar Coletas

Guia passo a passo para subir arquivos de coleta via Pull Request.

## Antes de Começar

- Certifique-se de que a pasta da semana já foi criada automaticamente (todo domingo às 18:00 UTC)
- Verifique em qual pasta de plataforma sua coleta deve ser colocada

## Estrutura de Pastas

```
coletas/
├── semana05-2026-03-02_2026-03-08/
│   ├── facebook/
│   ├── instagram/
│   ├── telegram/
│   ├── tiktok/
│   ├── x/
│   └── youtube/
├── semana06-2026-03-09_2026-03-15/
│   └── ...
└── ...
```

O número da semana (`05`) é sequencial e contínuo entre meses.

## Arquivos Permitidos

Dentro de cada pasta de plataforma, **somente** os seguintes arquivos são aceitos:

| Tipo | Formato do Nome | Obrigatório? |
|---|---|---|
| Coleta | `{plataforma}_{YYYY-MM-DD}_{YYYY-MM-DD}.csv` | Sim |
| Registro | `registro_{plataforma}_{YYYY-MM-DD}_{YYYY-MM-DD}.csv` | Não |
| Observações | `*.txt` | Não |

### Exemplos válidos

```
instagram/
├── instagram_2026-03-02_2026-03-08.csv            (ok - coleta)
├── registro_instagram_2026-03-02_2026-03-08.csv   (ok - registro)
└── observacoes.txt                                (ok - notas)
```

### Exemplos inválidos

```
instagram/
├── Instagram_2026-03-02.csv           ERRO: falta segunda data
├── insta_2026-03-02_2026-03-08.csv    ERRO: nome da plataforma incorreto
├── dados.xlsx                         ERRO: formato não permitido
├── meu_arquivo.csv                    ERRO: nome fora do padrão
└── facebook_2026-03-02_2026-03-08.csv ERRO: plataforma diferente da pasta
```

## Passo a Passo

### 1. Criar uma branch

```bash
git checkout main
git pull
git checkout -b coleta/<plataforma>-semanaNN
```

Exemplo: `coleta/instagram-semana05`

### 2. Adicionar os arquivos

Coloque o CSV de coleta na pasta correta:

```bash
cp seu_arquivo.csv coletas/semana05-2026-03-02_2026-03-08/instagram/instagram_2026-03-02_2026-03-08.csv
```

> **Importante:** o nome do arquivo deve ser **exatamente** `{plataforma}_{YYYY-MM-DD}_{YYYY-MM-DD}.csv`.

### 3. Commit e push

```bash
git add coletas/
git commit -m "coleta: instagram semana 05"
git push origin coleta/instagram-semana05
```

### 4. Abrir o Pull Request

- Vá ao GitHub e abra um PR da sua branch para `main`
- O CI vai rodar automaticamente:
  1. **Pré-validação** — verifica se os nomes dos arquivos estão corretos
  2. **Validação de conteúdo** — verifica colunas, tipos e formatos do CSV
  3. **Upload para Google Drive** — se tudo passar, os arquivos são enviados automaticamente
  4. **Fechamento do PR** — o PR é fechado automaticamente com comentário de sucesso

> **Nota:** O PR **não é mergeado**. Ele serve apenas como gate de validação. Os CSVs vão direto para o Google Drive.

### 5. Corrigir erros (se houver)

Se o CI falhar, verifique os logs na aba Actions do GitHub:

- **`[FAIL] File not allowed`** — arquivo com nome ou formato incorreto
- **`[FAIL] Platform mismatch`** — arquivo na pasta da plataforma errada
- **Erros de schema** — colunas faltando ou tipos incorretos no CSV

Corrija os erros, faça commit e push novamente. O CI roda automaticamente a cada push. O upload só acontece quando todas as validações passarem.

## PRs Parciais

É permitido subir arquivos em PRs separados:

- Um PR só com o CSV de coleta
- Um PR só com o registro
- Um PR com coleta + registro + txt

## Dúvidas

Em caso de dúvidas sobre o formato dos dados ou erros de validação, consulte o [README do data_validator](scripts/data_validator/README.md) ou entre em contato pelo grupo dos alunos.
