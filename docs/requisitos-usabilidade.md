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

### 4.5 Quantidade

#### Tipo de Limite
- **Tipo:** Radio buttons
- **Opções:** 
  - "Quantidade absoluta (número exato)"
  - "Porcentagem do total filtrado"

#### Valor
- **Tipo:** Number input
- **Validação:** 
  - Absoluto: 1-50.000
  - Porcentagem: 1-100%
- **Formato:** Inteiro para absoluto, decimal para porcentagem

---

## 5. Regras de Validação

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

### 6.1 Fluxo Básico
1. **Selecionar UF** (obrigatório)
2. **Escolher cidades** (carregadas automaticamente)
3. **Selecionar bairros** (opcional, com busca)
4. **Definir características** (gênero, idade, profissão)
5. **Escolher bairros nobres** (opcional)
6. **Configurar contato** (telefone, email)
7. **Definir quantidade** (absoluta ou porcentagem)
8. **Fazer levantamento** (verificar contagem)
9. **Gerar lista** (download automático)

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

### 7.3 Estados de Sucesso
- **Levantamento OK:** Badge verde com contagem
- **Geração OK:** Download automático + toast verde
- **Lista pronta:** Link para download adicional

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
- **Taxa de erro:** < 5% em configurações válidas
- **Satisfação:** > 4.5/5 em testes de usuário

### 10.2 Performance
- **Carregamento inicial:** < 3 segundos
- **Carregamento de cidades:** < 2 segundos
- **Levantamento:** < 10 segundos para 100k registros
- **Geração:** < 30 segundos para 10k registros

### 10.3 Acessibilidade
- **WCAG 2.1 AA:** 100% conformidade
- **Navegação por teclado:** 100% funcional
- **Leitores de tela:** 100% compatível</content>
<parameter name="filePath">c:\Users\marti\Desktop\Projeto Listas\docs\requisitos-usabilidade.md