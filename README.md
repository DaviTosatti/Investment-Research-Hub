# Investment Research Hub

Plataforma privada para um grupo aprender, pesquisar e acompanhar investimentos.
**Etapa 1 em implementação.** A fundação permite acesso individual, titulares
econômicos separados, carteiras, registro de operações, posições e caixa derivados,
avaliações manuais, painel e exportação CSV. As Etapas 2 e 3 ainda não começaram.

[Progresso](docs/STATUS.md) · [Plano em três etapas](docs/IMPLEMENTATION_PLAN.md) ·
[Matriz de requisitos](docs/REQUIREMENTS_MATRIX.md) · [Continuidade](docs/HANDOFF.md) ·
[Referências visuais](docs/VISUAL_REFERENCES.md) · [Padrão de commits](CONTRIBUTING.md) ·
[PR da fundação](https://github.com/DaviTosatti/Investment-Research-Hub/pull/1)

## Executar localmente

Caminho principal: Linux ou WSL2, Docker Compose, Python 3.12, uv 0.13.4,
Node.js 24.22.1 e npm 11.9.0. Dependências Python e web têm lockfiles.

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

Se os comandos forem executados no ambiente remoto do Codex, `localhost` aponta
para aquela máquina, não para o computador do usuário. Nesse caso, o acesso exige
o navegador compartilhado do ambiente ou um encaminhamento nativo de porta
efetivamente configurado. Uma resposta HTTP interna ou uma abertura de aba com
estado `queued` não comprovam acesso pelo usuário. Não há URL pública publicada.

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

Com PostgreSQL iniciado e dependências instaladas:

```bash
bash scripts/check.sh
```

Os testes de integração criam um banco temporário exclusivo e o removem ao
final; o usuário local do PostgreSQL precisa de permissão para criar banco.
Eles não limpam o banco configurado da aplicação. Consulte STATUS para resultados
executados e limites de revisão visual.

Para instalar uma atualização revisada, preserve `.env` e o volume do banco,
faça backup PostgreSQL antes da migração, atualize o código, execute
`uv sync --locked`, `npm ci --prefix apps/web`, `uv run alembic upgrade head` e
reinicie API/frontend. Não use `docker compose down -v` para atualizar.
Restauração completa e operação supervisionada ainda são critérios pendentes
da Etapa 1; a validação deste incremento usa bases de teste descartáveis.

## Estrutura

| Caminho | Responsabilidade |
| --- | --- |
| `apps/web` | Next.js, React, TypeScript e identidade fintech própria |
| `apps/api` | FastAPI, sessões, autorização, PostgreSQL e migrações |
| `packages/engines` | Motor Python canônico com Decimal |
| `tests` | Domínio, invariantes e integração real com PostgreSQL |
| `docs` | Escopo integral, contratos, decisões, evidências e pendências |

O anexo original é preservado byte a byte em [Promptx.txt](docs/reference/Promptx.txt).
Sua presença mantém o escopo de 23 skills e 23 páginas, sem alegar que já existem.

## English

Private shared investment research platform. Stage 1 is in progress; Stages 2
and 3 have not started. The first slice includes individual sessions and roles,
separate economic owners, BRL portfolios, an exact immutable event ledger,
manual valuations, a dashboard and CSV exports. No brokerage orders are sent.

Use the Linux/WSL2 setup above, create an administrator through the hidden password
prompt, then run the API and Next.js separately. The UI supports Portuguese and
English. Cost history is not investment performance; missing valuations remain
missing. See STATUS for verification and remaining Stage 1 requirements.
