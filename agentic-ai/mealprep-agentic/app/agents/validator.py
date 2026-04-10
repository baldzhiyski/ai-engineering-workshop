from __future__ import annotations
from langchain.agents import create_agent
from ..domain.models import ValidationReport
from ..middleware.groups import validator_middleware
from ..config import settings

VALIDATOR_PROMPT = """
You validate meal plans for consistency and safety.

Check:
- plan completeness
- macro coherence
- contradiction between warnings and recommendations
- supplement conservatism
- whether medical review is needed

Be strict. If anything is questionable, flag it.
"""

def build_validator_agent(*, store=None):
    return create_agent(
        model=settings.validator_model,
        tools=[],
        middleware= validator_middleware(),
        system_prompt=VALIDATOR_PROMPT,
        response_format=ValidationReport,
        store=store,
    )