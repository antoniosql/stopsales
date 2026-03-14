from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Configuración de la solución.

    Nota:
      - En local se suele cargar desde un fichero .env (dotenv).
      - En Azure Functions se inyecta como Application Settings.

    Evita meter secretos en git; en producción usa Key Vault + Managed Identity.
    """

    # Azure
    azure_subscription_id: str
    azure_tenant_id: Optional[str]
    azure_location: str
    resource_group: str
    prefix: str

    # Storage / messaging
    storage_account_name: str
    blob_container_raw_emails: str
    blob_container_attachments: str

    servicebus_namespace: str
    servicebus_queue: str
    servicebus_max_delivery_count: int

    # Observability / security
    app_insights_name: str
    keyvault_name: str

    # Apps
    functionapp_name: str
    functionapp_plan: str
    reviewapp_name: str
    reviewapp_plan: str

    # SQL
    sql_server_name: str
    sql_database_name: str
    sql_admin_user: str
    sql_admin_password: Optional[str]

    # Foundry
    foundry_resource_name: str
    foundry_project_name: str
    azure_ai_project_endpoint: str
    azure_ai_model_deployment_name: str

    # Agents
    agent_classifier_name: str
    agent_body_extractor_name: str
    agent_pdf_extractor_name: str
    agent_visual_extractor_name: str
    agent_normalizer_name: str

    # Integration
    destination_api_url: str
    destination_api_key: Optional[str]

    # Decisioning
    confidence_threshold: float

    @staticmethod
    def from_env(env_file: Optional[str] = None) -> "Settings":
        """Carga settings desde variables de entorno, opcionalmente cargando un fichero .env."""
        if env_file:
            load_dotenv(env_file, override=False)

        def req(name: str) -> str:
            v = os.getenv(name)
            if not v:
                raise ValueError(f"Missing required env var: {name}")
            return v

        def opt(name: str) -> Optional[str]:
            return os.getenv(name)

        return Settings(
            azure_subscription_id=req("AZURE_SUBSCRIPTION_ID"),
            azure_tenant_id=opt("AZURE_TENANT_ID"),
            azure_location=os.getenv("AZURE_LOCATION", "westeurope"),
            resource_group=os.getenv("RESOURCE_GROUP", "rg-stopsales-dev"),
            prefix=os.getenv("PREFIX", "stopsales"),

            storage_account_name=req("STORAGE_ACCOUNT_NAME"),
            blob_container_raw_emails=os.getenv("BLOB_CONTAINER_RAW_EMAILS", "raw-emails"),
            blob_container_attachments=os.getenv("BLOB_CONTAINER_ATTACHMENTS", "attachments"),

            servicebus_namespace=req("SERVICEBUS_NAMESPACE"),
            servicebus_queue=os.getenv("SERVICEBUS_QUEUE", "stopsales"),
            servicebus_max_delivery_count=int(os.getenv("SERVICEBUS_MAX_DELIVERY_COUNT", "10")),

            app_insights_name=os.getenv("APP_INSIGHTS_NAME", ""),
            keyvault_name=os.getenv("KEYVAULT_NAME", ""),

            functionapp_name=os.getenv("FUNCTIONAPP_NAME", ""),
            functionapp_plan=os.getenv("FUNCTIONAPP_PLAN", ""),
            reviewapp_name=os.getenv("REVIEWAPP_NAME", ""),
            reviewapp_plan=os.getenv("REVIEWAPP_PLAN", ""),

            sql_server_name=os.getenv("SQL_SERVER_NAME", ""),
            sql_database_name=os.getenv("SQL_DATABASE_NAME", ""),
            sql_admin_user=os.getenv("SQL_ADMIN_USER", ""),
            sql_admin_password=opt("SQL_ADMIN_PASSWORD"),

            foundry_resource_name=os.getenv("FOUNDRY_RESOURCE_NAME", ""),
            foundry_project_name=os.getenv("FOUNDRY_PROJECT_NAME", ""),
            azure_ai_project_endpoint=req("AZURE_AI_PROJECT_ENDPOINT"),
            azure_ai_model_deployment_name=req("AZURE_AI_MODEL_DEPLOYMENT_NAME"),

            agent_classifier_name=os.getenv("AGENT_CLASSIFIER_NAME", "StopSales-Classifier"),
            agent_body_extractor_name=os.getenv("AGENT_BODY_EXTRACTOR_NAME", "StopSales-BodyExtractor"),
            agent_pdf_extractor_name=os.getenv("AGENT_PDF_EXTRACTOR_NAME", "StopSales-PDFExtractor"),
            agent_visual_extractor_name=os.getenv("AGENT_VISUAL_EXTRACTOR_NAME", "StopSales-VisualExtractor"),
            agent_normalizer_name=os.getenv("AGENT_NORMALIZER_NAME", "StopSales-Normalizer"),

            destination_api_url=req("DESTINATION_API_URL"),
            destination_api_key=opt("DESTINATION_API_KEY"),

            confidence_threshold=float(os.getenv("CONFIDENCE_THRESHOLD", "0.85")),
        )
