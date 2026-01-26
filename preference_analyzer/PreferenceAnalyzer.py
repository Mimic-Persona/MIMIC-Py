from action_executor.Execution import Execution
from bot_components.BotComponent import BotComponent
from hybrid_planner.Plan import Plan
from memory_system.MemorySystem import MemorySystem
from preference_analyzer.PreferenceAnalysis import PreferenceAnalysis
from summarizer.Summary import Summary
from utils.InputGenerator import generate_preference_analysis_input
from utils.file_utils import read_file, write_file
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class PreferenceAnalyzer(BotComponent):
    def __init__(
            self,
            prompt_root_path: str,
            model_name: str = "openai/gpt-4o",
            model_url: str = "",
            model_provider: str = "",
            signature: str = "system, context, question -> analysis",
            temperature: float = 0,
            max_tokens: int = 4096,
            num_retries: int = 3
    ):
        super().__init__(
            prompt_root_path=prompt_root_path,
            has_llm=True,
            is_code_module=False,
            instruction_model_name=model_name,
            instruction_model_url=model_url,
            instruction_model_provider=model_provider,
            signature=signature,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries
        )

        self.bot_msg = f"{self.game_subject}:preference_analyzer.PreferenceAnalyzer:log:"
        self.err_msg = f"{self.game_subject}:preference_analyzer.PreferenceAnalyzer:err:"

    def compute_preference_level(self, analysis: str) -> int:
        """
        Computes the preference level based on the analysis string.
        :param analysis: The analysis string returned by the LLM.
        :return: An integer representing the preference level.
        """
        pass

    @staticmethod
    def compute_preference_score(
            analysis: str,
            persa_context: str
    ) -> float:
        """
        Computes the preference score based on the Cosine Similarity between the analysis and the personality context.
        :param analysis: The analysis string returned by the LLM.
        :param persa_context: The personality context string used for comparison.
        :return: A float representing the preference score.
        """
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([analysis, persa_context])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return float(similarity[0][0])

    def analyze(
            self,
            memory_system: MemorySystem,
            prev_status: dict,
            analysis_root_path: str,
            plan: Plan,
            execution: Execution,
            summary: Summary,
            verbose: bool = False,
    ) -> PreferenceAnalysis | None:
        """
        Analyzes the preferences based on the current game state, plan, decision, execution results, and summary.
        :param memory_system: The memory system used to count memories.
        :param prev_status: The Previous game state as a dictionary.
        :param analysis_root_path: Root path for saving analysis results.
        :param plan: The plan that was executed.
        :param execution: The execution results of the plan.
        :param summary: The summary of the game state.
        :return: A PreferenceAnalysis object containing the analysis, or None if the analysis could not be generated.
        """
        # Load personality contexts
        personalities_path = f"{self.prompt_root_path}/{self.game_subject}/personalities"
        persa_context = read_file(f"{personalities_path}/{self.personality}.txt")

        # Load main prompt
        prompt_path = f"{self.prompt_root_path}/{self.game_subject}/preference_analyze_prompt.txt"
        context = read_file(prompt_path)

        # Replace placeholders
        context = context.replace("{Personalities}", persa_context)

        # Convert the current game state to prompt input
        input_data = generate_preference_analysis_input(
            game_subject=self.game_subject,
            prev_status=prev_status,
            plan=plan,
            summary=summary,
            execution=execution
        )

        self.c("Query:\n", input_data)

        # Call the language model
        analysis = self.llm.predict(
            verbose=verbose,
            bot_msg=self.bot_msg,
            system="You are a helpful analyzer.",
            context=context,
            question=input_data
        ).analysis

        if not analysis:
            self.e("LLM response was empty. Ignore.")
            return None

        analysis_path = f'{analysis_root_path}/{self.game_subject}/{self.personality}/pa_{memory_system.count_memories()}.txt'

        write_file(analysis_path, analysis)

        analysis = PreferenceAnalysis(
            plan=plan,
            execution=execution,
            analysis_path=analysis_path,
            preference_level=-1,
            preference_score=self.compute_preference_score(analysis, persa_context),
        )

        self.c(f'Preference Analysis of Plan "{plan.plan}":\n', str(analysis.to_dict()))

        return analysis
