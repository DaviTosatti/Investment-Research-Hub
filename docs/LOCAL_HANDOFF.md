# Abrir o Hub no computador do usuário

## Caminho de execução

O acesso no computador do usuário passa pelo **porte Windows nativo portátil**,
validado em CI. A pessoa baixa o ZIP, extrai tudo e abre **Iniciar Hub.cmd**.
Esse fluxo dispensa Linux, WSL, Docker, Git, privilégios de administrador e
serviços globais. Não depende de trocar de conversa, reconectar chats ou abrir
um chat associado a um executor local.

A Etapa 1 continua parcial; as Etapas 2 e 3 não começaram. A retomada de acesso
não altera as [três etapas do plano](IMPLEMENTATION_PLAN.md) nem declara uma
skill completa. A [execução Windows aprovada](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42145542854)
e sua cobertura estão descritas em [WINDOWS.md](WINDOWS.md).

Fonte: [DaviTosatti/Investment-Research-Hub](https://github.com/DaviTosatti/Investment-Research-Hub).
Branch de trabalho:
[`codex/etapa-1-fundacao`](https://github.com/DaviTosatti/Investment-Research-Hub/tree/codex/etapa-1-fundacao).
[PR da fundação](https://github.com/DaviTosatti/Investment-Research-Hub/pull/1).

## Procedimento para quem vai usar

1. Entre no GitHub com uma conta autorizada ao repositório privado. Baixe o ZIP
   do [artefato Windows validado](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42145542854/artifacts/13469499679), ou use
   **Code → Download ZIP** na branch indicada acima.
2. Use **Extrair Tudo** no Explorador de Arquivos. Preserve qualquer pasta
   existente com arquivos próprios; uma nova extração pode ficar em outra pasta.
   Abra a pasta que contém os três iniciadores `.cmd`, com todas as subpastas.
3. Dê duplo clique em **Iniciar Hub.cmd** no Windows 10/11 x64. Na primeira
   preparação, mantenha a internet disponível e aguarde cerca de 400 MB de
   runtimes, além do Python e dos pacotes.
4. Se ainda não houver administrador, informe e-mail, nome e uma senha de pelo
   menos 12 caracteres, oculta durante a digitação. Não existe senha padrão.
   Contas e configurações de uma instalação existente são preservadas.
5. Mantenha a janela aberta. O navegador abre depois das verificações HTTP de
   saúde, em **http://127.0.0.1:8766**. Entre com sua conta e siga o
   [primeiro fluxo do README](../README.md#primeiro-fluxo).
6. Ao terminar, dê duplo clique em **Parar Hub.cmd** e aguarde o encerramento
   apenas da execução gerenciada. Fechar diretamente a janela pode
   interromper o runtime. Não há inicialização automática com o Windows.
7. Se precisar de diagnóstico de uma instalação preparada, use
   **Verificar Hub.cmd** e as orientações de [WINDOWS.md](WINDOWS.md).

O [LEIA-ME-WINDOWS.txt](../LEIA-ME-WINDOWS.txt) acompanha o ZIP na raiz. O
[guia Windows](WINDOWS.md) detalha arquivos, endereços e atualização.

## Contrato técnico para a integração

- Windows PowerShell 5.1 coordena uv 0.13.4, Python 3.12.14, Node.js 24.22.1 e
  PostgreSQL 17.6 portáteis, com bibliotecas Microsoft VC++ app-local.
  Os downloads de runtime usam HTTPS e SHA-256 fixado no manifesto; as
  dependências Python e web têm lockfiles.
- Runtimes em `%LOCALAPPDATA%\InvestmentResearchHub\runtime`. Banco,
  configuração e logs em `%LOCALAPPDATA%\InvestmentResearchHub\data`, por
  usuário do Windows e fora do ZIP/repositório. A configuração existente deve
  ser preservada, sem sobrescrever valores nem redefinir credenciais.
- `.venv-windows` e `apps\web\node_modules` ficam na pasta extraída. O ZIP
  contém a aplicação; os dados do usuário permanecem na pasta persistente.
- API em `127.0.0.1:8765`, interface em `127.0.0.1:8766` e PostgreSQL em
  `127.0.0.1:54329`, todos somente em loopback. O navegador abre após a saúde
  HTTP; a parada deve respeitar os processos gerenciados.

Ao atualizar, encerre com **Parar Hub.cmd**, confirme que o banco parou, faça
uma cópia completa da pasta `data` e extraia o novo ZIP em uma pasta separada.
Abra a nova cópia com o mesmo usuário Windows para reutilizar os dados e a
configuração. A restauração completa ainda exige validação da Etapa 1.

## Evidências registradas

A execução `42145542854`, commit `4d1ddaf`, passou em **`windows-2022`** com
Windows PowerShell 5.1. Cobriu instalação limpa em caminho com espaços e acentos,
123 testes Python, 24 web, verificação funcional da API/frontend, persistência,
reinício, parada e criação do artefato ZIP. [STATUS](STATUS.md) registra os links.

Mantenha separadas as evidências de CI, saúde HTTP e uso no navegador do usuário.
Uma resposta HTTP não comprova homologação visual. Não prometer executável
assinado ou instalador de binário único. Nenhum dado ou segredo do usuário deve
ser incluído no artefato ou nos registros de validação.

## Contexto do acesso anterior

A tentativa remota anterior respondeu por HTTP, mas a prévia do ambiente não
entregou acesso ao navegador do usuário. Essa limitação consta no histórico;
o procedimento atual usa a aplicação executada no próprio Windows. Os endereços
locais deste documento passam a apontar para essa execução no computador do
usuário. Não há URL pública de implantação.

## English summary

Use the portable native Windows flow: download the private branch ZIP or a
published Windows artifact, extract it fully and double-click `Iniciar Hub.cmd`.
No WSL, Docker, Git, admin rights or local chat is needed. Keep the console open,
use `Parar Hub.cmd` to stop and `Verificar Hub.cmd` for installed-runtime
diagnostics. Preserve per-user data/configuration under `%LOCALAPPDATA%`.
Native Windows CI passed; Stage 1 remains partial within the three-stage
plan.
