import time
from typing import Union

from action_executor.ActionExecutor import ActionExecutor
from action_executor.Execution import Execution
from action_executor.Feedback import Feedback
from bot_components.BotComponent import BotComponent
from hybrid_planner.Decision import Decision
from hybrid_planner.PlanDecider import PlanDecider
from hybrid_planner.PlanDecomposer import PlanDecomposer
from hybrid_planner.Planner import Planner
from hybrid_planner.TopDownPlan import TopDownPlan
from memory_system.Memory import Memory
from memory_system.MemorySystem import MemorySystem
from preference_analyzer.PreferenceAnalyzer import PreferenceAnalyzer
from skill_system.SkillSystem import SkillSystem
from summarizer.Summarizer import Summarizer
from utils.Bridge import Bridge
from utils.SocketTCP import SocketTCP
from utils.SocketWS import SocketWS
from utils.types import Executor


class TopDownActions(BotComponent):
    def __init__(
            self,
            memory_system: MemorySystem,
            skill_system: SkillSystem,
            socket: Union[SocketTCP, SocketWS],
            bridge: Bridge,
            is_retrieve_separate: bool = True,
            prompt_root_path: str = "./prompts",
            analysis_root_path: str = "./preference_analyzer/analysis",
            instruction_model_name: str = "openai/gpt-4o",
            instruction_model_url: str = "",
            instruction_model_path: str = "",
            instruction_model_provider: str = "",
            code_model_name: str = "openai/gpt-4o",
            code_model_url: str = "",
            code_model_path: str = "",
            code_model_provider: str = "",
            code_executor: Executor = None,
            temperature: float = 0,
            max_tokens: int = 4096,
            num_retries: int = 3,
            num_decompose_retries: int = 3,
    ):
        super().__init__(
            prompt_root_path=prompt_root_path,
            has_llm=False,
            instruction_model_name=instruction_model_name,
            instruction_model_url=instruction_model_url,
            instruction_model_path=instruction_model_path,
            instruction_model_provider=instruction_model_provider,
            code_model_name=code_model_name,
            code_model_url=code_model_url,
            code_model_path=code_model_path,
            code_model_provider=code_model_provider,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries,
        )
        self.socket = socket
        self.bridge = bridge
        self.prompt_root_path = prompt_root_path
        self.analysis_root_path = analysis_root_path
        self.is_retrieve_separate = is_retrieve_separate
        self.num_decompose_retries = num_decompose_retries

        self.memory_system = memory_system
        self.skill_system = skill_system
        self.planner = Planner(
            prompt_root_path=prompt_root_path,
            planner_type="topDown",
            model_name=instruction_model_name,
            model_url=instruction_model_url,
            model_path=instruction_model_path,
            model_provider=instruction_model_provider,
            signature=self.plan_signature,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries
        )
        self.plan_decomposer = PlanDecomposer(
            prompt_root_path=prompt_root_path,
            model_name=instruction_model_name,
            model_url=instruction_model_url,
            model_path=instruction_model_path,
            model_provider=instruction_model_provider,
            signature=self.decomposer_signature,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries
        )
        self.plan_decider = PlanDecider(
            prompt_root_path=prompt_root_path,
            model_name=instruction_model_name,
            model_url=instruction_model_url,
            model_path=instruction_model_path,
            model_provider=instruction_model_provider,
            signature=self.decision_signature,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries
        )
        self.summarizer = Summarizer(
            prompt_root_path=prompt_root_path,
            model_name=instruction_model_name,
            model_url=instruction_model_url,
            model_path=instruction_model_path,
            model_provider=instruction_model_provider,
            signature=self.summary_signature,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries
        )
        self.action_executor = ActionExecutor(
            socket=self.socket,
            bridge=self.bridge,
            prompt_root_path=prompt_root_path,
            skill_system=self.skill_system,
            summarizer=self.summarizer,
            instruction_model_name=instruction_model_name,
            instruction_model_url=instruction_model_url,
            instruction_model_path=instruction_model_path,
            instruction_model_provider=instruction_model_provider,
            code_model_name=code_model_name,
            code_model_url=code_model_url,
            code_model_path=code_model_path,
            code_model_provider=code_model_provider,
            code_executor=code_executor,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries
        )
        self.preference_analyzer = PreferenceAnalyzer(
            prompt_root_path=prompt_root_path,
            model_name=instruction_model_name,
            model_url=instruction_model_url,
            model_path=instruction_model_path,
            model_provider=instruction_model_provider,
            signature=self.preference_analysis_signature,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries
        )

        self.bot_msg = f"{self.game_subject}:bot_components.TopDownActions:log:"
        self.err_msg = f"{self.game_subject}:bot_components.TopDownActions:err:"

    def run(
            self
    ):
        # prev_status = read_json("./prompts/SPD/status_sample.json")
        prev_status = self.bridge.get_status()
        self.c("Prev Status:\n", prev_status)

        # Planner + Plan Decomposer + PlanDecider loop
        latest_bad_plans = []
        latest_bad_sub_plans = []
        sub_plans = []
        curr_plan = None
        plan_decision = False
        while not plan_decision:
            curr_plan = self.planner.plan(
                memory_stream=self.memory_system,
                status=prev_status,
                latest_bad_plans=latest_bad_plans,
                is_retrieve_separate=self.is_retrieve_separate,
            )

            # Decompose the plan for num_decompose_retries times before rejecting it
            plan_decision = True
            for i in range(self.num_decompose_retries):
                sub_plans = self.plan_decomposer.decompose(
                    status=prev_status,
                    plan=curr_plan,
                    latest_bad_sub_plans=latest_bad_sub_plans
                )

                # Any sub-plan rejected, then we need to decompose again
                for plan in sub_plans:
                    decision = self.plan_decider.decide(
                        latest_bad_plans=latest_bad_sub_plans,
                        plan=plan
                    )

                    if not decision.decision:
                        latest_bad_sub_plans.append(decision)
                        plan_decision = False
                        self.c(f'Sub Plan "{plan.plan}" rejected: {decision.reason}')

                if plan_decision:
                    break

            if not plan_decision:
                latest_bad_plans.append(Decision(
                    plan=curr_plan.plan,
                    decision=False,
                    reason="Failed in decomposing this plan.",
                    critique="The plan could not be decomposed into valid sub-plans after multiple attempts. Try a different approach or refine the plan further."
                ))
                self.c(f'Plan "{curr_plan.plan}" rejected due to failed decomposition after {self.num_decompose_retries} tries.')

        # Plan Redefined
        curr_plan = TopDownPlan(
            plan=curr_plan.plan,
            plan_reason=curr_plan.plan_reason,
            sub_plans=sub_plans
        )

        for sp in sub_plans:
            sp.parent_plan = curr_plan

        # Action Executor
        executions = []
        summary, curr_status = None, None

        for sub_plan in sub_plans:
            self.c(f'Executing Sub Plan: {sub_plan.plan}')

            execution, summary, curr_status = self.action_executor.execute(
                prev_status=prev_status,
                plan=curr_plan,
            )

            executions.append(execution)

            if execution.is_error:
                self.e(f'Execution Error:\n{execution}. Stopping the execution of the remaining sub-plans...')
                break

        feedbacks = [feedback for execution in executions for feedback in execution.feedbacks]
        top_feedbacks = Feedback.combine_list_of_feedbacks(feedbacks)

        skills_created = [
            skill
            for execution in executions
            if execution.skills_created  # check first
            for skill in execution.skills_created
        ]

        skills_used = [
            skill
            for execution in executions
            if execution.skills_used  # check first
            for skill in execution.skills_used
        ]


        top_execution = Execution(
            plan=curr_plan,
            feedbacks=top_feedbacks,
            skills_created=skills_created,
            skills_used=skills_used
        )

        if not self.is_plan_to_code:
            curr_status = self.bridge.get_status()
            self.c("Curr Status:\n", curr_status)

            # Summarizer
            summary = self.summarizer.summarize(
                prev_status=prev_status,
                curr_status=curr_status,
                plan=curr_plan,
                execution=top_execution,
            )

        # Preference Analysis
        analysis = None
        while not analysis:
            analysis = self.preference_analyzer.analyze(
                memory_system=self.memory_system,
                prev_status=prev_status,
                analysis_root_path=self.analysis_root_path,
                plan=curr_plan,
                execution=top_execution,
                summary=summary
            )

        timestamp = time.time()

        self.memory_system.store_memory(Memory(
            memory_id=self.memory_system.count_memories(),
            personality=self.personality,
            prev_env=str(prev_status),
            post_env=str(curr_status),
            plan=curr_plan,
            execution=top_execution,
            summary=summary,
            preference_analysis=analysis,
            time_created=timestamp,
            time_accessed=timestamp,
            time_expired=None
        ))
