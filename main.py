from src.entry.main import run


def lambda_handler(event, context):
    output = run()

    return output
