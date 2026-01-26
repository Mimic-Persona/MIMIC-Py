import time
from typing import Union

from action_executor.Code import Code
from action_executor.CodeGenerator import CodeGenerator
from action_executor.Execution import Execution
from action_executor.Feedback import Feedback
from action_executor.ResultPredictor import ResultPredictor
from action_executor.SkillDescriber import SkillDescriber
from action_executor.TimePredictor import TimePredictor
from bot_components.BotComponent import BotComponent
from hybrid_planner.Plan import Plan
from skill_system.Skill import Skill
from skill_system.SkillSystem import SkillSystem
from summarizer.Summarizer import Summarizer
from summarizer.Summary import Summary
from utils.Bridge import Bridge
from utils.SocketTCP import SocketTCP
from utils.SocketWS import SocketWS
from utils.types import Executor


class ActionExecutor(BotComponent):
    def __init__(
            self,
            socket: Union[SocketTCP, SocketWS],
            bridge: Bridge,
            prompt_root_path: str,
            skill_system: SkillSystem = None,
            summarizer: Summarizer = None,
            instruction_model_name: str = "openai/gpt-4o",
            instruction_model_url: str = "",
            instruction_model_provider: str = "",
            code_model_name: str = "openai/gpt-4o",
            code_model_url: str = "",
            code_model_provider: str = "",
            code_executor: Executor = None,
            temperature: float = 0,
            max_tokens: int = 4096,
            num_retries: int = 3,
    ):
        super().__init__(
            prompt_root_path=prompt_root_path,
            has_llm=False
        )

        self.socket = socket
        self.bridge = bridge
        self.skill_system = skill_system
        self.code_executor = code_executor

        self.result_predictor = None
        self.code_generator = None
        self.time_predictor = None
        self.summarizer = None
        self.skill_describer = None

        if self.is_plan_to_code:
            self.result_predictor = ResultPredictor(
                prompt_root_path=prompt_root_path,
                model_name=instruction_model_name,
                model_url=instruction_model_url,
                model_provider=instruction_model_provider,
                signature=self.result_prediction_signature,
                temperature=temperature,
                max_tokens=max_tokens,
                num_retries=num_retries
            )

            self.code_generator = CodeGenerator(
                prompt_root_path=prompt_root_path,
                skill_system=self.skill_system,
                model_name=code_model_name,
                model_url=code_model_url,
                model_provider=code_model_provider,
                signature=self.code_signature,
                temperature=temperature,
                max_tokens=max_tokens,
                num_retries=num_retries
            )

            self.time_predictor = TimePredictor(
                prompt_root_path=prompt_root_path,
                model_name=instruction_model_name,
                model_url=instruction_model_url,
                model_provider=instruction_model_provider,
                signature=self.time_prediction_signature,
                temperature=temperature,
                max_tokens=max_tokens,
                num_retries=num_retries
            )

            self.summarizer = summarizer

            self.skill_describer = SkillDescriber(
                prompt_root_path=prompt_root_path,
                model_name=instruction_model_name,
                model_url=instruction_model_url,
                model_provider=instruction_model_provider,
                signature=self.skill_description_signature,
                temperature=temperature,
                max_tokens=max_tokens,
                num_retries=num_retries
            )

        self.bot_msg = f"{self.game_subject}:action_executor.ActionExecutor:log:"
        self.err_msg = f"{self.game_subject}:action_executor.ActionExecutor:err:"

    def _plan_to_action(
            self,
            plan: Plan
    ) -> tuple[Execution, None, None]:
        """
        Executes a plan by directly acting on it and returning the execution result.
        :param plan: The plan to be executed.
        :return: Execution and None.
        """
        feedbacks = self.bridge.act_and_feedback(
            plan=plan
        )

        execution = Execution(
            plan=plan,
            feedbacks=feedbacks
        )

        self.c(f'Parameter execution of "{plan.plan}:"\n', str(execution.to_dict()))

        return execution, None, None

    def _execute_code(
            self,
            plan: Plan,
            code: Code,
            timeout: float,
            num_retries: int,
    ) -> tuple[Execution, dict | None]:
        """
        Executes the code generated for a plan, simulating the action and returning the execution result.
        :param plan: The plan to be executed.
        :param code: The code generated for the plan.
        :param timeout: The time limit for the code execution.
        :param num_retries: The number of retries for the code execution.
        :return: Execution object containing the results of the code execution.
        """
        code_to_run = self.skill_system.skill_imports
        code_to_run += f"{code.code}\n\n"

        if code_to_run.startswith("```"):
            # Remove the first line if it starts with "```"
            code_to_run = code_to_run.split("\n", 1)[1]

        # Remove the last line if it ends with "```"
        if code_to_run.endswith("```"):
            code_to_run = code_to_run.rsplit("\n", 1)[0]

        if not code or not code_to_run:
            raise ValueError("Code is empty or not provided.")

        # Prepare the called codes for execution
        code_to_run += self.skill_system.used_skills_name_to_code(code.used_skills_name)

        if self.code_language == "javascript":
            programs = f"await {code.skill_name}(bot, mcData);"

        else:
            raise ValueError(f"Unsupported code language: {self.code_language}")

        self.h(f"Executing the code:\n{programs}\n{code_to_run}")

        obs, info = self.bridge.run_and_feedback(
            code=code_to_run,
            programs=programs,
            timeout=timeout,
            executor=self.code_executor,
        )

        feedbacks = []
        if info["bot_msg"]:
            log_feedback = info["bot_msg"]
            feedbacks.append(Feedback(False, log_feedback))

        if info["err_msg"]:
            err_feedback = info["err_msg"]
            feedbacks.append(Feedback(True, err_feedback))

        execution = Execution(
            plan=plan,
            feedbacks=feedbacks,
            is_timeout=info["is_timeout"],
            skills_created=code.skill_name,
            skills_used=code.used_skills_name,
        )

        # # Action Execution
        # log_feedback = f"Stone mined."
        # err_feedback = f"Need an iron pickaxe to mine diamond ore."
        #
        # good_feedback = Feedback(False, log_feedback)
        # bad_feedback = Feedback(True, err_feedback)
        #
        # # feedbacks = [good_feedback, bad_feedback]
        # feedbacks = [good_feedback]
        #
        # execution = Execution(
        #     plan=plan,
        #     feedbacks=feedbacks,
        #     is_timeout=False,
        # )

        self.h(f'Code execution (retries: {num_retries}) of "{plan.plan}:"\n', str(execution.to_dict()))

        return execution, obs

    def _plan_to_code(
            self,
            init_status: dict,
            plan: Plan,
    ) -> tuple[Execution, Summary, dict]:
        """
        Converts a plan into code, executes it, and returns the execution result and summary.
        :param init_status: The previous status of the game.
        :param plan: The plan to be executed.
        :return: Execution and Summary objects.
        """
        prev_code = None
        prev_execution = None
        prev_summary = None

        # Result Predictor
        num_retries = 0
        result_prediction = None
        while not result_prediction and num_retries < self.num_retries:
            try:
                result_prediction = self.result_predictor.predict(
                    plan=plan
                )
            except Exception as e:
                self.e(f"Error in result prediction: {e}")
                result_prediction = None

            num_retries += 1

        assert num_retries < self.num_retries, "Result prediction failed after maximum retries."

        prev_status = init_status
        num_retries = 0
        execution = None
        summary = None
        curr_status = None
        code = None

        # Regenerate and execute the code until a successful summary is obtained,
        # or the maximum number of retries is reached
        while not summary or (not summary.is_success and num_retries < self.num_code_reties):
            # Code Generator
            retry_count = 0
            code = None
            while not code and retry_count < self.num_retries:
                try:
                    code = self.code_generator.generate(
                        status=prev_status,
                        plan=plan,
                        prev_code=prev_code.code if prev_code else "",
                        prev_execution=prev_execution,
                        prev_summary=prev_summary,
                    )
                except Exception as e:
                    self.e(f"Error in code generation: {e}")
                    code = None
                retry_count += 1

            assert retry_count < self.num_retries, "Code generation failed after maximum retries."

            # Time Predictor
            retry_count = 0
            time_prediction = None
            while not time_prediction and retry_count < self.num_retries:
                try:
                    time_prediction = self.time_predictor.predict(
                        curr_status=prev_status,
                        plan=plan,
                        result_prediction=result_prediction,
                        code=code.code,
                    )
                except Exception as e:
                    self.e(f"Error in time prediction: {e}")
                    time_prediction = None
                retry_count += 1

            assert retry_count < self.num_retries, "Time prediction failed after maximum retries."
    
            execution, curr_status = self._execute_code(
                plan=plan,
                code=code,
                timeout=time_prediction.prediction,
                num_retries=num_retries,
            )

            self.c("Curr Status:\n", curr_status)

            # Summarizer
            retry_count = 0
            summary = None
            while not summary and retry_count < self.num_retries:
                try:
                    summary = self.summarizer.summarize(
                        prev_status=init_status,
                        curr_status=curr_status,
                        plan=plan,
                        execution=execution,
                    )
                except Exception as e:
                    self.e(f"Error in summarization: {e}")
                    summary = None
                retry_count += 1

            assert retry_count < self.num_retries, "Summarization failed after maximum retries."

            num_retries += 1
            prev_status = curr_status

        retry_count = 0
        description = ""
        while not description and retry_count < self.num_retries:
            assert code is not None, "Code must be generated before describing the skill."
            try:
                description = self.skill_describer.describe(code.code)
            except Exception as e:
                self.e(f"Error in skill description: {e}")
                description = ""
            retry_count += 1

        assert retry_count < self.num_retries, "Skill description failed after maximum retries."

        timestamp = time.time()

        skill = Skill(
            skill_id=self.skill_system.count_skills(),
            skill_name=code.skill_name,
            skill_root_path= f"{self.skill_system.skill_root_directory}/generated_skills/{self.report_prefix}",
            code=code.code,
            description=description,
            used_skills_ids=self.skill_system.retrieve_ids_by_names(code.used_skills_name),
            used_skills_names=code.used_skills_name,
            code_language=self.code_language,
            language_file_extension=self.language_file_extension,
            time_created=timestamp,
            time_accessed=timestamp,
            time_expired=None,
            is_from_chroma=False,
        )

        self.skill_system.store_skill(skill)

        return execution, summary, curr_status

    def execute(
            self,
            prev_status: dict,
            plan: Plan,
    ) -> tuple[Execution, Summary, dict]:
        """
        Executes a plan and returns the execution result and summary.
        :param prev_status: The previous status of the game.
        :param plan: The plan to be executed.
        :return: Execution and Summary objects.
        """
        if self.is_plan_to_code:
            res = self._plan_to_code(
                init_status=prev_status,
                plan=plan,
            )

        else:
            res = self._plan_to_action(
                plan=plan,
            )

        return res
