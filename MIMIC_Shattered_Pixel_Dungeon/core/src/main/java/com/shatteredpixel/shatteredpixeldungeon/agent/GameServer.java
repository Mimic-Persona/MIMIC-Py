package com.shatteredpixel.shatteredpixeldungeon.agent;

import java.net.InetSocketAddress;

import com.shatteredpixel.shatteredpixeldungeon.APIs.AgentAPI;
import com.shatteredpixel.shatteredpixeldungeon.APIs.status.Status;
import com.shatteredpixel.shatteredpixeldungeon.Dungeon;
import com.shatteredpixel.shatteredpixeldungeon.scenes.GameScene;
import com.shatteredpixel.shatteredpixeldungeon.utils.GLog;
import org.java_websocket.server.WebSocketServer;
import org.java_websocket.WebSocket;
import org.java_websocket.handshake.ClientHandshake;
import org.json.JSONArray;
import org.json.JSONObject;

public class GameServer extends WebSocketServer {
    public static final String BOT_MSG = "agent.GameServer: ";
    public static final String ERR_MSG = "agent.GameServer:error: ";

    public GameServer(String host, int port) {
        // get the host after "//" if exists
        super(new InetSocketAddress(
                host,
                port));
    }

    @Override
    public void broadcast(String message) {
        super.broadcast(message);
        GLog.c(BOT_MSG + "Broadcast message: " + message);
    }

    @Override
    public void onStart() {
        GLog.c(BOT_MSG + "GameServer started on port: " + getAddress());
    }

    @Override
    public void onOpen(WebSocket conn, ClientHandshake handshake) {
        GLog.c(BOT_MSG + "New connection: " + conn.getRemoteSocketAddress());
    }

    @Override
    public void onClose(WebSocket conn, int code, String reason, boolean remote) {
        GLog.c(BOT_MSG + "Closed connection to " + conn.getRemoteSocketAddress());
    }

    @Override
    public void onMessage(WebSocket conn, String message) {
        GLog.c(BOT_MSG + message);

        // Fetching the Status for the client
        if (message.equals("GetStatus")) {
            JSONObject status;

            try {
                status = Status.getStatus();
                status.put("msgType", "status");
                conn.send(status.toString());

            } catch (Exception e) {
                GLog.e(ERR_MSG + "Error in getting status: " + e.getMessage());
            }
        }

        else if (message.startsWith("ACTION: ")) {
            GLog.c("======================================================================== Action #" + (Dungeon.agentActionCounter + 2) + " ========================================================================");

            JSONObject newPlan = null;

            try {
                newPlan = new JSONObject(message.replace("ACTION: ", ""));

            } catch (Exception e) {
                GLog.e(ERR_MSG + "Error in creating JSONObject: " + e.getMessage());
            }

            GLog.resetBotMsg();
            GLog.resetErrMsg();
            GameScene.isUpdated = false;

            int[] tile = null;

            try {
                // Cast tile - the JSONArray to an int array
                if (newPlan.get("action").toString().equals("act") ||
                    newPlan.get("action").toString().equals("throw")) {

                    JSONArray jsonArray = new JSONArray(newPlan.get("tile").toString());
                    tile = new int[jsonArray.length()];

                    for (int i = 0; i < jsonArray.length(); i++) {
                        tile[i] = jsonArray.getInt(i);
                    }
                }

                AgentAPI.handle(
                        newPlan.get("action").toString().toLowerCase(),
                        tile,
                        newPlan.get("item1").toString(),
                        newPlan.get("item2").toString(),
                        Integer.parseInt(newPlan.get("wait_turns").toString()));
            } catch (Exception e) {
                GameScene.isUpdated = true;
                GLog.e(ERR_MSG + "Error in performing actions properly due to bad request: " + e.getMessage());
            }

            Dungeon.toReport = true;

        } else if (message.equals("TERMINATED")) {
            GLog.c(BOT_MSG + "Terminating the connection...");

            // Send the logs, errors and status to the client
            JSONObject termination = new JSONObject();

            termination.put("msgType", "TERMINATED");

            conn.send(termination.toString());

            conn.close();

            try {
                Dungeon.gameServer.stop();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

            Dungeon.isAgentNext = false;
            Dungeon.isInMonkeyMode = false;
        }
    }

    @Override
    public void onError(WebSocket conn, Exception ex) {
        ex.printStackTrace();
    }
}
