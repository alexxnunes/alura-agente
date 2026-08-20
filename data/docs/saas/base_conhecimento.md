# Base de Conhecimento — CloudSync Pro Platform

Bem-vindo à documentação técnica oficial da plataforma **CloudSync Pro**, a solução corporativa para automação de dados e integrações em nuvem.

## 1. Arquitetura e Módulos Principais
A plataforma CloudSync Pro é composta por quatro módulos integrados:
1. **Pipeline Builder**: Criação visual de fluxos de transformação ETL/ELT sem necessidade de código (no-code / low-code).
2. **API Management & Webhooks**: Gateway para recepção e disparo de eventos HTTP em tempo real com retry exponencial automático em caso de falha 5xx.
3. **Audit Log & Compliance**: Rastreabilidade completa de todas as ações de usuários, alterações de configuração e logs de execução armazenados por até 365 dias.
4. **Connector Hub**: Mais de 120 conectores nativos pré-construídos para bancos de dados (PostgreSQL, MySQL, Oracle, MongoDB) e ferramentas SaaS (Salesforce, HubSpot, Jira, Slack).

## 2. Autenticação e Segurança
- **API Keys**: Geradas com permissões granulares por workspace (Read-only, Write, Admin).
- **OAuth 2.0 / SAML 2.0**: Suporte a Single Sign-On (SSO) com provedores Okta, Azure Active Directory e Google Workspace no plano Enterprise.
- **Rate Limits**: 1.000 requisições por minuto no plano Pro e 5.000 requisições por minuto no plano Enterprise.
