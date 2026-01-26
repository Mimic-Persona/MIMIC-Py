import time
from typing import Union

from action_executor.ActionExecutor import ActionExecutor
from bot_components.BotComponent import BotComponent
from hybrid_planner.PlanDecider import PlanDecider
from hybrid_planner.Planner import Planner
from memory_system.Memory import Memory
from memory_system.MemorySystem import MemorySystem
from preference_analyzer.PreferenceAnalyzer import PreferenceAnalyzer
from skill_system.SkillSystem import SkillSystem
from summarizer.Summarizer import Summarizer
from utils.Bridge import Bridge
from utils.types import Executor
from utils.SocketTCP import SocketTCP
from utils.SocketWS import SocketWS


class BottomUpActions(BotComponent):
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

        self.memory_system = memory_system
        self.skill_system = skill_system
        self.planner = Planner(
            prompt_root_path=prompt_root_path,
            planner_type="bottomUp",
            model_name=instruction_model_name,
            model_url=instruction_model_url,
            model_path=instruction_model_path,
            model_provider=instruction_model_provider,
            signature=self.plan_signature,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries
        )
        self.plan_decider = PlanDecider(
            prompt_root_path=prompt_root_path,
            model_name=instruction_model_name,
            model_url=instruction_model_url,
            model_provider=instruction_model_provider,
            signature=self.decomposer_signature,
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
            instruction_model_provider=instruction_model_provider,
            code_model_name=code_model_name,
            code_model_url=code_model_url,
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
            model_provider=instruction_model_provider,
            signature=self.preference_analysis_signature,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries
        )

        self.bot_msg = f"{self.game_subject}:bot_components.BottomUpActions:log:"
        self.err_msg = f"{self.game_subject}:bot_components.BottomUpActions:err:"

    def run(
            self
    ):
        prev_status = self.bridge.get_status()
        self.c("Prev Status:\n", prev_status)

        # Planner + PlanDecider loop
        latest_bad_plans = []

        curr_plan = None
        plan_decision = None
        while not plan_decision or not plan_decision.decision:
            curr_plan = self.planner.plan(
                memory_stream=self.memory_system,
                status=prev_status,
                latest_bad_plans=latest_bad_plans,
                is_retrieve_separate=self.is_retrieve_separate,
            )

            plan_decision = self.plan_decider.decide(
                latest_bad_plans=latest_bad_plans,
                plan=curr_plan
            )

            if not plan_decision.decision:
                latest_bad_plans.append(plan_decision)
                self.c(f'Plan "{curr_plan.plan}" rejected: {plan_decision.reason}')

        # Action Executor
        execution, summary, curr_status = self.action_executor.execute(
            prev_status=prev_status,
            plan=curr_plan,
        )

        if not self.is_plan_to_code:
            curr_status = self.bridge.get_status()
            self.c("Curr Status:\n", curr_status)

            # Summarizer
            summary = self.summarizer.summarize(
                prev_status=prev_status,
                curr_status=curr_status,
                plan=curr_plan,
                execution=execution,
            )

        # Preference Analysis
        analysis = None
        while not analysis:
            analysis = self.preference_analyzer.analyze(
                memory_system=self.memory_system,
                prev_status=prev_status,
                analysis_root_path=self.analysis_root_path,
                plan=curr_plan,
                execution=execution,
                summary=summary
            )

        timestamp = time.time()

        self.memory_system.store_memory(Memory(
            memory_id=self.memory_system.count_memories(),
            personality=self.personality,
            prev_env=str(prev_status),
            post_env=str(curr_status),
            plan=curr_plan,
            execution=execution,
            summary=summary,
            preference_analysis=analysis,
            time_created=timestamp,
            time_accessed=timestamp,
            time_expired=None
        ))
