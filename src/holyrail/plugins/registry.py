from __future__ import annotations

from typing import Protocol


class Plugin(Protocol):
    name: str

    def register(self, registry: PluginRegistry) -> None: ...


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def add(self, plugin: Plugin) -> None:
        self._plugins[plugin.name] = plugin

    def get(self, name: str) -> Plugin:
        return self._plugins[name]

    def names(self) -> list[str]:
        return sorted(self._plugins)
