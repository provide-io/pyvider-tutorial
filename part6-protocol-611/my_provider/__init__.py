from pyvider.providers import BaseProvider, ProviderMetadata, register_provider
from pyvider.schema import PvsSchema, s_provider

import my_provider.server         # noqa: F401
import my_provider.server_info    # noqa: F401
import my_provider.names          # noqa: F401
import my_provider.session_token  # noqa: F401
import my_provider.server_list    # noqa: F401
import my_provider.restart_server # noqa: F401


@register_provider("mycloud")
class MyCloudProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__(
            metadata=ProviderMetadata(name="mycloud", version="0.1.0", protocol_version="6")
        )

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_provider({})


def main() -> None:
    from pyvider.cli import main as pyvider_main
    pyvider_main()
