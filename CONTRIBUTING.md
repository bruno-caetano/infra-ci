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
├── facebook_2026-03-02_2026-03-08.csv ERRO: plataforma diferente da pasta
└── subpasta/                          ERRO: subpastas não são permitidas
```

> **Atenção:** os arquivos devem estar **diretamente** na pasta da plataforma. Subpastas dentro da plataforma serão rejeitadas pelo CI.

## Passo a Passo (via terminal)

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

### 5. Corrigir erros (se houver)

Se o CI falhar, verifique os logs na aba Actions do GitHub:

- **`[FAIL] File not allowed`** — arquivo com nome ou formato incorreto
- **`[FAIL] Platform mismatch`** — arquivo na pasta da plataforma errada
- **`[FAIL] Nested folder`** — subpasta encontrada dentro da pasta da plataforma
- **Erros de schema** — colunas faltando ou tipos incorretos no CSV

Corrija os erros, faça commit e push novamente. O CI roda automaticamente a cada push.

### 6. Enviar ao Cloudinary

Após a validação passar, o bot vai comentar no PR:

> Validacao concluida com sucesso. Para enviar os arquivos ao Cloudinary, adicione o label **`upload`** a este PR.

1. No PR, clique em **Labels** (barra lateral direita)
2. Selecione o label **`upload`**
3. O workflow de upload será disparado automaticamente
4. Após o upload, o PR será fechado com um comentário contendo os links dos arquivos

> **Nota:** O PR **não é mergeado**. Os CSVs vão direto para o Cloudinary. O índice de links é atualizado em [`coletas_index.md`](coletas_index.md).

## Passo a Passo (via GitHub Web)

Se preferir subir os arquivos diretamente pelo navegador, sem usar o terminal:

### 1. Criar uma branch

1. No repositório, clique no seletor de branch (onde diz `main`)
2. Digite o nome da nova branch: `coleta/<plataforma>-semanaNN`
3. Clique em **Create branch: coleta/...**

### 2. Navegar até a pasta correta

1. Navegue até `coletas/semanaNN-datas/<plataforma>/`
   - Exemplo: `coletas/semana05-2026-03-02_2026-03-08/instagram/`
2. Certifique-se de que está **dentro da pasta da plataforma** antes de fazer upload

### 3. Fazer upload dos arquivos

1. Clique em **Add file > Upload files**
2. Arraste ou selecione **apenas os arquivos CSV/TXT** da coleta
3. **Não crie subpastas** — os arquivos devem ficar diretamente na pasta da plataforma
4. Em "Commit message", escreva: `coleta: <plataforma> semana NN`
5. Confirme que o commit vai para a **sua branch** (não para `main`)
6. Clique em **Commit changes**

### 4. Abrir o Pull Request

1. O GitHub vai sugerir criar um PR — clique em **Compare & pull request**
2. Verifique se o destino é `main`
3. Clique em **Create pull request**
4. O CI roda automaticamente

### 5. Corrigir erros (se houver)

Se o CI falhar, volte à sua branch, delete os arquivos incorretos e suba novamente.

### 6. Enviar ao Cloudinary

Quando a validação passar, adicione o label **`upload`** ao PR para disparar o envio ao Cloudinary. O PR será fechado automaticamente após o upload.

## PRs Parciais

É permitido subir arquivos em PRs separados:

- Um PR só com o CSV de coleta
- Um PR só com o registro
- Um PR com coleta + registro + txt

## Dúvidas

Em caso de dúvidas sobre o formato dos dados ou erros de validação, consulte o [README do data_validator](scripts/data_validator/README.md) ou entre em contato pelo grupo dos alunos.
