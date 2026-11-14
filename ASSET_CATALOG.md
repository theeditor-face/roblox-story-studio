# Roblox 3D Story Studio — Master Asset Catalog

Use this catalog as your reference before writing `shots.py` for any new video (`Video-2`, `Video-3`, etc.).
All modules are auto-imported when you use `from shotkit import *`.

---

## 1. Characters (`chars`, `story`, `LIB`)

### Classic Cast (`chars.*` / `story.*`)
| Call | Description | Default Face |
|---|---|---|
| `chars.eddie()` / `story.eddie()` | Main kid hero (blue shirt, spiky brown hair) | `hero` |
| `chars.teacher()` | Adult teacher / Principal | `plain` |
| `chars.girl()` | Girl classmate / friend | `girl` |
| `chars.dad()` | Dad character | `mustache` |
| `chars.yellow_guy()` | Yellow-skinned classic Roblox guy | `plain` |
| `chars.firefighter()` | Firefighter in gear + helmet | `hero` |
| `chars.kid()` | Generic kid (customizable colors) | `kid` |
| `story.leo()` | Kid sidekick | `kid` |
| `story.grandma()` | Grandma character | `plain` |
| `story.pilot()` | Airplane pilot | `mustache` |
| `story.mayor()` | Town mayor | `mustache` |
| `story.gus()` / `story.pickle()` / `story.townie()` | Supporting townies | `plain` |

### New Expanded Cast (`LIB.*`)
| Call | Description | Accessories |
|---|---|---|
| `LIB.police_officer(name, loc, rot, scale)` | Police officer in navy uniform | Police cap + gold chest badge |
| `LIB.judge(name, loc, rot, scale)` | Courtroom judge in black robe | White judge hair + white collar |
| `LIB.doctor_nurse(name, loc, rot, scale)` | School nurse / doctor in scrubs | Nurse cap + bun |
| `LIB.chef(name, loc, rot, scale)` | Chef in white coat & checkered pants | Tall chef toque hat |
| `LIB.astronaut(name, loc, rot, scale)` | Astronaut in white space suit | Oxygen pack + glass visor helmet |
| `LIB.bully(name, loc, rot, scale)` | Tall tough bully (sleeveless red) | Spiky dark hair + villain face |
| `LIB.nerd(name, loc, rot, scale)` | Smart classmate | Parted hair + glasses |
| `LIB.rich_kid(name, loc, rot, scale)` | Purple-suit rich kid | Blonde pompadour + gold collar |
| `LIB.ninja(name, loc, rot, scale)` | Black ninja outfit | Red headband |
| `LIB.robber(name, loc, rot, scale)` | Striped-shirt burglar | Black cap + villain face |
| `LIB.alien(name, loc, rot, scale)` | Green sci-fi alien | Glowing dual antennae |
| `LIB.robot(name, loc, rot, scale)` | Metallic grey robot | Glowing red head antenna |

### Available Face Atlases (`engine/assets/faces/`)
- `hero`, `hero_blood`, `girl`, `kid`, `mustache`, `plain`, `villain`

---

## 2. 3D Environments / Backgrounds (`LIB`, `W`, `W2`, `sets`, `locs`)

### New Pre-Lit Open-Front Rooms (`LIB.*`) — Ready for Camera (`-Y` open)
| Call | Setting | Key Props Included |
|---|---|---|
| `LIB.nurse_office()` | Bright school nurse's office | Exam bed, pillow, medicine cabinet, red cross, `NURSE OFFICE` sign |
| `LIB.courtroom()` | Wood-paneled courtroom | Raised judge's bench, witness stand, red carpet, lawyer tables |
| `LIB.diner()` | Retro burger diner | Checkered floor, red booths, counter, stools, glowing `BLOX BURGER` neon |
| `LIB.grocery_store()` | Supermarket aisle | Stocked colorful shelves, checkout counter, conveyor belt |
| `LIB.gym()` | School basketball gym | Hardwood court lines, basketball hoop/backboard, bleachers |
| `LIB.police_station()` | Police precinct | Booking height chart (`1–6 ft`), front desk, `POLICE DEPT` sign |
| `LIB.park_day()` | Sunny daytime park | Grass, paved walkway, wooden bench, blocky Roblox trees |
| `LIB.rooftop_night()` | Night city rooftop | Parapet wall, AC unit, glowing city skyline buildings, moon rim light |
| `LIB.subway_station()` | Underground metro | Yellow safety line, pillars, parked subway train car |
| `LIB.space_station()` | Sci-fi spaceship bridge | Metallic deck, glowing cyan & orange consoles, starfield sky |
| `LIB.haunted_house()` | Spooky mansion foyer | Pillars, grandfather clock, eerie purple & green lighting |
| `LIB.beach()` | Sunny tropical beach | Golden sand, turquoise ocean, palm tree, beach umbrella |

### Classic Kit Environments (`W.*`, `W2.*`, `sets.*`, `locs.*`)
- **School:** `W.classroom_day()`, `W.hallway_day()`, `locs.school_exterior()`, `locs.school_bathroom()`, `locs.teacher_room()`
- **Town / Public:** `W.town()`, `W.comedy_club()`, `W2.flower_shop()`, `W2.parking_lot()`, `W2.pepper_jail()`
- **Home / Indoor:** `sets.bedroom()`, `locs.living_room()`, `W.tv_room()`, `locs.dad_bathroom()`, `sets.mirror_world()`
- **Sky / Travel:** `W.space_world()`, `W.cockpit()`, `W2.airliner()`, `W2.cabin()`, `W.cloud_field()`

---

## 3. Reusable 3D Props (`LIB.prop_*`, `W.*`, `W2.*`, `story.*`)
- **New Props (`LIB.*`):** `prop_gavel()`, `prop_burger_tray()`, `prop_shopping_cart()`, `prop_basketball()`, `prop_treasure_chest()`, `prop_phone()`, `prop_trophy()`, `prop_megaphone()`, `prop_skateboard()`, `prop_desk_mic()`
- **Classic Props:** `W.car()`, `W.dog()`, `W.pigeon()`, `W2.cat()`, `W2.pepper_shaker()`, `W2.tomato()`, `W2.astronaut_helmet()`, `story.backpack()`, `story.pencil()`, `locs.mug()`

---

## 4. Animations, FX & Audio (`acting`, `fx`, `W2`, `engine/sfx/`)
- **Character Acting (`acting.*`):** `face()`, `blink()`, `talk()`, `act()`, `hold_pose()`, `wiggle()`, `panic()`, `nod()`, `shake()`, `look()`, `jump()`, `run()`, `breathe()`
- **Visual FX (`fx.*`, `W2.*`):** `W2.sneeze()`, `W2.poof()`, `W2.vanish()`, `W2.appear()`, `fx.fire_cluster()`, `fx.embers()`, `fx.smoke_volume()`, `fx.white_flash()`
- **Audio:** 45 built-in SFX in `engine/sfx/` + `engine/music/music.m4a` + `Montserrat-Black.ttf` captions.
