"""An action: restart a server.

Protocol 6.11 added this component type for the operation that is not "make
reality match this configuration" -- restart a node, rotate a credential,
trigger a run. Before it, these were modelled as resources with a trigger
attribute, which put an imperative verb in a declarative graph and left state
describing something that had already finished.

An action plans, then invokes, and streams progress while it runs.
"""

from collections.abc import AsyncIterator

from attrs import define
from pyvider.actions import ActionContext, ActionPlan, ActionProgress, BaseAction, register_action
from pyvider.schema import PvsSchema, a_str, s_resource

from my_provider.server import Server


@define
class RestartConfig:
    server_id: str


@register_action("mycloud_restart_server")
class RestartServer(BaseAction):
    config_class = RestartConfig

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_resource({
            "server_id": a_str(required=True, description="Server to restart"),
        })

    async def validate(self, config: RestartConfig | None) -> list[str]:
        # None when the configuration is not wholly known -- `server_id` may
        # reference a server that does not exist yet at plan time.
        if config is None:
            return []
        return [] if config.server_id else ["server_id cannot be empty"]

    async def plan(self, ctx: ActionContext[RestartConfig]) -> ActionPlan:
        """Warn about what invoking this will do.

        A plan is the place to say something the operator should read *before*
        approving, since an action's effect is not visible as a state diff.
        """
        if ctx.config is None:
            return ActionPlan()
        return ActionPlan(
            warnings=(f"{ctx.config.server_id} will be briefly unavailable while it restarts.",)
        )

    async def invoke(self, ctx: ActionContext[RestartConfig]) -> AsyncIterator[ActionProgress]:
        server_id = ctx.config.server_id
        server = Server._servers.get(server_id)

        if server is None:
            raise ValueError(f"no such server: {server_id}")

        yield ActionProgress(message=f"Stopping {server['name']}...")
        server["status"] = "stopped"

        yield ActionProgress(message=f"Starting {server['name']}...")
        server["status"] = "running"

        yield ActionProgress(message=f"{server['name']} is running again.")
