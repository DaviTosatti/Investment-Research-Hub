# Executar no Windows nativo

O caminho principal usa **Windows 10 ou 11 x64**, Windows PowerShell 5.1 e
componentes portáteis. Você pode baixar a aplicação pelo navegador e iniciá-la
com duplo clique. Não exige Linux, WSL, Docker, Git, outro chat, privilégios de
administrador ou instalação de serviços globais.

O porte foi validado em Windows nativo pelo
[GitHub Actions](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42147690848).
A [Etapa 1 continua parcial](STATUS.md); as Etapas 2 e 3 não começaram. O
[plano mantém exatamente três etapas](IMPLEMENTATION_PLAN.md).

## 1. Baixar e extrair

Entre no GitHub com uma conta autorizada a acessar o repositório privado
[DaviTosatti/Investment-Research-Hub](https://github.com/DaviTosatti/Investment-Research-Hub).
Há duas formas de obter os arquivos:

- **Artefato Windows em ZIP:** [baixe o pacote validado](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42147690848/artifacts/13470653605).
  Os artefatos ficam disponíveis por 30 dias. Novas execuções aprovadas no
  [GitHub Actions](https://github.com/DaviTosatti/Investment-Research-Hub/actions/workflows/windows.yml)
  geram novos pacotes.
- **Download ZIP da branch:** abra
  [`codex/etapa-1-fundacao`](https://github.com/DaviTosatti/Investment-Research-Hub/tree/codex/etapa-1-fundacao)
  e escolha **Code → Download ZIP**. Esse caminho baixa a branch de trabalho;
  o download por si só não comprova aprovação do CI Windows.

No Explorador de Arquivos, clique com o botão direito no ZIP e escolha
**Extrair Tudo**. Abra a pasta extraída que contém `Iniciar Hub.cmd`,
`Parar Hub.cmd`, `Verificar Hub.cmd` e este projeto. Extraia o conteúdo inteiro:
os atalhos dependem dos arquivos e subpastas que os acompanham. Execute-os a
partir da pasta extraída, fora da visualização do ZIP.

Se já houver uma cópia do projeto com arquivos próprios, preserve-a e extraia o
novo ZIP em outra pasta. O download dispensa o uso de Git.

## 2. Iniciar pela primeira vez

1. Dê duplo clique em **Iniciar Hub.cmd**. A janela usa o Windows PowerShell 5.1
   incluído no Windows. Mantenha-a aberta.
2. Aguarde a preparação. Na primeira vez é necessária internet: o download dos
   runtimes soma cerca de **400 MB, além do Python e dos pacotes Python/web**.
   A duração depende da conexão e do computador.
3. Quando solicitado, informe seu **e-mail**, **nome** e uma **senha com pelo
   menos 12 caracteres** para o primeiro administrador. A digitação da senha
   fica oculta. Não há senha padrão nem credenciais de outro ambiente a copiar.
4. Aguarde as verificações HTTP de saúde. O navegador abre depois que a API e a
   interface respondem. Entre em **http://127.0.0.1:8766** com a conta criada.

O iniciador prepara o banco PostgreSQL, as dependências e a aplicação. Nas
próximas execuções, reutiliza o banco e a configuração do mesmo usuário Windows,
preservando os valores existentes e sem redefinir contas ou senhas.

Se o navegador não abrir automaticamente, confira primeiro a janela do iniciador.
Depois de ela confirmar que a aplicação está pronta, abra manualmente
**http://127.0.0.1:8766** no navegador do mesmo computador.

## 3. Usar, parar e abrir novamente

Mantenha a janela de **Iniciar Hub.cmd** aberta durante o uso. Fechá-la pode
interromper o runtime. Para encerrar, dê duplo clique em **Parar Hub.cmd** e
aguarde o encerramento da API, da interface e do PostgreSQL gerenciados.
O comando atua somente na execução gerenciada pelo Hub, preservando processos
de outros programas.

Para voltar a usar, dê duplo clique em **Iniciar Hub.cmd** na pasta extraída e
entre com a conta existente. O Hub não instala inicialização automática com o
Windows; você o abre quando quiser usar.

O [primeiro fluxo do README](../README.md#primeiro-fluxo) explica como cadastrar
titulares, carteiras, operações já realizadas e avaliações manuais. O programa
não envia ordens a corretoras. Histórico a custo não representa rentabilidade;
TWR/MWR, provedores de mercado, IA e MCP ainda não estão integrados.

## Componentes preparados pelo iniciador

| Componente | Versão ou origem |
| --- | --- |
| Windows PowerShell | 5.1, fornecido pelo Windows |
| uv | 0.13.4 portátil |
| Python | 3.12.14, preparado pelo uv |
| Node.js | 24.22.1 portátil |
| PostgreSQL | 17.6 portátil |
| Bibliotecas VC++ | Microsoft, distribuídas junto aos componentes que as usam (app-local) |

Os downloads de runtime usam **HTTPS** e **SHA-256 fixado** no
[manifesto de downloads](../scripts/windows/downloads.json). As versões não
dependem de um endereço genérico de “última versão”. Dependências da aplicação
são resolvidas pelos lockfiles `uv.lock` e `apps/web/package-lock.json`.
As bibliotecas VC++ são usadas localmente, sem instalar um redistribuível global.

## Onde ficam os arquivos

Cole `%LOCALAPPDATA%\InvestmentResearchHub` na barra de endereço do Explorador
de Arquivos para localizar os arquivos do Hub pertencentes ao seu usuário.

| Local | Conteúdo |
| --- | --- |
| `%LOCALAPPDATA%\InvestmentResearchHub\runtime` | Runtimes portáteis |
| `%LOCALAPPDATA%\InvestmentResearchHub\data` | Banco, configuração e logs persistentes |
| `.venv-windows`, na pasta extraída | Ambiente Python da aplicação |
| `apps\web\node_modules`, na pasta extraída | Dependências da interface |

Banco e configuração ficam fora do ZIP e do repositório. Extrações novas pelo
mesmo usuário reutilizam esses dados; o iniciador preserva a configuração
existente. Outro usuário do Windows tem sua própria pasta `%LOCALAPPDATA%`.
Enviar apenas o ZIP a outro computador não transfere o banco nem as contas.

## Endereços locais

| Componente | Endereço |
| --- | --- |
| Interface | `http://127.0.0.1:8766` |
| API | `http://127.0.0.1:8765` |
| Saúde da API | `http://127.0.0.1:8765/api/v1/health` |
| PostgreSQL | `127.0.0.1:54329` |

Todos escutam apenas em loopback, no computador que executa o Hub. Não há URL
pública nem acesso de outro dispositivo nesse fluxo. A interface encaminha as
chamadas à API; use o endereço `127.0.0.1` indicado pelo iniciador.

## Diagnóstico

Dê duplo clique em **Verificar Hub.cmd** para diagnosticar o runtime já
instalado. A primeira preparação é feita por **Iniciar Hub.cmd**. O diagnóstico
ajuda a identificar o estado da instalação e não equivale à suíte de testes do
projeto ou à homologação visual.

| Situação | Próximo passo |
| --- | --- |
| Atalho aberto dentro do ZIP ou arquivos ausentes | Extraia o ZIP inteiro e abra o atalho da pasta extraída. |
| Primeira preparação demora | Acompanhe a janela; os downloads e a instalação dos pacotes precisam terminar. |
| Aparece “Primeiro acesso” sem o campo, em um ZIP anterior à correção | Nessa mesma janela, digite e-mail + Enter, nome + Enter, senha de 12 a 128 caracteres + Enter e repita a senha + Enter. A senha fica oculta. O iniciador corrigido exibe os rótulos antes de aguardar entrada. |
| Falha de download | Confira a conexão e a mensagem exibida; mantenha a verificação SHA-256. |
| Porta ocupada | Confira o diagnóstico; encerre normalmente o programa que estiver usando a porta. Se for uma execução gerenciada do Hub, use `Parar Hub.cmd`. |
| Navegador sem página | Confira se o iniciador concluiu as verificações HTTP e se sua janela continua aberta. Depois abra `http://127.0.0.1:8766`. |

Para relatar um problema, guarde a mensagem exibida e o resultado do diagnóstico.
Os logs ficam sob `%LOCALAPPDATA%\InvestmentResearchHub\data`. Não compartilhe
senhas ou arquivos de configuração completos. Preserve os dados existentes
durante o diagnóstico.

## Atualizar preservando dados

1. Execute **Parar Hub.cmd** e aguarde a confirmação do encerramento dos
   processos gerenciados, incluindo o PostgreSQL.
2. Com o banco parado, faça uma cópia completa de
   `%LOCALAPPDATA%\InvestmentResearchHub\data` para um local seguro, preservando
   banco e configuração juntos.
3. Extraia o novo ZIP em uma pasta separada, preservando os arquivos próprios da
   cópia anterior. Mantenha os arquivos de configuração existentes em
   `%LOCALAPPDATA%`; não os substitua por exemplos.
4. Execute **Iniciar Hub.cmd** da nova pasta com o mesmo usuário do Windows.
   O iniciador prepara as dependências dessa cópia e reutiliza o banco e a
   configuração persistentes.
5. Confira o acesso e os dados existentes antes de remover a pasta anterior.

Restauração completa, migrações entre versões e operação supervisionada continuam
sujeitas aos critérios de validação da Etapa 1. A cópia de segurança não é uma
alegação de restauração já testada; consulte [STATUS](STATUS.md).

## Evidência da integração Windows

O [job nativo](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42147690848)
passou em **Windows Server 2022 x64**, usando Windows PowerShell 5.1:
instalação limpa em caminho com espaços e acentos; 128 testes Python e 25 web;
Ruff, mypy, Alembic, TypeScript, ESLint e build; login por HTTP através do Next.js;
ledger Decimal, idempotência e CSV; recusa de segunda instância; encerramento e
reinício preservando perfil, contas, operações, posições e checksum. Os atalhos
CMD de verificação e parada também foram executados. O ZIP contém apenas arquivos
versionados, sem banco, credenciais ou dependências baixadas durante o teste.

O alvo de uso é Windows 10/11 x64; não houve execução no computador do usuário
nem homologação visual dessas versões desktop. A verificação HTTP não comprova
revisão visual. A distribuição é um ZIP com
iniciadores e runtimes portáteis; não há promessa de executável assinado,
instalador de binário único ou homologação visual.

## English summary

Native Windows 10/11 x64 setup is available. Download the private branch
ZIP or a published Windows CI artifact, extract everything, then double-click
`Iniciar Hub.cmd`. First use needs internet and prompts for an administrator with
a hidden password of at least 12 characters. Keep the console open; browse to
`http://127.0.0.1:8766`, use `Parar Hub.cmd` to stop and `Verificar Hub.cmd` for
installed-runtime diagnostics. Data/configuration stay under the Windows user's
`%LOCALAPPDATA%\InvestmentResearchHub\data`. No WSL, Docker, Git, admin rights or
local chat is required. Native Windows Server 2022 CI passed; Stage 1 remains partial.
