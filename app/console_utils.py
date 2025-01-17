from app.utils import load_local_yaml
class ConsoleConfig():
    def __init__(self):
        self.__dict__ = load_local_yaml(r"app\console_config.yaml")