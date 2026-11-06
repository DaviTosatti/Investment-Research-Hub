# Investment Research Hub

Plataforma privada para um grupo aprender, pesquisar e acompanhar investimentos.
**Etapa 1 em implementação.** A fundação permite acesso individual, titulares
econômicos separados, carteiras, registro de operações, posições e caixa derivados,
avaliações manuais, painel e exportação CSV. As Etapas 2 e 3 ainda não começaram.

[Progresso](docs/STATUS.md) · [Plano em três etapas](docs/IMPLEMENTATION_PLAN.md) ·
[Matriz de requisitos](docs/REQUIREMENTS_MATRIX.md) · [Continuidade](docs/HANDOFF.md) ·
[Windows nativo](docs/WINDOWS.md) · [Execução no seu computador](docs/LOCAL_HANDOFF.md) ·
[Referências visuais](docs/VISUAL_REFERENCES.md) · [Padrão de commits](CONTRIBUTING.md) ·
[PR da fundação](https://github.com/DaviTosatti/Investment-Research-Hub/pull/1)

## Windows 10/11 x64 — caminho principal

O porte Windows nativo está disponível. O fluxo usa duplo clique e
componentes portáteis, sem Linux, WSL, Docker, Git, privilégios de administrador
ou serviços globais. Não é necessário abrir outro chat ou conectar um executor
local. A instalação e o uso passaram no
[CI Windows](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42142399687);
consulte [STATUS](docs/STATUS.md) para a cobertura e os limites.

1. [Baixe o ZIP Windows validado](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42142399687/artifacts/13468401568)
   ou abra a
   [branch `codex/etapa-1-fundacao`](https://github.com/DaviTosatti/Investment-Research-Hub/tree/codex/etapa-1-fundacao)
   e escolha **Code → Download ZIP**. O repositório é privado: entre no GitHub com
   uma conta que tenha acesso.
2. No Explorador de Arquivos, use **Extrair Tudo**. Abra a pasta extraída que contém
   este README e `Iniciar Hub.cmd`; mantenha todos os arquivos e subpastas juntos.
3. Dê duplo clique em **Iniciar Hub.cmd**. Na primeira vez, mantenha a internet
   disponível: são cerca de 400 MB de runtimes, além do Python e dos pacotes.
   Aguarde os downloads, a preparação do banco e da aplicação.
4. Quando solicitado, informe e-mail, nome e uma senha de pelo menos 12 caracteres
   para o primeiro administrador. A senha fica oculta durante a digitação;
   não existe senha padrão. Instalações existentes mantêm contas e configuração.
5. Mantenha a janela do iniciador aberta. O navegador abre após as verificações
   HTTP de saúde em **http://127.0.0.1:8766**. Entre com a conta criada.
6. Para encerrar, dê duplo clique em **Parar Hub.cmd** e aguarde. Ele encerra
   apenas os processos da execução gerenciada pelo Hub e preserva o banco.

O iniciador usa Windows PowerShell 5.1 e prepara uv 0.13.4, Python 3.12.14,
Node.js 24.22.1, PostgreSQL 17.6 e bibliotecas Microsoft VC++ junto à aplicação.
Os downloads de runtime usam HTTPS e verificação SHA-256 fixada no manifesto.
As dependências Python e web têm lockfiles.

Os runtimes ficam em `%LOCALAPPDATA%\InvestmentResearchHub\runtime`; banco,
configuração e logs ficam em `%LOCALAPPDATA%\InvestmentResearchHub\data`, por
usuário do Windows e fora do ZIP/repositório. A pasta extraída recebe
`.venv-windows` e `apps\web\node_modules`. O iniciador preserva os dados e a
configuração existentes. API `127.0.0.1:8765`, interface `127.0.0.1:8766` e
PostgreSQL `127.0.0.1:54329` atendem somente neste computador.

**Verificar Hub.cmd** diagnostica uma instalação já preparada. Fechar a janela
do iniciador pode interromper o runtime; use **Parar Hub.cmd**. O Hub não inicia
automaticamente com o Windows. Veja o [guia Windows](docs/WINDOWS.md) para
diagnóstico, atualização e limites de validação, ou o
[LEIA-ME-WINDOWS.txt](LEIA-ME-WINDOWS.txt) para os passos essenciais.

## Linux com Docker — alternativa de desenvolvimento

O fluxo existente para Linux usa Docker Compose, Python 3.12, uv 0.13.4,
Node.js 24.22.1 e npm 11.9.0.

```bash
git clone https://github.com/DaviTosatti/Investment-Research-Hub.git
cd Investment-Research-Hub
git switch codex/etapa-1-fundacao
bash scripts/bootstrap.sh
uv run python -m hub_api.cli create-admin --email voce@example.com --name 'Seu nome'
```

O comando solicita a senha sem exibi-la. Não há cadastro público, senha de
administrador padrão nem carga automática de dados fictícios. O bootstrap copia
`.env.example` se `.env` não existir e mantém o banco no volume `hub_postgres`.
O exemplo de senha do banco serve somente ao desenvolvimento local.

Execute em dois terminais, a partir da raiz:

```bash
uv run uvicorn hub_api.main:app --host 127.0.0.1 --port 8000
```

```bash
npm --prefix apps/web run dev
```

Abra `http://localhost:3000` e entre com o administrador criado. Use esse hostname
para coincidir com `HUB_PUBLIC_ORIGIN`. A interface encaminha `/api/v1` ao backend;
não é preciso abrir CORS. Para outra origem, ajuste `HUB_PUBLIC_ORIGIN` no backend
e `HUB_API_URL` no ambiente do Next.js ou em `apps/web/.env.local`.
Use `HUB_COOKIE_SECURE=true` para operação compartilhada por HTTPS.
O caminho de hospedagem compartilhada ainda não foi homologado.

Esses endereços e comandos se referem à máquina Linux onde os processos foram
iniciados. Para usar o Hub no Windows, siga o fluxo de duplo clique acima.

## Primeiro fluxo

1. Em **Carteiras**, cadastre um titular econômico e uma carteira com conta.
2. Em **Operações**, registre um aporte. Cadastre um ativo e registre a compra
   já realizada, incluindo taxas e tributos do documento original.
3. Em **Dados e auditoria**, cadastre uma avaliação manual com data e origem para
   visualizar valor de mercado.
4. Em **Início**, filtre por titular, carteira e data; confira posições, caixa,
   custos e qualidade das avaliações. Exporte o CSV da mesma seleção.
5. Em **Administração**, crie os demais usuários. Membros colaboram com os dados
   do grupo; leitores consultam. A autoria fica no histórico de auditoria.

Este fluxo registra fatos; não envia ordens a corretoras. O saldo usa data de
negociação, não liquidação. Eventos entram em ordem cronológica por carteira;
retificação/estorno, importação CSV/XLSX, transferências e câmbio serão concluídos
nos próximos blocos da Etapa 1. O histórico do painel é a custo, não uma série de
rentabilidade. TWR/MWR, provedores de mercado, IA e MCP ainda não estão integrados.
Nenhuma skill completa está declarada concluída.

## Verificar e atualizar

No Windows, use **Verificar Hub.cmd** para diagnóstico. Para atualizar, encerre
com **Parar Hub.cmd**, faça uma cópia de segurança dos dados com o banco parado
e extraia o novo ZIP em uma pasta separada. **Iniciar Hub.cmd**, executado pelo
mesmo usuário do Windows, reutiliza o banco e a configuração em `%LOCALAPPDATA%`.
Veja os detalhes e limites de recuperação em [WINDOWS.md](docs/WINDOWS.md).

No ambiente Linux/Docker, com PostgreSQL iniciado e dependências instaladas:

```bash
bash scripts/check.sh
```

Os testes de integração criam um banco temporário exclusivo e o removem ao
final; o usuário local do PostgreSQL precisa de permissão para criar banco.
Eles não limpam o banco configurado da aplicação. Consulte STATUS para resultados
executados e limites de revisão visual.

Para instalar uma atualização revisada no Linux, preserve `.env` e o volume do
banco, faça backup PostgreSQL antes da migração, atualize o código, execute
`uv sync --locked`, `npm ci --prefix apps/web`, `uv run alembic upgrade head` e
reinicie API/frontend. Não use `docker compose down -v` para atualizar.
Restauração completa e operação supervisionada ainda são critérios pendentes
da Etapa 1; os testes registrados em STATUS usam bases descartáveis.

## Estrutura

| Caminho | Responsabilidade |
| --- | --- |
| `apps/web` | Next.js, React, TypeScript e identidade fintech própria |
| `apps/api` | FastAPI, sessões, autorização, PostgreSQL e migrações |
| `packages/engines` | Motor Python canônico com Decimal |
| `scripts/windows` | Preparação e gerenciamento do runtime Windows portátil |
| `tests` | Domínio, invariantes e integração real com PostgreSQL |
| `docs` | Escopo integral, contratos, decisões, evidências e pendências |

O anexo original é preservado byte a byte em [Promptx.txt](docs/reference/Promptx.txt).
Sua presença mantém o escopo de 23 skills e 23 páginas, sem alegar que já existem.

## English

Private shared investment research platform. Stage 1 is in progress; Stages 2
and 3 have not started. The first slice includes individual sessions and roles,
separate economic owners, BRL portfolios, an exact immutable event ledger,
manual valuations, a dashboard and CSV exports. No brokerage orders are sent.

The primary setup targets native Windows 10/11 x64: extract the complete ZIP and
double-click `Iniciar Hub.cmd`. No WSL, Docker, Git, admin rights or local chat is
required. First use downloads portable runtimes and prompts for an administrator
with a hidden password of at least 12 characters. Keep the console open; use
`Parar Hub.cmd` to stop and `Verificar Hub.cmd` for installed-runtime diagnostics.
Data stays under the Windows user's `%LOCALAPPDATA%\InvestmentResearchHub\data`.
Native Windows CI passed installation, application suites and restart persistence.
Linux/Docker remains an alternative; see
[WINDOWS.md](docs/WINDOWS.md) and STATUS for details and evidence.
