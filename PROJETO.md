# Alura Agente — Desafio Alura Agentes

Bem-vindo ao nosso mais recente desafio **Alura Agentes**!

## História

Neste projeto vamos trabalhar na construção de um agente de IA focado em responder perguntas de colaboradores de uma empresa hipotética em relação a diversos documentos pertinentes no contexto desta empresa. Reiteramos que é um agente aberto a qualquer colaborador da empresa, então **não há necessidade de restringir seu acesso**.

### Formatos de documento suportados

Podemos lidar com diversos formatos e diversos contextos. Os formatos mais comuns a considerar:

- **PDF**
- **Word**
- **Excel**
- **PowerPoint**
- **Markdown**
- **CSV**
- **JSON**
- **HTML**

### Contextos (categorias de documentos)

Os possíveis contextos são variados — a lista abaixo é apenas uma sugestão e referência para aplicar no projeto:

| Categoria | Exemplos |
|-----------|----------|
| Recursos Humanos | políticas, benefícios, onboarding |
| Financeiro e Contábil | DRE, balanços, políticas de despesa |
| Operacional | processos, procedimentos, manuais técnicos |
| Estratégico | planos, OKRs, roadmaps |
| Legal e Compliance | contratos, NDAs, LGPD |
| Marketing e Comercial | pitch decks, tabelas de preço |
| Dados e Sistemas | planilhas, bases de clientes, APIs |
| Pesquisa e Desenvolvimento | market research, business cases |
| Qualidade | auditorias, ISO, planos corretivos |
| Comunicação Interna | comunicados, atas, newsletters |

Este é o nosso desafio aplicando os conhecimentos de Inteligência Artificial estudados na Alura.

## Objetivo

Desenvolver um agente de inteligência artificial **corporativo**, acessível a todos os colaboradores, capaz de responder perguntas com base em documentos internos da empresa.

O agente deve:
- Compreender e processar **múltiplos formatos de arquivo** (PDF, Word, Excel, PowerPoint, Markdown, CSV, JSON e HTML);
- Cobrir **diferentes domínios organizacionais** — de RH e financeiro a jurídico, operacional e estratégico;
- Funcionar como uma **base de conhecimento conversacional, centralizada e sempre disponível**.

## Requisitos

1. Colocar o projeto num **repositório público no GitHub**;
2. Realizar o deploy do agente na nuvem **Oracle (OCI — Oracle Cloud Infrastructure)**. Deve-se utilizar **ao menos um serviço OCI** no challenge;
3. Inserir no **README** do projeto uma **imagem ou vídeo do agente sendo executado em nuvem**, ou seja, em um serviço online de hospedagem/execução de projetos de tecnologia.

## Etapas do desafio

O desafio tem **três partes principais**:

### 1. Escolher e processar um documento
Escolher um documento (PDF ou CSV). Criar um código que leia e processe esse arquivo — a aplicação vai entender o conteúdo dele. O documento pode tratar de políticas internas, dados sobre chegada de produtos ou documentação sobre ferramentas e tecnologias da empresa. Há um documento de referência disponibilizado, mas é incentivado o uso de documentos próprios para personalizar o agente.

### 2. Construir o agente de IA
Construir um agente de IA que responda perguntas sobre o(s) documento(s). Exemplos de perguntas:
- "Qual foi o produto mais vendido em dezembro de 2015?"
- "Quais são as linguagens de programação usadas no back-end (camada de servidor) da plataforma de vendas da empresa?"

O agente busca a resposta no documento (ou documentos, pois é possível usar mais de um) e deve devolvê-la de forma clara.

### 3. Implantar na nuvem (OCI)
Implantar o agente na nuvem da Oracle (OCI). A aplicação sai do ambiente local e fica acessível publicamente, executando de fato na nuvem.

> Três etapas: um projeto completo, desde o documento até a implantação.

## Tecnologias sugeridas

Sugestões (não obrigatórias — o importante é que a solução funcione):

| Camada | Sugestão |
|--------|----------|
| Linguagem | Python |
| Framework do agente | LangChain |
| Leitura de documentos | pypdf ou pandas |
| Modelo de linguagem | Gemini, ChatGPT, Cohere, Claude ou outro de preferência |
| Implantação | OCI Compute |

## Entregas

- **Código no GitHub**, em repositório organizado, com histórico de commits;
- **README bem estruturado** contendo:
  - Descrição da arquitetura montada;
  - Exemplos de perguntas e respostas que o agente consegue responder;
  - Instruções para quem quiser executar o projeto;
  - Link ou captura de tela da aplicação em execução na OCI;
  - Demonstração de que a implantação funcionou de fato.

## Critérios de avaliação

- A aplicação funciona;
- A solução como um todo funciona;
- O código está organizado;
- O README explica bem o que foi feito e apresenta uma demonstração do funcionamento.

> Sem mistério: foi entregue funcionando e está bem documentado? Perfeito.

## Conselhos práticos

1. **Comece sempre pelo agente local** — faça funcionar na sua máquina primeiro e só depois pense na implantação. Muitas pessoas tentam subir para a nuvem algo que ainda não funciona localmente, e isso complica tudo.
2. **Use o Google Colab para prototipar** — é gratuito, já vem com Python configurado e economiza tempo de configuração.
3. **Não fique preso criando interface elaborada** — o valor do projeto está no agente funcionando, não na camada visual. Foque no que importa.

## Personalização

O projeto é nosso: podemos personalizá-lo como quisermos — dar outro nome, enviar documentos diferentes dos sugeridos e usar outras tecnologias.

## Gestão ágil com Trello

O sistema de desenvolvimento ágil usa o Trello da seguinte forma:

| Coluna | Descrição |
|--------|-----------|
| **Pronto para começar** | Cartões com elementos ainda não desenvolvidos |
| **Em Desenvolvimento** | Elementos que estão sendo desenvolvidos no momento (ao iniciar uma tarefa, mova o cartão para esta coluna) |
| **Pausado** | Itens que começaram a ser desenvolvidos, mas precisaram parar por algum motivo |
| **Concluído** | Elementos já concluídos |

> O Trello é uma ferramenta para acompanhar o andamento das atividades, mas **não será avaliado**.

Bom projeto!