# Investment Research Hub

<div align="center">

![Investment Research Hub](https://img.shields.io/badge/Status-Etapa%201%20em%20Implementa%C3%A7%C3%A3o-0072bc?style=for-the-badge)
![Licença Proprietária](https://img.shields.io/badge/Licen%C3%A7a-Propriet%C3%A1ria%20%7C%20Todos%20os%20Direitos%20Reservados-red?style=for-the-badge)
![Arquitetura](https://img.shields.io/badge/Arquitetura-ICM%20%7C%20Mon%C3%B3lito%20Modular-001c30?style=for-the-badge)

**Plataforma institucional de inteligência, análise fundamentalista e acompanhamento contábil-financeiro de carteiras de investimentos (ações, FIIs, renda fixa e ETFs).**

[Progresso](docs/STATUS.md) · [Plano em 3 Etapas](docs/IMPLEMENTATION_PLAN.md) · [Matriz de Requisitos](docs/REQUIREMENTS_MATRIX.md) · [Metodologia ICM](docs/metodologia-contexto.md) · [Windows Nativo](docs/WINDOWS.md) · [Referências Visuais](docs/VISUAL_REFERENCES.md) · [Contratos da API](docs/API_CONTRACT.md) · [Importar CSV/XLSX](docs/IMPORTS.md)

</div>

Para compartilhar o contexto com colegas ou outro GPT, envie
[Contexto para colaboradores e normas de PR](docs/CONTEXTO_PARA_COLABORADORES.md).
O documento distingue a implementação atual do plano das três etapas e orienta
branches, validação e aprovação por DaviTosatti.

---

## 🔒 Propriedade Intelectual e Licença

> ### ⚠️ AVISO DE DIREITOS AUTORAIS E LICENÇA RESTRITA
> **Copyright © 2026 Investment Research Hub. Todos os direitos reservados.**
>
> Este software, código-fonte, arquitetura de sistemas, algoritmos contábeis, documentação e identidade visual constituem **propriedade intelectual exclusivamente privada e confidencial**.
>
> - **Proibição Total de Cópia e Reprodução:** É estritamente vedada a cópia, clonagem, distribuição, sublicenciamento, engenharia reversa, descompilação, espelhamento público ou comercialização total ou parcial deste código sem autorização expressa, prévia e formal por escrito dos detentores dos direitos.
> - **Uso Restrito e Fechado:** O repositório é estritamente privado, destinado unicamente aos membros e titulares autorizados do grupo.
> - **Proteção Legal:** Quaisquer violações, reproduções não autorizadas ou apropriações indevidas estarão sujeitas às penalidades civis e criminais cabíveis conforme as legislações de proteção de propriedade intelectual e direitos autorais.

---

## 📌 Visão Geral do Produto

O **Investment Research Hub** foi projetado para operar com rigor institucional, integridade contábil e profundidade analítica:

- **Contabilidade em Partidas Dobradas:** Operações registradas como fatos imutáveis com precisão `Decimal` estrita (sem arredondamentos de `float`).
- **Isolamento por Titularidade Econômica:** Separação contábil clara entre titulares e contas, sem misturar patrimônios individuais.
- **Identidade Fintech Escura:** Experiência visual refinada e profissional, projetada para longas sessões de análise e em conformidade com as referências visuais aprovadas.
- **Arquitetura ICM (Menos Agentes, Mais Contexto):** Organização orientada a pastas com arquivos de contexto `CONTEXT.md` (Layers 0 a 5), permitindo que desenvolvedores e agentes operem com contexto delimitado e invariantes protegidas.
- **Plano Fiel de Três Etapas:**
  1. *Etapa 1 (Ativa):* Fundação, experiência visual, contabilidade e acompanhamento (12 páginas-base e 7 skills iniciais).
  2. *Etapa 2 (Planejada):* Análise avançada, valuation, risco, Monte Carlo, otimização e classes de ativos (9 páginas e 12 skills).
  3. *Etapa 3 (Planejada):* Comitê de IA com especialistas independentes, auditoria, alertas e operação supervisionada.

---

## 🚀 Como Executar

### 💻 Opção 1: Windows 10/11 x64 (Caminho Nativo Recomendado)

O porte nativo do Windows foi construído para operação sem necessidade de WSL, Docker ou privilégios de administrador.

1. **Obtenha o repositório:**
   - Faça o clone do repositório ou baixe o ZIP oficial através de uma conta autorizada.
2. **Inicie o Hub:**
   - Dê duplo clique em **`Iniciar Hub.cmd`**.
   - Na primeira execução, o iniciador baixa e configura automaticamente em `%LOCALAPPDATA%` os runtimes portáteis com hashes SHA-256 verificados (uv, Python 3.12, Node.js e PostgreSQL 17).
3. **Crie o primeiro Administrador:**
   - O console solicitará o e-mail, nome e senha de acesso do administrador mestre (mínimo de 12 caracteres).
4. **Acesse a Aplicação:**
   - O navegador abrirá automaticamente em **`http://127.0.0.1:8766`**.
5. **Encerramento:**
   - Dê duplo clique em **`Parar Hub.cmd`** para interromper ordenadamente todos os processos mantendo os dados preservados.
6. **Diagnóstico:**
   - Use **`Verificar Hub.cmd`** para auditar a integridade da instalação.

---

### 🐧 Opção 2: Linux com Docker (Ambiente de Desenvolvimento)

Para ambientes Linux baseados em containers e ferramentas POSIX:

```bash
# 1. Clone e acerte a branch
git clone https://github.com/DaviTosatti/Investment-Research-Hub.git
cd Investment-Research-Hub
git switch codex/etapa-1-fundacao

# 2. Inicialize o ambiente e o banco de dados
bash scripts/bootstrap.sh

# 3. Crie o primeiro usuário administrador
uv run python -m hub_api.cli create-admin --email voce@example.com --name 'Seu Nome'

# 4. Inicie o servidor da API (Terminal 1)
uv run uvicorn hub_api.main:app --host 127.0.0.1 --port 8000

# 5. Inicie o frontend Next.js (Terminal 2)
npm --prefix apps/web run dev
```

Abra **`http://localhost:3000`** no navegador e autentique-se com a conta configurada.

---

## 🧭 Primeiro Fluxo Operacional

1. **Carteiras (`/carteiras`):** Cadastre um titular econômico e crie uma carteira associada à conta de custódia.
2. **Operações (`/operacoes`):** Registre um aporte em dinheiro, cadastre um ativo (B3) e lance a compra já realizada informando preço e taxas reais do extrato.
3. **Dados (`/dados`):** Registre uma cotação de fechamento manual com data e fonte para habilitar o cálculo de valor de mercado e resultado não realizado.
4. **Início (`/inicio`):** Filtre por titular e carteira; examine posições consolidadas, caixa e exporte o relatório oficial em CSV.
5. **Administração (`/administracao`):** Cadastre os demais membros do grupo com permissões apropriadas (`member` ou `viewer`). Todas as mutações alimentam a trilha imutável de auditoria.

> *Nota: O sistema registra fatos econômicos passados; ele **nunca envia ordens** para corretoras ou exchanges.*

---

## 🏛️ Estrutura do Repositório (Arquitetura ICM)

Cada diretório do monólito modular contém seu próprio arquivo `CONTEXT.md` com objetivo (Goal), checklist real do que existe, contratos I/O, invariantes e roadmap por etapas:

```
Investment-Research-Hub/
├── CONTEXT.md               # [Layer 1] Mapa de contexto e governança da raiz
├── AGENTS.md                # [Layer 0] Regras invioláveis para modelos de IA
├── CLAUDE.md                # Apontador para regras unificadas
├── CONTRIBUTING.md          # Padrão de Conventional Commits e fluxo de PR
├── Iniciar Hub.cmd          # Atalho Windows para inicialização em 1 clique
├── Parar Hub.cmd            # Atalho Windows para parada limpa de processos
├── Verificar Hub.cmd        # Atalho Windows para diagnóstico e saúde
│
├── apps/                    # [Layer 1] Processos e servidores executáveis
│   ├── CONTEXT.md
│   ├── api/                 # Backend FastAPI, SQLAlchemy 2.0, PostgreSQL
│   │   └── CONTEXT.md       # Contrato de rotas /api/v1, regras de auditoria e modelos
│   └── web/                 # Frontend Next.js 15, Tailwind CSS, TypeScript
│       └── CONTEXT.md       # Componentes fintech escuros, tipos e acessibilidade
│
├── packages/                # [Layer 1] Pacotes reutilizáveis em memória
│   ├── CONTEXT.md
│   └── engines/             # Motor financeiro institucional (hub_finance)
│       └── CONTEXT.md       # Ledger contábil, precisão Decimal estrita e fórmulas
│
├── tests/                   # [Layer 5] Baterias de testes e auditoria
│   ├── CONTEXT.md           # Regras dos testes unitários, integração e Hypothesis
│   ├── unit/                # Testes contábeis puros e testes adversariais
│   ├── integration/         # Testes ponta a ponta com PostgreSQL real
│   └── windows/             # Testes de integridade da execução nativa Windows
│
├── scripts/                 # Automação de ambiente e runtimes portáteis
│   ├── CONTEXT.md
│   ├── bootstrap.sh         # Inicialização para Linux
│   ├── check.sh             # Pipeline local de verificação
│   ├── sync_agent_skills.py # Sincronizador multi-LLM (.agents -> .claude)
│   └── windows/             # Manifesto downloads.json e orquestrador de runtimes
│
├── docs/                    # Especificação, arquitetura e planejamento
│   ├── CONTEXT.md
│   ├── IMPLEMENTATION_PLAN.md # Plano oficial de três etapas
│   ├── REQUIREMENTS_MATRIX.md # Matriz com as 23 skills de negócio e 23 páginas
│   ├── STATUS.md            # Registro vivo de entregas e evidências comprovadas
│   ├── API_CONTRACT.md      # Especificação completa dos endpoints e payloads
│   ├── VISUAL_REFERENCES.md # Guia estético do tema fintech escuro
│   └── metodologia-contexto.md # Princípios da arquitetura ICM
│
└── .agents/                 # Governança de skills de engenharia multi-LLM
    ├── CONTEXT.md
    ├── skills/              # 26 skills canônicas (TDD, Code Review, Security, REA...)
    └── references/          # Checklists técnicos de qualidade e validação
```

---

## 🧪 Verificação de Qualidade

Para auditar o código e garantir que nenhum invariante foi violado:

```bash
# Verificar formatação e linter Python
uv run ruff check .

# Verificar tipagem estrita
uv run mypy packages/engines/src apps/api/src

# Executar bateria de testes unitários e de integração
uv run pytest tests/unit tests/integration -v

# Validar sincronismo e hashes das skills multi-LLM
uv run python scripts/sync_agent_skills.py --check

# Verificar frontend Next.js (dentro de apps/web)
npm run typecheck && npm run lint && npm run test && npm run build
```

---

<div align="center">

**Investment Research Hub** · Plataforma Privada & Confidencial · 2026

</div>
