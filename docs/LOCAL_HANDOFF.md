# Abrir o Hub no computador do usuário

## Objetivo desta retomada

Executar o incremento existente e permitir que o usuário o utilize. A Etapa 1
continua parcial; não iniciar as Etapas 2/3 nem ampliar funcionalidades durante
esta retomada de acesso.

O projeto local foi identificado pelo Codex em
`C:\Users\davit\Documents\Códigos\Investment Research Hub`, com rótulo
`Investment Research Hub`. O catálogo informa que essa pasta ainda não é um
repositório Git. Seu conteúdo e os programas instalados no Windows não foram
inspecionados pela sessão remota; conferir antes de alterar qualquer arquivo.

Fonte: `https://github.com/DaviTosatti/Investment-Research-Hub.git`.
Branch de trabalho: `codex/etapa-1-fundacao`.
PR: `https://github.com/DaviTosatti/Investment-Research-Hub/pull/1`.
O código está nessa branch; a main ainda contém apenas o README inicial.

## Procedimento para o agente local

1. Confirmar que o executor pertence ao computador do usuário e que consegue
   acessar a pasta indicada. Não tratar um novo chat na nuvem como execução local.
2. Conferir a pasta e preservar seus arquivos. Se já existir um checkout correto,
   examinar estado/branch antes de atualizar. Caso contrário, clonar a branch em
   uma pasta vazia, usando subpasta se houver conteúdo existente. Não sobrescrever
   dados para acomodar o clone e não reescrever o histórico publicado.
3. Ler `AGENTS.md`, `README.md`, `docs/STATUS.md` e `docs/HANDOFF.md`. Detectar as
   ferramentas locais. O caminho documentado usa WSL2/Linux, Docker Compose,
   Python 3.12, uv 0.13.4, Node 24.22.1 e npm 11.9.0. Conferir integração do Docker
   com WSL e disponibilidade das portas antes de executar o bootstrap.
4. Usar `bash scripts/bootstrap.sh` no checkout Linux/WSL. Preservar configurações
   e volumes existentes; não remover banco ou redefinir credenciais. A instalação
   no Windows/WSL ainda precisa ser verificada, não foi demonstrada pela sessão cloud.
5. Se o banco local não tiver administrador, criar o primeiro acesso pelo CLI
   documentado. A senha criada na máquina remota não foi versionada e não é uma
   senha padrão do produto. Não publicar credenciais em commits, PRs ou logs.
6. Iniciar API e frontend conforme o README. Validar HTTP, acesso autenticado e,
   quando houver ferramenta disponível, o navegador do próprio usuário. Só
   fornecer o endereço depois de confirmar que ele alcança essa execução local.
   Não equiparar abertura de aba em estado `queued` a acesso efetivo.
7. Deixar os serviços disponíveis para uso e registrar apenas mudanças/evidências
   necessárias. Se houver alteração de código/configuração/documentação, verificar,
   atualizar o progresso e fazer commit/push com Conventional Commits na branch.

## Motivo da mudança de ambiente

A execução remota respondeu a login, consulta e arquivos JavaScript, mas o serviço
de prévia ficou indisponível e o navegador compartilhado não recebeu a credencial
interna exigida pela plataforma. Não existe URL pública de implantação. O usuário
mostrou uma aba vazia, e o menu de conversa contém apenas ações como renomear,
compartilhar e arquivar; não apresenta uma opção de reconexão.

Esta sessão não disponibiliza uma ferramenta para criar/transferir automaticamente
a tarefa a um executor local. O usuário precisa abrir um chat associado à pasta
local. Não solicitar mais reinicializações ou menus aleatórios como se uma opção
de reparo tivesse sido confirmada.
