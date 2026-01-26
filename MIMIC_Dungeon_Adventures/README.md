![logo](https://user-images.githubusercontent.com/106514178/227779667-51a0dbef-5e22-4cd8-8ba9-002bb418530f.png)

# Game Description

🗡️**Dungeon Adventures** is a project inspired by roguelike games. Roguelike is an exciting and challenging game genre in which players take on the role of a character exploring a procedurally generated dungeon.

🎯 The goal of the game is to reach the end of the dungeon while fighting off dangerous monsters and collecting treasure along the way, all while uncovering the truth about the main character. **Get ready for an epic adventure!**

🌟 The game consists of two levels where the hero must face a large number of monsters. By collecting items, the hero's abilities increase. After completing the labyrinth, the hero must face a boss. If he defeat the boss, he will be teleported to a room with crowns where he will be put to the test of wit and must find the crown that stands out.

This game is a modified version dedicated to MIMIC-Py, check the original game from https://github.com/stelmaszczykadrian/Dungeon-Adventures

# How to Run MIMIC-Py

## Prerequisites
- This game supports running only tested on Windows.

## IMPORTANT
- Make sure your working directory is set to the `MIMIC-Python` directory, as all commands and configurations will be based on this path.
- **Before starting the configuration in this section**, please **make sure** you have completed the general setup of MIMIC-Py as described in the [main README file](../README.md) and set `GAME_SUBJECT` in `.env` file to `DA`.

## Virtual Machine [Recommended for Demonstration Only]
1. If you are using a VM for running MIMIC-Py, please make sure you follow information about general setup for VM is provided in the [main README file](../README.md#virtual-machine-recommended-for-demonstration-only).

2. Then you can jump to Section [Run the Game and Start the Server](./README.md#run-the-game-and-start-the-server) at step 2.


## Run the Game and Start the Server
1. Ensure a [JDK (Java Development Kit)](https://www.oracle.com/java/technologies/javase/jdk22-archive-downloads.html) is installed on your computer. (Java 22 is tested)

2. Run `./src/main/java/com/codecool/dungeoncrawl/App.java` file to start the game, you can find it [here](./src/main/java/com/codecool/dungeoncrawl/App.java).

3. Click on the `New Adventure` button and then the `Start the Game` to start the game and server once you see the main game window.

4. Before running MIMIC-Py, make sure you are in the game, and you should see the following output in the console:
   
   ```
   SLF4J: No SLF4J providers were found.
   SLF4J: Defaulting to no-operation (NOP) logger implementation
   SLF4J: See https://www.slf4j.org/codes.html#noProviders for further details.
   $$ MIMIC Mode Enabled!
   Log file appended successfully.
   Log file appended successfully.
   Log file appended successfully.
   $$ agent.GameServer: GameServer started on port: /127.0.0.1:1111
   Log file appended successfully.
   ```
   
### Note

Please ignore the following error messages, since they are related to the Jacoco code coverage tool and do not affect the functionality of MIMIC-Py or the game:
```
java.net.ConnectException: Connection refused: connect
	at java.base/sun.nio.ch.Net.connect0(Native Method)
	at java.base/sun.nio.ch.Net.connect(Net.java:589)
	at java.base/sun.nio.ch.Net.connect(Net.java:578)
	at java.base/sun.nio.ch.NioSocketImpl.connect(NioSocketImpl.java:583)
	at java.base/java.net.SocksSocketImpl.connect(SocksSocketImpl.java:327)
	at java.base/java.net.Socket.connect(Socket.java:752)
	at java.base/java.net.Socket.connect(Socket.java:687)
	at java.base/java.net.Socket.<init>(Socket.java:556)
	at java.base/java.net.Socket.<init>(Socket.java:357)
	at org.jacoco.core.tools.ExecDumpClient.tryConnect(ExecDumpClient.java:144)
	at org.jacoco.core.tools.ExecDumpClient.dump(ExecDumpClient.java:116)
	at org.jacoco.core.tools.ExecDumpClient.dump(ExecDumpClient.java:99)
	at com.codecool.dungeoncrawl.agent.reporter.JacocoReporter.dumpData(JacocoReporter.java:304)
	at com.codecool.dungeoncrawl.agent.reporter.JacocoReporter.dumpData(JacocoReporter.java:362)
	...
```

## Run MIMIC-Py in Dungeon Adventures
1. Once you are in the game, you can start MIMIC-Py by running the `run.py` file [here](../run.py), 
or by running the following command in the terminal while in the `./MIMIC_Shattered_Pixel_Dungeon` directory:
    ```bash
    python ../run.py
    ```

2. After running the command, you should see the following output:

   ```
   [INFO] File written successfully: ./out/DA//openai/gpt-4o/out_2026-01-23_20-52-57_example.log
   INFO:websocket:Websocket connected
   INFO:Socket:✅ Connected (WebSocket) to ws://127.0.0.1:1111
   $$ DA:memory_system.MemorySystem:log: Memory System initialized with 0 memories.
   ```

3. Now, MIMIC-Py is running and ready to interact with the game. You can press the key `B` on your keyboard to start MIMIC-Py.

[//]: # (## [Option 1] Run MIMIC-P Baseline)

[//]: # (1. Once you are in the game, open a terminal and navigate to the `./MIMIC_Dungeon_Adventures` directory.)

[//]: # ()
[//]: # (   ```bash)

[//]: # (    cd ./MIMIC_Dungeon_Adventures)

[//]: # (   ```)

[//]: # ()
[//]: # (2. Run the following command to start MIMIC-P:)

[//]: # ()
[//]: # (    ```bash)

[//]: # (    node ./src/main/java/com/codecool/dungeoncrawl/agent/LLMBaseline/LLMPlannerAgentClient.js)

[//]: # (    ```)

[//]: # ()
[//]: # (3. After running the command, you should see the following output:)

[//]: # ()
[//]: # (    ```)

[//]: # (    LLMBaseline.LLMPlannerAgent:log LLMPlannerAgent connected to WebSocket server.)

[//]: # (    ```)

[//]: # ()
[//]: # (4. Now, MIMIC-P is running and ready to interact with the game. You can start MIMIC-P by pressing the key `L` on your keyboard while playing the game.)

[//]: # ()
[//]: # ()
[//]: # (## [Option 2] Run MIMIC-P+S Baseline)

[//]: # (1. Once you are in the game, open a terminal and navigate to the `./MIMIC_Dungeon_Adventures` directory.)

[//]: # ()
[//]: # (   ```bash)

[//]: # (    cd ./MIMIC_Dungeon_Adventures)

[//]: # (   ```)

[//]: # ()
[//]: # (2. Run the following command to start MIMIC-P:)

[//]: # ()
[//]: # (    ```bash)

[//]: # (    node ./src/main/java/com/codecool/dungeoncrawl/agent/LLMBaseline/LLMPlannerSummarizerAgentClient.js)

[//]: # (    ```)

[//]: # ()
[//]: # (3. After running the command, you should see the following output:)

[//]: # ()
[//]: # (    ```)

[//]: # (    LLMBaseline.LLMPlannerSummarizerAgent:log LLMPlannerSummarizerAgent connected to WebSocket server.)

[//]: # (    ```)

[//]: # ()
[//]: # (4. Now, MIMIC-P+S is running and ready to interact with the game. You can start MIMIC-P+S by pressing the key `K` on your keyboard while playing the game.)

[//]: # ()
[//]: # ()
[//]: # (## [Option 3] Run Monkey Baselines)

[//]: # (1. Once you are in the game, Monkey is ready to interact with the game. You can start Monkey by pressing the key `R` on your keyboard while playing the game.)

[//]: # ()
[//]: # (2. Set the "IS_SMART_MONKEY" in your `config.json` file to `true` if you want to use the Smart Monkey baseline, or `false` if you want to use the Dumb Monkey baseline.)

[//]: # ()
[//]: # (# :rocket: Screenshots)

[//]: # (![dungeon1]&#40;https://github.com/stelmaszczykadrian/Dungeon-Adventures/assets/106514178/1b4a7d3b-aab3-4505-ad88-d33bff9848fe&#41;)

[//]: # (<br>)

[//]: # (![dungeon2]&#40;https://github.com/stelmaszczykadrian/Dungeon-Adventures/assets/106514178/aec45150-3835-4c2c-ac06-a11366fb0387&#41;)

[//]: # (<br>)

[//]: # (![dungeon3]&#40;https://github.com/stelmaszczykadrian/Dungeon-Adventures/assets/106514178/228c324a-46cb-43ed-b295-7b7c0946fa1f&#41;)

[//]: # (<br>)

# Game States
Notice, the game states are defined by the researchers according to the understanding to the game and the code.
They are not necessarily the same as the game states intentionally done by the original game developers since the original game states were not provided in the original game repository.
As a result, these game states are subject to change in the future, and none of them is used in the evaluation of MIMIC-Py.

![DA Game States](../images/DA/DA_Game_States.png)