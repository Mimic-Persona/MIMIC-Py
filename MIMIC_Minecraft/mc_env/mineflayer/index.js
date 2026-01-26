const fs = require("fs");
const express = require("express");
const bodyParser = require("body-parser");
const mineflayer = require("mineflayer");
const net = require("net");

const skills = require("./bridge/skillLoader");
const { initCounter, getNextTime } = require("./bridge/utils");
const obs = require("./bridge/observation/Observation");
const OnChat = require("./bridge/observation/OnChat");
const OnError = require("./bridge/observation/OnError");
const { Voxels, BlockRecords } = require("./bridge/observation/Voxels");
const Status = require("./bridge/observation/Status");
const Inventory = require("./bridge/observation/Inventory");
const OnSave = require("./bridge/observation/OnSave");
const Chests = require("./bridge/observation/Chests");
const { plugin: tool } = require("mineflayer-tool");

const {
    Movements,
    goals: {
        Goal,
        GoalBlock,
        GoalNear,
        GoalXZ,
        GoalNearXZ,
        GoalY,
        GoalGetToBlock,
        GoalLookAtBlock,
        GoalBreakBlock,
        GoalCompositeAny,
        GoalCompositeAll,
        GoalInvert,
        GoalFollow,
        GoalPlaceBlock,
    },
    pathfinder,
    Move,
    ComputedPath,
    PartiallyComputedPath,
    XZCoordinates,
    XYZCoordinates,
    SafeBlock,
    GoalPlaceBlockOptions,
} = require("mineflayer-pathfinder");
const { Vec3 } = require("vec3");
const { goals } = require('mineflayer-pathfinder');

const failedCraftFeedback = require("../../../skill_system/skill_library/MC/basic_skills/code/craftHelper");
const { waitForMobRemoved, waitForMobShot } = require("../../../skill_system/skill_library/MC/basic_skills/code/waitForMobRemoved");
const equipSword = require('../../../skill_system/skill_library/MC/basic_skills/code/equipSword');
const equipArmor = require('../../../skill_system/skill_library/MC/basic_skills/code/equipArmor');
const killMob = require('../../../skill_system/skill_library/MC/basic_skills/code/killMob');
const killMonsters = require("../../../skill_system/skill_library/MC/basic_skills/code/killMonsters");


let bot = null;
let mcData;

const app = express();

let startTimestamp;
let botInventory;
let lastInventory = "{}";

// Store connection socket to Python bridge
let SOCKET_SERVER = null;

app.use(bodyParser.json({ limit: "50mb" }));
app.use(bodyParser.urlencoded({ limit: "50mb", extended: false }));

app.post("/start", (req, res) => {
    if (bot) onDisconnect("Restarting bot");
    bot = null;
    console.log(req.body);

    let lastBotConfig = {
        mcHost: req.body.mc_host,
        mcPort: req.body.mc_port,
        socketHost: req.body.socket_host,
        socketPort: req.body.socket_port,
        username: req.body.username,
        disableChatSigning: true,
        checkTimeoutInterval: 60 * 60 * 1000,
    }

    bot = mineflayer.createBot({
        host: lastBotConfig.mcHost,
        port: lastBotConfig.mcPort,
        username: lastBotConfig.username,
        disableChatSigning: lastBotConfig.disableChatSigning,
        checkTimeoutInterval: lastBotConfig.checkTimeoutInterval,
    });

    bot.lastBotConfig = lastBotConfig;

    bot.once("error", onConnectionFailed);

    bot.task = req.body.task;
    bot.id = req.body.id;

    bot.is_player_observer = req.body.is_player_observer === true || req.body.is_player_observer === "true";
    console.log(bot.is_player_observer);
    console.log(bot.is_player_observer ? "🕵️‍♂️ Player observer mode enabled" : "🤖 Bot mode enabled");

    bot.chat_log_path = `./out/MC/${bot.task}/${bot.task}_${bot.id}_chat.log`;
    bot.move_log_path = `./out/MC/${bot.task}/${bot.task}_${bot.id}_move.log`;
    bot.inventory_log_path = `./out/MC/${bot.task}/${bot.task}_${bot.id}_inventory.log`;

    const server = net.createServer((socket) => {
        console.log("Python bridge connected");

        SOCKET_SERVER = socket;

        socket.on("end", () => {
            console.log("🔌 Python bridge disconnected");
            SOCKET_SERVER = null;
        });

        socket.on("error", (err) => {
            console.error("Socket error:", err.message);
            SOCKET_SERVER = null;
        });

        // You can listen to messages from Python here
        socket.on("data", (data) => {
            const msg = data.toString().trim();
            console.log("Message from Python:", msg);
            // optional: forward to Minecraft chat if needed
        });
    });

    server.listen(lastBotConfig.socketPort, () => {
        console.log(`Node socket server listening on port ${lastBotConfig.socketPort}`);
    });


    // Create all the log files only if not exist
    const logDir = `./out/MC/${bot.task}`;
    if (!fs.existsSync(logDir)) {
        fs.mkdirSync(logDir, { recursive: true });
    }
    fs.appendFileSync(bot.chat_log_path, "");
    fs.appendFileSync(bot.move_log_path, "");
    fs.appendFileSync(bot.inventory_log_path, "");

    // Event subscriptions
    bot.waitTicks = req.body.waitTicks;
    bot.globalTickCounter = 0;
    bot.stuckTickCounter = 0;
    bot.stuckPosList = [];
    bot.iron_pickaxe = false;
    bot.botMsg = "";
    bot.errMsg = "";
    bot.isTimeout = false;

    bot.on("kicked", onDisconnect);

    // mounting will cause physicsTick to stop
    bot.on("mount", () => {
        bot.dismount();
    });

    // Listen for chat messages
    bot.on('chat', (username, message) => {
        // Output the message to the given log file
        fs.appendFileSync(bot.chat_log_path, `${Date.now() - startTimestamp} - ${bot.time.timeOfDay} - ${username}: ${message}\n`);

        // Store the message from the bot
        if (username === bot.username) bot.botMsg += `${message}\n`;
        // Store the error message from the bot
        else {
            if (SOCKET_SERVER) {
                const msg = JSON.stringify({ msgType: "command", from: username, command: message }) + "\n";
                SOCKET_SERVER.write(msg);
            }
        }
    });

    // Listen on bot move
    bot.on('move', () => {
        fs.appendFileSync(bot.move_log_path, `${Date.now() - startTimestamp} - ${bot.time.timeOfDay} - ${bot.entity.position}\n`);
    });

    bot.once("spawn", async () => {
        startTimestamp = Date.now();
        botInventory = new Inventory(bot);
        bot.removeListener("error", onConnectionFailed);
        let itemTicks = 1;
        if (req.body.reset === "hard") {
            bot.chat("/clear @s");
            bot.chat("/kill @s");
            const inventory = req.body.inventory ? req.body.inventory : {};
            const equipment = req.body.equipment
                ? req.body.equipment
                : [null, null, null, null, null, null];
            for (let key in inventory) {
                bot.chat(`/give @s minecraft:${key} ${inventory[key]}`);
                itemTicks += 1;
            }
            const equipmentNames = [
                "armor.head",
                "armor.chest",
                "armor.legs",
                "armor.feet",
                "weapon.mainhand",
                "weapon.offhand",
            ];
            for (let i = 0; i < 6; i++) {
                if (i === 4) continue;
                if (equipment[i]) {
                    bot.chat(
                        `/item replace entity @s ${equipmentNames[i]} with minecraft:${equipment[i]}`
                    );
                    itemTicks += 1;
                }
            }
        }

        if (req.body.position) {
            bot.chat(
                `/tp @s ${req.body.position.x} ${req.body.position.y} ${req.body.position.z}`
            );
        }

        // if iron_pickaxe is in bot's inventory
        if (
            bot.inventory.items().find((item) => item.name === "iron_pickaxe")
        ) {
            bot.iron_pickaxe = true;
        }

        const { pathfinder } = require("mineflayer-pathfinder");
        const tool = require("mineflayer-tool").plugin;
        const collectBlock = require("mineflayer-collectblock").plugin;
        const pvp = require("mineflayer-pvp").plugin;
        const minecraftHawkEye = require("minecrafthawkeye");
        bot.loadPlugin(pathfinder);
        bot.loadPlugin(tool);
        bot.loadPlugin(collectBlock);
        bot.loadPlugin(pvp);
        bot.loadPlugin(minecraftHawkEye);

        // bot.collectBlock.movements.digCost = 0;
        // bot.collectBlock.movements.placeCost = 0;

        obs.inject(bot, [
            OnChat,
            OnError,
            Voxels,
            Status,
            Inventory,
            OnSave,
            Chests,
            BlockRecords,
        ]);
        skills.inject(bot);

        if (req.body.spread) {
            bot.chat(`/spreadplayers ~ ~ 0 300 under 80 false @s`);
            await bot.waitForTicks(bot.waitTicks);
        }

        await bot.waitForTicks(bot.waitTicks * itemTicks);
        res.json(bot.observe());

        initCounter(bot);
        bot.chat("/gamerule keepInventory true");
        bot.chat("/gamerule doDaylightCycle true");
    });

    function onConnectionFailed(e) {
        console.log(e);
        bot = null;
        res.status(400).json({ error: e });
    }
    function onDisconnect(message) {
        if (bot.viewer) {
            bot.viewer.close();
        }
        bot.end();
        console.log(message);
        bot = null;
    }
});

app.post("/step", async (req, res) => {
    bot.botMsg = "";
    bot.errMsg = "";
    bot.isTimeout = false;

    // import useful package
    let response_sent = false;
    function otherError(err) {
        console.log("Uncaught Error");
        bot.emit("error", handleError(err));
        bot.waitForTicks(bot.waitTicks).then(() => {
            if (!response_sent) {
                response_sent = true;
                res.json(bot.observe());
            }
        });
    }

    process.on("uncaughtException", otherError);

    mcData = require("minecraft-data")(bot.version);
    mcData.itemsByName["leather_cap"] = mcData.itemsByName["leather_helmet"];
    mcData.itemsByName["leather_tunic"] =
        mcData.itemsByName["leather_chestplate"];
    mcData.itemsByName["leather_pants"] =
        mcData.itemsByName["leather_leggings"];
    mcData.itemsByName["leather_boots"] = mcData.itemsByName["leather_boots"];
    mcData.itemsByName["lapis_lazuli_ore"] = mcData.itemsByName["lapis_ore"];
    mcData.blocksByName["lapis_lazuli_ore"] = mcData.blocksByName["lapis_ore"];

    // Set up pathfinder
    const movements = new Movements(bot, mcData);
    bot.pathfinder.setMovements(movements);

    bot.globalTickCounter = 0;
    bot.stuckTickCounter = 0;
    bot.stuckPosList = [];

    function onTick() {
        bot.globalTickCounter++;
        if (bot.pathfinder.isMoving()) {
            bot.stuckTickCounter++;
            if (bot.stuckTickCounter >= 100) {
                onStuck(1.5);
                bot.stuckTickCounter = 0;
            }
        }
        if (JSON.stringify(botInventory.observe()) !== lastInventory) {
            fs.appendFileSync(bot.inventory_log_path, `${Date.now() - startTimestamp} - ${bot.time.timeOfDay} - ${JSON.stringify(botInventory.observe())}\n`);
        }
        lastInventory = JSON.stringify(botInventory.observe());

        // if (bot.time.day > 0) {
        //     bot.chat("TERMINATE");
        //     bot.end();
        // }

        // let currTime = bot.time.day;
        //
        // let rawData = fs.readFileSync("./out/temp_time_record.json", "utf8");
        // let prevTime = JSON.parse(rawData);
        //
        // if (currTime < prevTime.day) {
        //     bot.chat("TERMINATE");
        //     bot.end();
        // }
        // fs.writeFileSync(
        //     `./out/temp_time_record.json`,
        //     JSON.stringify({ day: currTime })
        // );
    }

    bot.on("physicTick", onTick);

    // initialize fail count
    let _craftItemFailCount = 0;
    let _killMobFailCount = 0;
    let _mineBlockFailCount = 0;
    let _placeItemFailCount = 0;
    let _smeltItemFailCount = 0;

    // Retrieve array form post bod
    const code = req.body.code;
    const programs = req.body.programs;
    const timeout = req.body.timeout ? req.body.timeout : 60000;
    bot.cumulativeObs = [];
    await bot.waitForTicks(bot.waitTicks);
    const r = await evaluateCode(code, programs, timeout);
    process.off("uncaughtException", otherError);
    if (r !== "success") {
        bot.emit("error", handleError(r));
        bot.errMsg += `${r}\n`;
    }
    await returnItems();
    // wait for the last message
    await bot.waitForTicks(bot.waitTicks);
    if (!response_sent) {
        response_sent = true;
        res.json({
            observation: bot.observe(),
            botMsg: bot.botMsg,
            errMsg: bot.errMsg,
            isTimeout: bot.isTimeout,
        });
    }

    bot.removeListener("physicTick", onTick);

    async function evaluateCode(code, programs, timeoutMs) {
        async function runEval() {
            return await eval("(async () => {" + code + "\n" + programs + "})()");
        }

        try {
            await Promise.race([
                runEval(),
                new Promise((_, reject) =>
                    setTimeout(() => reject(new Error("Code execution timed out")), timeoutMs)
                ),
            ]);
            return "success";
        } catch (err) {
            if (err.message === "Code execution timed out") {
                console.warn("Eval timed out. Restarting bot...");
                bot.isTimeout = true;

                // Trigger re-login with previous options
                try {
                    bot.isTimeout = false;
                    console.log("Bot restarted after timeout.");
                } catch (loginErr) {
                    console.error("Failed to restart bot after timeout:", loginErr);
                    return loginErr;
                }

                return new Error("Code execution timed out and bot was restarted.");
            }

            return err;
        }
    }

    function onStuck(posThreshold) {
        const currentPos = bot.entity.position;
        bot.stuckPosList.push(currentPos);

        // Check if the list is full
        if (bot.stuckPosList.length === 5) {
            const oldestPos = bot.stuckPosList[0];
            const posDifference = currentPos.distanceTo(oldestPos);

            if (posDifference < posThreshold) {
                teleportBot(); // execute the function
            }

            // Remove the oldest time from the list
            bot.stuckPosList.shift();
        }
    }

    function teleportBot() {
        const blocks = bot.findBlocks({
            matching: (block) => {
                return block.type === 0;
            },
            maxDistance: 1,
            count: 27,
        });

        if (blocks) {
            // console.log(blocks.length);
            const randomIndex = Math.floor(Math.random() * blocks.length);
            const block = blocks[randomIndex];
            bot.chat(`/tp @s ${block.x} ${block.y} ${block.z}`);
        } else {
            bot.chat("/tp @s ~ ~1.25 ~");
        }
    }

    function returnItems() {
        bot.chat("/gamerule doTileDrops false");
        const crafting_table = bot.findBlock({
            matching: mcData.blocksByName.crafting_table.id,
            maxDistance: 128,
        });
        if (crafting_table) {
            bot.chat(
                `/setblock ${crafting_table.position.x} ${crafting_table.position.y} ${crafting_table.position.z} air destroy`
            );
            bot.chat("/give @s crafting_table");
        }
        const furnace = bot.findBlock({
            matching: mcData.blocksByName.furnace.id,
            maxDistance: 128,
        });
        if (furnace) {
            bot.chat(
                `/setblock ${furnace.position.x} ${furnace.position.y} ${furnace.position.z} air destroy`
            );
            bot.chat("/give @s furnace");
        }
        if (bot.inventoryUsed() >= 32) {
            // if chest is not in bot's inventory
            if (!bot.inventory.items().find((item) => item.name === "chest")) {
                bot.chat("/give @s chest");
            }
        }
        // if iron_pickaxe not in bot's inventory and bot.iron_pickaxe
        if (
            bot.iron_pickaxe &&
            !bot.inventory.items().find((item) => item.name === "iron_pickaxe")
        ) {
            bot.chat("/give @s iron_pickaxe");
        }
        bot.chat("/gamerule doTileDrops true");
    }

    function handleError(err) {
        let stack = err.stack;
        if (!stack) {
            return err;
        }
        console.log(stack);
        const final_line = stack.split("\n")[1];
        const regex = /<anonymous>:(\d+):\d+\)/;

        const programs_length = programs.split("\n").length;
        let match_line = null;
        for (const line of stack.split("\n")) {
            const match = regex.exec(line);
            if (match) {
                const line_num = parseInt(match[1]);
                if (line_num >= programs_length) {
                    match_line = line_num - programs_length;
                    break;
                }
            }
        }
        if (!match_line) {
            return err.message;
        }
        let f_line = final_line.match(
            /\((?<file>.*):(?<line>\d+):(?<pos>\d+)\)/
        );
        if (f_line && f_line.groups && fs.existsSync(f_line.groups.file)) {
            const { file, line, pos } = f_line.groups;
            const f = fs.readFileSync(file, "utf8").split("\n");
            // let filename = file.match(/(?<=node_modules\\)(.*)/)[1];
            let source = file + `:${line}\n${f[line - 1].trim()}\n `;

            const code_source =
                "at " +
                code.split("\n")[match_line - 1].trim() +
                " in your code";
            return source + err.message + "\n" + code_source;
        } else if (
            f_line &&
            f_line.groups &&
            f_line.groups.file.includes("<anonymous>")
        ) {
            const { file, line, pos } = f_line.groups;
            let source =
                "Your code" +
                `:${match_line}\n${code.split("\n")[match_line - 1].trim()}\n `;
            let code_source = "";
            if (line < programs_length) {
                source =
                    "In your program code: " +
                    programs.split("\n")[line - 1].trim() +
                    "\n";
                code_source = `at line ${match_line}:${code
                    .split("\n")
                    [match_line - 1].trim()} in your code`;
            }
            return source + err.message + "\n" + code_source;
        }
        return err.message;
    }
});

app.post("/observe", (req, res) => {
    if (!bot) {
        res.status(400).json({ error: "Bot not spawned" });
        return;
    }
    bot.waitForTicks(bot.waitTicks).then(() => {
        res.json({
            observation: bot.observe()
        });
    });
});

app.post("/stop", (req, res) => {
    bot.end();
    res.json({
        message: "Bot stopped",
    });
});

app.post("/pause", (req, res) => {
    if (!bot) {
        res.status(400).json({ error: "Bot not spawned" });
        return;
    }
    bot.chat("/pause");
    bot.waitForTicks(bot.waitTicks).then(() => {
        res.json({ message: "Success" });
    });
});

// Server listening to PORT 3000

const DEFAULT_PORT = 3000;
const PORT = process.argv[2] || DEFAULT_PORT;
app.listen(PORT, () => {
    console.log(`Server started on port ${PORT}`);
});
