package com.codecool.dungeoncrawl.APIs.actions;

import com.codecool.dungeoncrawl.agent.GLog;

import static com.codecool.dungeoncrawl.gui.Main.map;

public class PickUp {
    public static boolean pickUp() {
        if (map.getPlayer().getCell().getItem() == null) {
            GLog.e("basic_skill.PickUp:error: There is no item to pick up.");
            return false;
        }
        return map.getPlayer().pickUpItem();
    }
}
