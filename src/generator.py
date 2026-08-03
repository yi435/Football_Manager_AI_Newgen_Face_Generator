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
        Retries up to 3 times, handles HTTP 429 rate limiting using exponential backoff,
        staggers concurrent requests, and bypasses Windows SSL issues.
        """
        import random
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={uid}&nologo=true&private=true"
        filepath = os.path.join(self.graphics_dir, f"{uid}.png")

        # Limit concurrent downloads to avoid rate limits
        async with self.semaphore:
            # Stagger requests by sleeping a random duration (1.5 to 2.5s) before each call
            await asyncio.sleep(random.uniform(1.5, 2.5))
            
            err_msg = "Unknown error"
            backoff_delay = 5.0  # Initial sleep time in seconds for HTTP 429
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://pollinations.ai/",
            }

            for attempt in range(1, 4):
                try:
                    async with session.get(url, headers=headers, timeout=30, ssl=False) as response:
                        if response.status == 200:
                            content = await response.read()
                            with open(filepath, "wb") as f:
                                f.write(content)
                            return {"uid": uid, "status": "success", "file": filepath}
                        elif response.status == 429:
                            err_msg = "HTTP 429 (Rate Limited)"
                            # Wait and backoff
                            await asyncio.sleep(backoff_delay)
                            backoff_delay *= 2.0
                            continue
                        else:
                            err_msg = f"HTTP {response.status}"
                except Exception as e:
                    err_msg = f"{type(e).__name__}: {str(e)}"
                
                # Wait 2 seconds before retrying on general errors
                if attempt < 3:
                    await asyncio.sleep(2.0)
            
            # Append URL to error message for debugging
            err_msg_with_url = f"{err_msg} (URL: {url})"
            return {"uid": uid, "status": "failed", "error": err_msg_with_url}

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
