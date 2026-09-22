import my_provider.server  # noqa: F401
from pyvider.providers import BaseProvider, ProviderMetadata, register_provider
from pyvider.schema import PvsSchema, s_provider


@register_provider("mycloud")
class MyCloudProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__(metadata=ProviderMetadata(name="mycloud", version="0.1.0", protocol_version="6"))

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_provider({})


def main() -> None:
    from pyvider.cli import main as pyvider_main

    pyvider_main()
