from attrs import define
from pyvider.data_sources import register_data_source
from pyvider.data_sources.base import BaseDataSource
from pyvider.resources.context import ResourceContext
from pyvider.schema import PvsSchema, a_str, s_data_source

from my_provider.server import Server


@define
class ServerInfoConfig:
    server_id: str


@define
class ServerInfoState:
    server_id: str
    id: str
    name: str
    status: str


@register_data_source("mycloud_server_info")
class ServerInfo(BaseDataSource):
    config_class = ServerInfoConfig
    state_class = ServerInfoState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_data_source({
            "server_id": a_str(required=True, description="ID of the server to look up"),
            "id":        a_str(computed=True,  description="Server ID"),
            "name":      a_str(computed=True,  description="Server name"),
            "status":    a_str(computed=True,  description="Server status"),
        })

    async def _validate_config(self, config: ServerInfoConfig) -> list[str]:
        # server_id may be unknown at plan time (e.g. when it references a
        # resource attribute computed during apply). Accept empty strings
        # here and let read() handle missing IDs.
        return []

    async def read(self, ctx: ResourceContext) -> ServerInfoState | None:
        data = Server._servers.get(ctx.config.server_id)
        if not data:
            return None
        return ServerInfoState(server_id=ctx.config.server_id, **data)
