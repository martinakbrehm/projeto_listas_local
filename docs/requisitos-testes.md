# Requisitos de Testes — Gerador de Listas PF

**Produto:** Gerador de Listas PF — Contatus  
**Versão:** 1.0  
**Data:** Abril 2026

---

## 1. Estratégia de Testes

### Filosofia

- Testes devem ser **independentes do banco de dados**. Nenhum teste deve exigir conexão MySQL.
- Testes **unitários** cobrem funções puras e helpers isolados.
- Testes de **integração interna** validam os pipelines completos (`limpar_dataframe`, `processar`) usando DataFrames construídos em memória.
- Chamadas HTTP externas (IBGE, Overpass) são sempre **mockadas** — nunca fazem requisições reais.
- Cada teste deve ser executado em **< 100 ms**. A suíte completa em **< 5 s**.

### Framework

| Ferramenta | Versão | Propósito |
|-----------|--------|-----------|
| `pytest` | ≥ 9.0 | Runner principal |
| `pytest-cov` | qualquer | Cobertura de código |
| `unittest.mock` | stdlib | Mocking de HTTP e dependências externas |

---

## 2. Estrutura da Suíte

```
tests/
├── __init__.py
├── conftest.py              ← fixtures compartilhadas
├── test_data_cleaner.py     ← validações CPF/email/telefone/nome + pipeline limpeza
├── test_data_processor.py   ← helpers de telefone + pipeline processar()
├── test_query_builder.py    ← construção SQL + params + ausência de score/renda
└── test_bairros_api.py      ← normalização + aliases + cache + HTTP mockado
```

**Total atual:** 181 testes | **Duração:** ~0.4 s | **Status:** ✅ 181/181 passando

---

## 3. Fixtures Compartilhadas (`conftest.py`)

| Fixture | Tipo | Descrição |
|---------|------|-----------|
| `df_valido` | `pd.DataFrame` | 3 registros PF válidos com campos completos |
| `df_com_sujeiras` | `pd.DataFrame` | Mix: válidos + CPF zero + `EM VALIDACAO` + nome curto + bairro inválido |
| `df_misturado_telefones` | `pd.DataFrame` | Celulares, fixos e números inválidos misturados |
| `filtros_basicos` | `dict` | `ufs=["SP"]`, `cidades=["SAO PAULO"]`, `tipo_telefone="movel"`, `quantidade=100` |

Todas as fixtures geram dados **100% em memória** — sem I/O, sem banco.

---

## 4. Módulo: `data_cleaner.py`

**Arquivo:** `tests/test_data_cleaner.py`  
**Classes de teste:** 6 | **Testes:** 35

### 4.1 `_eh_string_invalida`

| Caso | Entrada | Esperado |
|------|---------|----------|
| String de validação | `"EM VALIDACAO"` | `True` |
| Com acento | `"EM VALIDAÇÃO"` | `True` |
| Não informado | `"NAO INFORMADO"` | `True` |
| Abreviação inválida | `"NSA"` | `True` |
| Placeholder | `"FULANO"` | `True` |
| Sequência repetida | `"AAAAAAA"` | `True` |
| String vazia | `""` | `True` |
| `None` | `None` | `False` — None é tratado separadamente |
| Nome válido | `"JOAO DA SILVA"` | `False` |
| Bairro válido | `"JARDIM BOTANICO"` | `False` |

### 4.2 `_validar_cpf`

| Caso | Entrada | Esperado |
|------|---------|----------|
| Todos zeros | `"00000000000"` | `False` |
| Sequência repetida | `"11111111111"` | `False` |
| CPF de teste clássico | `"12345678901"` | `False` |
| Comprimento < 11 | `"123456789"` | `False` |
| Comprimento > 11 | `"123456789012"` | `False` |
| `None` | `None` | `False` |
| `NaN` | `float("nan")` | `False` |
| Com pontuação | `"321.654.987-00"` | `True` — extrai dígitos |
| Válido sem pontuação | `"32165498700"` | `True` |

### 4.3 `_validar_email`

| Caso | Entrada | Esperado |
|------|---------|----------|
| Sem arroba | `"emailsemarroba.com"` | `False` |
| Domínio sem ponto | `"usuario@dominio"` | `False` |
| Usuário vazio | `"@dominio.com"` | `False` |
| String inválida | `"EM VALIDACAO"` | `False` |
| E-mail válido | `"usuario@dominio.com"` | `True` |
| Com subdomínio | `"x@sub.dominio.com.br"` | `True` |
| `None` | `None` | `True` — campo vazio é aceito |
| `NaN` | `np.nan` | `True` — campo vazio é aceito |

### 4.4 `_validar_telefone`

| Caso | Entrada | Esperado |
|------|---------|----------|
| < 10 dígitos | `"11987654"` | `False` |
| > 11 dígitos | `"119876543210"` | `False` |
| Todos iguais | `"11111111111"` | `False` |
| DDD 00 | `"00987654321"` | `False` |
| Celular válido | `"11987654321"` | `True` |
| Fixo válido | `"1132165498"` | `True` |
| `None` | `None` | `True` — campo vazio é aceito |
| String vazia | `""` | `True` — campo vazio é aceito |

### 4.5 `_validar_nome`

| Caso | Entrada | Esperado |
|------|---------|----------|
| Menor que 3 caracteres | `"AB"` | `False` |
| Apenas números | `"12345678"` | `False` |
| Placeholder | `"FULANO"` | `False` |
| String inválida | `"EM VALIDACAO"` | `False` |
| `None` | `None` | `False` |
| Simples | `"JOAO SILVA"` | `True` |
| Composto | `"MARIA DE FATIMA SOUZA"` | `True` |

### 4.6 `limpar_dataframe` — Pipeline Completo

| Caso | Comportamento esperado |
|------|----------------------|
| DataFrame vazio | Retorna vazio sem erro |
| Registros válidos | Nenhum removido; relatório com zeros |
| CPF `"00000000000"` | `removidos_cpf = 1` |
| Nome `"EM VALIDACAO"` | `removidos_validacao >= 1`; registro removido |
| Email inválido | Registro mantido; campo `EMAIL_1 = None`; `removidos_email >= 1` |
| Telefone inválido | Registro mantido; campo `TELEFONE_1 = None`; `removidos_telefone >= 1` |
| `relatorio_html(r)` | Retorna `str` contendo `<strong>` e `"Limpeza de dados"` |

---

## 5. Módulo: `data_processor.py`

**Arquivo:** `tests/test_data_processor.py`  
**Classes de teste:** 8 | **Testes:** 58

### 5.1 `_apenas_digitos`

| Entrada | Esperado |
|---------|----------|
| `"11987654321"` | `"11987654321"` |
| `"321.654.987-00"` | `"32165498700"` |
| `"(11) 98765-4321"` | `"11987654321"` |
| `None` | `""` |
| `""` | `""` |
| `"abc-def"` | `""` |

### 5.2 `_eh_celular`

| Caso | Entrada | Esperado |
|------|---------|----------|
| Celular SP | `"11987654321"` | `True` |
| Celular RJ | `"21956781234"` | `True` |
| Celular MG | `"31912345678"` | `True` |
| Fixo (10 dígitos) | `"1132165498"` | `False` |
| 3º dígito = 1 | `"11187654321"` | `False` |
| 3º dígito = 8 | `"11887654321"` | `False` |
| Curto (10 dígitos, 3º=9) | `"1198765432"` | `False` |
| Longo (12 dígitos) | `"119876543210"` | `False` |
| Vazio | `""` | `False` |
| `None` | `None` | `False` |
| Com máscara | `"(11) 98765-4321"` | `True` |

### 5.3 `_eh_fixo`

| Caso | Entrada | Esperado |
|------|---------|----------|
| Fixo válido SP | `"1132165498"` | `True` |
| Fixo válido RJ | `"2132165498"` | `True` |
| Celular (11 dígitos) | `"11987654321"` | `False` |
| 9 dígitos | `"113216549"` | `False` |
| 12 dígitos | `"113216549834"` | `False` |
| Vazio | `""` | `False` |

### 5.4 `_tem_telefone_do_tipo`

| Caso | Configuração | Tipo | Esperado |
|------|-------------|------|----------|
| Celular em `TELEFONE_1` | `TELEFONE_1="11987654321"` | `movel` | `True` |
| Celular em `TELEFONE_3` | `TELEFONE_3="11987654321"` | `movel` | `True` |
| Fixo em `TELEFONE_2` | `TELEFONE_2="1132165498"` | `fixo` | `True` |
| Sem telefones | todos `None` | `movel` | `False` |
| Só fixo, busca celular | `TELEFONE_1="1132165498"` | `movel` | `False` |
| Só celular, busca fixo | `TELEFONE_1="11987654321"` | `fixo` | `False` |
| `ambos` + celular | `TELEFONE_1="11987654321"` | `ambos` | `True` |
| `ambos` + fixo | `TELEFONE_1="1132165498"` | `ambos` | `True` |
| `ambos` + nenhum | todos `None` | `ambos` | `False` |
| Celular apenas em `TELEFONE_6` | `TELEFONE_6="11987654321"` | `movel` | `True` |

### 5.5 `processar` — Pipeline Completo

Todos os testes mocam `limpar_dataframe` para retornar o DataFrame sem modificações (isola o pipeline Python dos dados).

| Caso | Filtros | Esperado |
|------|---------|----------|
| DataFrame vazio | qualquer | `(DataFrame vazio, "")` |
| Retorno é tupla | `tipo_telefone="movel"` | `isinstance(result, tuple)` e `len == 2` |
| Filtro celular | 1 celular + 1 fixo | `len == 1` (fixo removido) |
| Filtro fixo | 1 celular + 1 fixo | `len == 1` (celular removido) |
| `ambos` mantém tudo | 1 celular + 1 fixo | `len == 2` |
| Filtro CBO | 2 CBO distintos, pede 1 | `len == 1` |
| CBO vazio não filtra | 2 registros | `len == 2` |
| Quantidade limita | 10 registros, `quantidade=3` | `len == 3` |
| Quantidade 0 = sem limite | 5 registros, `quantidade=0` | `len == 5` |
| Email preferencial ordena | 1 sem email + 1 com email | primeiro registro tem `@` |
| Index resetado | qualquer | `list(index) == list(range(n))` |
| HTML é string | qualquer | `isinstance(html, str)` |

### 5.6 `colunas_saida`

| Verificação | Esperado |
|-------------|----------|
| Retorno | `list` |
| Colunas obrigatórias | `NOME, CPF, TELEFONE_1, UF, CIDADE, BAIRRO` presentes |
| Com email (padrão) | `EMAIL_1, EMAIL_2` presentes |
| Sem email | `EMAIL_1, EMAIL_2` ausentes |
| Sem score | `SCORE` ausente |
| Sem renda | `RENDA` ausente |
| Todos os telefones | `TELEFONE_1` … `TELEFONE_6` presentes |

---

## 6. Módulo: `query_builder.py`

**Arquivo:** `tests/test_query_builder.py`  
**Classes de teste:** 8 | **Testes:** 35

### 6.1 Validação básica

| Caso | Esperado |
|------|----------|
| `ufs=[]` | `ValueError` com mensagem contendo `"UF"` |
| Retorno SQL | `isinstance(sql, str)` |
| Retorno params | `isinstance(params, list)` |
| Início do SQL | `sql.strip().upper().startswith("SELECT")` |
| Tabela no FROM | `"latest_contacts"` ou `"lc"` no SQL |
| Cláusula WHERE | `"WHERE"` presente no SQL |

### 6.2 Filtro UF

| Caso | Entrada | Esperado |
|------|---------|----------|
| UF único | `ufs=["SP"]` | `"SP"` em `params` |
| Múltiplos UFs | `ufs=["SP","RJ","MG"]` | todos em `params` |
| Múltiplos geram placeholders | `ufs=["SP","RJ"]` | `sql.count("%s") >= 2` |
| Minúsculo convertido | `ufs=["sp"]` | `"SP"` em params; `"sp"` fora |
| Cláusula IN | qualquer UF | `"IN"` no SQL |

### 6.3 Filtro Cidade / Bairro

| Caso | Esperado |
|------|----------|
| Sem cidade | valor de cidade não aparece no SQL |
| Com cidade | cidade em `params` |
| Múltiplas cidades | todas em `params` |
| Sem bairro | valor de bairro não aparece em `params` |
| Com bairro | bairro em `params` maiúsculo |

### 6.4 Filtro Gênero

| Entrada | Esperado |
|---------|----------|
| `"ambos"` | Sem `LIKE` no SQL |
| `"F"` | `LIKE` no SQL; `"%F%"` em `params` |
| `"M"` | `LIKE` no SQL; `"%M%"` em `params` |
| `"FEMININO"` | `"%F%"` em `params` |
| `"MASCULINO"` | `"%M%"` em `params` |

### 6.5 Filtro Idade

| Caso | Esperado |
|------|----------|
| Sem informar | `BETWEEN` no SQL; `IDADE_MAX_PADRAO` e `IDADE_MIN_PADRAO` em `params` |
| `idade_min=30, max=50` | `50` e `30` em `params` |
| `idade_min=5` | `IDADE_MIN_PADRAO` (18) em params; `5` fora |
| SQL gerado | `data_nascimento`, `INTERVAL`, `YEAR` no SQL |

### 6.6 Filtro Email

| Entrada | Esperado |
|---------|----------|
| `"nao_filtrar"` | Sem `IS NOT NULL` e sem `IS NULL` |
| `"obrigatorio"` | `IS NOT NULL` no SQL |
| `"nao"` | Sem `IS NULL` (sem redução de base) |

### 6.7 Ausência de Score e Renda

| Caso | Esperado |
|------|----------|
| SQL gerado | `"score"` ausente (case-insensitive) |
| SQL gerado | `"renda"` ausente (case-insensitive) |
| `score_min/max` passados nos filtros | `500` e `900` fora de `params` |

### 6.8 `descrever_filtros_db`

| Caso | Esperado |
|------|----------|
| Retorno | `str` |
| Com UF `"PR"` | `"PR"` na string |
| Com cidade | cidade na string |
| Sem cidade | `"Cidade"` fora da string |
| Com faixas etárias | valores de idade na string |
| Email obrigatório | `"mail"` na string (case-insensitive) |

---

## 7. Módulo: `bairros_api.py`

**Arquivo:** `tests/test_bairros_api.py`  
**Classes de teste:** 4 | **Testes:** 53

Toda requisição HTTP (`_get_json`, `_post_json`) é mockada via `unittest.mock.patch`.  
O fixture `limpa_cache_antes_de_cada_teste` garante isolamento total entre testes (autouse).

### 7.1 `_normalizar`

| Entrada | Esperado |
|---------|----------|
| `"São Paulo"` | `"SAO PAULO"` |
| `"Belém"` | `"BELEM"` |
| `"curitiba"` | `"CURITIBA"` |
| `"  RIO  "` | `"RIO"` |
| `"FLORIANOPOLIS"` | `"FLORIANOPOLIS"` |
| `"Maceió"` | contém `"MACEI"` |

### 7.2 `_resolver_nome_ibge` (aliases)

| Alias | Esperado |
|-------|----------|
| `"BH"` | `"Belo Horizonte"` |
| `"bh"` (minúsculo) | `"Belo Horizonte"` |
| `"RIO"` | `"Rio de Janeiro"` |
| `"floripa"` | `"Florianópolis"` |
| `"SAMPA"` | `"São Paulo"` |
| `"Curitiba"` | `"Curitiba"` (sem alteração) |
| `"Londrina"` | `"Londrina"` (sem alteração) |

### 7.3 Cache

| Caso | Esperado |
|------|----------|
| Chave inexistente | `_cache_valido()` → `False` |
| Cache recém-salvo | `_cache_valido()` → `True` |
| Cache com 48h+ | `_cache_valido()` → `False` (expirado) |
| Dados retornados | `ts, dados = _cache[chave]`; dados corretos |
| `limpar_cache()` | `_cache_valido()` → `False` após limpeza |
| Chave normalizada | `_chave_cache("São Paulo") == _chave_cache("SAO PAULO")` |

### 7.4 `obter_bairros` (HTTP mockado)

| Caso | Mock | Esperado |
|------|------|----------|
| Retorno básico | IBGE + Overpass com 3 bairros | `list[str]` com 3 itens |
| Maiúsculas | qualquer | todos `b == b.upper()` |
| Ordem alfabética | qualquer | `bairros == sorted(bairros)` |
| Bairro curto ≤ 2 chars | tag `"it"` no Overpass | `"IT"` fora da lista |
| Bairros válidos | `"Moema"`, `"Pinheiros"` | `"MOEMA"`, `"PINHEIROS"` presentes |
| Cache 2ª chamada | 2 chamadas `obter_bairros` | `_get_json` chamado apenas 1x |
| Município não encontrado | IBGE retorna `None` | `[]` |
| IBGE lista vazia | `[]` | `[]` |
| Overpass sem elementos | `{"elements": []}` | `[]` |
| Alias BH | `"BH"` como entrada | URL IBGE contém `"Belo"` ou `"belo"` |
| Cache salvo após sucesso | chamada com sucesso | `_cache_valido(chave)` → `True` |

---

## 8. Requisitos de Qualidade dos Testes

### Cobertura mínima

| Módulo | Cobertura mínima |
|--------|-----------------|
| `data_cleaner.py` | **90%** |
| `data_processor.py` | **90%** |
| `query_builder.py` | **95%** |
| `bairros_api.py` | **85%** |

Para verificar:
```bash
python -m pytest tests/ --cov=. --cov-report=term-missing --cov-config=.coveragerc
```

### Regras dos testes

| Regra | Descrição |
|-------|-----------|
| **Isolamento total** | Nenhum teste dependente de outro. Fixtures são recriadas a cada teste. |
| **Sem I/O real** | Zero chamadas HTTP reais. Zero leituras de arquivo externo. Zero banco MySQL. |
| **Nomes descritivos** | `test_<o_que_testa>_<situacao>` (ex: `test_eh_celular_terceiro_digito_nao_9`). |
| **Um assert por propósito** | Cada teste verifica uma única propriedade do sistema. |
| **Sem `time.sleep`** | Expiração de cache testada manipulando `_cache[chave]` diretamente com timestamp falso. |
| **Sem prints nos testes** | Saída capturada pelo pytest; nenhum `print()` nos arquivos de teste. |

---

## 9. Execução

### Comandos

```bash
# Rodar tudo
python -m pytest tests/ -v

# Rodar módulo específico
python -m pytest tests/test_data_cleaner.py -v

# Rodar classe específica
python -m pytest tests/test_data_processor.py::TestEhCelular -v

# Com cobertura
python -m pytest tests/ --cov=. --cov-report=term-missing

# Parar no primeiro erro
python -m pytest tests/ -x

# Silencioso (apenas placar)
python -m pytest tests/ -q
```

### Saída esperada (suíte completa)

```
181 passed in 0.40s
```

---

## 10. Casos Não Cobertos (Fora de Escopo)

| Área | Justificativa |
|------|--------------|
| Testes de integração com MySQL | Banco de dados de produção; sem ambiente de teste separado. |
| Testes end-to-end (Selenium/Playwright) | Interface interna simples; ROI baixo para uso atual. |
| Testes de performance/carga | Sistema de uso concorrente baixo (1–3 usuários simultâneos). |
| Testes de autenticação | Sistema sem autenticação (rede interna fechada). |
| Testes de `app.py` (rotas Flask) | Dependem de DB; cobertos indiretamente pelos módulos de negócio. |
