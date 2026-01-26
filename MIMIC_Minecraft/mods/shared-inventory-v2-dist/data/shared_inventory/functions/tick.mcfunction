#built using mc-build (https://github.com/mc-build/mc-build)

summon chest_minecart ~ ~ ~ {UUID:[I;5849264,-1488663120,1923158597,-862482619],NoGravity:1b,Silent:1b,Invulnerable:1b}
execute as @a[tag=!shared_inventory_joined] run function shared_inventory:join
execute as @a[scores={shared_inventory_leave=1}] run function shared_inventory:join
execute as @a at @s run function shared_inventory:slots
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 with air
kill 005940b0-a744-cdb0-72a1-1245cc978f45