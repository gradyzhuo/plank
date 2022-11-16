from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from plank.serving.service import Service


class ServiceManagerable:
    def add_service(self, service: Service):
        from plank.serving.service import Service
        Service.register(service, name=service.name())

    def add_services(self, *services: Service):
        for service in services:
            self.add_service(service)

    def services(self) -> List[Service]:
        from plank.serving.service import Service
        return Service.registered()

    def service(self, name: str) -> Service:
        from plank.serving.service import Service
        return Service.from_name(name=name)
