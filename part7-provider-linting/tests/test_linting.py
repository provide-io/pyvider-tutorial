from __future__ import annotations

from typing import Any

from my_provider.server import ALL_LINTS, NAMING, PRODUCTION_NAME, Server, ServerConfig
import pytest

from pyvider.lint import LintContext, LintFinding, LintSelector


async def findings_for(name: Any, *selectors: str) -> tuple[LintFinding, ...]:
    return await Server().lint(
        LintContext(
            config=ServerConfig(name=name) if isinstance(name, str) else name,
            selector=LintSelector.parse(selectors),
        )
    )


@pytest.mark.asyncio
async def test_exact_rule_enables_the_finding() -> None:
    findings = await findings_for("web-prod", PRODUCTION_NAME)

    assert len(findings) == 1
    assert findings[0].rule == PRODUCTION_NAME
    assert findings[0].groups == (ALL_LINTS, NAMING)
    assert findings[0].attribute_path == "name"


@pytest.mark.asyncio
async def test_all_group_enables_the_finding() -> None:
    assert len(await findings_for("web-prod", ALL_LINTS)) == 1


@pytest.mark.asyncio
async def test_naming_group_enables_the_finding() -> None:
    assert len(await findings_for("web-prod", NAMING)) == 1


@pytest.mark.asyncio
async def test_exact_exclusion_suppresses_group_selection() -> None:
    assert await findings_for("web-prod", ALL_LINTS, f"!{PRODUCTION_NAME}") == ()


@pytest.mark.asyncio
async def test_empty_selector_keeps_linting_off() -> None:
    assert await findings_for("web-prod") == ()


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["web-dev", "", None, object()])
async def test_non_production_and_unknown_names_are_safe(name: Any) -> None:
    assert await findings_for(name, ALL_LINTS) == ()
