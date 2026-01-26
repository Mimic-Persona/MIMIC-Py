#built using mc-build (https://github.com/mc-build/mc-build)

data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.0
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.0
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.0 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.0 from entity @s inventory.0
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.1
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.1
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.1 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.1 from entity @s inventory.1
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.2
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.2
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.2 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.2 from entity @s inventory.2
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.3
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.3
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.3 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.3 from entity @s inventory.3
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.4
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.4
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.4 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.4 from entity @s inventory.4
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.5
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.5
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.5 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.5 from entity @s inventory.5
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.6
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.6
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.6 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.6 from entity @s inventory.6
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.7
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.7
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.7 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.7 from entity @s inventory.7
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.8
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.8
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.8 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.8 from entity @s inventory.8
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.9
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.9
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.9 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.9 from entity @s inventory.9
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.10
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.10
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.10 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.10 from entity @s inventory.10
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.11
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.11
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.11 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.11 from entity @s inventory.11
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.12
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.12
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.12 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.12 from entity @s inventory.12
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.13
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.13
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.13 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.13 from entity @s inventory.13
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.14
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.14
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.14 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.14 from entity @s inventory.14
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.15
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.15
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.15 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.15 from entity @s inventory.15
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.16
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.16
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.16 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.16 from entity @s inventory.16
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.17
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.17
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.17 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.17 from entity @s inventory.17
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.18
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.18
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.18 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.18 from entity @s inventory.18
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.19
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.19
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.19 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.19 from entity @s inventory.19
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.20
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.20
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.20 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.20 from entity @s inventory.20
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.21
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.21
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.21 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.21 from entity @s inventory.21
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.22
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.22
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.22 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.22 from entity @s inventory.22
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.23
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.23
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.23 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.23 from entity @s inventory.23
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.24
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.24
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.24 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.24 from entity @s inventory.24
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.25
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.25
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.25 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.25 from entity @s inventory.25
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory inventory.26
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s inventory.26
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory inventory.26 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a inventory.26 from entity @s inventory.26
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory hotbar.0
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s hotbar.0
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory hotbar.0 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a hotbar.0 from entity @s hotbar.0
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory hotbar.1
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s hotbar.1
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory hotbar.1 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a hotbar.1 from entity @s hotbar.1
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory hotbar.2
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s hotbar.2
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory hotbar.2 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a hotbar.2 from entity @s hotbar.2
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory hotbar.3
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s hotbar.3
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory hotbar.3 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a hotbar.3 from entity @s hotbar.3
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory hotbar.4
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s hotbar.4
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory hotbar.4 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a hotbar.4 from entity @s hotbar.4
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory hotbar.5
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s hotbar.5
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory hotbar.5 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a hotbar.5 from entity @s hotbar.5
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory hotbar.6
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s hotbar.6
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory hotbar.6 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a hotbar.6 from entity @s hotbar.6
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory hotbar.7
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s hotbar.7
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory hotbar.7 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a hotbar.7 from entity @s hotbar.7
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory hotbar.8
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s hotbar.8
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory hotbar.8 set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a hotbar.8 from entity @s hotbar.8
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory weapon.offhand
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s weapon.offhand
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory weapon.offhand set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a weapon.offhand from entity @s weapon.offhand
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory armor.head
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s armor.head
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory armor.head set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a armor.head from entity @s armor.head
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory armor.chest
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s armor.chest
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory armor.chest set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a armor.chest from entity @s armor.chest
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory armor.legs
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s armor.legs
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory armor.legs set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a armor.legs from entity @s armor.legs
data modify entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items set from storage shared_inventory:inventory armor.feet
data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
item replace entity 005940b0-a744-cdb0-72a1-1245cc978f45 container.0 from entity @s armor.feet
execute store success score default shared_inventory_temp run data modify storage shared_inventory:compare default set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run data modify storage shared_inventory:inventory armor.feet set from entity 005940b0-a744-cdb0-72a1-1245cc978f45 Items
execute if score default shared_inventory_temp matches 1 run item replace entity @a armor.feet from entity @s armor.feet