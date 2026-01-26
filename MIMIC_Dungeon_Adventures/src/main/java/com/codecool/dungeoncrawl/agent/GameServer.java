package com.codecool.dungeoncrawl.agent;

import java.net.InetSocketAddress;
import com.codecool.dungeoncrawl.APIs.AgentAPI;
import com.codecool.dungeoncrawl.APIs.status.Status;
import com.codecool.dungeoncrawl.gui.Main;
import org.java_websocket.server.WebSocketServer;
import org.java_websocket.WebSocket;
import org.java_websocket.handshake.ClientHandshake;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import static com.codecool.dungeoncrawl.APIs.status.Environment.updateVisitedMap;

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
        updateVisitedMap();

        // Fetching the Status for the client
        if (message.equals("GetStatus")) {
            JSONObject status;

            try {
                status = Status.getStatus();
                status.put("msgType", "status");
                conn.send(status.toString());

            } catch (JSONException e) {
                GLog.e(ERR_MSG + "Error in getting status: " + e.getMessage());
            }
        }

        // Try to handle the action commands from the client
        else if (message.startsWith("ACTION: ")) {
            JSONObject newPlan = null;

            try {
                newPlan = new JSONObject(message.replace("ACTION: ", ""));

            } catch (JSONException e) {
                GLog.e(ERR_MSG + "Error in creating JSONObject: " + e.getMessage());
            }

            GLog.resetBotMsg();
            GLog.resetErrMsg();

            int[] tile = null;

            try {
                assert newPlan != null;

                JSONArray jsonArray = new JSONArray(newPlan.get("tile").toString());
                tile = new int[jsonArray.length()];

                    for (int i = 0; i < jsonArray.length(); i++) {
                        tile[i] = jsonArray.getInt(i);
                    }

                AgentAPI.handle(newPlan.get("action").toString().toLowerCase(), tile);

            } catch (Exception e) {
                GLog.e(ERR_MSG + "Error in performing actions properly due to bad request: " + e.getMessage());
            }

            // Send the logs, errors and status to the client
            JSONObject feedback = new JSONObject();

            try {
                feedback.put("msgType", "feedback");
                feedback.put("logs", GLog.BOT_MSG);
                feedback.put("errors", GLog.ERR_MSG);

            } catch (JSONException e) {
                GLog.e("Error in creating feedback: " + e.getMessage());
            }

            conn.send(feedback.toString());

        } else if (message.equals("TERMINATED")) {
            GLog.c(BOT_MSG + "Terminating the connection...");

            // Send the logs, errors and status to the client
            JSONObject termination = new JSONObject();

            try {
                termination.put("msgType", "TERMINATED");

            } catch (JSONException e) {
                GLog.e("Error in creating termination: " + e.getMessage());
            }

            conn.send(termination.toString());

            conn.close();

            try {
                Main.gameServer.stop();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

            Main.isAgentNext = false;
            Main.isInMonkeyMode = false;
        }
    }

    @Override
    public void onError(WebSocket conn, Exception ex) {
        ex.printStackTrace();
    }
}
