# Design System — Gerador de Listas PF

**Produto:** Gerador de Listas PF — Contatus  
**Versão:** 1.0  
**Data:** Abril 2026

---

## 1. Princípios

| Princípio | Aplicação prática |
|-----------|------------------|
| **Clareza** | Cada elemento tem um único propósito visível. Sem decoração sem função. |
| **Hierarquia** | O operador enxerga primeiro o que é obrigatório, depois o opcional. |
| **Feedback imediato** | Cada ação tem resposta visual: spinner, badge de contagem, alerta de sucesso. |
| **Contexto técnico visível** | A separação banco/Python é exposta na UI — o operador entende o peso de cada filtro. |

---

## 2. Paleta de Cores

### Cores primárias

| Token | Hex | Uso |
|-------|-----|-----|
| `--azul-escuro` | `#1a2238` | Fundo da sidebar |
| `--azul-primario` | `#1565c0` | Botões principais, bordas de filtros banco |
| `--azul-hover` | `#0d47a1` | Estado hover do botão principal |
| `--azul-texto` | `#4fc3f7` | Ícone/logo na sidebar |

### Cores de destaque

| Token | Hex | Uso |
|-------|-----|-----|
| `--verde-primario` | `#00897b` | Botão "Levantamento", bordas de filtros Python |
| `--verde-hover` | `#00695c` | Estado hover do botão levantamento |

### Cores funcionais

| Token | Hex | Uso |
|-------|-----|-----|
| `--sucesso` | Bootstrap `success` | Alerta de lista gerada com sucesso |
| `--aviso` | Bootstrap `warning` | Relatório de limpeza de dados |
| `--erro` | Bootstrap `danger` | Mensagens de erro de validação |

### Cores neutras

| Token | Hex | Uso |
|-------|-----|-----|
| `--fundo-pagina` | `#f4f6f9` | Fundo geral da aplicação |
| `--fundo-card` | `#ffffff` | Cards de seção |
| `--texto-sidebar` | `#cfd8e3` | Texto secundário na sidebar |
| `--texto-sidebar-secundario` | `#8fa8c8` | Dicas e descrições na sidebar |
| `--separador` | `#e9ecef` | Bordas de separação internas |
| `--sombra-card` | `rgba(0,0,0,.07)` | Sombra dos cards |

### Badges de camada

| Badge | Fundo | Texto |
|-------|-------|-------|
| `banco` | `#e3f0ff` | `#1565c0` |
| `python` | `#e6f7f5` | `#00695c` |

---

## 3. Tipografia

**Família:** `'Segoe UI', system-ui, sans-serif`  
Sem fontes customizadas — usa a fonte do sistema para máxima legibilidade e carregamento zero.

| Elemento | Tamanho | Peso | Observação |
|----------|---------|------|------------|
| Título sidebar | `1.1rem` | `700` | Branco puro |
| Rótulos de campo | padrão Bootstrap | `600` (`fw-semibold`) | |
| Títulos de seção | `0.75rem` | `700` | Maiúsculo, `letter-spacing: 1px`, cinza |
| Texto ajuda (`form-text`) | `0.8rem` | `400` | |
| Conteúdo da tabela de preview | `0.78rem` | `400` | Compacto |
| Badges de camada | `0.65rem` | Bootstrap badge | |
| Tags de bairro | `0.8rem` | `400` | |

---

## 4. Layout

### Estrutura geral

```
┌─────────────┬──────────────────────────────────────────┐
│   Sidebar   │            Conteúdo principal             │
│   210 px    │            max-width: 1100 px             │
│   sticky    │            padding: 1.5rem                 │
└─────────────┴──────────────────────────────────────────┘
```

- Layout `d-flex` (Bootstrap Flexbox).
- Sidebar com `position: sticky; top: 0` — acompanha o scroll vertical sem abandonar a tela.
- Conteúdo principal usa `flex-grow-1` para ocupar o espaço restante.

### Cards de seção

```
┌──────────────────────────────────────────────────┐
│  TÍTULO DA SEÇÃO ─────────────────────────────── │  ← 0.75rem, maiúsculo, separador abaixo
│                                                  │
│  [campos do formulário]                          │
│                                                  │
└──────────────────────────────────────────────────┘
```

- `border-radius: 10px`
- `box-shadow: 0 1px 6px rgba(0,0,0,.07)`
- `padding: 1.25rem 1.5rem`
- `margin-bottom: 1.25rem`

### Grid interno dos cards

- Grid Bootstrap 12 colunas (`row g-3`).
- Campos amplos (cidade, bairros): `col-md-4` ou `col-md-5`.
- Campos curtos (UF, gênero): `col-md-3`.
- Campos numéricos (idade, quantidade): `col-md-2` ou `col-md-3`.

---

## 5. Componentes

### 5.1 Sidebar

- Fundo `#1a2238`, largura fixa `210px`.
- Ícone logo: `<i class="bi bi-list-check">` em `#4fc3f7`, tamanho `1.6rem`.
- Legenda visual explicando a codificação por cores (azul = banco, verde = Python).
- Lista de filtros como referência rápida para o operador.

### 5.2 Seção com separador visual de camada

Cada campo de filtro recebe uma borda lateral colorida:

```css
/* Campo que vai ao banco */
.filtro-banco  { border-left: 3px solid #1565c0; padding-left: 0.75rem; }

/* Campo processado em Python */
.filtro-python { border-left: 3px solid #00897b; padding-left: 0.75rem; }
```

### 5.3 Título de seção

```css
.section-title {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #6c757d;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}
```

### 5.4 Tags de bairro

Bairros selecionados aparecem como chips removíveis:

```
[ Moema  ×]  [ Pinheiros  ×]  [ Vila Madalena  ×]
```

- Fundo `#e3f2fd`, texto `#0d47a1`.
- `border-radius: 20px`, `padding: 2px 10px`.
- Ícone `×` visível ao hover com cor `#c62828`.

### 5.5 Lista de sugestões de bairros

- Aparece em dropdown com borda, fundo `#f8f9fa`.
- `max-height: 260px` com scroll vertical.
- Cada item com hover `background: #e3f2fd`.
- Ícone `+` à direita de cada item indica ação de adição.
- Spinner visível enquanto a API carrega (`<div class="spinner-border">`).
- Atribuição da fonte: `Fonte: OSM / OpenStreetMap` em `0.65rem` cinza.

### 5.6 Botões de ação

| Botão | Cor | Ícone | Posição |
|-------|-----|-------|---------|
| **Levantamento** | `#00897b` | `bi-search` | Card de ação, esquerda |
| **Gerar lista** | `#1565c0` | `bi-download` | Card de ação, direita |
| **Baixar Excel** | Bootstrap `success` | `bi-download` | Alerta de sucesso |

### 5.7 Tabela de preview

- Cabeçalho fixo (`position: sticky; top: 0`) com fundo `#1a2238` e texto branco.
- `font-size: 0.78rem` — compacto sem sacrificar legibilidade.
- Scroll vertical em `max-height: 420px`.
- Scroll horizontal para colunas excedentes.
- Listras `table-striped` com `table-hover`.

### 5.8 Alertas de status

| Situação | Tipo | Ícone |
|----------|------|-------|
| Lista gerada com sucesso | `alert-success` | `bi-check-circle-fill` |
| Relatório de limpeza | `alert-warning` | `bi-funnel-fill` |
| Erro de validação / banco | `alert-danger` | `bi-exclamation-triangle-fill` |
| Resultado do levantamento | Badge inline | `bi-info-circle` |

---

## 6. Interações e Comportamento

### Carregamento de bairros

- Debounce de **800 ms** após mudança de cidade ou UF antes de chamar `/bairros/<cidade>`.
- Durante o carregamento: spinner visível, lista desabilitada, texto `Carregando bairros...`.
- Após retorno: lista populada, spinner removido, fonte atribuída.
- Se a cidade não for encontrada: mensagem `Nenhum bairro encontrado` sem erro visível.

### Animações

```css
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

Aplicado em: resultado do levantamento ao aparecer.

### Validação do formulário

- Campo UF com `required` nativo do HTML5.
- Validação Bootstrap (`needs-validation`) aplicada ao `submit`.
- Mensagem de erro inline abaixo do campo inválido.

---

## 7. Responsividade

O sistema é projetado para uso interno em **desktop** (1280 px+). Sem requisito de mobile.  
A sidebar colapsa naturalmente em telas menores via Flexbox, mas não há breakpoint de sidebar responsiva definido.

---

## 8. Acessibilidade (mínimo)

- Todos os campos de formulário possuem `<label>` associado.
- Campos obrigatórios marcados com `*` e `text-danger`.
- Botões com texto descritivo (não somente ícone).
- Contraste sidebar: texto `#cfd8e3` sobre fundo `#1a2238` ≈ 7:1 (AAA).
- Contraste botão principal: branco sobre `#1565c0` ≈ 4.7:1 (AA).

---

## 9. Biblioteca de componentes

| Biblioteca | Versão | Uso |
|-----------|--------|-----|
| Bootstrap | 5.3.3 | Grid, componentes, utilitários |
| Bootstrap Icons | 1.11.3 | Ícones SVG via classe `bi-*` |

Sem jQuery. Sem frameworks JavaScript adicionais.  
Interações de bairros implementadas em **Vanilla JS** puro no `<script>` do template.
