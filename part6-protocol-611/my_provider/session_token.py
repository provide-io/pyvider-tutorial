import secrets
from datetime import datetime, timedelta, timezone

import attrs
from pyvider.ephemerals import BaseEphemeralResource, EphemeralResourceContext, register_ephemeral_resource
from pyvider.resources.private_state import PrivateState
from pyvider.schema import PvsSchema, a_num, a_str, s_resource

from my_provider.server import Server


@attrs.define(frozen=True)
class SessionTokenConfig:
    server_id: str
    ttl_seconds: int = 3600


@attrs.define(frozen=True)
class SessionTokenResult:
    server_id: str
    ttl_seconds: int
    token: str
    token_id: str
    expires_at: str


@attrs.define(frozen=True)
class SessionTokenPrivateState(PrivateState):
    token: str
    token_id: str
    ttl_seconds: int


@register_ephemeral_resource("mycloud_session_token")
class SessionToken(BaseEphemeralResource):
    config_class = SessionTokenConfig
    result_class = SessionTokenResult
    private_state_class = SessionTokenPrivateState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_resource({
            "server_id":   a_str(required=True, description="Server to grant access to"),
            "ttl_seconds": a_num(optional=True,  description="Token lifetime in seconds"),
            "token":       a_str(computed=True, sensitive=True, description="Access token"),
            "token_id":    a_str(computed=True, description="Token identifier"),
            "expires_at":  a_str(computed=True, description="ISO-8601 expiry timestamp"),
        })

    async def validate(self, config: SessionTokenConfig | None) -> list[str]:
        # `config` is None when the configuration is not wholly known -- here
        # `server_id` references a resource that does not exist yet, so at plan
        # time pyvider collapses the whole object rather than handing over one
        # whose fields are silently None. There is nothing to check until the
        # values are real, so accept it and let open() do the work.
        if config is None:
            return []

        errors = []
        if config.ttl_seconds is not None and config.ttl_seconds < 60:
            errors.append("ttl_seconds must be at least 60")
        return errors

    async def open(
        self, ctx: EphemeralResourceContext[SessionTokenConfig, None]
    ) -> tuple[SessionTokenResult, SessionTokenPrivateState, datetime]:
        ttl        = int(ctx.config.ttl_seconds)
        token_id   = f"tok-{secrets.token_hex(6)}"
        token      = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
        result  = SessionTokenResult(
            server_id=ctx.config.server_id,
            ttl_seconds=ttl,
            token=token,
            token_id=token_id,
            expires_at=expires_at.isoformat(),
        )
        private = SessionTokenPrivateState(token=token, token_id=token_id, ttl_seconds=ttl)
        return result, private, expires_at

    async def renew(
        self, ctx: EphemeralResourceContext[None, SessionTokenPrivateState]
    ) -> tuple[SessionTokenPrivateState, datetime]:
        new_token  = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ctx.private_state.ttl_seconds)
        return SessionTokenPrivateState(
            token=new_token, token_id=ctx.private_state.token_id, ttl_seconds=ctx.private_state.ttl_seconds
        ), expires_at

    async def close(self, ctx: EphemeralResourceContext[None, SessionTokenPrivateState]) -> None:
        pass  # real provider: revoke token via API
