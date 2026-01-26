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
const killMonsters = require("../../../skill_system/skill_library/MC/basic_skills/code/killMonsters");