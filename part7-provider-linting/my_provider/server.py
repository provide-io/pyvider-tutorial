from __future__ import annotations

from typing import Any, ClassVar

from attrs import define

from pyvider.lint import LintContext, LintFinding
from pyvider.resources import BaseResource, ResourceContext, register_resource
from pyvider.schema import PvsSchema, a_str, s_resource

PRODUCTION_NAME = "example/mycloud:production-name"
ALL_LINTS = "example/mycloud:all"
NAMING = "example/mycloud:naming"


@define
class ServerConfig:
    name: str


@define
class ServerState:
    id: str
    name: str


@register_resource("mycloud_server")
class Server(BaseResource["Server", ServerState, ServerConfig]):
    """A tiny in-memory server with one opt-in advisory rule."""

    config_class = ServerConfig
    state_class = ServerState
    _servers: ClassVar[dict[str, dict[str, Any]]] = {}

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_resource(
            {
                "id": a_str(computed=True, description="Server identifier"),
                "name": a_str(required=True, description="Server name"),
            }
        )

    async def _validate_config(self, config: ServerConfig) -> list[str]:
        return [] if config.name else ["name cannot be empty"]

    async def lint(self, ctx: LintContext[ServerConfig]) -> tuple[LintFinding, ...]:
        if not ctx.enabled(PRODUCTION_NAME, ALL_LINTS, NAMING):
            return ()

        name = getattr(ctx.config, "name", None)
        if not isinstance(name, str) or "prod" not in name.lower():
            return ()

        return (
            LintFinding(
                rule=PRODUCTION_NAME,
                groups=(ALL_LINTS, NAMING),
                summary="Production environment is encoded in the server name",
                detail=(
                    "Explicit environment metadata is easier to review and automate. "
                    "Exclude !example/mycloud:production-name when this naming convention is deliberate."
                ),
                attribute_path="name",
            ),
        )

    async def read(self, ctx: ResourceContext[ServerConfig, ServerState, Any]) -> ServerState | None:
        if ctx.state is None:
            return None
        data = self._servers.get(ctx.state.id)
        return ServerState(**data) if data else None

    async def _delete_apply(self, ctx: ResourceContext[ServerConfig, ServerState, Any]) -> None:
        if ctx.state is not None:
            self._servers.pop(ctx.state.id, None)
