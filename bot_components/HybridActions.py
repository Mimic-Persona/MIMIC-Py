from typing import Union

from bot_components.BotComponent import BotComponent
from bot_components.BottomUpActions import BottomUpActions
from bot_components.TopDownActions import TopDownActions
from memory_system.MemorySystem import MemorySystem
from skill_system.SkillSystem import SkillSystem
from utils.Bridge import Bridge
from utils.SocketTCP import SocketTCP
from utils.SocketWS import SocketWS
from utils.types import Executor


class HybridActions(BotComponent):
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
            code_model_provider=code_model_provider,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries,
        )
        self.memory_system = memory_system
        self.skill_system = skill_system
        self.socket = socket
        self.bridge = bridge
        self.prompt_root_path = prompt_root_path
        self.analysis_root_path = analysis_root_path
        self.is_retrieve_separate = is_retrieve_separate

        self.bottom_up_actions = BottomUpActions(
            memory_system=self.memory_system,
            skill_system=self.skill_system,
            socket=self.socket,
            bridge=self.bridge,
            is_retrieve_separate=self.is_retrieve_separate,
            prompt_root_path=self.prompt_root_path,
            analysis_root_path=self.analysis_root_path,
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

        self.top_down_actions = TopDownActions(
            memory_system=self.memory_system,
            skill_system=self.skill_system,
            socket=self.socket,
            bridge=self.bridge,
            is_retrieve_separate=self.is_retrieve_separate,
            prompt_root_path=self.prompt_root_path,
            analysis_root_path=self.analysis_root_path,
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
            num_retries=num_retries,
            num_decompose_retries=num_decompose_retries
        )

        self.is_bottom_up = True
        self.is_toggled = False
        self.diverse_count = 0

        self.bot_msg = f"{self.game_subject}:bot_components.HybridActions:log:"
        self.err_msg = f"{self.game_subject}:bot_components.HybridActions:err:"

    def run(
            self,
    ):
        if (not self.is_toggled and
                self.memory_system.count_memories() > self.base_toggle_threshold):
            self.is_bottom_up = False

        if self.is_toggled and self.memory_system.is_action_same_as_last():
            self.diverse_count += 1
        else:
            self.diverse_count = 0

        if self.diverse_count > self.diverse_toggle_threshold:
            self.is_bottom_up = not self.is_bottom_up
            self.diverse_count = 0

        if self.is_bottom_up:
            self.h(f"Running with Bottom-Up Planner")
            self.bottom_up_actions.run()
        else:
            self.h(f"Running with Top-Down Planner")
            self.top_down_actions.run()

