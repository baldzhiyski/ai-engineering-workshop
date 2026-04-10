from langchain.agents import create_agent
from ..domain.models import MealPlan
from ..agents.state import NutritionAgentState
from ..tools.memory_tools import get_user_preferences, remember_user_fact
from ..tools.nutrition_tools import calculate_macro_targets, analyze_meal_totals
from ..tools.recipe_tools import search_recipe_corpus
from ..tools.safety_tools import supplement_risk_check
from ..tools.skills_tools import load_skill
from ..middleware.groups import planner_middleware
from ..config import settings

PLANNER_SYSTEM_PROMPT = """
You are a senior nutrition-performance meal planning agent.

Rules:
- Use tools for macro math and recipe search.
- Do not invent exact nutrient totals if deterministic tools can calculate them.
- Prefer reusable meal templates and adherence.
- Never diagnose disease, prescribe treatment, or override medication guidance.
- If medications or medical flags appear, be conservative and escalate with warnings.
- Use skills on demand when specialized reasoning is needed.
- Final answer must be structured and implementation-ready.
"""

def build_planner_agent(*, store=None, checkpointer=None):
    return create_agent(
    model=settings.default_model,
    tools=[
        get_user_preferences,
        remember_user_fact,
        calculate_macro_targets,
        analyze_meal_totals,
        search_recipe_corpus,
        supplement_risk_check,
        load_skill,
    ],
    system_prompt=PLANNER_SYSTEM_PROMPT,
    response_format=MealPlan,
    state_schema=NutritionAgentState,
    middleware= planner_middleware() ,
    store=store,
    checkpointer=checkpointer
)

