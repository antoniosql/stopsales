import json
import logging

import azure.functions as func
import azure.durable_functions as df


async def main(msg: func.ServiceBusMessage, starter: str):
    """ServiceBus trigger que arranca una instancia Durable por correo."""
    client = df.DurableOrchestrationClient(starter)

    payload = json.loads(msg.get_body().decode("utf-8"))
    email_id = payload.get("email_id") or None

    instance_id = await client.start_new("StopSalesOrchestrator", instance_id=email_id, client_input=payload)
    logging.info("Started orchestration: %s", instance_id)
