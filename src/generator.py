import os
import asyncio
import urllib.parse
import aiohttp

class FaceGenerator:
    def __init__(self, graphics_dir, concurrency_limit=5):
        self.graphics_dir = graphics_dir
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        os.makedirs(self.graphics_dir, exist_ok=True)

    async def download_face(self, session, uid, prompt):
        """
        Asynchronously downloads a single AI generated face from Pollinations.ai.
        Uses the player's Unique ID (UID) as the seed for visual consistency.
        """
        # Encode prompt for URL
        encoded_prompt = urllib.parse.quote(prompt)
        # Using Flux/Stable Diffusion via Pollinations with seed mapping
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={uid}&nologo=true&private=true"
        
        filepath = os.path.join(self.graphics_dir, f"{uid}.png")

        # Limit concurrent downloads to avoid rate limits
        async with self.semaphore:
            try:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.read()
                        # Write the image to disk
                        with open(filepath, "wb") as f:
                            f.write(content)
                        return {"uid": uid, "status": "success", "file": filepath}
                    else:
                        return {"uid": uid, "status": "failed", "error": f"HTTP {response.status}"}
            except Exception as e:
                return {"uid": uid, "status": "failed", "error": str(e)}

    async def generate_faces_async(self, players_to_generate, prompt_template, progress_callback=None):
        """
        Takes a list of player dicts, generates prompts, and downloads their faces concurrently.
        """
        from src.parser import PromptBuilder
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for player in players_to_generate:
                uid = player["uid"]
                # Build the prompt
                prompt = PromptBuilder.build_prompt(player, prompt_template)
                # Queue the task
                tasks.append(self.download_face(session, uid, prompt))

            results = []
            for count, future in enumerate(asyncio.as_completed(tasks), 1):
                res = await future
                results.append(res)
                if progress_callback:
                    # Trigger UI update
                    progress_callback(count, len(tasks), res)
            
            return results
