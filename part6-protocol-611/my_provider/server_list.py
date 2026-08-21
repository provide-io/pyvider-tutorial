"""A list resource: enumerate servers that already exist.

Protocol 6.11 added this component type. Before it, showing a caller what was
already out there meant writing a data source per resource type and hand-rolling
a shape for the results. A list resource answers Terraform's `ListResource` RPC
instead, and describes its results with the identity and state schemas of a
managed resource you have already written.
"""

from collections.abc import AsyncIterator

from attrs import define
from pyvider.list_resources import BaseListResource, ListResourceContext, ListResult, register_list_resource
from pyvider.schema import PvsSchema, a_str, s_resource

from my_provider.server import Server


@define
class ServerListConfig:
    # Optional filter. None means "everything", which is what Terraform sends
    # when the block omits it.
    status: str | None = None


# A list resource is registered under the *same type name* as the managed
# resource it lists. That is not a naming convention, it is how Terraform
# resolves it: `list "mycloud_server" "all"` looks the provider up for a list
# resource called `mycloud_server`, and takes the identity schema from the
# managed resource of that name. Registering it as `mycloud_servers` gets
# "Identity schema not found for resource type mycloud_servers".
@register_list_resource("mycloud_server", resource_type="mycloud_server")
class ServerList(BaseListResource):
    """Every server, optionally filtered by status.

    `resource_type` points at the managed resource whose identity and state
    schemas describe these results, so neither is restated here. Identity is
    mandatory for a list resource -- it is how Terraform ties a listed instance
    back to a `mycloud_server` -- and `Server.get_identity_schema` supplies it.
    """

    config_class = ServerListConfig
    resource_type = "mycloud_server"

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_resource({
            "status": a_str(optional=True, description="Only list servers in this status"),
        })

    async def validate(self, config: ServerListConfig | None) -> list[str]:
        # None when the configuration is not wholly known. Nothing to check yet.
        if config is None or config.status is None:
            return []
        allowed = {"running", "stopped"}
        if config.status not in allowed:
            return [f"status must be one of {sorted(allowed)}, got {config.status!r}"]
        return []

    async def list(self, ctx: ListResourceContext[ServerListConfig]) -> AsyncIterator[ListResult]:
        wanted = ctx.config.status if ctx.config else None

        for data in Server._servers.values():
            if wanted is not None and data["status"] != wanted:
                continue

            yield ListResult(
                identity={"id": data["id"]},
                display_name=f"{data['name']} ({data['status']})",
                # Only built when the caller asked for it: assembling full state
                # is usually the expensive half of listing.
                resource_object=data if ctx.include_resource_object else None,
            )
