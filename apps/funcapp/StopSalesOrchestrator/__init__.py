import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    payload = context.get_input() or {}
    outcome = yield context.call_activity("ProcessStopSalesActivity", payload)
    return outcome


main = df.Orchestrator.create(orchestrator_function)
