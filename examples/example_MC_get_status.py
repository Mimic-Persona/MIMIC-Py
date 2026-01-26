import os

from dotenv import load_dotenv

from MIMIC_Minecraft.mc_env.MineEnv import MineEnv
from utils.Bridge import Bridge
from utils.SocketTCP import SocketTCP


def main():
    load_dotenv()

    report_prefix = os.getenv("AGENT_NAME", "example")

    env = MineEnv()
    env.reset(
        options={
            "mode": "soft",
            "username": report_prefix
        }
    )

    socket_host = os.getenv("SOCKET_HOST", "127.0.0.1")
    socket_port = int(os.getenv("SOCKET_PORT", "1111"))

    socket = SocketTCP(host=socket_host, port=socket_port)

    bridge = Bridge(
        socket=socket,
        mine_env=env,
        timeout=10,
        code_timeout=300,
    )

    print(bridge.get_status())


if __name__ == "__main__":
    main()
