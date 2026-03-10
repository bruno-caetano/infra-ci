# Setup Inicial (para administradores)

Guia para configurar o projeto do zero em um novo repositório.

## 1. Cloudinary

O Cloudinary é utilizado para armazenar os arquivos de coleta (CSVs e TXTs).

1. Acesse [cloudinary.com](https://cloudinary.com) e crie uma conta (plano free: 25GB)
2. No **Dashboard**, copie os 3 valores: **Cloud Name**, **API Key** e **API Secret**

## 2. GitHub Secrets

No repositório, vá em **Settings > Secrets and variables > Actions** e crie os seguintes secrets:

| Secret | Valor | Onde encontrar |
|---|---|---|
| `CLOUDINARY_CLOUD_NAME` | Cloud Name | Dashboard do Cloudinary |
| `CLOUDINARY_API_KEY` | API Key | Dashboard do Cloudinary |
| `CLOUDINARY_API_SECRET` | API Secret | Dashboard do Cloudinary |

> Esses secrets são usados pelo workflow `upload_to_cloudinary.yml` para enviar os arquivos.

## 3. Label de upload

Crie o label que dispara o envio ao Cloudinary:

1. No repositório, vá em **Issues > Labels > New label**
2. Nome: **`upload`**
3. Cor: escolha uma cor (sugestão: `#0E8A16` verde)
4. Descrição (opcional): `Dispara upload dos arquivos para o Cloudinary`

## 4. Verificar workflows

Confirme que os 3 workflows estão presentes em `.github/workflows/`:

| Workflow | Trigger | Função |
|---|---|---|
| `create_next_week_folder.yml` | Cron (domingo 18h UTC) + manual | Cria pastas da próxima semana |
| `collection_pr.yml` | PR em `coletas/**` | Valida arquivos e avisa para não mergear |
| `upload_to_cloudinary.yml` | Label `upload` no PR | Envia arquivos ao Cloudinary e fecha PR |

## Resumo do fluxo

```
Contribuidor abre PR com CSVs em coletas/
        │
        ▼
  collection_pr.yml roda:
  ├── Validação (pre_validate + validate_csv)
  └── Comentário: "Não faça merge. Adicione label upload"
        │
        ▼
  Revisor adiciona label "upload"
        │
        ▼
  upload_to_cloudinary.yml roda:
  ├── Verifica se validação passou
  ├── Faz upload para Cloudinary
  ├── Atualiza coletas_index.md
  └── Fecha PR automaticamente
```

Após esses passos, o projeto está pronto para receber coletas.
