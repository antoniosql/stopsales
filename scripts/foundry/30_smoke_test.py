#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True)
    args = parser.parse_args()

    load_dotenv(args.env, override=False)

    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    model = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

    with DefaultAzureCredential() as cred, AIProjectClient(endpoint=endpoint, credential=cred) as project_client:
        with project_client.get_openai_client() as openai_client:
            r = openai_client.responses.create(
                model=model,
                input="Di 'OK' y devuelve un JSON {\"status\":\"ok\"}.",
                max_output_tokens=100,
                temperature=0.0,
            )
            print(r.output_text)


if __name__ == "__main__":
    main()
