# Deploy na Oracle Cloud Infrastructure (OCI)

Este guia publica o agente em uma instância **OCI Compute com Ubuntu**. Para o modelo
local de embeddings, prefira uma instância com pelo menos 4 GB de memória. A opção
Always Free `VM.Standard.A1.Flex`, quando disponível na região, oferece recursos mais
adequados que a `VM.Standard.E2.1.Micro` de 1 GB.

Referências oficiais:

- [Criar uma instância Compute](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/launchinginstance.htm)
- [Recursos Always Free](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm)

## 1. Criar a instância

1. Na região principal da tenancy, crie uma instância Compute.
2. Escolha Ubuntu e, preferencialmente, `VM.Standard.A1.Flex` com 2 OCPUs e 12 GB de RAM.
3. Use uma sub-rede pública, atribua IPv4 público e salve a chave SSH privada.
4. Na Network Security Group ou Security List, adicione uma regra de entrada stateful:
   origem `0.0.0.0/0`, protocolo TCP, porta de destino `8501`.

Durante a instalação, é mais seguro restringir a origem ao seu IP. Abra para
`0.0.0.0/0` somente quando precisar disponibilizar a demonstração publicamente.

## 2. Conectar e clonar

No computador local:

```bash
ssh -i /caminho/chave.key ubuntu@IP_PUBLICO
```

Na instância:

```bash
sudo git clone URL_DO_REPOSITORIO_PUBLICO /opt/alura-agente
sudo chown -R ubuntu:ubuntu /opt/alura-agente
cd /opt/alura-agente
cp .env.example .env
nano .env
```

Preencha `OPENROUTER_API_KEY` e ajuste `OPENROUTER_SITE_URL` para a URL pública do
repositório ou da aplicação. Nunca envie o arquivo `.env` ao Git.

## 3. Instalar e iniciar

```bash
cd /opt/alura-agente
sudo bash deploy/setup_oci.sh
curl --fail http://127.0.0.1:8501/_stcore/health
```

O setup instala as dependências, baixa o modelo de embeddings, cria o índice e registra
um serviço systemd. Depois do primeiro download, o serviço usa o cache local do modelo.

Abra `http://IP_PUBLICO:8501` e faça uma pergunta. Para conferir logs:

```bash
sudo systemctl status alura-agente
sudo journalctl -u alura-agente -n 100 --no-pager
```

## 4. Atualizar uma instalação

```bash
cd /opt/alura-agente
sudo -u ubuntu git pull --ff-only
sudo bash deploy/setup_oci.sh
```

O manifesto do índice detecta alterações nos documentos e evita servir uma base antiga.

## 5. Validar e registrar a entrega

1. Execute ao menos as cinco perguntas de `scripts/smoke_test.py` pela interface.
2. Confirme uma pergunta fora do escopo: o agente deve dizer que não encontrou a informação.
3. Capture uma tela contendo a URL/IP e uma resposta com fontes.
4. Salve como `docs/screenshots/agente_oci.png` e atualize o README.

Para uma implantação corporativa real, coloque HTTPS e um proxy reverso ou Load
Balancer na frente do Streamlit. A porta 8501 pública é adequada apenas para a
demonstração do desafio.
