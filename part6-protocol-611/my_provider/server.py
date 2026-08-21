from typing import Any, ClassVar

from attrs import define
from pyvider.resources import BaseResource, ResourceContext, register_resource
from pyvider.schema import PvsSchema, a_str, a_unknown, s_resource


@define
class ServerConfig:
    name: str


@define
class ServerState:
    id: str
    name: str
    status: str


@register_resource("mycloud_server")
class Server(BaseResource):
    config_class = ServerConfig
    state_class = ServerState

    # Pre-existing infrastructure, so `mycloud_servers` has something to find on
    # a fresh run. A real provider would call its API here instead.
    _servers: ClassVar[dict[str, dict[str, Any]]] = {
        "srv-900": {"id": "srv-900", "name": "legacy-db", "status": "running"},
        "srv-901": {"id": "srv-901", "name": "legacy-cache", "status": "stopped"},
    }
    _next_id: ClassVar[int] = 1

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_resource({
            "id":     a_str(computed=True, description="Server identifier"),
            "name":   a_str(required=True,  description="Server name"),
            "status": a_str(computed=True,  description="Server status"),
        })

    @classmethod
    def get_identity_schema(cls) -> PvsSchema:
        """Opt in to resource identity.

        Identity is optional for a managed resource and *mandatory* for a list
        resource: Terraform matches a listed instance back to a managed one by
        identity, so `mycloud_servers` cannot emit a result without it. Declaring
        it here means the list resource can borrow it rather than restate it.
        """
        return s_resource({
            "id": a_str(required=True, description="Server identifier"),
        })

    async def _validate_config(self, config: ServerConfig) -> list[str]:
        return [] if config.name else ["name cannot be empty"]

    # Plan hooks: mark computed fields as "known-after-apply".
    async def _create(
        self, ctx: ResourceContext, base_plan: dict[str, Any]
    ) -> tuple[dict[str, Any] | None, None]:
        base_plan["id"] = a_unknown(a_str())
        base_plan["status"] = a_unknown(a_str())
        return base_plan, None

    async def _update(
        self, ctx: ResourceContext, base_plan: dict[str, Any]
    ) -> tuple[dict[str, Any] | None, None]:
        base_plan["status"] = a_unknown(a_str())
        return base_plan, None

    async def _create_apply(self, ctx: ResourceContext) -> tuple[ServerState | None, None]:
        server_id = f"srv-{Server._next_id:03d}"
        Server._next_id += 1
        data = {"id": server_id, "name": ctx.config.name, "status": "running"}
        Server._servers[server_id] = data
        return ServerState(**data), None

    async def read(self, ctx: ResourceContext) -> ServerState | None:
        data = Server._servers.get(ctx.state.id)
        return ServerState(**data) if data else None

    async def _update_apply(self, ctx: ResourceContext) -> tuple[ServerState | None, None]:
        data = Server._servers[ctx.state.id]
        data["name"] = ctx.config.name
        return ServerState(**data), None

    async def _delete_apply(self, ctx: ResourceContext) -> None:
        Server._servers.pop(ctx.state.id, None)
