![logo](https://shatteredpixel.com/assets/images/SHPD-Desc/title.gif)

# Game Description

[Shattered Pixel Dungeon](https://shatteredpixel.com/shatteredpd/) is an open-source traditional roguelike dungeon crawler with randomized levels 
and enemies, and hundreds of items to collect and use. 
It's based on the [source code of Pixel Dungeon](https://github.com/00-Evan/pixel-dungeon-gradle), by [Watabou](https://www.watabou.ru).

Shattered Pixel Dungeon compiles for Android, iOS, and Desktop platforms.

This game is a modified version dedicated to MIMIC-Py, check the original game at https://github.com/00-Evan/shattered-pixel-dungeon on [**v2.4.0**](https://github.com/00-Evan/shattered-pixel-dungeon/compare/v2.4.0...3.1.0-BETA)

# How to Run MIMIC-Py

## Prerequisites
- This game supports running on Windows, Android, and IOS. But the MIMIC-Py agent for SPD is only tested on Windows.

## IMPORTANT
- Make sure your working directory is set to the `MIMIC-Python` directory, as all commands and configurations will be based on this path.
- **Before starting the configuration in this section**, please **make sure** you have completed the general setup of MIMIC-Py as described in the [main README file](./README.md) and set `GAME_SUBJECT` in `.env` file to `SPD`.

## Virtual Machine [Recommended for Demonstration Only]
1. If you are using a VM for running MIMIC-Py, please make sure you follow information about general setup for VM is provided in the [main README file](../README.md#virtual-machine-recommended-for-demonstration-only).

2. Then you can jump to Section [Run the Game and Start the Server](./README.md#run-the-game-and-start-the-server) at step 2.


## Run the Game and Start the Server

1. Ensure a [JDK (Java Development Kit)](https://www.oracle.com/java/technologies/javase/jdk21-archive-downloads.html) is installed on your computer. (Java 21 is tested)

2. Navigate to the `./MIMIC_Shattered_Pixel_Dungeon` directory.

    ```bash
    cd ./MIMIC_Shattered_Pixel_Dungeon
    ```
   
3. Run the following command to start the game in debug mode:

    ```bash
    ./gradlew desktop:debug
    ```

4. Click on the `Enter the Dungeon` button and then the `New Game` to start choosing the character. Choose Warrior as the character and then click on the `Start` button to start the game.
   - To be noticed, in the experiment, only the Warrior character is used for fairness and consistency.
   - Please only choose the Warrior character, as MIMIC-Py is only tested with this Warrior character.

5. Before running any tools, make sure you are in the game. And you should see the following output in the console:

    ```
    > Task :desktop:debug
   [Controllers] added manager for application, 1 managers active
   [GAME] @@ You descend to floor 1 of the dungeon.
   Log file appended successfully.
   Log file appended successfully.
   $$ Game Server Opened!
   [GAME] $$ Game Server Opened!
   Log file appended successfully.
   SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder".
   SLF4J: Defaulting to no-operation (NOP) logger implementation
   SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.
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
	at com.shatteredpixel.shatteredpixeldungeon.agent.reporter.JacocoReporter.dumpData(JacocoReporter.java:304)
	...
```

## Run MIMIC-Py in Shattered Pixel Dungeon
1. Once you are in the game, press `B`, and you should see a pop-up window asking you to `Enter your command`. At the same time, you should see the following message in your console:
   ```
   > Task :desktop:debug
   [Controllers] added manager for application, 1 managers active
   [GAME] @@ You descend to floor 1 of the dungeon.
   Log file appended successfully.
   Log file appended successfully.
   $$ Game Server Opened!
   [GAME] $$ Game Server Opened!
   Log file appended successfully.
   SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder".
   SLF4J: Defaulting to no-operation (NOP) logger implementation
   SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.
   $$ MIMIC Mode Started with XXX milliseconds!
   [GAME] $$ MIMIC Mode Started with XXX milliseconds!
   Log file appended successfully.
   ```

2. Once you see messages above in the console, you can start MIMIC-Py by running the `run.py` file [here](../run.py), 
or by running the following command in the terminal while in the `./MIMIC_Shattered_Pixel_Dungeon` directory:
    ```bash
    python ../run.py
    ```

3. After running the command, you should see the following output:

    ```
    bridge.agentClient:log Agent connected to WebSocket server.
   skill_library.SkillManager:log achievement_skill_collection_Example created successfully.
   memory_stream.MemoryStream:log Writing ./core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/agent/memory_system/Example//{MIMIC_PERSONALITY}/{MIMIC_PERSONALITY}.json...
   memory_stream.MemoryStream:log "./core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/agent/memory_system/Example//{MIMIC_PERSONALITY}/{MIMIC_PERSONALITY}.json" written successfully
   memory_stream.MemoryStream:log {MIMIC_PERSONALITY}_memory_collectionR_Example created successfully.
   memory_stream.MemoryStream:log {MIMIC_PERSONALITY}_memory_collectionP_Example created successfully.
    ```

4. Now, MIMIC-Py is running and ready to interact with the game. You can start MIMIC-Py by enter the command `1` in the pop-up window and click `Set` button to start MIMIC-Py.

[//]: # (## [Option 1] Run MIMIC-P Baseline)

[//]: # (1. Once you are in the game, press `L`, and you should see a pop-up window asking you to "Enter your command." At the same time, you should see the following message in your console:)

[//]: # (   ```)

[//]: # (   > Task :desktop:debug)

[//]: # (   [Controllers] added manager for application, 1 managers active)

[//]: # (   Current working directory: D:\McGill\Graduated Study\MIMIC\MIMIC_Shattered_Pixel_Dungeon\desktop)

[//]: # (   Current working directory: D:\McGill\Graduated Study\MIMIC\MIMIC_Shattered_Pixel_Dungeon\desktop)

[//]: # (   SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder".)

[//]: # (   SLF4J: Defaulting to no-operation &#40;NOP&#41; logger implementation)

[//]: # (   SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.)

[//]: # (   [GAME] @@ You descend to floor 1 of the dungeon.)

[//]: # (   Log file appended successfully.)

[//]: # (   Log file appended successfully.)

[//]: # (   $$ Game Server Opened!)

[//]: # (   [GAME] $$ Game Server Opened!)

[//]: # (   Log file appended successfully.)

[//]: # (   $$ MIMIC Mode Started with XXX milliseconds!)

[//]: # (   [GAME] $$ MIMIC Mode Started with XXX milliseconds!)

[//]: # (   Log file appended successfully.)

[//]: # (   ```)

[//]: # ()
[//]: # (2. open a terminal and navigate to the `./MIMIC_Shattered_Pixel_Dungeon` directory.)

[//]: # ()
[//]: # (    ```bash)

[//]: # (    cd ./MIMIC_Shattered_Pixel_Dungeon)

[//]: # (    ```)

[//]: # ()
[//]: # (3. Run the following command to start MIMIC-P:)

[//]: # ()
[//]: # (    ```bash)

[//]: # (    node ./core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/agent/LLMBaseline/LLMPlannerAgentClient.js)

[//]: # (    ```)

[//]: # ()
[//]: # (4. After running the command, you should see the following output:)

[//]: # ()
[//]: # (    ```)

[//]: # (    LLMPlannerBaseline.LLMPlannerAgent:log LLMPlannerAgent connected to WebSocket server.)

[//]: # (    ```)

[//]: # ()
[//]: # (5. Now, MIMIC-P is running and ready to interact with the game. You can start MIMIC-P by enter the command `l` in the pop-up window and press "Set" button to start MIMIC-P.)

[//]: # ()
[//]: # ()
[//]: # (## [Option 2] Run MIMIC-P+S Baseline)

[//]: # (1. Once you are in the game, press `L`, and you should see a pop-up window asking you to "Enter your command." At the same time, you should see the following message in your console:)

[//]: # (   ```)

[//]: # (   > Task :desktop:debug)

[//]: # (   [Controllers] added manager for application, 1 managers active)

[//]: # (   Current working directory: D:\McGill\Graduated Study\MIMIC\MIMIC_Shattered_Pixel_Dungeon\desktop)

[//]: # (   Current working directory: D:\McGill\Graduated Study\MIMIC\MIMIC_Shattered_Pixel_Dungeon\desktop)

[//]: # (   SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder".)

[//]: # (   SLF4J: Defaulting to no-operation &#40;NOP&#41; logger implementation)

[//]: # (   SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.)

[//]: # (   [GAME] @@ You descend to floor 1 of the dungeon.)

[//]: # (   Log file appended successfully.)

[//]: # (   Log file appended successfully.)

[//]: # (   $$ Game Server Opened!)

[//]: # (   [GAME] $$ Game Server Opened!)

[//]: # (   Log file appended successfully.)

[//]: # (   $$ MIMIC Mode Started with XXX milliseconds!)

[//]: # (   [GAME] $$ MIMIC Mode Started with XXX milliseconds!)

[//]: # (   Log file appended successfully.)

[//]: # (   ```)

[//]: # ()
[//]: # (2. open a terminal and navigate to the `./MIMIC_Shattered_Pixel_Dungeon` directory.)

[//]: # ()
[//]: # (    ```bash)

[//]: # (    cd ./MIMIC_Shattered_Pixel_Dungeon)

[//]: # (    ```)

[//]: # ()
[//]: # (3. Run the following command to start MIMIC-P+S:)

[//]: # ()
[//]: # (    ```bash)

[//]: # (    node ./core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/agent/LLMBaseline/LLMPlannerSummarizerAgentClient.js)

[//]: # (    ```)

[//]: # ()
[//]: # (4. After running the command, you should see the following output:)

[//]: # ()
[//]: # (    ```)

[//]: # (    LLMBaseline.LLMPlannerSummarizerAgent:log LLMPlannerSummarizerAgent connected to WebSocket server.)

[//]: # (    ```)

[//]: # ()
[//]: # (5. Now, MIMIC-P+S is running and ready to interact with the game. You can start MIMIC-P+S by enter the command `k` in the pop-up window and press "Set" button to start MIMIC-P+S.)

[//]: # ()
[//]: # ()
[//]: # (## [Option 3] Run Monkey Baselines)

[//]: # (1. Once you are in the game, Monkey is ready to interact with the game. You can start Monkey by pressing the key `N` on your keyboard while playing the game.)

[//]: # ()
[//]: # (2. Set the "IS_SMART_MONKEY" in your `config.json` file to `true` if you want to use the Smart Monkey baseline, or `false` if you want to use the Dumb Monkey baseline.)

## IMPORTANT:
If the running failed due to socket bad connection, try to check if the GameServer is enabled in the game from the console / game log. If not, you can toggle it by pressing `G` on your keyboard while playing the game. Note, pressing `L` or `B` will also toggle the GameServer on, so you can press `L` or `B` to toggle it on as well.

# Some Code Information
All messages used in the game can be found [here](core/src/main/assets/messages).

All buffs can be found [here](core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/actors/buffs).

All hero's information can be found [here](core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/actors/hero).
- Remember, we are only using the character [Warrior](core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/actors/hero/abilities/warrior).

All Information about mobs can be found [here](core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/actors/mobs).