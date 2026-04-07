# Requisitos de Usabilidade — Gerador de Listas PF

**Produto:** Gerador de Listas PF — Contatus  
**Versão:** 3.0 (Proposta)  
**Data:** Abril 2026  
**Classificação:** Interno

---

## 1. Visão Geral da Usabilidade

A interface deve ser **intuitiva e eficiente**, permitindo que operadores não-técnicos configurem filtros complexos de forma simples e visual. O foco está em **seleções diretas** sem estimativas ou presets automáticos.

---

## 2. Princípios de Design

### 2.1 Simplicidade
- **Seleções diretas:** Sem presets ou estimativas automáticas
- **Controles claros:** Cada filtro tem função óbvia
- **Feedback imediato:** Validação visual em tempo real

### 2.2 Eficiência
- **Fluxo linear:** Do geral para o específico (UF → Cidade → Bairro)
- **Agrupamento lógico:** Filtros relacionados juntos
- **Valores padrão sensatos:** Mas sempre explícitos

### 2.3 Segurança
- **Validação obrigatória:** Campos obrigatórios destacados
- **Confirmação de ações:** Levantamento antes da geração
- **Limites claros:** Máximos e mínimos definidos

---

## 3. Estrutura da Interface

### 3.1 Layout Principal

```
┌─────────────────────────────────────────────────────────────┐
│                    HEADER COM TÍTULO                         │
│              "Gerador de Listas PF - Contatus"               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    SEÇÃO: LOCALIZAÇÃO                        │
│  ┌─────────┐  ┌─────────────────┐  ┌─────────────────────┐   │
│  │ Estado  │  │     Cidade      │  │      Bairro         │   │
│  │ (UF)    │  │   (Seleção)     │  │   (Seleção múltipla) │   │
│  └─────────┘  └─────────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 SEÇÃO: CARACTERÍSTICAS                       │
│  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │   Gênero    │  │     Idade       │  │    Profissão     │   │
│  │ (Radio)     │  │   (Range)       │  │   (Checkbox)     │   │
│  └─────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   SEÇÃO: BAIRROS NOBRES                      │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ Lista de bairros nobres disponíveis                 │     │
│  │ ☑ Bairro A (R$ 15.000+)                             │     │
│  │ ☐ Bairro B (R$ 12.000+)                             │     │
│  │ ☑ Bairro C (R$ 18.000+)                             │     │
│  │ [Selecionar quantos desejar]                        │     │
│  └─────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    SEÇÃO: CONTATO                            │
│  ┌─────────────────┐  ┌─────────────────┐                    │
│  │ Tipo Telefone   │  │ Email Obrigatório│                    │
│  │   (Radio)       │  │   (Checkbox)     │                    │
│  └─────────────────┘  └─────────────────┘                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   SEÇÃO: QUANTIDADE                          │
│  ┌─────────────────┐  ┌─────────────────┐                    │
│  │ Tipo de Limite  │  │     Valor       │                    │
│  │ (Absoluto/% )   │  │   (Número)      │                    │
│  └─────────────────┘  └─────────────────┘                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    CONTROLES FINAIS                          │
│  [Levantamento] [Gerar Lista] [Limpar Tudo]                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Funcionalidades Específicas

### 4.1 Localização (Obrigatória)

#### Estado (UF)
- **Tipo:** Select obrigatório
- **Valores:** Lista completa de UFs brasileiras
- **Comportamento:** Ao selecionar, carrega cidades disponíveis
- **Validação:** Campo obrigatório, destacado em vermelho se vazio

#### Cidade
- **Tipo:** Select múltiplo ou textarea
- **Fonte:** Carregadas dinamicamente via API IBGE/OpenStreetMap
- **Formato:** Uma cidade por linha
- **Busca:** Campo de busca para facilitar seleção
- **Validação:** Pelo menos uma cidade se UF selecionada

#### Bairro
- **Tipo:** Select múltiplo inteligente
- **Fonte:** API bairros baseada nas cidades selecionadas
- **Interface:** Busca com autocomplete + rankings
- **Seleção:** Múltipla com tags visuais
- **Limpeza:** Botão X para remover individualmente

### 4.2 Características

#### Gênero
- **Tipo:** Radio buttons (Ambos/Feminino/Masculino)
- **Padrão:** "Ambos" selecionado
- **Visual:** Ícones para masculino/feminino

#### Idade
- **Tipo:** Range slider duplo (mín/máx)
- **Valores:** 18-120 anos
- **Padrão:** 18-70 anos
- **Visual:** Labels mostrando valores atuais

#### Profissão
- **Tipo:** Checkbox múltiplo
- **Fonte:** Categorias CBO agrupadas
- **Grupos:** Gerencial, Comercial, Técnico, Serviços, etc.
- **Seleção:** Múltipla independente
- **Visual:** Árvore expansível por categoria

### 4.3 Bairros Nobres

#### Lista Disponível
- **Tipo:** Checkbox list
- **Fonte:** Bairros classificados por renda média
- **Formato:** "Nome do Bairro (R$ XX.000+)"
- **Ordenação:** Por renda decrescente
- **Seleção:** Independente, quantos desejar

#### Comportamento
- **Selecionado:** Filtrar apenas por bairros marcados
- **Nenhum selecionado:** Não aplicar filtro de bairro nobre
- **Visual:** Destaque visual para bairros selecionados

### 4.4 Contato

#### Tipo de Telefone
- **Tipo:** Radio buttons
- **Opções:** Móvel, Fixo, Ambos
- **Padrão:** Móvel
- **Visual:** Ícones para cada tipo

#### Email
- **Tipo:** Checkbox simples
- **Label:** "Obrigatório (só registros com email)"
- **Comportamento:** Quando marcado, remove registros sem email

### 4.5 Quantidade e Distribuição

#### Lógica Geral
O sistema deve suportar **distribuição proporcional** ou **absoluta** por diferentes dimensões, com **bônus automático de 10%** mantendo a proporção exata.

- **Quantidade absoluta geral** + **distribuição proporcional** por localidade
- **Quantidade absoluta geral** + **distribuição proporcional** por gênero
- **Quantidade absoluta geral** + **distribuição proporcional** por profissão
- **Combinações** dessas distribuições
- **Bônus automático:** +10% mantendo proporção exata

#### Interface de Quantidade

```
┌─────────────────────────────────────────────────────────────┐
│                   SEÇÃO: QUANTIDADE                          │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                    │
│  │ Quantidade Total│  │   Distribuição  │                    │
│  │   (Solicitada)  │  │     (Tipo)      │                    │
│  │     [5.000]     │  │   [Por Local]   │                    │
│  └─────────────────┘  └─────────────────┘                    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐     │
│  │                TOTAL COM BÔNUS                       │     │
│  │                                                     │     │
│  │ 🎁 Bônus automático: +10%                           │     │
│  │ Total final: 5.500 registros                        │     │
│  │                                                     │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐     │
│  │           DISTRIBUIÇÃO POR LOCALIDADE               │     │
│  │  (Mantém proporção exata no bônus)                 │     │
│  │ ☑ Por Cidade:                                      │     │
│  │   São Paulo: 40% (2.200)   Campinas: 30% (1.650)   │     │
│  │   Santos: 30% (1.650)                              │     │
│  │                                                     │     │
│  │ ☑ Por Bairro:                                      │     │
│  │   Centro: 25% (1.375)   Jardins: 20% (1.100)       │     │
│  │                                                     │     │
│  └─────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

#### Campos Específicos

##### Quantidade Total
- **Tipo:** Number input obrigatório
- **Valores:** 1-50.000
- **Função:** Define o total absoluto de registros desejado
- **Validação:** Campo obrigatório

##### Tipo de Distribuição
- **Tipo:** Select dropdown
- **Opções:**
  - "Nenhuma distribuição (total aleatório)"
  - "Por localidade (cidade/bairro/estado)"
  - "Por gênero (homens/mulheres)"
  - "Por profissão (categorias CBO)"
  - "Múltipla (local + gênero + profissão)"

##### Distribuição por Localidade
- **Tipo:** Checkbox + inputs dinâmicos
- **Opções:**
  - ☐ **Por Cidade:** Campos porcentagem para cada cidade selecionada
  - ☐ **Por Bairro:** Campos porcentagem para cada bairro selecionado
  - ☐ **Por Estado:** Campos porcentagem para cada UF selecionada
- **Comportamento:** Só aparece se "Por localidade" selecionado
- **Validação:** Soma deve ser 100%

##### Distribuição por Gênero
- **Tipo:** Checkbox + inputs duplos
- **Campos:** Homens (%): [60]   Mulheres (%): [40]
- **Comportamento:** Só aparece se "Por gênero" selecionado
- **Validação:** Soma deve ser 100%

##### Distribuição por Profissão
- **Tipo:** Checkbox + inputs múltiplos
- **Fonte:** Categorias CBO selecionadas
- **Campos:** Um input % para cada categoria marcada
- **Comportamento:** Só aparece se "Por profissão" selecionado
- **Validação:** Soma deve ser 100%

---

## 5. Lógica de Distribuição

### 5.1 Princípios Gerais

A distribuição funciona em **camadas hierárquicas** com **bônus automático de 10%**:

1. **Quantidade Solicitada:** Define o objetivo principal do cliente
2. **Bônus Automático:** +10% calculado sobre a quantidade solicitada
3. **Total Final:** Solicitado + Bônus (mantém proporção exata)
4. **Distribuição Primária:** Divide por localidade (cidade/bairro/estado)
5. **Distribuição Secundária:** Dentro de cada localidade, divide por gênero
6. **Distribuição Terciária:** Dentro de cada combinação local+gênero, divide por profissão

### 5.2 Lógica do Bônus Proporcional

#### Cálculo Básico
```
Quantidade Solicitada: 5.000
Bônus: 10% = 500
Total Final: 5.500 registros
```

#### Distribuição com Bônus
```
Solicitado: 5.000
├── São Paulo: 40% (2.000)
├── Campinas: 30% (1.500)
└── Santos: 30% (1.500)

Bônus: +500 (10%)
├── São Paulo: 40% (200) → Total: 2.200
├── Campinas: 30% (150) → Total: 1.650
└── Santos: 30% (150) → Total: 1.650
```

#### Distribuição Hierárquica com Bônus
```
Solicitado: 10.000
Bônus: +1.000 (10%)
Total Final: 11.000

São Paulo (40% solicitado = 4.000 + 400 bônus = 4.400):
├── Homens (60% = 2.640):
│   ├── Gerencial: 20% (528)
│   ├── Comercial: 30% (792)
│   └── Técnico: 25% (660)
└── Mulheres (40% = 1.760):
    ├── Gerencial: 20% (352)
    ├── Comercial: 30% (528)
    └── Técnico: 25% (440)
```

### 5.2 Exemplos de Uso

#### Exemplo 1: Distribuição por Cidade
```
Total: 5.000 registros
Por Cidade:
- São Paulo: 40% (2.000 registros)
- Campinas: 30% (1.500 registros)  
- Santos: 30% (1.500 registros)
```

#### Exemplo 2: Distribuição por Gênero
```
Total: 5.000 registros
Por Gênero:
- Homens: 60% (3.000 registros)
- Mulheres: 40% (2.000 registros)
```

#### Exemplo 3: Distribuição Combinada
```
Total: 5.000 registros
Por Cidade:
- São Paulo: 40% (2.000) → Homens: 60% (1.200), Mulheres: 40% (800)
- Campinas: 30% (1.500) → Homens: 60% (900), Mulheres: 40% (600)
- Santos: 30% (1.500) → Homens: 60% (900), Mulheres: 40% (600)
```

#### Exemplo 4: Distribuição Completa
```
Total: 10.000 registros
Por Cidade + Gênero + Profissão:

São Paulo (40% = 4.000):
├── Homens (60% = 2.400):
│   ├── Gerencial: 20% (480)
│   ├── Comercial: 30% (720)
│   └── Técnico: 25% (600)
└── Mulheres (40% = 1.600):
    ├── Gerencial: 20% (320)
    ├── Comercial: 30% (480)
    └── Técnico: 25% (400)
```

### 5.3 Regras de Validação

#### Somas Percentuais
- **Cada nível deve somar 100%**
- **Validação em tempo real** com feedback visual
- **Ajuste automático** se soma > 100%

#### Bônus Proporcional
- **Bônus sempre 10%** sobre quantidade solicitada
- **Proporção exata mantida** em todas as distribuições
- **Cálculo automático** não editável pelo usuário
- **Arredondamento inteligente** para evitar frações

#### Dependências
- **Profissão só se gênero selecionado**
- **Gênero só se localidade selecionada**
- **Localidade pode ser independente**
- **Bônus sempre aplicado** independente da distribuição

#### Limites Mínimos
- **Mínimo por combinação:** 1 registro (solicitado + bônus)
- **Ajuste proporcional** se combinação resultaria em < 1
- **Bônus nunca reduz** quantidade solicitada

### 5.4 Interface Dinâmica

#### Campos Condicionais
- **Seleção de distribuição** mostra/esconde seções relevantes
- **Campos de porcentagem** aparecem dinamicamente
- **Validação visual** com cores (verde = válido, vermelho = inválido)

#### Preview da Distribuição
- **Tabela preview** mostrando quantidades por combinação
- **Atualização em tempo real** conforme mudanças
- **Alertas** para combinações que resultariam em zero registros

### 5.1 Campos Obrigatórios
- **Estado (UF):** Sempre obrigatório
- **Cidade:** Pelo menos uma se UF selecionada
- **Quantidade:** Sempre obrigatória

### 5.2 Dependências
- **Cidade depende de UF:** Lista só carrega após UF selecionada
- **Bairro depende de Cidade:** Só mostra bairros das cidades selecionadas
- **Bairros Nobres:** Independente, mas só aplicável se bairros normais não selecionados

### 5.3 Limites
- **Máximo de cidades:** 50 por UF
- **Máximo de bairros:** 100 por cidade
- **Máximo de registros:** 50.000 absoluto
- **Mínimo de registros:** 1

---

## 6. Fluxo de Uso

### 6.1 Fluxo Básico Atualizado
1. **Selecionar UF** (obrigatório)
2. **Escolher cidades** (carregadas automaticamente)
3. **Selecionar bairros** (opcional, com busca)
4. **Definir características** (gênero, idade, profissão)
5. **Escolher bairros nobres** (opcional)
6. **Configurar contato** (telefone, email)
7. **Definir quantidade total** (absoluta obrigatória)
8. **Configurar distribuição** (opcional: por local, gênero, profissão)
9. **Fazer levantamento** (verificar distribuição resultante)
10. **Gerar lista** (download automático com distribuição aplicada)

### 6.2 Levantamento
- **Botão:** "Fazer Levantamento"
- **Resultado:** Mostra contagem exata baseada nos filtros
- **Formato:** "X registros encontrados"
- **Ação:** Habilita/desabilita botão "Gerar Lista"

### 6.3 Geração
- **Botão:** "Gerar Lista Completa"
- **Feedback:** Progress bar ou spinner
- **Resultado:** Download automático do Excel
- **Confirmação:** Notificação de sucesso

---

## 7. Estados da Interface

### 7.1 Estados de Carregamento
- **Carregando cidades:** Spinner no select de cidade
- **Carregando bairros:** Spinner na lista de bairros
- **Processando levantamento:** Spinner no botão
- **Gerando lista:** Progress bar

### 7.2 Estados de Erro
- **UF não selecionada:** Destaque vermelho + tooltip
- **Cidade não carregou:** Mensagem de erro + retry
- **Levantamento falhou:** Alert vermelho
- **Geração falhou:** Alert vermelho + detalhes

### 7.3 Estados de Distribuição

#### Estados de Validação
- **Distribuição válida:** Badge verde "100% ✓"
- **Distribuição incompleta:** Badge amarelo "85% ⚠️"
- **Distribuição inválida:** Badge vermelho "110% ❌"

#### Preview da Distribuição
- **Tabela dinâmica** mostrando quantidades por combinação
- **Hierarquia visual:** Localidade → Gênero → Profissão
- **Cálculo em tempo real** conforme mudanças nos percentuais
- **Bônus destacado** em cor diferente (verde para bônus)
- **Totais por nível** sempre visíveis
- **Alertas visuais** para combinações que resultariam em zero

#### Estados de Carregamento
- **Calculando distribuição:** Spinner durante preview
- **Aplicando filtros:** Progress durante levantamento
- **Gerando com distribuição:** Progress bar mostrando avanço por combinação

---

## 8. Acessibilidade

### 8.1 Navegação por Teclado
- **Tab order:** Lógico e completo
- **Enter/Space:** Ativa botões e checkboxes
- **Arrow keys:** Navega selects e radios
- **Escape:** Fecha modais ou cancela

### 8.2 Leitores de Tela
- **Labels:** Todos os campos têm labels descritivos
- **ARIA:** Atributos apropriados para estado dinâmico
- **Anúncios:** Mudanças de estado anunciadas
- **Hierarquia:** Headings estruturados (H1-H3)

### 8.3 Contraste e Visual
- **Contraste:** Mínimo 4.5:1 para texto normal
- **Foco:** Indicador visível em todos os elementos
- **Tamanhos:** Texto legível (mínimo 14px)
- **Cores:** Não usar cor como única forma de informação

---

## 9. Responsividade

### 9.1 Breakpoints
- **Desktop:** > 1200px - Layout completo lado a lado
- **Tablet:** 768-1199px - Colunas empilhadas
- **Mobile:** < 768px - Campos empilhados, controles touch-friendly

### 9.2 Adaptação Touch
- **Botões grandes:** Mínimo 44px touch target
- **Espaçamento:** Campos não muito próximos
- **Seleção fácil:** Radios e checkboxes de tamanho adequado

---

## 10. Métricas de Sucesso

### 10.1 Usabilidade
- **Tempo para configuração básica:** < 2 minutos
- **Tempo para configuração com distribuição:** < 5 minutos
- **Taxa de erro na distribuição:** < 3% (validações impedem erros comuns)
- **Precisão da distribuição:** ±1% do solicitado
- **Valor percebido do bônus:** +10% automático aumenta satisfação
- **Satisfação:** > 4.5/5 em testes de usuário

### 10.2 Performance
- **Carregamento inicial:** < 3 segundos
- **Carregamento de cidades:** < 2 segundos
- **Levantamento:** < 10 segundos para 100k registros
- **Geração:** < 30 segundos para 10k registros

### 10.3 Benefícios do Bônus Automático

#### Valor Percebido
- **Cliente recebe mais** sem custo adicional
- **Proporção mantida** = distribuição perfeita
- **Surpresa positiva** aumenta satisfação
- **Diferencial competitivo** no mercado

#### Aspectos Técnicos
- **Cálculo transparente** sempre 10% sobre solicitado
- **Arredondamento inteligente** evita registros fracionados
- **Aplicado automaticamente** não requer configuração
- **Documentado claramente** no relatório final</content>
<parameter name="filePath">c:\Users\marti\Desktop\Projeto Listas\docs\requisitos-usabilidade.md