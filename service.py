from src.entry.main import run
from src.tools.ib_gateway_launcher import launch_ib_gateway


def run(event, context):
    launch_ib_gateway("bin/run.sh", "root/conf.yaml", "/home/matan/clientportal.beta.gw")

    output = run()

    return output
