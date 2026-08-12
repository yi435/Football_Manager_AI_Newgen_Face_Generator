import os
import json
import asyncio
from src.parser import PlayerParser, PromptBuilder
from src.generator import FaceGenerator
from src.xml_manager import XMLManager

# Base configuration mock
TEST_PROMPT_TEMPLATE = "professional headshot photo of a male [AGE]-year-old [NATIONALITY] football player, [PERSONALITY], athletic build, realistic face, highly detailed skin texture, professional sports photography, neutral background"

def create_mock_export():
    """
    Creates a simulated FM player export file (mock_export.txt) in the exports directory.
    """
    os.makedirs("exports", exist_ok=True)
    filepath = os.path.join("exports", "mock_export.txt")
    
    # Headers and 3 mock newgens
    data = [
        "ID\tName\tNat\t2nd Nat\tAge\tPersonality",
        "2001000001\tTakashi Inamoto\tJPN\t\t16\tModel Citizen",
        "2001000002\tMoussa Sow\tFRA\tSEN\t20\tTemperamental",
        "2001000003\tMarcus Smith\tENG\t\t24\tJovial"
    ]
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(data))
    
    print(f"[Verify] Mock export file created at: {filepath}")
    return filepath

async def run_verification():
    print("=== Starting FM AI Newgen Generator Verification Run ===")
    
    # 1. Create mock data
    filepath = create_mock_export()
    
    # 2. Test Parser
    print("\n--- Testing Parser ---")
    try:
        players = PlayerParser.parse_file(filepath)
        print(f"[Success] Parsed {len(players)} players successfully:")
        for p in players:
            print(f"  - UID: {p['uid']} | Name: {p['name']} | Nat: {p['nat']} | 2nd Nat: {p['sec_nat']} | Age: {p['age']} | Personality: {p['personality']}")
    except Exception as e:
        print(f"[Error] Parsing failed: {e}")
        return

    # 3. Test Prompt Builder
    print("\n--- Testing Prompt Builder ---")
    prompts = {}
    for p in players:
        prompt = PromptBuilder.build_prompt(p, TEST_PROMPT_TEMPLATE)
        prompts[p["uid"]] = prompt
        print(f"  - Prompt for UID {p['uid']} ({p['name']}):\n    '{prompt}'\n")

    # 4. Test Image Generation (via the configured provider from config.json)
    config = {}
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

    provider = config.get("provider", "comfyui")
    print(f"--- Testing Image Generation ({provider}) ---")
    # We will test download for the first player (Japanese Model Citizen, UID: 2001000001)
    test_player = players[0]
    test_prompt = prompts[test_player["uid"]]
    
    graphics_dir = os.path.join("graphics", "AI Newgen Faces")
    os.makedirs(graphics_dir, exist_ok=True)
    
    generator = FaceGenerator(
        graphics_dir,
        concurrency_limit=1,
        api_key=config.get("api_key"),
        provider=provider,
        comfyui_base_url=config.get("comfyui_base_url", "http://127.0.0.1:8188"),
        comfyui_model=config.get("comfyui_model", ""),
        negative_prompt=config.get("comfyui_negative_prompt", ""),
        steps=config.get("comfyui_steps", 25),
        cfg=config.get("comfyui_cfg", 6.0),
        sampler=config.get("comfyui_sampler", "euler_a"),
        scheduler=config.get("comfyui_scheduler", "karras"),
        size=config.get("comfyui_size", 1024)
    )
    
    # Pre-flight connection check
    ok, msg = await generator.check_connection()
    print(f"[Info] Provider connection: {msg}")
    if not ok:
        print(f"[Error] Provider unreachable. Aborting download test.")
        return
    
    import aiohttp
    async with aiohttp.ClientSession() as session:
        print(f"[Info] Attempting to generate face for {test_player['name']} (UID: {test_player['uid']})...")
        res = await generator.download_face(session, test_player["uid"], test_prompt)
        
        if res["status"] == "success":
            print(f"[Success] Image generated and saved to: {res['file']}")
        else:
            print(f"[Error] Image generation failed: {res['error']}")
            return

    # 5. Test XML Manager & Metadata
    print("\n--- Testing XML Mapping and Metadata update ---")
    xml_manager = XMLManager(graphics_dir)
    
    # Simulate mapping updates
    mappings = xml_manager.load_mappings()
    mappings[test_player["uid"]] = test_player["uid"]
    xml_manager.save_mappings(mappings)
    
    # Save test metadata
    metadata_path = os.path.join(graphics_dir, "metadata.json")
    metadata = {test_player["uid"]: 16}
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"[Success] config.xml updated at: {os.path.join(graphics_dir, 'config.xml')}")
    print(f"[Success] metadata.json updated at: {metadata_path}")
    print("\n=== Verification Run Completed Successfully ===")

if __name__ == "__main__":
    asyncio.run(run_verification())
