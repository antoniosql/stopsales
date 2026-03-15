# Stop Sales automation (Azure + Microsoft Foundry + Python)

Solución end-to-end para transformar correos de *Stop Sales / Open Sales* hoteleros en un **JSON normalizado** listo para publicar en un endpoint destino, con:
- Ingesta desacoplada (Graph/Logic Apps → Blob → Service Bus)
- Orquestación con estado (Azure Functions + Durable Functions)
- Extracción multimodal (Microsoft Foundry Agent Service + modelos)
- Normalización/validación determinista + decisión por confianza
- Human-in-the-loop (portal de revisión) y trazabilidad (SQL + Application Insights)

> Este repo es un **scaffold**: incluye armazón, contratos y scripts de despliegue. La lógica de negocio / JSON final se completa con tu contrato real.

## 1) Prerrequisitos
- Python 3.10+
- Azure CLI (`az`) autenticado (`az login`)
- Azure Functions Core Tools (para publicar la Function App)
- Acceso RBAC para crear recursos y asignar roles (RG/subscription)

## 2) Configuración por entorno
1. Copia `.env.example` a `.env.dev` (o `.env` para local) y rellena valores.
2. Los scripts leen variables desde el fichero `.env.*`.

> **Seguridad**: no guardes secretos en Git. Para producción, usa Key Vault y Managed Identity.

## 3) Deploy rápido (Dev)
### 3.1 Infra base (Storage + ServiceBus + Functions + AI + etc.)
```bash
cp .env.example .env.dev
# edita .env.dev

# Linux/macOS
bash scripts/deploy/10_deploy_azure_resources.sh .env.dev
bash scripts/deploy/20_deploy_foundry_project.sh .env.dev
bash scripts/deploy/30_assign_roles.sh .env.dev

# Windows (PowerShell)
pwsh ./scripts/deploy/10_deploy_azure_resources.ps1 .env.dev
pwsh ./scripts/deploy/20_deploy_foundry_project.ps1 .env.dev
pwsh ./scripts/deploy/30_assign_roles.ps1 .env.dev
```

### 3.2 (Opcional) Crear agentes en Foundry vía SDK
```bash
python scripts/foundry/20_setup_agents.py --env .env.dev
```

### 3.3 Publicar Function App
```bash
# Linux/macOS
bash scripts/deploy/40_publish_functionapp.sh .env.dev

# Windows (PowerShell)
pwsh ./scripts/deploy/40_publish_functionapp.ps1 .env.dev
```

## 4) Smoke test local con muestras (.msg)
En `data/samples/` coloca correos `.msg` (ej. los del ZIP StopSales.zip) y ejecuta:
```bash
python scripts/local/10_process_samples.py --env .env.dev --samples data/samples
```

## 5) Flujo lógico (alto nivel)
1. **Nuevo correo** → persistencia raw en Blob
2. **Clasificación + limpieza** → elegir extractor
3. **Extracción** (body o adjunto) → JSON intermedio (eventos atómicos)
4. **Normalización + reglas** → mapping catálogos + validación
5. **Decisión por confianza** → publicar o mandar a revisión
6. **Auditoría** → trazas y evidencias (SQL/Blob/AppInsights)

## 6) Estructura de carpetas
- `apps/funcapp/` → Azure Functions (Durable + triggers)
- `src/stopsales/` → librería core (pipeline, reglas, integración, Foundry SDK)
- `infra/` → plantillas (opcional) / notas de recursos
- `scripts/` → despliegue + bootstrap de Foundry + tests locales

## 7) Nota sobre “Foundry projects”
- El endpoint de proyecto tiene formato:
  `https://<resource>.services.ai.azure.com/api/projects/<project>`
- El SDK recomendado para Python es `azure-ai-projects>=2.0.0`.

