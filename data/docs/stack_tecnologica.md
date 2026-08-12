# Stack Tecnologica da Plataforma de Vendas

## Back-end (camada de servidor)
A plataforma de vendas usa **Python (FastAPI)** como linguagem principal do back-end,
com servicos auxiliares escritos em **Go** para gateway de pagamentos e **Java (Spring
Boot)** para o modulo de estoque. O banco de dados principal e **PostgreSQL** e o cache
e **Redis**.

## Front-end
O front-end web e construido com **React + TypeScript**, e o aplicativo mobile nativo e
desenvolvido em **Kotlin** (Android) e **Swift** (iOS).

## Infraestrutura
Os servicos rodam em containers **Docker** orquestrados por **Kubernetes (EKS)** na
nuvem. O monitoramento usa **Prometheus** e **Grafana**, e o CI/CD e feito com
**GitLab CI**.

## Integracoes
Pagamentos: **Stripe** e **Pix (API do banco parceiro)**. Envio de e-mails: **SendGrid**.
Notificacoes push: **Firebase Cloud Messaging**.
