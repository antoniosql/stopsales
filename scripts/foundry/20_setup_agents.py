#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True, help="Ruta al .env")
    args = parser.parse_args()

    load_dotenv(args.env, override=False)

    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    model = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

    prompts_dir = Path(__file__).resolve().parents[2] / "src" / "stopsales" / "foundry" / "prompts"

    agents = [
        (os.getenv("AGENT_CLASSIFIER_NAME", "StopSales-Classifier"), prompts_dir / "classifier.md"),
        (os.getenv("AGENT_BODY_EXTRACTOR_NAME", "StopSales-BodyExtractor"), prompts_dir / "body_extractor.md"),
        (os.getenv("AGENT_PDF_EXTRACTOR_NAME", "StopSales-PDFExtractor"), prompts_dir / "pdf_extractor.md"),
        (os.getenv("AGENT_VISUAL_EXTRACTOR_NAME", "StopSales-VisualExtractor"), prompts_dir / "visual_extractor.md"),
        (os.getenv("AGENT_NORMALIZER_NAME", "StopSales-Normalizer"), prompts_dir / "normalizer.md"),
    ]

    with DefaultAzureCredential() as cred, AIProjectClient(endpoint=endpoint, credential=cred) as project_client:
        for name, prompt_file in agents:
            instructions = read_text(prompt_file)
            agent = project_client.agents.create_version(
                agent_name=name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions=instructions,
                    temperature=0.0,
                ),
            )
            print(f"✓ Agent created/updated: {agent.name} v{agent.version} (id: {agent.id})")


if __name__ == "__main__":
    main()
