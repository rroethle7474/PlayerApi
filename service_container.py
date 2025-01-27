class ServiceContainer:
    def __init__(self):
        self._services = {}

    def register(self, service_name, service_instance):
        self._services[service_name] = service_instance

    def get(self, service_name):
        return self._services.get(service_name)