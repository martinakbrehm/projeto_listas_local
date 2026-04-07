# Requisitos de Projeto — Gerador de Listas PF

**Produto:** Gerador de Listas PF — Contatus  
**Versão:** 2.0 (Atualizada Abril 2026)  
**Data:** Abril 2026  
**Classificação:** Interno

---

## 📋 Histórico de Versões

### Versão 2.0 (Abril 2026) — Interface Moderna + Validação Robusta
- ✅ **Interface completamente redesenhada** com presets, estimativas visuais e UX moderna
- ✅ **Validação de dados aprimorada** para emails, telefones, nomes e CPFs
- ✅ **Novos filtros:** DDD por região, segmento socioeconômico, renda estimada
- ✅ **Usabilidade:** Sidebar inteligente, notificações, design responsivo
- ✅ **Formatos:** Excel e CSV como opções de saída
- ✅ **Testes:** 231 testes automatizados (102 para data_cleaner)

### Versão 1.0 (Original)
- Sistema básico funcional com filtros essenciais
- Interface técnica adequada apenas para usuários avançados
- Validação básica de dados

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
| F8 | **Região do DDD** | Restringe telefones para DDDs específicos (ex: 11,12,13,14,15,16,17,18,19 para São Paulo). |
| F9 | **Validação de Contato** | Remove automaticamente telefones/emails malformados ou inválidos. |
| F10 | **Priorização por E-mail** | Registros com e-mail válido aparecem primeiro no arquivo. |
| F11 | **CBO / Profissão** | Match exato no campo CBO ou por categoria profissional. |
| F12 | **Segmento Socioeconômico** | Filtro estimado por CBO e localização (Alto/Médio/Básico). |
| F13 | **Faixa de Renda** | Filtro estimado baseado em CBO e região geográfica. |
| F14 | **Quantidade** | Limite total de registros no arquivo de saída (`.head(n)`). Máximo 50.000. |

> **Score e Renda são campos inexistentes no banco — filtros implementados como estimativa baseada em CBO e localização.**

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
| CPF inválido (sequência repetida, zerado, teste, com letras) | **Remove** o registro |
| Nome inválido (`FULANO`, muito curto, numérico, só símbolos, caracteres inválidos) | **Remove** o registro |
| Campos com `EM VALIDACAO`, `NSA`, `NULO` e similares | **Remove** o registro |
| E-mail mal formado (`sememail@`, `@sememail`, sem @, domínio inválido, etc.) | **Anula** o campo (mantém registro) |
| Telefone inválido (DDD 00, todos iguais, com letras, comprimento incorreto) | **Anula** o campo (mantém registro) |
| Localidade inválida (só números, só símbolos, caracteres inválidos) | **Remove** o registro se bairro/cidade crítica |

**Validações específicas implementadas:**
- **Emails:** Detecta padrões como `sememail@`, `@sememail`, múltiplos `@`, espaços, caracteres de controle
- **Telefones:** Valida nono dígito (6-9 para móveis), DDDs válidos (11-99), presença de letras
- **Nomes:** Rejeita nomes só com símbolos, números, caracteres repetidos, início/fim inválido
- **CPFs:** Detecta letras, sequências óbvias além das já existentes

### 3.6 Interface e Usabilidade

O sistema apresenta uma **interface web moderna** com foco na usabilidade:

#### Controles Rápidos (Preset)
- **Região Geográfica:** Presets para regiões comuns (SP Capital, Sudeste, Nordeste, etc.)
- **Perfil de Contato:** Presets para tipos de contato (Digital, Telefônico, Equilibrado, Básico)
- **Tamanho da Lista:** Presets para volumes (Pequena 1k, Média 5k, Grande 10k, Ilimitada)

#### Estimativas Visuais
- **Contagem Estimada:** Cálculo aproximado baseado nos filtros aplicados
- **Tempo de Processamento:** Estimativa (instantâneo, 2-5 min, 5-15 min)
- **Qualidade Estimada:** Baseada nos filtros de validação (baixa/média/alta)

#### Funcionalidades Avançadas
- **Sidebar Inteligente:** Status de filtros ativos, atalhos, legenda visual
- **Notificações Toast:** Feedback imediato para todas as ações
- **Busca Inteligente de Bairros:** Interface com autocomplete e rankings
- **Validação Visual:** Campos obrigatórios destacados, feedback de erro
- **Responsividade:** Interface adaptável para desktop, tablet e mobile

### 3.7 Formatos de Saída

- **Excel (.xlsx):** Formatação automática com alinhamentos, formatos numéricos, zoom 90%
- **CSV:** Opção alternativa para integração com outros sistemas
- Arquivo salvo em `output/` com nome `lista_pf_UF_YYYYMMDD_HHMMSS.xlsx`
- Download imediato via botão na interface
- Arquivo sobrescrito a cada geração (apenas último disponível)

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
| NF7 | **Usabilidade** | Interface intuitiva com presets, estimativas visuais e feedback imediato. Curva de aprendizado < 30 min. |
| NF8 | **Compatibilidade** | Excel (.xlsx) e CSV com formatações aplicadas automaticamente. Interface responsiva. |
| NF9 | **Acessibilidade** | Contraste adequado, navegação por teclado, leitores de tela compatíveis. |

---

## 5. Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                     Cliente (Browser)                        │
│               Bootstrap 5 — templates/index.html             │
│    ✅ Interface moderna com presets e estimativas           │
│    ✅ JavaScript avançado para UX interativa                │
│    ✅ Design responsivo e acessível                         │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP (Flask)
┌──────────────────────────▼──────────────────────────────────┐
│                        app.py                                │
│   GET /          → formulário com UX avançada               │
│   GET /bairros/<cidade> → bairros_api.py                     │
│   POST /levantamento → contagem com estimativas             │
│   POST /gerar    → pipeline completo                         │
│   GET /download  → entrega Excel/CSV                        │
└─────┬───────────────────────┬────────────────────────────────┘
      │                       │
┌─────▼──────┐         ┌──────▼──────────────────────────────┐
│query_builder│         │         data_processor.py           │
│  .py        │         │  limpar_dataframe (data_cleaner.py)  │
│  SQL + params│        │  → validação robusta de dados       │
│             │         │  → filtros avançados (DDD, segmento) │
│             │         │  → CBO por categoria                 │
└─────┬──────┘         └──────────────────────────────────────┘
      │
┌─────▼─────────────┐         ┌────────────────────────────────┐
│  MySQL (big data)  │         │        bairros_api.py           │
│  latest_contacts   │         │  IBGE Localidades + Overpass    │
│  (tabela principal)│         │  Cache 24 h em memória          │
│                    │         │  ✅ Busca inteligente aprimorada │
└───────────────────┘         └────────────────────────────────┘
```

---

## 6. Estrutura de Arquivos

```
Projeto Listas/
├── app.py                  # Rotas Flask + lógica de negócio
├── config.py               # Constantes globais
├── config_db.py            # Credenciais do banco (não versionado)
├── config_db.example.py    # Template de credenciais (versionado)
├── query_builder.py         # Montagem da query SQL
├── data_processor.py        # Filtros Python + orquestração
├── data_cleaner.py          # ✅ Limpeza robusta de dados (emails, telefones, etc.)
├── bairros_api.py           # API dinâmica de bairros (IBGE + OSM)
├── list_logger.py           # Auditoria de gerações
├── requirements.txt
├── run.bat                  # Script de execução Windows
├── .gitignore
├── README.md                # ✅ Documentação completa atualizada
├── docs/                   # ← este diretório
│   ├── requisitos-projeto.md   # ✅ Este arquivo (atualizado)
│   ├── requisitos-design.md
│   ├── requisitos-testes.md
│   └── configuracao-credenciais.md
├── logs/
│   ├── app/                # flask_YYYY-MM-DD.log (rotativo 30 d)
│   └── geracoes/           # geracoes.csv (auditoria permanente)
├── output/                 # Excels/CSV gerados para download
├── pedidos/                # PDFs dos pedidos recebidos
├── templates/
│   └── index.html          # ✅ Interface completamente redesenhada
└── tests/
    ├── conftest.py
    ├── test_data_cleaner.py    # ✅ 102 testes (melhorias incluídas)
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

- [x] Operador consegue gerar lista apenas informando UF.
- [x] Arquivo Excel abre corretamente com formatações aplicadas.
- [x] Registros com CPF zerado ou `EM VALIDACAO` não aparecem na saída.
- [x] Filtro celular retorna apenas números com 11 dígitos e 3º dígito = `9`.
- [x] Toda geração gera uma linha em `logs/geracoes/geracoes.csv`.
- [x] Score e renda não aparecem em nenhum ponto da interface ou do arquivo.
- [x] **Emails inválidos** como `sememail@` ou `@sememail` são detectados e removidos.
- [x] **Telefones com letras** ou DDD inválido são rejeitados.
- [x] **Nomes só com símbolos** ou caracteres inválidos são removidos.
- [x] **CPFs com letras** são detectados como inválidos.
- [x] **Interface responsiva** funciona em desktop, tablet e mobile.
- [x] **Presets de região** aplicam filtros automaticamente.
- [x] **Estimativas visuais** mostram contagem aproximada em tempo real.
- [x] **Notificações toast** fornecem feedback para todas as ações.
- [x] **Validação obrigatória de contato** remove dados malformados quando ativada.
- [x] **Filtros por segmento socioeconômico** funcionam baseado em CBO.
- [x] **Busca inteligente de bairros** com autocomplete e rankings.
- [x] **Sidebar mostra filtros ativos** em tempo real.
- [x] **Formato CSV** disponível como alternativa ao Excel.
