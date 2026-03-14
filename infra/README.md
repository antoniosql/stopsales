# Infra (notas)

En este scaffold el despliegue se hace con **Azure CLI** (ver `scripts/deploy/`).

Si tu organización exige IaC (Bicep/Terraform), puedes migrar estos comandos a plantillas.

Recursos principales (según arquitectura):
- Storage Account + contenedores (raw emails, attachments)
- Service Bus Namespace + queue (con DLQ)
- Azure Functions (Durable) con Managed Identity
- Application Insights
- Key Vault
- Azure SQL (catálogos + auditoría)
- Microsoft Foundry (AIServices) + Project
- (Opcional) Azure AI Search
- (Opcional) Document Intelligence / Content Understanding
