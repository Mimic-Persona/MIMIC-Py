import os
import time

from dotenv import load_dotenv

from MIMIC_Minecraft.mc_env.MineEnv import MineEnv
from bot_components.HybridActions import HybridActions
from memory_system.MemorySystem import MemorySystem
from skill_system.SkillSystem import SkillSystem
from utils.Bridge import Bridge
from utils.SocketTCP import SocketTCP
from utils.SocketWS import SocketWS


def run():
    load_dotenv()

    # Initialize code executor for the Action Executor - Plan-to-Code module if needed
    code_executor = None

    exp_duration = int(os.getenv("EXP_DURATION", 125))
    game_subject = os.getenv("GAME_SUBJECT", "MC")
    report_prefix = os.getenv("AGENT_NAME", "example")

    instruction_model_name = os.getenv("INSTRUCTION_MODEL_NAME", "")
    instruction_model_url = os.getenv("INSTRUCTION_MODEL_URL", "")
    instruction_model_path = os.getenv("INSTRUCTION_MODEL_PATH", "")
    instruction_model_provider = os.getenv("INSTRUCTION_MODEL_PROVIDER", "")

    code_model_name = os.getenv("CODE_MODEL_NAME", "")
    code_model_url = os.getenv("CODE_MODEL_URL", "")
    code_model_path = os.getenv("CODE_MODEL_PATH", "")
    code_model_provider = os.getenv("CODE_MODEL_PROVIDER", "")
    prompt_root_path = os.getenv("PROMPT_ROOT_PATH", "./prompts")

    env = None
    if game_subject == "MC":
        env = MineEnv(is_planner_only=False)

        env.reset(
            options={
                "mode": "soft",
                "username": report_prefix
            }
        )

    socket_host = os.getenv("SOCKET_HOST", "127.0.0.1")
    socket_port = int(os.getenv("SOCKET_PORT", "1111"))
    if game_subject == "MC":
        socket = SocketTCP(host=socket_host, port=socket_port)
    else:
        socket = SocketWS(host=socket_host, port=socket_port)

    bridge = Bridge(
        socket=socket,
        mine_env=env,
        timeout=10,
        code_timeout=300,
    )

    ms = MemorySystem(
        prompt_root_path=prompt_root_path,
        embedder="text-embedding-3-small",
        collection_name=f"{game_subject}_{report_prefix}_memory_system",
        persist_directory=f"./memory_system/chroma_store/{game_subject}"
    )

    ss = None
    if (game_subject == "MC" or
            (game_subject not in ["DA", "SPD"] and
             os.getenv("IS_PLAN_TO_CODE", "False").lower() == "true")):
        ss = SkillSystem(
            prompt_root_path=prompt_root_path,
            embedder="text-embedding-3-small",
            collection_name=f"{game_subject}_{report_prefix}_skill_system",
            persist_directory=f"./skill_system/chroma_store/{game_subject}",
            skill_root_directory=f"./skill_system/skill_library/{game_subject}",
        )

    agent = HybridActions(
        memory_system=ms,
        skill_system=ss,
        socket=socket,
        bridge=bridge,
        is_retrieve_separate=True,
        prompt_root_path=prompt_root_path,
        analysis_root_path="./preference_analyzer/analysis",
        instruction_model_name=instruction_model_name,
        instruction_model_url=instruction_model_url,
        instruction_model_path=instruction_model_path,
        instruction_model_provider=instruction_model_provider,
        code_model_name=code_model_name,
        code_model_url=code_model_url,
        code_model_path=code_model_path,
        code_model_provider=code_model_provider,
        code_executor=code_executor,
        temperature=0,
        max_tokens=4096,
        num_retries=3,
        num_decompose_retries=3,
    )

    command = ""
    while command != "1" and command != "b":
        command_dict = agent.bridge.get_command()
        if command_dict:
            agent.c(f"Command received: {command_dict}")
            command = command_dict.get("command", "")

        if command == "s":
            status = agent.bridge.get_status()
            agent.h(f"Current Status: {status}")

    start_time = time.time()

    while time.time() - start_time < exp_duration * 60:
        agent.run()


if __name__ == "__main__":
    run()
