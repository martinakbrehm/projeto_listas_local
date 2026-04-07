# Requisitos de Projeto — Gerador de Listas PF

**Produto:** Gerador de Listas PF — Contatus  
**Versão:** 1.0  
**Data:** Abril 2026  
**Classificação:** Interno

---

## 1. Visão Geral

Sistema web interno para geração de listas de contatos de **Pessoas Físicas (PF)** a partir de um banco de dados big data. O operador seleciona filtros em formulário web, o sistema consulta o banco, aplica filtros adicionais em Python, e disponibiliza um arquivo Excel para download.

---

## 2. Contexto e Motivação

O processo anterior de geração de listas era manual, dependia de acesso direto ao banco e exigia conhecimento técnico. O sistema elimina essa dependência, padroniza as saídas e cria trilha de auditoria completa para toda geração.

---

## 3. Requisitos Funcionais

### 3.1 Filtros de Consulta

Os filtros são divididos em duas camadas de execução:

#### Camada Banco (SQL — campos indexados)

| # | Filtro | Campo | Comportamento |
|---|--------|-------|---------------|
| F1 | **Estado (UF)** | `lc.UF` | Obrigatório. `IN (...)`. |
| F2 | **Cidade** | `CIDADE` | Opcional. `IN (...)`. Sem acento, maiúsculo. |
| F3 | **Bairro** | `BAIRRO` | Opcional. `IN (...)`. Seleção por lista dinâmica. |
| F4 | **Gênero** | `lc.genero` | Opcional. `LIKE "%M%"` / `LIKE "%F%"`. |
| F5 | **Faixa Etária** | `data_nascimento` | `BETWEEN (CURDATE - max)` e `(CURDATE - min)`. Padrão: 18–70 anos. |
| F6 | **E-mail** | `email_1` | `IS NOT NULL` (obrigatório), sem filtro (indiferente). |

#### Camada Python (pós-banco)

| # | Filtro | Comportamento |
|---|--------|---------------|
| F7 | **Tipo de Telefone** | `movel` (11 dígitos, 3º dígito = `9`), `fixo` (10 dígitos), `ambos`. |
| F8 | **CBO / Profissão** | Match exato no campo CBO. |
| F9 | **Priorização por E-mail** | Registros com e-mail aparecem primeiro no arquivo. |
| F10 | **Quantidade** | Limite total de registros no arquivo de saída (`.head(n)`). |

> **Score e Renda são campos inexistentes no banco — não constam em nenhum filtro.**

---

### 3.2 Levantamento Prévio

- Antes de gerar, o operador pode executar um **levantamento** que retorna apenas a contagem estimada de registros, sem exportar dados.
- O resultado mostra: total bruto do banco + total esperado após filtros Python + estimativa final.

### 3.3 Geração de Arquivo

- Formato: **Excel (.xlsx)** com formatações aplicadas (alinhamentos, formatos numéricos, zoom 90%)
- Arquivo salvo em `output/` com nome `lista_pf_UF_YYYYMMDD_HHMMSS.xlsx`
- Download disponível imediatamente após a geração via botão na interface.
- Arquivo sobrescrito a cada nova geração; apenas o último arquivo fica disponível.

### 3.4 Limpeza de Dados

Antes de aplicar filtros Python, o sistema aplica limpeza automática nos dados retornados do banco:

| Tipo | Tratamento |
|------|-----------|
| CPF inválido (sequência repetida, zerado, teste) | **Remove** o registro |
| Nome inválido (`FULANO`, muito curto, numérico) | **Remove** o registro |
| Campos com `EM VALIDACAO`, `NSA`, `NULO` e similares | **Remove** o registro |
| E-mail mal formado | **Anula** o campo (mantém registro) |
| Telefone inválido (DDD 00, todos iguais) | **Anula** o campo (mantém registro) |

### 3.5 Bairros Dinâmicos

- A lista de bairros é carregada dinamicamente ao selecionar a cidade, via API interna `/bairros/<cidade>`.
- A API consulta **IBGE Localidades** (nome oficial do município) seguido de **Overpass/OpenStreetMap** (bairros cadastrados).
- Resultados ficam em cache em memória por **24 horas**.
- Aliases suportados: `BH → Belo Horizonte`, `RIO → Rio de Janeiro`, `FLORIPA → Florianópolis`, etc.

### 3.6 Auditoria e Logs

- Cada geração registra uma linha em `logs/geracoes/geracoes.csv` com:
  - Timestamp, filtros utilizados, total banco, total pós-limpeza, total final, nome do arquivo, duração (s), status, observações.
- Log da aplicação em `logs/app/flask_YYYY-MM-DD.log`, rotação diária, retenção 30 dias.

---

## 4. Requisitos Não Funcionais

| Código | Requisito | Critério de aceitação |
|--------|-----------|----------------------|
| NF1 | **Performance** | Levantamento < 5 s para até 500 k registros. |
| NF2 | **Disponibilidade** | Sistema local; sem requisito de uptime formal. |
| NF3 | **Segurança** | Sem autenticação (uso interno em rede fechada). Sem exposição de dados em URL. |
| NF4 | **Escalabilidade** | Suporta resultados de até 200 k registros sem estouro de memória. |
| NF5 | **Auditabilidade** | 100% das gerações registradas em log. |
| NF6 | **Manutenibilidade** | Código coberto por testes automatizados. Módulos independentes e desacoplados. |
| NF7 | **Compatibilidade** | Excel (.xlsx) com formatações aplicadas automaticamente. |

---

## 5. Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                     Cliente (Browser)                        │
│               Bootstrap 5 — templates/index.html             │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP (Flask)
┌──────────────────────────▼──────────────────────────────────┐
│                        app.py                                │
│   GET /          → formulário                                │
│   GET /bairros/<cidade> → bairros_api.py                     │
│   POST /levantamento → contagem                              │
│   POST /gerar    → pipeline completo                         │
│   GET /download  → entrega o Excel                             │
└─────┬───────────────────────┬────────────────────────────────┘
      │                       │
┌─────▼──────┐         ┌──────▼──────────────────────────────┐
│query_builder│         │         data_processor.py           │
│  .py        │         │  limpar_dataframe (data_cleaner.py)  │
│  SQL + params│        │  → tipo telefone → CBO → qtd        │
└─────┬──────┘         └──────────────────────────────────────┘
      │
┌─────▼─────────────┐         ┌────────────────────────────────┐
│  MySQL (big data)  │         │        bairros_api.py           │
│  latest_contacts   │         │  IBGE Localidades + Overpass    │
│  (tabela principal)│         │  Cache 24 h em memória          │
└───────────────────┘         └────────────────────────────────┘
```

---

## 6. Estrutura de Arquivos

```
Projeto Listas/
├── app.py                  # Rotas Flask
├── config.py               # Constantes globais
├── query_builder.py         # Montagem da query SQL
├── data_processor.py        # Filtros Python + orquestração
├── data_cleaner.py          # Limpeza de sujeiras nos dados
├── bairros_api.py           # API dinâmica de bairros (IBGE + OSM)
├── list_logger.py           # Auditoria de gerações
├── requirements.txt
├── .gitignore
├── docs/                   # ← este diretório
│   ├── requisitos-projeto.md
│   ├── requisitos-design.md
│   └── requisitos-testes.md
├── logs/
│   ├── app/                # flask_YYYY-MM-DD.log (rotativo 30 d)
│   └── geracoes/           # geracoes.csv (auditoria permanente)
├── output/                 # Excels gerados para download
├── pedidos/                # PDFs dos pedidos recebidos
├── templates/
│   └── index.html
└── tests/
    ├── conftest.py
    ├── test_data_cleaner.py
    ├── test_data_processor.py
    ├── test_query_builder.py
    └── test_bairros_api.py
```

---

## 7. Colunas do Arquivo de Saída

| Coluna | Sempre presente | Condicional |
|--------|:--------------:|:-----------:|
| NOME, CPF | ✓ | |
| DDD_1, TELEFONE_1, DDD_2, TELEFONE_2, DDD_3, TELEFONE_3 | ✓ | |
| DDD_4, TELEFONE_4, DDD_5, TELEFONE_5, DDD_6, TELEFONE_6 | ✓ | |
| GENERO, DATA_NASCIMENTO | ✓ | |
| ENDERECO, NUM_END, COMPLEMENTO | ✓ | |
| BAIRRO, CIDADE, UF, CEP | ✓ | |
| EMAIL_1, EMAIL_2 | | Se `com_email=True` |
| CBO | | Se `COLUNAS_OPCIONAIS["cbo"]` |

---

## 8. Dependências Técnicas

```
Flask >= 3.0
pandas >= 2.0
mysql-connector-python
pytest >= 9.0
```

Bairros dinâmicos utilizam **apenas bibliotecas padrão do Python** (`urllib`, `gzip`, `json`) — sem dependências externas adicionais.

---

## 9. Restrições e Decisões de Projeto

| Decisão | Justificativa |
|---------|--------------|
| Filtros de bairro, gênero, idade e email vão ao **banco** | Campos indexados — busca mais eficiente que filtro Python. |
| Filtros de telefone, CBO e quantidade ficam no **Python** | Campos não indexados; processamento pós-banco é mais seguro. |
| Score e renda **não existem** no banco | Confirmado na análise do schema. Não há filtros nem colunas relacionadas. |
| Cache de bairros em memória (não Redis) | Sistema local de uso interno; simplicidade > distribuição. |
| Sem autenticação | Uso em rede interna corporativa fechada. |
| Excel (.xlsx) com formatações | Formatações aplicadas automaticamente no servidor, dispensando macro manual. |

---

## 10. Critérios de Aceite Global

- [ ] Operador consegue gerar lista apenas informando UF.
- [ ] Arquivo Excel abre corretamente com formatações aplicadas.
- [ ] Registros com CPF zerado ou `EM VALIDACAO` não aparecem na saída.
- [ ] Filtro celular retorna apenas números com 11 dígitos e 3º dígito = `9`.
- [ ] Toda geração gera uma linha em `logs/geracoes/geracoes.csv`.
- [ ] Score e renda não aparecem em nenhum ponto da interface ou do arquivo.
