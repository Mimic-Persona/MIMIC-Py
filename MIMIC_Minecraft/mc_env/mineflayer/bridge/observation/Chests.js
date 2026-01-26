const { Observation } = require("./Observation");

class Chests extends Observation {
    constructor(bot) {
        super(bot);
        this.name = "nearbyChests";
        this.chestsItems = {};
        bot.on("closeChest", (chestItems, position) => {
            this.chestsItems[position] = chestItems;
        });
        bot.on("removeChest", (chestPosition) => {
            this.chestsItems[chestPosition] = "Invalid";
        });
    }

    observe() {
        let observerEntity;
        if (this.bot.is_player_observer) {
            const playerFilter = (entity) => entity.type === 'player'
            observerEntity = this.bot.nearestEntity(playerFilter)
        } else {
            observerEntity = this.bot.entity;
        }

        const chests = this.bot.findBlocks({
            point: observerEntity.position,
            matching: this.bot.registry.blocksByName.chest.id,
            maxDistance: 16,
            count: 999,
        });
        chests.forEach((chest) => {
            if (!this.chestsItems.hasOwnProperty(chest)) {
                this.chestsItems[chest] = "Unknown";
            }
        });
        return this.chestsItems;
    }
}

module.exports = Chests;
