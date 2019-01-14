
from ibapi import wrapper
from ibapi.client import EClient
from ibapi.utils import iswrapper


class TestWrapper(wrapper.EWrapper):
    pass


class TestClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)


class TestApp(TestWrapper, TestClient):
    def __init__(self):
        TestWrapper.__init__(self)
        TestClient.__init__(self, wrapper=self)

def main():
    app = TestApp()

    app.connect("127.0.0.1", 7497, clientId=0)

    app.run()


if __name__ == '__main__':
    main()