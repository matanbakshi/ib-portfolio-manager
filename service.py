from src.entry.main import run


def run_service(event, context):
    output = run()

    return output
