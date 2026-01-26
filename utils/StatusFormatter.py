class StatusFormatter:
    @staticmethod
    def DA_status_to_prompt(
            status: dict,
            prefix: str = ""
    ) -> str:
        res = ""

        res += f"{prefix}damage: {status['damage']}\n"
        res += f"{prefix}environment: {status['environment']}\n"
        res += f"{prefix}keys: {status['keys']}\n"
        res += f"{prefix}health: {status['health']}\n"
        res += f"{prefix}heroPositionInXY: {status['heroPositionInXY']}\n"

        return res


    @staticmethod
    def SPD_status_to_prompt(
            status: dict,
            prefix: str = ""
    ) -> str:
        res = ""

        # Hero Status
        res += f"{prefix}health: {status['health']}/{status['maxHealth']}\n"
        res += f"{prefix}level: {status['level']}\n"
        res += f"{prefix}experience: {status['experience']}/{status['maxExperience']}\n"
        res += f"{prefix}strength: {status['strength']}\n"
        res += f"{prefix}gold: {status['gold']}\n"
        res += f"{prefix}hero position in xy: [{status['heroPositionInXY']}]\n"
        res += f"{prefix}buffs/debuffs: {status['buffs']}\n"

        # Hero Talents
        res += f"{prefix}free talent points: {status['freeTalentPoints']}\n"
        res += f"{prefix}talents: {status['currTalents']}\n"

        # Hero Equipment
        res += f"{prefix}equipments: {status['equipments']}\n"

        # Hero Inventory
        res += f"{prefix}inventory: {status['items']}\n"
        res += f"{prefix}keys: {status['keys']}\n"

        # Environment
        res += f"{prefix}depth: {status['depth']}\n"
        res += f"{prefix}environment: {status['environment']}\n"

        return res


    @staticmethod
    def MC_status_to_prompt(
            status: dict,
            prefix: str = ""
    ) -> str:
        res = ""

        res += f"{prefix}Biome: {status['status']['biome']}\n"
        res += f"{prefix}Time of the day: {status['status']['timeOfDay']}\n"

        res += f"{prefix}Health: {status['status']['health']}\n"
        res += f"{prefix}Food: {status['status']['food']}\n"
        res += f"{prefix}Saturation: {status['status']['saturation']}\n"
        res += f"{prefix}Position: {status['status']['position']}\n"

        res += f"{prefix}Is on ground: {status['status']['onGround']}\n"
        res += f"{prefix}Is in water: {status['status']['isInWater']}\n"
        res += f"{prefix}Is in lava: {status['status']['isInLava']}\n"

        if status['status']['equipment']:
            for i, equipment in enumerate(status['status']['equipment']):
                if equipment is None:
                    status['status']['equipment'][i] = "None"
            res += f"{prefix}Equipment: {', '.join(status['status']['equipment'])}\n"
        else:
            res += f"{prefix}Equipment: [None, None, None, None, None, None]\n"


        res += f"{prefix}Inventory used: {status['status']['inventoryUsed']}\n"
        res += f"{prefix}Inventory({status['status']['inventoryUsed']}/36): {status['inventory']}\n"

        if status['nearbyChests']:
            res += f"{prefix}Nearby chests: {', '.join(status['nearbyChests'])}\n"
        else:
            res += f"{prefix}Nearby chests: None.\n"

        if status['voxels']:
            res += f"{prefix}Nearby blocks: {', '.join(status['voxels'])}\n"
        else:
            res += f"{prefix}Nearby blocks: None.\n"

        res += f"{prefix}Nearby entities (nearest to farthest): {status['status']['entities']}\n"

        return res

    @staticmethod
    def get_inventory_diff(
            prev_inventory,
            curr_inventory,
    ) -> dict:
        """
        Generate a dictionary that contains the differences between the previous and current status.
        Key is the status field,
        and if the value is positive, it indicates an increase with that amount, otherwise a decrease,
        and zero indicates no change.
        :param prev_inventory: The previous status of the game.
        :param curr_inventory: The current status of the game.
        :return: A dictionary containing the differences between the previous and current status.
        """
        status_diff = {}

        for item in curr_inventory:
            if item in prev_inventory:
                prev_count = prev_inventory[item]
            else:
                prev_count = 0

            curr_count = curr_inventory[item]

            if curr_count > prev_count:
                status_diff[item] = curr_count - prev_count
            elif curr_count < prev_count:
                status_diff[item] = -(prev_count - curr_count)

        for item in prev_inventory:
            if item not in curr_inventory:
                status_diff[item] = -prev_inventory[item]

        return status_diff

    @staticmethod
    def MC_status_to_summarizer_prompt(
            prev_status: dict,
            status: dict,
            prefix: str = ""
    ) -> str:
        """
        Formats the Minecraft status for summarization, including both previous and current status.
        :param prev_status: The previous status of the game.
        :param status: The current status of the game.
        :param prefix: Optional, a prefix to prepend to each line of the status output.
        :return: The formatted Minecraft status for summarization.
        """
        res = ""

        res += f"{prefix}Biome: {status['status']['biome']}\n"
        res += f"{prefix}Time of the day: {status['status']['timeOfDay']}\n"

        res += f"{prefix}Change of Health: {prev_status['status']['health']} -> {status['status']['health']}\n"
        res += f"{prefix}Change of Food: {prev_status['status']['food']} -> {status['status']['food']}\n"
        res += f"{prefix}Change of Saturation: {prev_status['status']['saturation']} -> {status['status']['saturation']}\n"
        res += f"{prefix}Position: {status['status']['position']}\n"

        res += f"{prefix}Is on ground: {status['status']['onGround']}\n"
        res += f"{prefix}Is in water: {status['status']['isInWater']}\n"
        res += f"{prefix}Is in lava: {status['status']['isInLava']}\n"

        if status['status']['equipment']:
            for i, equipment in enumerate(status['status']['equipment']):
                if equipment is None:
                    status['status']['equipment'][i] = "None"
            res += f"{prefix}Current Equipment: {', '.join(status['status']['equipment'])}\n"
        else:
            res += f"{prefix}Current Equipment: [None, None, None, None, None, None]\n"

        res += f"{prefix}Current Inventory({status['status']['inventoryUsed']}/36): {status['inventory']}\n"

        res += f"{prefix}Change of Inventory({prev_status['status']['inventoryUsed']}/36 -> {status['status']['inventoryUsed']}/36): "
        res += f"{StatusFormatter.get_inventory_diff(prev_status['inventory'], status['inventory'])}\n"

        if status['nearbyChests']:
            res += f"{prefix}Nearby chests: {', '.join(status['nearbyChests'])}\n"
        else:
            res += f"{prefix}Nearby chests: None.\n"

        if status['voxels']:
            res += f"{prefix}Nearby blocks: {', '.join(status['voxels'])}\n"
        else:
            res += f"{prefix}Nearby blocks: None.\n"

        res += f"{prefix}Nearby entities (nearest to farthest): {status['status']['entities']}\n"

        return res

    @staticmethod
    def get_current_status(
            game_subject: str,
            status: dict,
            prefix: str = "",
            prev_status: dict = None,
    ):
        """
        Returns the current status formatted as a string based on the game subject.
        :param game_subject: The game subject (e.g., "DA", "SPD", "MC")
        :param status: The current status of the game
        :param prefix: Optional, a prefix to prepend to each line of the status output
        :param prev_status: Optional, the previous status of the game (not used in this method)
        :return: The formatted current status
        """
        if game_subject == "DA":
            curr_status = StatusFormatter.DA_status_to_prompt(status, prefix)

        elif game_subject == "SPD":
            curr_status = StatusFormatter.SPD_status_to_prompt(status, prefix)

        elif game_subject == "MC" and prev_status:
            curr_status = StatusFormatter.MC_status_to_summarizer_prompt(prev_status, status, prefix)

        elif game_subject == "MC":
            curr_status = StatusFormatter.MC_status_to_prompt(status, prefix)

        else:
            raise ValueError(f"Unsupported game subject: {game_subject}")

        return curr_status