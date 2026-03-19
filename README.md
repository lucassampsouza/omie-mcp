# 🏦 omie-mcp

Servidor [MCP (Model Context Protocol)](https://modelcontextprotocol.io) para integração com o ERP **OMIE**. Permite controlar suas finanças diretamente pelo Claude (ou qualquer cliente MCP), usando linguagem natural.

## ✨ O que você pode fazer

Converse com o Claude e peça coisas como:

- *"Liste todas as contas a pagar em aberto do mês"*
- *"Registre o pagamento da fatura do fornecedor X"*
- *"Mostre o extrato bancário da conta corrente de março"*
- *"Qual o fluxo de caixa previsto vs realizado em fevereiro?"*
- *"Cadastre um novo fornecedor com CNPJ 12.345.678/0001-99"*

---

## 🗂️ Módulos disponíveis

| Módulo | Ferramentas |
|---|---|
| **Fornecedores** | Listar, consultar, cadastrar e alterar fornecedores |
| **Contas a Pagar** | Listar, consultar, incluir, lançar pagamento, cancelar e excluir |
| **Contas a Receber** | Listar, consultar, incluir, lançar recebimento, cancelar e excluir |
| **Lançamentos Bancários** | Listar, consultar, incluir e excluir transações em conta corrente |
| **Contas Correntes** | Listar contas, consultar detalhes e extrato bancário por período |
| **Fluxo de Caixa** | Previsto vs realizado, resumo financeiro, títulos em aberto e pesquisa unificada |

**Total: 27 ferramentas MCP**

---

## 📋 Pré-requisitos

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) instalado
- Credenciais de API do OMIE (`app_key` e `app_secret`)

> Para obter as credenciais, acesse no OMIE: **Configurações → API → Aplicações**

---

## 🚀 Instalação e uso

### Opção 1 — `uvx` direto do GitHub (sem instalar nada)

```bash
uvx --from git+https://github.com/lucassampsouza/omie-mcp omie-mcp
```

As credenciais podem ser passadas por variáveis de ambiente ou por um arquivo `.env`:

```bash
# Via variáveis de ambiente
OMIE_APP_KEY=sua_key OMIE_APP_SECRET=seu_secret \
  uvx --from git+https://github.com/lucassampsouza/omie-mcp omie-mcp
```

```bash
# Via arquivo de configuração global (recomendado para uso contínuo)
mkdir -p ~/.config/omie-mcp
echo "OMIE_APP_KEY=sua_key"     >> ~/.config/omie-mcp/.env
echo "OMIE_APP_SECRET=seu_secret" >> ~/.config/omie-mcp/.env

uvx --from git+https://github.com/lucassampsouza/omie-mcp omie-mcp
```

---

### Opção 2 — Clone local com `uv`

```bash
git clone https://github.com/lucassampsouza/omie-mcp
cd omie-mcp

# Configure as credenciais
cp .env.example .env
# Edite o .env com sua app_key e app_secret

uv run omie-mcp
```

---

## 🖥️ Configuração no Claude Desktop

### Linux / macOS

Edite o arquivo de configuração do Claude Desktop:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "omie": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/lucassampsouza/omie-mcp",
        "omie-mcp"
      ],
      "env": {
        "OMIE_APP_KEY": "sua_app_key",
        "OMIE_APP_SECRET": "seu_app_secret"
      }
    }
  }
}
```

---

### Windows com WSL

Como o Python roda dentro do WSL, a forma mais confiável é usar um script wrapper que carrega as credenciais.

**1. Configure as credenciais dentro do WSL:**

```bash
mkdir -p ~/.config/omie-mcp
cat > ~/.config/omie-mcp/.env << EOF
OMIE_APP_KEY=sua_app_key
OMIE_APP_SECRET=seu_app_secret
EOF
```

**2. Crie o script wrapper** em `~/omie-mcp-run.sh`:

```bash
cat > ~/omie-mcp-run.sh << 'EOF'
#!/bin/bash
set -e
export $(grep -v '^#' ~/.config/omie-mcp/.env | xargs)
exec uvx --from git+https://github.com/lucassampsouza/omie-mcp omie-mcp
EOF
chmod +x ~/omie-mcp-run.sh
```

**3. Edite** `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "omie": {
      "command": "wsl",
      "args": ["/home/SEU_USUARIO/omie-mcp-run.sh"]
    }
  }
}
```

> Substitua `SEU_USUARIO` pelo seu usuário no WSL (rode `whoami` no terminal WSL para confirmar).

---

## 🔧 Referência das ferramentas

### Fornecedores

| Ferramenta | Descrição |
|---|---|
| `listar_fornecedores` | Lista fornecedores com filtros por nome ou CNPJ |
| `consultar_fornecedor` | Consulta detalhes de um fornecedor pelo código ou CNPJ |
| `incluir_fornecedor` | Cadastra um novo fornecedor |
| `alterar_fornecedor` | Atualiza dados de um fornecedor existente |

### Contas a Pagar

| Ferramenta | Descrição |
|---|---|
| `listar_contas_pagar` | Lista contas filtrando por status, período e fornecedor |
| `consultar_conta_pagar` | Consulta detalhes de uma conta específica |
| `incluir_conta_pagar` | Cria uma nova conta a pagar |
| `lancar_pagamento` | Registra o pagamento (baixa) de uma conta |
| `cancelar_pagamento_conta_pagar` | Estorna o pagamento de uma conta |
| `excluir_conta_pagar` | Exclui uma conta a pagar em aberto |

### Contas a Receber

| Ferramenta | Descrição |
|---|---|
| `listar_contas_receber` | Lista contas filtrando por status, período e cliente |
| `consultar_conta_receber` | Consulta detalhes de uma conta específica |
| `incluir_conta_receber` | Cria uma nova conta a receber |
| `lancar_recebimento` | Registra o recebimento (baixa) de uma conta |
| `cancelar_recebimento` | Estorna o recebimento de uma conta |
| `excluir_conta_receber` | Exclui uma conta a receber em aberto |

### Lançamentos Bancários

| Ferramenta | Descrição |
|---|---|
| `listar_lancamentos_bancarios` | Lista transações de conta corrente por período |
| `consultar_lancamento_bancario` | Consulta detalhes de um lançamento |
| `incluir_lancamento_bancario` | Cria lançamento manual (débito ou crédito) |
| `excluir_lancamento_bancario` | Exclui um lançamento bancário |

### Contas Correntes

| Ferramenta | Descrição |
|---|---|
| `listar_contas_correntes` | Lista todas as contas bancárias cadastradas no OMIE |
| `consultar_conta_corrente` | Consulta detalhes de uma conta corrente específica |
| `consultar_extrato_bancario` | Extrato completo de uma conta em um período |

### Fluxo de Caixa

| Ferramenta | Descrição |
|---|---|
| `consultar_fluxo_caixa` | Previsto vs realizado por categoria em um mês |
| `obter_resumo_financeiro` | Resumo consolidado do período |
| `listar_titulos_em_aberto` | Lista todos os títulos não liquidados |
| `pesquisar_lancamentos_financeiros` | Pesquisa unificada (pagar + receber + bancário) |

---

## 📁 Estrutura do projeto

```
omie-mcp/
├── src/omie_mcp/
│   ├── client.py          # Cliente HTTP para a API do OMIE
│   ├── server.py          # Servidor MCP (FastMCP)
│   └── tools/
│       ├── fornecedores.py
│       ├── contas_pagar.py
│       ├── contas_receber.py
│       ├── lancamentos_cc.py
│       ├── contas_correntes.py
│       └── fluxo_caixa.py
├── .env.example           # Modelo de variáveis de ambiente
├── pyproject.toml
└── README.md
```

---

## 📄 Licença

MIT — veja o arquivo [LICENSE](LICENSE) para detalhes.
