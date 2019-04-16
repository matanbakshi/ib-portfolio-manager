from src.logger import logger


class TransactionManager:
    def __init__(self):
        self._methods_to_execute = []

    def queue_for_execution(self, method, *args, **kwargs):
        self._methods_to_execute.append((method, args, kwargs))

    def execute_all(self):
        for method, args, kwargs in self._methods_to_execute:
            ret_val = method(*args, **kwargs)
            logger.info(f"{method.__name__}({args},{kwargs}) executed. Return Value: {ret_val}")

    def discard_all(self):
        self._methods_to_execute.clear()
