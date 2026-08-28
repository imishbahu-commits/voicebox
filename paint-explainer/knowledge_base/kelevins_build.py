#!/usr/bin/env python3
"""Builds the Kelevins-style script JSON + a readable VO script from one beat list.

Timings are computed from each beat's spoken length at WPM (155 — the pace his real
chapter spacing implies: 6 entries over ~15:40), so timestamps and the description's
chapter list are derived, not decorative. Run: python3 kelevins_build.py
"""
import json
from pathlib import Path

WPM = 155
HOLD = 1.1  # seconds of visual/breath padding per beat
HERE = Path(__file__).resolve().parent

# chapter, entry, [(narration, visual, edit, keywords)]
SEGMENTS = [
    (
        "Hook",
        "Bronze Age",
        [
            (
                "This helmet is four thousand years old, it is cast from bronze, and the man inside it cannot see. "
                "Not as a metaphor. There are two slits here and a nose guard here, and the lower half of his vision is simply gone. "
                "He is walking into a melee like this, on purpose, because it was the best his city could build.",
                "gold bronze helmet on black; red arrows at the eye slits and nose guard; a first-person view of almost nothing",
                "cold open, no intro music: hard cut on 'cannot see', 8% punch-in over 0.4s, arrows pop one per clause",
                ["4000 years old", "cannot see", "best they could build"],
            ),
            (
                "And that is the whole trick of this video. Nobody in these next fifteen minutes was stupid. "
                "The worst safety gear from every time period, in order, and the order is the punchline.",
                "title card 'THE WORST SAFETY GEAR FROM EVERY TIME PERIOD' over a six-icon timeline strip",
                "title slams on 'was stupid', timeline strip wipes left to right, one era per beat of the line",
                ["nobody was stupid", "title promise"],
            ),
        ],
    ),
    (
        "00:00 Bronze Age",
        "Bronze Age",
        [
            (
                "We start with the Mycenaeans, who looked at a human skull and said: yes, but what if it were a kettle. "
                "The answer was a helmet. The boar's tusk helmet, which is exactly what it sounds like and twice as ridiculous.",
                "boar's tusk helmet, product-shot lighting, a kettle morphing into the helmet",
                "morph cut 0.35s, tusks pop in row by row with a 0.12s stagger",
                ["kettle", "boar's tusk"],
            ),
            (
                "Roughly sixty boar tusks, hand-drilled, threaded onto a leather cap. Ivory nose guard, a comb on top. "
                "It is genuinely beautiful, it is a nightmare to make, and it is mostly a hairpiece that happens to stop a spear.",
                "exploded view: tusks, thread, leather cap, ivory guard; a count-up to 60",
                "parts fly in from off-screen and assemble on 'stop a spear'; counter ticks to 60",
                ["60 tusks", "hairpiece"],
            ),
            (
                "The bronze ones you have seen in films are the Corinthian type, and they are a masterpiece of the wrong priorities. "
                "Excellent coverage. Terrible eyesight. The design protects the head from a swing and sacrifices the thing you need to survive a fight: seeing the fight.",
                "Corinthian helmet rotating, vision cone diagram showing ~30° usable, arrow deflecting off the dome",
                "rotation 22°/s, vision cone draws on and clamps at 30°, red hatch over the blocked field",
                ["wrong priorities", "30 degree vision"],
            ),
            (
                "Why the dome? Because bronze is soft. A flat panel crumples, a curved one sheds the blow sideways. "
                "They solved a materials problem and created an anatomy problem. Also the shape funnels a downward thrust toward the neck. Fair trade, honestly.",
                "two helmets: flat-top crumpling under a hammer, dome deflecting; a thrust arrow sliding down to the neck",
                "hammer impact = 3-frame white flash + 12% shake; arrow trails 0.5s down to the neck",
                ["bronze is soft", "funnels the thrust"],
            ),
            (
                "The Greeks knew. That is the part that gets left out. Later types, the Italic and Chalcidian, cut the cheeks away, "
                "moved the eye holes apart and added a moustache to deflect sword points. They fixed it. Slowly, and it took three centuries, but they fixed it.",
                "three helmets in a row, morphing: Corinthian to Chalcidian to Italic; moustache highlight",
                "morph on each name, moustache gets a 0.2s glint sweep",
                ["they knew", "moustache deflects"],
            ),
            (
                "And heat. Two kilos of metal in an Aegean summer, so the field solution was to push the helmet up onto the crown "
                "and wear it like a hat until the fighting started. Vases show this. Greek artwork of soldiers with their safety gear around their heads like a beanie is not a joke; it is documentation.",
                "red-figure vase animation of a helmet pushed up, sun rays, sweat drops, a thermometer",
                "helmet slides up with a bounce, sun rays rotate 6°/s, 'IT IS DOCUMENTATION' stamp tilts -4°",
                ["worn as a beanie", "vases confirm"],
            ),
            (
                "Light troops got a felt cap called a pilos, which is a hat. That is the entire specification. "
                "If you could not afford bronze, your head protection was millinery, and nobody wrote that down as a problem.",
                "wool pilos cap next to the bronze helmet, price tags: 1 day's wage vs 3 months",
                "split wipe, price tags drop with a squash, 'millinery' underline draws on",
                ["a hat", "millinery"],
            ),
        ],
    ),
    (
        "02:35 Gladiators",
        "Galerus",
        [
            (
                "Rome. Everybody talks about the sword. Nobody talks about the fact that a gladiator's guard arm was, functionally, "
                "a door. The galerus is canvas and leather, stuffed with wool, strapped to the forearm. That is the technology.",
                "galerus build-up: canvas tube, wool stuffing, straps; a door icon fading into the arm",
                "exploded parts fly in, assemble on 'that is the technology', door morph 0.3s",
                ["a door", "wool and canvas"],
            ),
            (
                "And it works. Test reconstructions take gladius cuts into layered wool and canvas and the edge binds and stops. "
                "The armour was never the weak part. The weak part is the man wearing it, standing in sand, at noon, for an audience.",
                "test rig: padded arm on a steel post, blade contact, slow-mo stop at the wool layer",
                "slow-mo to 25% on 'binds and stops', back to 100% on 'for an audience', crowd audio swell",
                ["it works", "for an audience"],
            ),
            (
                "The gladiator helmet is the real artefact of the age. The Thraex type has a grille where a face should be "
                "and slots two centimetres high. Modern experiments wearing reconstructions: you cannot see the ground. You cannot see sideways. "
                "You are duelling a man with a sword while looking through a mail slot.",
                "Thraex helmet with the fishtail crest, macro of the grille, first-person view of legs and nothing else",
                "macro push-in 0.5s, POV gets a vignette + 2cm slit mask, 'YOU CANNOT SEE THE GROUND' on the beat",
                ["2cm slots", "mail slot"],
            ),
            (
                "Those eye slots are the trade: a sword point cannot enter a slot that small, so the arena is fought half-blind on purpose. "
                "Ancient writers actually joke about gladiators missing each other. The joke is that the gear made it normal.",
                "two gladiators swinging at empty air, a measurement of the slot vs a blade tip, an ancient bust shrugging",
                "blade whooshes miss by 30cm with dashed arcs, caliper reads 20mm, shrug with a comic 'well' caption",
                ["half-blind on purpose", "made it normal"],
            ),
            (
                "Now the part nobody puts on a poster: heat illness. Sand, metal, oil, no shade, four fights in an afternoon. "
                "Ancient accounts describe men pulled out confused and vomiting, and the arena floor had a lime layer partly to soak blood. "
                "It also tells you what the day was like: hot, bright, and lethal before anyone was hit.",
                "infrared view of an arena floor, thermometer climbing, lime being scattered",
                "thermal palette shift over 0.6s, mercury rises with a 1.2s ease-in-out, lime falls as particles",
                ["heat illness", "lime for blood"],
            ),
            (
                "The fix that existed: a referee with a hammer, and a missio, a reprieve, so a fighter could stand down and drink. "
                "They invented the water break and the fight-stop. They did not invent a vent. That is still on the list of things we have not solved for helmets.",
                "summa rudis official with hammer, a 'MISSIO' tablet, a modern helmet with a red 'NO VENTS' tag",
                "hammer raises on 'reprieve', tablet stamps, cut to modern helmet with a 0.2s glint on 'no vents'",
                ["they invented the water break", "still no vents"],
            ),
            (
                "Summary of Roman personal protection: brilliant padding on the arm, a face cage for the arena, and a head boiled in a bucket. "
                "The Romans were engineers. They engineered a spectator sport so hard that the safety problem became a business model.",
                "three icons: galerus check, grille check, bucket cross; a ticket stub over the bucket",
                "checks stamp 0.2s each, cross buzzes, ticket stub slides in with a cash-register SFX",
                ["safety as a business model", "engineered a sport"],
            ),
        ],
    ),
    (
        "05:05 Medieval",
        "The Quilt",
        [
            (
                "Medieval Europe. Forget the plate armour you are picturing. Plate is the top one percent, literally. "
                "Most men who went to war in the thirteen-hundreds wore a coat. Twenty-odd layers of quilted linen. A gambeson. That was the plan.",
                "population pyramid of helmet icons: 1% plate, 99% quilted coat; a farmer holding the coat like a gift",
                "pyramid builds bottom-up in 0.8s, 99% layer gets a highlight sweep, coat unfolds with a cloth sound",
                ["top one percent", "a coat"],
            ),
            (
                "It is not a bad coat. Reproduction testing puts arrows into layered linen and the padding grabs the point; "
                "some arrow tests are beaten by the quilt rather than by the mail. Quoting the surviving contracts, tailors were paid by the layer, "
                "which is the most medieval sentence I can say on camera: your armour had a spec sheet and a piece rate.",
                "cross-section of quilted layers, an arrow burying itself, a guild contract with 'per layer' highlighted",
                "layers peel apart on the count, arrow embeds with a 0.15s recoil, contract line underlines",
                ["stops arrows", "paid by the layer"],
            ),
            (
                "It is also a sponge. Rain, sweat, mud, five kilos of wet fabric that never dries inside, on a campaign that lasts four months. "
                "Chroniclers complain about men shedding the coats to stop chafing, right before battle. So the armour is optional in practice, because it is miserable.",
                "gambeson dripping, scale jumping to 5kg, calendar flipping, a line of soldiers shrugging coats off",
                "droplets at 0.4s intervals, needle overshoots and settles, calendar flips accelerate, coats fall off one by one",
                ["sponge", "they took it off"],
            ),
            (
                "Mail solves the cut and adds twelve kilos of holes. A hauberk stops a slash, and a heavy spear or a war hammer "
                "just pushes the rings apart and hurts anyway. Medieval armourers knew this, which is why the fourteenth century suddenly gets plate over the mail: "
                "the longbow and the crossbow changed the maths.",
                "ring spread diagram under a spear point, then a layer of plate plates snapping over the mail",
                "rings stretch with a 0.3s stress glow, plate pieces click on in sequence 0.1s each",
                ["12 kilos of holes", "the bow changed the maths"],
            ),
            (
                "The great helm, the bucket you see in every film, is arguably worse for the man wearing it than for the man hitting him. "
                "Reconstructed ones run 2 to 2.5 kilos, no peripheral vision, restricted breathing, and heat that climbs fast. "
                "Chronicles describe knights being hoisted back onto horses because they could not see or breathe well enough to mount.",
                "great helm with a vision-band diagram, CO2 buildup animation, a knight being lifted by two men",
                "vision band clamps to 55°, CO2 haze fills over 0.9s, hoist rope tightens with a lift sound",
                ["worse for the wearer", "hoisted onto the horse"],
            ),
            (
                "Which brings us to the most honest fact about medieval armour: you wore it for the fight and took it off after, "
                "and battles lasted minutes. Reenactment and biomechanics work keeps landing on the same limit: stamina, not penetration. "
                "The suit is nearly invulnerable for eleven minutes and then the man inside is finished.",
                "a timer counting 11:00 over an armoured figure, heart rate climbing, the figure sitting down",
                "timer digits flip, heart-rate line rises in sync, figure drops to a knee on 'finished'",
                ["stamina not penetration", "eleven minutes"],
            ),
            (
                "So the medieval kit is 90 percent coverage and a designer's eye for exactly where not to put any: "
                "back of the knee, armpit, groin, the visor gap you only remember to close when you see them coming. "
                "Every one of those is a hole a professional was aware of and priced.",
                "armoured figure with four pulsing red gaps, a pricing ledger next to each gap",
                "gaps pulse at 1.1Hz, targeting lines converge, ledger numbers tick up per gap",
                ["priced the holes", "visor gap"],
            ),
        ],
    ),
    (
        "07:40 Renaissance",
        "The Ruff",
        [
            (
                "Renaissance. Somebody looks at neck protection and delivers a starched collar the size of a cart wheel. "
                "The ruff: stiffened with starch, wired with a support staple, ironed for an hour every morning. It makes turning your head physically impossible.",
                "elizabethan ruff on a mannequin, wire and iron icons, a head trying to turn and clamping at 25°",
                "ruff unfurls with a 0.6s scale-in, rotation clamps with a 'NOPE' tag, iron steam puffs",
                ["cart wheel", "cannot turn your head"],
            ),
            (
                "Was it armour? No. It is status, and the message is 'I have so many servants that one of them irons my neck'. "
                "There is a real design lesson in that: once gear signals wealth, it stops being optimised for the hazard.",
                "a servant ironing at dawn, then a courtier; a 'STATUS' label replacing a 'PROTECTION' label",
                "label swaps with a 0.25s flip, gold flecks drift across the courtier side",
                ["status not armour", "stops being optimised"],
            ),
            (
                "And it is a fire hazard. Starched linen next to candles, at a collar height that is basically a wick. "
                "There are period jokes about it, which is the historians' way of telling you it happened.",
                "ruff near candles, a singed edge, a page of marginalia",
                "flame licks with a 0.4s flicker, singe creeps along the edge, manuscript page flips in",
                ["collar-height wick", "period jokes"],
            ),
            (
                "Meanwhile real soldiers get the morion and the cabasset, which are beautiful and shade the sun magnificently. "
                "Neither has cheek protection, and neither has a chin strap requirement. Your helmet becomes a hat again, in a war of pike and shot.",
                "morion and cabasset side by side, symmetrical mirror, bare jaw hatched red",
                "symmetry mirror effect on 'beautiful', jaw wipes to red hatch, hat-tilt on the word 'hat'",
                ["a hat again", "no chin strap"],
            ),
            (
                "The armourers of the sixteenth century get credit they are owed: they proof-marked pieces. "
                "A proof is a deliberate hammer or pistol strike, and the dent is left in, and the piece is stamped. "
                "That dent is a warranty. It is the first time in this video somebody is legally accountable for a helmet.",
                "proof dent macro, a stamped mark, a hammer blow and a pistol on a bench",
                "hammer impact 3-frame flash, dent highlight pulses, stamp presses with dust puff",
                ["the dent is a warranty", "accountable"],
            ),
            (
                "And then the thing nobody mentions: armour got worse at the exact moment it got prettier. "
                "By 1600 breastplates are engraved, fluted for rigidity, decorated, and thinner, because black powder made thickness pointless and parade made it profitable.",
                "ornate engraved cuirass, a caliper shrinking 3mm to 1.2mm, a parade ground",
                "engraving traces in 0.5s, caliper animates down with a 'THINNER' label, confetti on 'parade'",
                ["thinner and prettier", "fluted for rigidity"],
            ),
            (
                "So: one century of genuinely clever metalwork, and the common soldier wearing boiled leather and a padded jack, "
                "with the fashion industry out-designing the military on protecting human beings. Put that in your pocket; it comes back in the 1800s.",
                "buff coat and jack next to a plumed helmet, a tailor's measuring tape, a 'TO BE CONTINUED' bar",
                "split wipe on 'boiled leather', tape animates, to-be-continued bar slides up 0.2s",
                ["boiled leather", "to be continued"],
            ),
        ],
    ),
    (
        "10:05 Industrial",
        "The Ledger",
        [
            (
                "Now the interesting century, because the enemy is no longer a weapon. It is a machine, and the maths changes. "
                "Safety gear in the eighteen-hundreds exists or does not exist based on one line in a ledger: which is cheaper, the guard or the arm.",
                "factory floor silhouette, unguarded shafts, a ledger: 'guard £4 / replacement worker £2'",
                "gears rotate at 40 RPM, ledger numbers count up, monochrome grade + film grain",
                ["which is cheaper", "the guard or the arm"],
            ),
            (
                "Textile mills. No guarding on drive shafts, no hair constraints, twelve-hour shifts in cotton dust. "
                "Byssinosis is the medical name for lungs slowly becoming the product. There is a phrase in the trade records for it: 'Monday fever', because the symptom came back after the weekend.",
                "loom shafts, long hair near a belt, dust in a light beam, a chest X-ray fading in",
                "dust motes at 0.6 opacity drift, X-ray fades over 0.5s, 'MONDAY FEVER' caption in period type",
                ["byssinosis", "monday fever"],
            ),
            (
                "Mining. A canvas cap with a leather brim and a candle nailed to it. A candle, in a room with firedamp. "
                "The safety lamp existed, and it was heavier, dimmer, cost money and could go out — so the candle won for decades. "
                "That is the shape of most industrial safety: the better option is available and loses.",
                "miner's cap with candle, a Davy lamp pushed aside with a price tag, a gas meter needle climbing",
                "flame flickers warmly, lamp slides off-screen, gas needle creeps with a soft alarm tone",
                ["candle in gas", "the better option loses"],
            ),
            (
                "Some pits went further and put a child at the door. A trapper, often eight years old, sitting in the dark for twelve hours "
                "opening a ventilation door, and the safety device here is not a device, it is a kid who is not allowed to fall asleep.",
                "a pit brow door in the dark, a small stool, a lantern, a 'TRAPPER: AGE 8' tag",
                "single lantern light with a slow 6% flicker, door creaks open on the beat, tag stamps in",
                ["the safety device is a child", "not allowed to sleep"],
            ),
            (
                "War catches up. 1915, the Brodie helmet: a steel saucer that stops falling shell fragments and does almost nothing "
                "for a bullet, with no face protection at all, so the trench answer for your face was a scarf and a good position.",
                "Brodie top view, fragment deflecting, side impact with a 'NO' badge, a scarf wrapping three times",
                "deflection arc animates 0.4s, 'NO' badge pops, scarf loops on a 0.15s beat each",
                ["stops fragments not bullets", "a scarf"],
            ),
            (
                "Gas arrives and the response time is the story. Chlorine at Ypres in April 1915; the improvised answer was a pad, "
                "urine if nothing else was available, and the honest point is not the punchline: men were given a instruction instead of equipment, "
                "and the equipment took months.",
                "green cloud over a trench, a helmet design evolution strip 1915 to 1916, dated notebook page",
                "cloud drifts left to right over 1.2s, evolution strip wipes with year stamps, notebook page turns",
                ["instruction instead of equipment", "took months"],
            ),
            (
                "The hard hat is the counter-example, and it is recent. 1918, a US Army officer who had seen the helmets in France comes back "
                "and pushes a fibre helmet on the home front; US Steel makes its first full crews wear them in 1919. "
                "Look at what changed: not the materials. Somebody decided, and then it was mandatory.",
                "1918 fibre helmet, an inspector's clipboard, a factory line all wearing hats on the same day",
                "clipboard ticks 14 rows in 0.6s, hats appear down the line one per 0.08s frame",
                ["not the materials", "it was mandatory"],
            ),
            (
                "Which is why this era is the hinge of the video. Before now, bad gear was mostly a limit of what could be made. "
                "From here on, bad gear is a choice somebody priced. Keep that frame in mind for the last section, because it is still running.",
                "the ledger again, now with a column 'LIVES', a hand stamping 'APPROVED'",
                "camera pushes in 10% over 0.8s, LIVES column types itself, stamp hits with shake + dust",
                ["the hinge", "somebody priced it"],
            ),
        ],
    ),
    (
        "12:35 Modern",
        "The Good News",
        [
            (
                "Which brings us to now, and here the video stops being a joke. A current combat helmet is aramid and polyethylene, "
                "rated by a V50 ballistic limit — the velocity where half the test shots penetrate — with a chin strap, "
                "eye protection, and a shell shaped to keep fragments off the neck. Four thousand years, and finally the head can see.",
                "modern helmet exploding into layers, V50 rig in slow motion, vision cone opening from 30° to 180°",
                "layers separate on a 0.9s ease-out-expo, V50 counter ticks, vision cone widens with a whoosh",
                ["V50", "finally the head can see"],
            ),
            (
                "Mine rescue gear now has sealed optics, supplied air and a radio, and the difference from 1850 is not that we got smarter. "
                "It is that the cost of a life finally got written in the same column as the cost of the lamp.",
                "split: candle cap vs modern rescue rig, both side-on, same wall behind them",
                "hard split wipe on 'not that we got smarter', modern gear highlights in 0.2s sequence",
                ["same column", "not smarter"],
            ),
            (
                "But look at your bicycle, because the pattern is not dead. A typical cycling helmet is about 250 grams of EPS foam, "
                "certified for one near-linear impact at roughly 20 kilometres an hour, and it is excellent at that exact thing. "
                "Rotational injury is a real mechanism and it barely shows up on the box.",
                "helmet cross-section, one straight impact arrow, a second diagonal arrow with a question mark, a standards label",
                "impact arrow squashes 0.15s, diagonal arrow jitters unanswered, label zooms and holds",
                ["one impact at 20 km/h", "not on the box"],
            ),
            (
                "That is not an argument to ride without one — the linear protection is worth it, and head-injury data on helmet laws "
                "keeps pointing the same way. It is an argument to read what a standard tests for. Every era in this video had gear that was "
                "brilliant at the thing the buyer cared about and silent about the thing that actually hurt people.",
                "spec sheet scrolling, three lines highlighted, then the six era icons again in a row",
                "scroll decelerates on 'cared about', icons flash in sync with 'every era'",
                ["read the standard", "silent about"],
            ),
            (
                "And the newest version of the old idea is already shipping: motorcycle airbag vests, cyclist airbags, "
                "helmets with rotational liners, all of which exist because someone measured the injury that the previous standard ignored. "
                "That is the only reliable pattern in fifteen centuries of safety gear.",
                "airbag deploying on a torso, a MIPS-style liner rotating, a graph of head-injury rates falling",
                "airbag inflates in 0.35s with a fabric snap, liner rotates 12° twice, graph line drops 28%",
                ["measured the ignored injury", "the only pattern"],
            ),
            (
                "Four thousand years, six centuries, one lesson: safety gear has never been only about safety. "
                "It is about what the person paying thought the body was worth, and how much the person wearing it was allowed to complain. "
                "That is it, that is the video.",
                "six helmets in a row, the last one lit; a ledger closing; the timeline strip from the open returns",
                "each helmet lights for 0.12s in sequence, ledger closes with a thud, strip rewinds to 0:00",
                ["one lesson", "how much to complain"],
            ),
            (
                "If you know a piece of gear I got wrong or left out, put it in the comments, because I read all of them and I steal the good ones. "
                "Timestamps are in the description as always. Love you all, see you in the next one.",
                "end card: subscribe button pops, chapter list scrolls, 'LOVE YOU ALL' fades in",
                "subscribe pops on 'steal the good ones' with a click SFX, chapters scroll at 40px/s, VO tail 0.4s before music out",
                ["CTA", "timestamps", "sign-off"],
            ),
        ],
    ),
]

SPONSOR_SLOT = {
    "place_after_chapter": "10:05 Industrial",
    "duration": "45-60s",
    "note": "His real videos carry one mid-roll sponsor read (Incogni, code 'kelevin'), and the description is often just the "
            "sponsor line. Same deadpan register, one joke, then straight back in — never before the first entry.",
}


def fmt(sec: float) -> str:
    m, s = divmod(int(round(sec)), 60)
    return f"{m}:{s:02d}"


def beat_len(text: str) -> float:
    return round(len(text.split()) / WPM * 60 + HOLD, 1)


def main() -> None:
    beats, t = [], 0.0
    chapter_start: dict[str, float] = {}
    first_entry = SEGMENTS[1][0]
    for chapter, entry, lines in SEGMENTS:
        # His videos have no separate intro chapter: the hook lives inside entry #1 at 00:00.
        if chapter == "Hook":
            chapter = first_entry
        for narration, visual, edit, kw in lines:
            dur = beat_len(narration)
            chapter_start.setdefault(chapter, t)
            beats.append({
                "beat": len(beats) + 1,
                "time": f"{fmt(t)}-{fmt(t + dur)}",
                "narration": narration,
                "visual": visual,
                "edit": edit,
                "keywords": kw,
                "duration": f"{dur}s",
                "chapter": chapter,
            })
            t += dur

    words = sum(len(l[0].split()) for _, _, ls in SEGMENTS for l in ls)
    # Description chapters: his videos list the entries, starting 00:00 with entry #1.
    chapters = [
        f"{fmt(chapter_start[first_entry]) if c == 'Hook' else fmt(chapter_start[c])} {e}"
        for c, e, _ in SEGMENTS
        if c == "Hook" or c in chapter_start
    ][1:]  # drop the duplicated hook label; entry #1 already opens at 00:00
    description = (
        "These are the worst safety gear from every time period in history.\n\n"
        "Let me know down below if you've got any other terrible gear which you want to know about!\n"
        "Timestamps as always for you guys, Love you all!\n\n" + "\n".join(chapters)
    )

    script = {
        "version": "1.0",
        "reference_style": "kelevins",
        "topic": "worst-safety-gear-from-every-time-period",
        "title": "The Worst Safety Gear From Every Time Period",
        "duration_target": f"{fmt(t)}",
        "beats_target": len(beats),
        "narration_words": words,
        "pace_wpm": WPM,
        "structure": {
            "cold_open": "entry #1 begins at 0:00 with no intro — his real cults video chapters start '00:00 The Thuggee'",
            "entries": 6,
            "per_entry_target": "140-180s (measured spacing: 2:34 / 2:00 / 2:52 / 2:41 / 2:43)",
            "arc": "chronological, escalating absurdity, final entry turns sincere",
            "hook_shape": "one concrete absurd object + a promise of order ('we are doing this in order, because the order is the joke')",
            "comedy_rule": "one joke per fact, never two per beat; the fact is the punchline",
            "sponsor_slot": SPONSOR_SLOT,
            "outro": "one-line lesson, comment CTA, 'Timestamps as always… Love you all'",
        },
        "description_draft": description,
        "thumbnail_direction": {
            "status": "INFERRED — could not fetch his thumbnails from this sandbox; verify against 2-3 real ones",
            "layout": "single hero object, dead-centred, hard-edged on black or a flat colour field",
            "text": "≤4 words, heavy sans, one word in the accent colour; no sentence case, no emoji",
            "device": "one red arrow or circle on the flaw (the eye slit, the gap, the flame)",
            "faces": "none or a masked/obscured face — the object is the subject",
        },
        "beats": beats,
    }

    out = HERE / "script_kelevins_worst_safety_gear.json"
    out.write_text(json.dumps(script, indent=2) + "\n", encoding="utf-8")

    md = [
        "# The Worst Safety Gear From Every Time Period",
        "",
        f"Kelevins-format VO script · runtime **{fmt(t)}** · {len(beats)} beats · {words} words @ {WPM} wpm · 6 entries",
        "",
        "Shot list + edit notes live in `script_kelevins_worst_safety_gear.json` (same beats).",
        "Structure is copied from his real chapter spacing; verify voice/timing against a transcript.",
        "",
        "| chapter | starts |",
        "| --- | --- |",
    ]
    for c, e, _ in SEGMENTS:
        if c in chapter_start:
            md.append(f"| {c} | {fmt(chapter_start[c])} |")
    md += ["", "---", ""]
    current = None
    for b in beats:
        if b["chapter"] != current:
            current = b["chapter"]
            md += [f"## {current}", ""]
        md += [f"**{b['beat']:02d} · {b['time']} · {b['duration']}**", "", b["narration"], ""]
        md += [f"> 🎬 {b['visual']}", f"> ✂️ {b['edit']}", ""]
    (HERE / "script_kelevins_worst_safety_gear.md").write_text("\n".join(md), encoding="utf-8")

    print(f"beats={len(beats)} runtime={fmt(t)} words={words} chapters={len(chapters)}")
    print("wrote", out.name, "and", out.with_suffix('.md').name)


if __name__ == "__main__":
    main()
