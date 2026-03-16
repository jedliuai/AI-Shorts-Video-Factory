import os
import json
from pathlib import Path

BASE_DIR = Path("Z:/shorts_system/manual_generation_queue/pending")

tasks = {
    # ─── CHANNEL A: AI Animal Stories (Targeting V_A001 and V_A002 success) ───
    "TASK_A013": {
        "prompt": """===============================================
VIDEO ID: V_A013
CHANNEL: CH_A (AI Animal Stories)
===============================================

[0s-2s Hook]: Macro close-up on a rainy city alleyway. A tiny, shivering ginger kitten is hiding under a wet cardboard box. A terrifying shadow falls over it. Ominous string music builds. Cinematic chiaroscuro lighting.

[2s-5s First Surprise]: Mid-shot. A massive, scarred Doberman approaches, teeth bared. The kitten closes its eyes in fear. Suddenly, the Doberman drops a large, perfectly dry piece of soft bread right in front of the kitten.

[5s-8s Second Upgrade]: Slow tracking shot. The Doberman lies down on the wet pavement, using its massive body to block the cold rain from hitting the kitten. The kitten slowly opens its eyes, sniffs the bread, and begins to eat. Extremely high photorealistic fur details on both animals.

[8s-12s Big Reversal]: Close-up of their faces. The kitten stops eating, walks up to the terrifying Doberman, and gently rubs its head against the dog's nose. The Doberman's expression softens completely, and it lets out a gentle, warm huff of air.

[12s-15s Final Shot]: Wide shot showing the giant dog and tiny kitten curled up together, fast asleep under the cardboard box, forming a silhouette of safety against the rainy neon city background. Heartwarming acoustic guitar melody.

4K ultra HD, masterpiece textures, photorealistic animal fur, cinematic warm lighting, heartwarming emotional bond, high emotional depth. No non-English text.""",
        "json": {
            "title": "A Terrifying Dog Found a Shivering Kitten 🥺❤️ #shorts",
            "description": "Never judge a book by its cover. The most heartwarming rescue! 🐶❤️🐱\n\n#shorts #animalrescue #doberman #kitten #cuteanimals #heartwarming #epic",
            "tags": ["shorts", "animal friendship", "doberman", "kitten", "heartwarming", "rescue", "cute animals"],
            "privacy_status": "public",
            "made_for_kids": False,
            "channel": "ch_a"
        },
        "note": "A013: Emotional bond theme replicating V_A001. Focus on soft lighting, high fur texture, and tear-jerking cross-species friendship."
    },
    
    "TASK_A014": {
        "prompt": """===============================================
VIDEO ID: V_A014
CHANNEL: CH_A (AI Animal Stories)
===============================================

[0s-2s Hook]: Extreme close-up of a perfectly round, hyperrealistic cartoon-style raccoon wearing a tiny burglar mask, tiptoeing hilariously across a kitchen counter towards a giant glowing wedge of cheese. Fast xylophone comedy music.

[2s-5s First Surprise]: Suddenly, a massive, buff security guard bulldog bursts from inside the refrigerator holding a tiny stop sign. The raccoon freezes mid-air, eyes bugging out comically. 

[5s-8s Second Upgrade]: The raccoon pulls an impossibly large rocket-launcher out of its tiny pocket. Instead of firing a rocket, it shoots an enormous, sticky pink bubblegum pie directly into the bulldog's face with a loud "SPLAT!".

[8s-12s Big Reversal]: The bulldog blindly stumbles backward on a skateboard that appeared from nowhere, crashes into the dishwasher, and triggers a massive explosion of rainbow-colored soap bubbles that fills the entire kitchen.

[12s-15s Final Shot]: The raccoon gracefully lands on top of the cheese, pulls out a tiny tuxedo, puts it on, and bows to the camera as the soap bubbles pop everywhere.

4K ultra HD, extreme slapstick comedy physics, explosive action, cinematic lighting, photorealistic textures mixed with cartoon logic, masterpiece. No non-English text.""",
        "json": {
            "title": "Raccoon Burglar VS Security Bulldog! 😂🧀 #shorts",
            "description": "The ultimate Tom & Jerry style heist! Wait for the bubble explosion! 💥🦝\n\n#shorts #raccoon #funnyanimals #slapstick #animalshorts #vfx #epic",
            "tags": ["shorts", "raccoon", "funny animals", "slapstick comedy", "vfx", "heist"],
            "privacy_status": "public",
            "made_for_kids": False,
            "channel": "ch_a"
        },
        "note": "A014: Tom & Jerry exaggerated physics replicating V_A002 success. Pure slapstick, crazy visual gags."
    },
    
    # ─── CHANNEL C: Stunning VFX Animation (Targeting V_C007 success) ───
    "TASK_C010": {
        "prompt": """===============================================
VIDEO ID: V_C010
CHANNEL: CH_C (Stunning VFX Animation)
===============================================

[0s-2s Hook]: [FOREGROUND]: 3D jagged crimson text "LIMIT BREAK" pulses like a heartbeat. [MIDGROUND]: A stunning cyberpunk girl with glowing blue twin-tails revs a massive plasma-chainsaw. [BACKGROUND]: A towering mechanical leviathan erupts from the concrete street. She yells "GET OUT OF MY WAY!" (English audio). High impact dubstep drop.

[2s-5s First Surprise]: Fast dynamic motion blur. [FOREGROUND]: Neon debris flying past lens. [MIDGROUND]: She leaps 50 feet into the air, spinning the chainsaw. [BACKGROUND]: The leviathan fires a million tracking missiles directly at her.

[5s-8s Second Upgrade]: Mid-air extreme 360 rotation. She screams "MAX OUTPUT!" (English audio). [FOREGROUND]: Blinding 3D typography "MAXIMUM" burns the screen in pure white fire. [MIDGROUND]: The chainsaw blade extends to 100 feet, glowing furiously with blue lightning. [BACKGROUND]: The missiles are frozen mid-flight by her energy field.

[8s-12s Big Reversal]: Real time resumes. She swings the colossal chainsaw down in a single, screen-splitting horizontal arc. The blue energy physically cuts the mechanical leviathan, all the missiles, and the clouds behind it cleanly in half. A deafening sonic boom of blue light engulfs everything.

[12s-15s Final Shot]: [FOREGROUND]: Blue electric sparks fading. [MIDGROUND]: She lands smoothly on a streetlamp, chainsaw retracting. [BACKGROUND]: The two halves of the leviathan slide apart and explode into an atomic mushroom cloud. 

4K ultra HD, insane spatial depth tracking, foreground/midground/background separation, gorgeous glowing 3D typography, game cutscene quality, anime masterpiece. Maintain text elements clearly.""",
        "json": {
            "title": "Cyber-Girl's CHAINSAW LIMIT BREAK! ⚙️💥 #vfx #anime",
            "description": "The most satisfying slice you will ever see! Pure cyberpunk adrenaline! ⚔️🔥\n\n#shorts #cyberpunk #vfx #animeedit #action #3Danimation #epic",
            "tags": ["shorts", "vfx", "anime edit", "cyberpunk", "chainsaw", "badass female", "3d text", "epic action", "depth"],
            "privacy_status": "public",
            "made_for_kids": False,
            "channel": "ch_c"
        },
        "note": "C010: Targeting V_C007 success. Intense spatial depth layers, vocalizations ('LIMIT BREAK'), and massive 3D Text FX."
    },

    "TASK_C011": {
        "prompt": """===============================================
VIDEO ID: V_C011
CHANNEL: CH_C (Stunning VFX Animation)
===============================================

[0s-2s Hook]: [FOREGROUND]: Complex glowing green magical runic circles spinning aggressively right in front of the lens. [MIDGROUND]: A breathtakingly beautiful necromancer queen, eyes bleeding dark green magic. [BACKGROUND]: An army of 10,000 holy knights charging across a blood-red desert. She screams "ARISE!" (English audio). Epic dark orchestral choir.

[2s-5s First Surprise]: [FOREGROUND]: Majestic 3D emerald typography "AWAKENING" slashes across the screen. [MIDGROUND]: She thrusts a jagged scythe deep into the sand. [BACKGROUND]: The ground violently erupts beneath the charging knights, shattering the entire army's formation.

[5s-8s Second Upgrade]: Extreme tilt-up cinematic shot. [FOREGROUND]: Green ash and screaming ghost particles flying. [MIDGROUND]: The queen levitating, laughing menacingly, she shouts "CONSUME THEM!" (English audio). [BACKGROUND]: A colossal, 500-foot tall skeletal dragon made entirely of emerald fire bursts from the sand canyon.

[8s-12s Big Reversal]: The skeletal dragon inhales sharply, warping space-time around its jaws. It unleashes a devastating, screen-filling torrent of pure green soul-fire. The breath weapon strikes the army in the background, vaporizing the knights into millions of glowing green embers in an earth-shattering shockwave.

[12s-15s Final Shot]: [FOREGROUND]: Glowing green embers floating gently. [MIDGROUND]: Close up on the queen's incredibly detailed face, smiling sadistically. [BACKGROUND]: The skeletal dragon roars triumphantly against the red sky.

4K ultra HD, extreme spatial depth layers, insanely detailed particle magic VFX, gorgeous 3D typography, unreal engine 5 game cinematic, perfect facial details. No non-English text.""",
        "json": {
            "title": "Necromancer Queen AWAKENS the Skeleton Dragon! 🐉💀 #vfx",
            "description": "The ultimate dark magic ultimate attack! Jaw-dropping Unreal Engine 5 VFX! ✨⚔️\n\n#shorts #necromancer #vfx #animation #epicmagic #fantasy #beautiful #cinematic",
            "tags": ["shorts", "vfx", "necromancer", "magic spell", "fantasy animation", "epic dragon", "beautiful anime", "game cutscene"],
            "privacy_status": "public",
            "made_for_kids": False,
            "channel": "ch_c"
        },
        "note": "C011: Targeting V_C007 success. Fantasy magic equivalent. FG runes, MG queen, BG army/dragon. 3D Text 'AWAKENING' and vocalizations."
    }
}

master_md_path = BASE_DIR / "ALL_PROMPTS_TO_GENERATE.md"
with open(master_md_path, "w", encoding="utf-8") as md_file:
    md_file.write("# 🎬 特选爆款总表 - 第三批 (Batch 3 Prompts)\n\n")
    md_file.write("> 这一批提示词**完全基于昨日数据跑通的最高流量视频**定制！\n> 请复制以下英文提示词放入 Seedance 2.0 中生成。\n> 生成后，重命名为对应的 VIDEO ID (如 `V_A013.mp4`)，并老规矩丢进 `Z:\\shorts_system\\nas_shorts\\inbox\\` 即可！\n\n")

    for task_id, content in tasks.items():
        task_dir = BASE_DIR / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        
        with open(task_dir / "prompt.txt", "w", encoding="utf-8") as f:
            f.write(content["prompt"])
            
        with open(task_dir / "publish_prep.json", "w", encoding="utf-8") as f:
            json.dump(content["json"], f, ensure_ascii=False, indent=2)
            
        with open(task_dir / "operator_note.txt", "w", encoding="utf-8") as f:
            f.write(content["note"])

        md_file.write(f"---\n\n## 🎞️ {task_id} ({content['json']['channel']})\n\n")
        
        if "A013" in task_id:
            md_file.write("**【中文定位】**：[对标 V_A001 大爆款] - 温情跨物种治愈：满脸刀疤的巨型杜宾犬在大雨中用身体为流浪小橘猫避雨，极致情绪拉扯与毛发质感展现\n\n")
        elif "A014" in task_id:
            md_file.write("**【中文定位】**：[对标 V_A002 大爆款] - 极端反差搞笑：戴眼罩的小浣熊遇上肌肉保安斗牛犬，掏出火箭筒却发射黏泡泡糖引发肥皂大爆炸，纯粹动画物理学演绎\n\n")
        elif "C010" in task_id:
            md_file.write("**【中文定位】**：[对标 V_C007 大爆款] - 多层景深赛博动作：赛博少女性感暴走，挥舞百尺等离子电锯斩断机甲鲲鹏。内含 3D艺术字、绝美远景爆炸，和角色英文怒吼配音！\n\n")
        elif "C011" in task_id:
            md_file.write("**【中文定位】**：[对标 V_C007 大爆款] - 多层景深黑暗奇幻：死灵女王在红沙漠复活百米翡翠骨龙瞬间秒杀圣骑士军团。内含 霸气3D魔法文字、复杂前后景，和施法英文怒吼配音！\n\n")
            
        md_file.write("**👇 请复制以下英文（包含结构标签）👇：**\n\n")
        md_file.write("```text\n")
        md_file.write(content["prompt"] + "\n")
        md_file.write("```\n\n")

print("Batch 3 (Targeted optimization tasks A013, A014, C010, C011) successfully generated!")
