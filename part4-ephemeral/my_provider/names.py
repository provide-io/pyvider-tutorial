from pyvider.cty import CtyString
from pyvider.functions import BaseFunction, FunctionParameter, FunctionReturnType, register_function
from pyvider.schema import PvsSchema, a_str, s_function


@register_function("generate_name")
class GenerateNameFunction(BaseFunction):
    """Generate a standardized server name from prefix and environment."""

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_function(
            parameters=[
                a_str(description="Name prefix — e.g. 'web', 'db'"),
                a_str(description="Environment — e.g. 'prod', 'dev'"),
            ],
            return_type=a_str(description="Generated name"),
        )

    def get_parameters(self) -> list[FunctionParameter]:
        return [
            FunctionParameter(name="prefix", type=CtyString()),
            FunctionParameter(name="env",    type=CtyString()),
        ]

    def get_return_type(self) -> FunctionReturnType:
        return FunctionReturnType(type=CtyString())

    async def call(self, prefix: str, env: str) -> str:
        return f"{prefix}-{env}"
