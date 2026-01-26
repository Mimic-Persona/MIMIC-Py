from action_executor.Code import Code
from action_executor.ResultPrediction import ResultPrediction
from utils.StatusFormatter import StatusFormatter
from action_executor.Execution import Execution
from hybrid_planner.Decision import Decision
from hybrid_planner.Plan import Plan
from memory_system.MemorySystem import MemorySystem
from summarizer.Summary import Summary


def generate_planner_input(
        game_subject: str,
        status: dict,
        memory_system: MemorySystem,
        latest_bad_plans: list[Decision],
        prefix : str = "",
        is_planner_only: bool = False,
        recent_plans: list[Plan | dict] | None = None
) -> str:
    """
    Generates a formatted input string for the planner based on the current status and memory system.
    :param game_subject: The subject of the game, used for context.
    :param status: Current game status as a dictionary.
    :param memory_system: Memory system to retrieve recent and relevant memories.
    :param latest_bad_plans: List of the latest rejected plans to inform the planner.
    :param prefix: Optional, a prefix to prepend to each line of the input data.
    :param is_planner_only: If True, it is in the exp of only having the planner.
    :param recent_plans: Optional, a list of recent plans to include in the input. Only used if is_planner_only is True.
    :return: A formatted string containing the current status, recent plans, related plans, and preferred tasks.
    """
    res = StatusFormatter.get_current_status(
        game_subject=game_subject,
        status=status,
        prefix=prefix
    )

    if latest_bad_plans:
        res += "Latest rejected plans: "
        for decision in latest_bad_plans:
            res += f"{decision.to_planner_input()}; "

    if not is_planner_only:
        recent_memories = memory_system.retrieve_by_recency()
        if recent_memories:
            last_memory = recent_memories.pop(0)
            res += f"\nPlan from last round: {last_memory.plan}"
            res += f"\nSuggestion for the next task: {last_memory.summary.critique}"

            res += "\nRecent plans: "
            for memory in recent_memories:
                res += f"{memory.to_planner_input()}; "

    else:
        if recent_plans:
            last_plan = recent_plans[0]
            res += f"\nPlan from last round: {last_plan.get('plan')}"
            res += f"\nHas the last plan been successful? {last_plan.get('is_success')}"
            res += f"\nSuggestion for the next task: {last_plan.get('critique')}"

        res += "\nRecent plans: "
        for i in range(1, len(recent_plans)):
            res += f"{recent_plans[i]}; "

    if not is_planner_only:
        related_memories = memory_system.retrieve_by_relevance(str(status))
        if related_memories:
            res += "\nRelated plans did before: "
            for memory in related_memories:
                res += f"{memory.to_planner_input()}; "

    if not is_planner_only:
        preferred_memories = memory_system.retrieve_by_preference()
        if preferred_memories and not is_planner_only:
            res += "\nPreferred tasks by the personality you have: "
            for memory in preferred_memories:
                res += f"{memory.to_planner_input()}; "

    return res


def generate_plan_decomposer_input(
        game_subject: str,
        status: dict,
        plan: Plan,
        latest_bad_sub_plans: list[Decision],
        prefix : str = "",
) -> str:
    """
    Generates a formatted input string for the plan decomposer based on the plan and latest rejected sub-plans.
    :param game_subject: The subject of the game, used for context.
    :param status: Current game status as a dictionary.
    :param plan: The plan to be decomposed.
    :param latest_bad_sub_plans: A tuple containing two lists:
    :param prefix: Optional, a prefix to prepend to each line of the input data.
    :return: A formatted string containing the plan and latest rejected sub-plans.
    """
    res = StatusFormatter.get_current_status(
        game_subject=game_subject,
        status=status,
        prefix=prefix
    )

    res += "Plan: " + plan.plan + "\n"
    res += "Plan reason: " + plan.plan_reason + "\n"

    if latest_bad_sub_plans:
        res += f"Latest rejected sub-plans: "
        for i in range(len(latest_bad_sub_plans)):
            if not latest_bad_sub_plans[i].decision:
                res += f"{latest_bad_sub_plans[i].plan} rejected since {latest_bad_sub_plans[0][i].reason}\n"

    return res

def generate_code_generator_input(
        game_subject: str,
        status: dict,
        plan: Plan,
        prev_code: Code = None,
        prev_execution: Execution = None,
        prev_summary: Summary = None,
        prefix : str = "",
) -> str:
    """
    Generates a formatted input string for the code generator based on the current status, plan, and previous execution details.
    :param game_subject: The subject of the game, used for context.
    :param status: Current game status as a dictionary.
    :param plan: Plan, The plan to be executed.
    :param prev_code: The code from the last round, if any.
    :param prev_execution: The execution results from the last round, if any.
    :param prev_summary: The summary from the last round, if any.
    :param prefix: Optional, a prefix to prepend to each line of the input data.
    :return: A formatted string containing the current status, previous code, execution feedback, and plan details.
    """
    res = StatusFormatter.get_current_status(
        game_subject=game_subject,
        status=status,
        prefix=prefix
    )

    if prev_code:
        res += "Code from the last round: " + prev_code.code + "\n"

    if prev_execution:
        for feedback in prev_execution.feedbacks:
            if feedback.is_error:
                res += f"Error message from the last round: {feedback.message}\n"
            else:
                res += f"Log message from the last round: {feedback.message}\n"
    if prev_summary:
        res += "Critique from the last round: " + prev_summary.critique + "\n"

    res += "Plan: " + plan.plan + "\n"
    res += "Plan reason: " + plan.plan_reason + "\n"

    return res

def generate_result_predictor_input(
        plan: Plan,
        prefix : str = "",
) -> str:
    """
    Generates a formatted input string for the result predictor based on the current status and plan.
    :param plan: The plan to be executed.
    :param prefix: Optional, a prefix to prepend to each line of the input data.
    :return: A formatted string containing the current status and plan details.
    """
    res = "Plan: " + plan.plan + "\n"
    res += "Plan reason: " + plan.plan_reason + "\n"

    return res

def generate_time_predictor_input(
        game_subject: str,
        status: dict,
        plan: Plan,
        result_prediction: ResultPrediction,
        code: str,
        prefix : str = "",
) -> str:
    """
    Generates a formatted input string for the time predictor based on the current status, plan, and expected results.
    :param game_subject:
    :param status:
    :param plan:
    :param result_prediction:
    :param code:
    :param prefix: Optional, a prefix to prepend to each line of the input data.
    :return:
    """
    res = StatusFormatter.get_current_status(
        game_subject=game_subject,
        status=status,
        prefix=prefix
    )

    res += "Plan: " + plan.plan + "\n"
    res += "Plan reason: " + plan.plan_reason + "\n"
    res += "Expectation: " + result_prediction.to_context_input() + "\n"
    res += "Expectation reason: " + result_prediction.prediction_reason + "\n"
    res += "Code: " + code + "\n"

    return res


def generate_summarizer_input(
        game_subject: str,
        prev_status: dict,
        curr_status: dict,
        plan: Plan,
        execution: Execution,
        prefix : str = "",
) -> str:
    """
    Generates a formatted input string for the summarizer based on the previous and current status, plan, and execution results.
    :param game_subject: The subject of the game, used for context.
    :param prev_status: The Previous game state as a dictionary.
    :param curr_status: The Current game states as a dictionary.
    :param plan: The plan that was executed.
    :param execution: The execution results of the plan.
    :param prefix: Optional, a prefix to prepend to each line of the input data.
    :return: A formatted string containing the previous status, current status, plan details, and execution feedback.
    """
    res = StatusFormatter.get_current_status(
        game_subject=game_subject,
        status=curr_status,
        prefix=prefix,
        prev_status= prev_status,
    )

    res += "Plan: " + plan.plan + "\n"
    res += "Plan reason: " + plan.plan_reason + "\n"

    for feedback in execution.feedbacks:
        if feedback.is_error:
            res += f"Error message: {feedback.message}\n"
        else:
            res += f"Log message: {feedback.message}\n"

    return res


def generate_preference_analysis_input(
        game_subject: str,
        prev_status: dict,
        plan: Plan,
        summary: Summary,
        execution: Execution = None,
        prefix : str = "",
) -> str:
    """
    Generates a formatted input string for preference analysis based on the previous status, plan, decision, execution, and summary.
    :param game_subject: The subject of the game, used for context.
    :param prev_status: The Previous game state as a dictionary.
    :param plan: The plan that was executed.
    :param summary: The summary of the game state.
    :param execution: The execution results of the plan.
    :param prefix: Optional, a prefix to prepend to each line of the input data.
    :return: A formatted string containing the input data for preference analysis.
    """
    curr_status = StatusFormatter.get_current_status(
        game_subject=game_subject,
        status=prev_status,
        prefix=prefix
    )

    res = "Is Success: " + str(summary.is_success) + "\n"
    res += "Plan: " + plan.plan + "\n"
    res += "Plan reason: " + plan.plan_reason + "\n"
    res += "Previous status: {\n" + curr_status + "}\n"
    res += "Summary reason: " + summary.summary + "\n"
    res += "Critique: " + summary.critique + "\n"

    if execution and execution.skills_used:
        res += "Skills: " + str(execution.skills_used) + "\n"

    return res
