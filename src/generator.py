import os
import json
import uuid
import asyncio
import urllib.parse
import aiohttp

# Default negative prompt tuned for photorealistic SDXL face generation
DEFAULT_NEGATIVE_PROMPT = (
    "deformed, blurry, out of focus, low quality, bad anatomy, watermark, "
    "text, logo, cartoon, illustration, 3d render, painting, extra fingers, "
    "mutated hands, extra limbs, ugly, distorted face, oversaturated"
)

PROVIDER_NAMES = {
    "pollinations": "Pollinations.ai (cloud)",
    "comfyui": "Local ComfyUI (SDXL)",
}


class FaceGenerator:
    def __init__(self, graphics_dir, concurrency_limit=1, api_key=None,
                 provider="comfyui", comfyui_base_url="http://127.0.0.1:8188",
                 comfyui_model="", negative_prompt=DEFAULT_NEGATIVE_PROMPT,
                 steps=25, cfg=6.0, sampler="euler_a", scheduler="karras", size=1024):
        self.graphics_dir = graphics_dir
        self.semaphore = asyncio.Semaphore(max(1, concurrency_limit))
        self.api_key = api_key
        self.provider = provider if provider in PROVIDER_NAMES else "comfyui"
        self.comfyui_base_url = comfyui_base_url.rstrip("/")
        self.comfyui_model = comfyui_model or ""
        self.negative_prompt = negative_prompt if negative_prompt else DEFAULT_NEGATIVE_PROMPT
        self.steps = int(steps) if steps else 25
        self.cfg = float(cfg) if cfg else 6.0
        self.sampler = sampler or "euler_a"
        self.scheduler = scheduler or "karras"
        self.size = int(size) if size else 1024
        self._resolved_checkpoint = None
        os.makedirs(self.graphics_dir, exist_ok=True)

    @property
    def provider_name(self):
        return PROVIDER_NAMES.get(self.provider, self.provider)

    async def check_connection(self):
        """
        Verifies the selected provider is reachable before generating.
        Returns (ok, message) so the UI can log a friendly status.
        """
        if self.provider != "comfyui":
            return True, "cloud provider (no local connection required)"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.comfyui_base_url}/system_stats",
                                       timeout=10, ssl=False) as resp:
                    if resp.status == 200:
                        return True, f"ComfyUI server reachable at {self.comfyui_base_url}"
                    return False, f"ComfyUI server returned HTTP {resp.status}"
            except Exception as e:
                return False, (f"ComfyUI server NOT reachable at {self.comfyui_base_url} - "
                               f"is ComfyUI running? ({type(e).__name__})")

    async def download_face(self, session, uid, prompt, checkpoint=None):
        """
        Dispatches to the configured provider:
        - comfyui     -> local SDXL generation via ComfyUI's JSON API
        - pollinations -> cloud generation via Pollinations.ai
        """
        if self.provider == "comfyui":
            ckpt = checkpoint or self._resolved_checkpoint or self.comfyui_model or "v1-5-pruned-emaonly.safetensors"
            return await self.download_face_comfy(session, uid, prompt, ckpt)
        return await self.download_face_pollinations(session, uid, prompt)

    # ------------------------------------------------------------------
    # Provider: Local ComfyUI (SDXL)
    # ------------------------------------------------------------------
    @staticmethod
    def _seed_for(uid):
        """Derives a stable 32-bit seed from the player UID."""
        try:
            return int(uid) % (2 ** 32)
        except (ValueError, TypeError):
            return 0

    def build_sdxl_workflow(self, uid, prompt, checkpoint):
        """
        Builds a minimal single-image SDXL workflow that ComfyUI can execute.
        The seed is derived from the player UID so faces stay consistent
        across age milestones (same face structure, updated details).
        """
        return {
            "4": {"class_type": "CheckpointLoaderSimple",
                  "inputs": {"ckpt_name": checkpoint}},
            "5": {"class_type": "EmptyLatentImage",
                  "inputs": {"width": self.size, "height": self.size, "batch_size": 1}},
            "6": {"class_type": "CLIPTextEncode",
                  "inputs": {"text": prompt, "clip": ["4", 1]}},
            "7": {"class_type": "CLIPTextEncode",
                  "inputs": {"text": self.negative_prompt, "clip": ["4", 1]}},
            "3": {"class_type": "KSampler",
                  "inputs": {
                      "seed": self._seed_for(uid),
                      "steps": self.steps,
                      "cfg": self.cfg,
                      "sampler_name": self.sampler,
                      "scheduler": self.scheduler,
                      "denoise": 1.0,
                      "model": ["4", 0],
                      "positive": ["6", 0],
                      "negative": ["7", 0],
                      "latent_image": ["5", 0],
                  }},
            "8": {"class_type": "VAEDecode",
                  "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
            "9": {"class_type": "SaveImage",
                  "inputs": {"filename_prefix": f"fm_{uid}", "images": ["8", 0]}},
        }

    async def download_face_comfy(self, session, uid, prompt, checkpoint):
        """
        Submits the SDXL workflow to a running ComfyUI server, polls its
        history endpoint until the image is ready, then downloads it.
        """
        workflow = self.build_sdxl_workflow(uid, prompt, checkpoint)
        payload = {"prompt": workflow, "client_id": f"fm-generator-{uuid.uuid4()}"}

        async with self.semaphore:
            try:
                # 1. Submit the workflow
                async with session.post(f"{self.comfyui_base_url}/prompt",
                                        json=payload, timeout=60, ssl=False) as resp:
                    if resp.status != 200:
                        body = await resp.text()
                        return {"uid": uid, "status": "failed",
                                "error": f"ComfyUI rejected request (HTTP {resp.status}): {body[:200]}"}
                    result = await resp.json()

                prompt_id = result.get("prompt_id")
                if not prompt_id:
                    return {"uid": uid, "status": "failed",
                            "error": "ComfyUI did not return a prompt_id (workflow rejected)"}

                # 2. Poll /history/{prompt_id} until the job finishes (~5 min cap)
                for _ in range(150):
                    await asyncio.sleep(2)
                    try:
                        async with session.get(
                                f"{self.comfyui_base_url}/history/{urllib.parse.quote(prompt_id)}",
                                timeout=30, ssl=False) as resp:
                            history = await resp.json()
                    except Exception:
                        continue

                    entry = history.get(prompt_id)
                    if not entry:
                        continue

                    status = entry.get("status", {})
                    if status.get("status_str") == "success":
                        # 3. Collect generated images from the SaveImage node
                        images = []
                        for out in entry.get("outputs", {}).values():
                            images.extend(out.get("images", []))
                        if not images:
                            return {"uid": uid, "status": "failed",
                                    "error": "ComfyUI finished but produced no image output"}

                        img = images[0]
                        view_url = (
                            f"{self.comfyui_base_url}/view"
                            f"?filename={urllib.parse.quote(img['filename'])}"
                            f"&subfolder={urllib.parse.quote(img.get('subfolder', ''))}"
                            f"&type={img.get('type', 'output')}"
                        )
                        async with session.get(view_url, timeout=60, ssl=False) as resp:
                            content = await resp.read()

                        filepath = os.path.join(self.graphics_dir, f"{uid}.png")
                        with open(filepath, "wb") as f:
                            f.write(content)
                        return {"uid": uid, "status": "success", "file": filepath}

                    if status.get("status_str") == "error":
                        messages = status.get("messages") or []
                        detail = messages[0][1] if messages else {"message": "Unknown ComfyUI error"}
                        return {"uid": uid, "status": "failed",
                                "error": f"ComfyUI error: {json.dumps(detail)[:300]}"}

                return {"uid": uid, "status": "failed",
                        "error": "ComfyUI generation timed out (took longer than 5 minutes)"}

            except asyncio.TimeoutError:
                return {"uid": uid, "status": "failed",
                        "error": "TimeoutError (ComfyUI did not respond in time)"}
            except aiohttp.ClientConnectorError:
                return {"uid": uid, "status": "failed",
                        "error": "ClientConnectorError (ComfyUI is not running. Start it before generating)"}
            except Exception as e:
                return {"uid": uid, "status": "failed", "error": f"{type(e).__name__}: {e}"}

    async def _resolve_checkpoint(self, session):
        """
        Picks the SDXL checkpoint to use:
        - Use the one configured in config.json if set.
        - Otherwise auto-detect the first checkpoint available in ComfyUI.
        """
        if self.comfyui_model:
            self._resolved_checkpoint = self.comfyui_model
            return self.comfyui_model

        try:
            async with session.get(
                    f"{self.comfyui_base_url}/object_info/CheckpointLoaderSimple",
                    timeout=30, ssl=False) as resp:
                info = await resp.json()
            names = info["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
            checkpoint = names[0] if names else "v1-5-pruned-emaonly.safetensors"
        except Exception:
            checkpoint = "v1-5-pruned-emaonly.safetensors"

        self._resolved_checkpoint = checkpoint
        return checkpoint

    # ------------------------------------------------------------------
    # Provider: Pollinations.ai (cloud, legacy)
    # ------------------------------------------------------------------
    async def download_face_pollinations(self, session, uid, prompt):
        """
        Downloads a single AI generated face from Pollinations.ai.
        Uses the player's Unique ID (UID) as the seed for visual consistency.
        Retries up to 5 times, handles HTTP 429 rate limiting using exponential
        backoff with jitter, staggers concurrent requests, and bypasses Windows SSL issues.
        """
        import random
        encoded_prompt = urllib.parse.quote(prompt)

        # Build URL depending on whether the user provided a free API key from enter.pollinations.ai
        if self.api_key:
            # Authenticated requests can use the premium 'flux' model for photorealism
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={uid}&model=flux&nologo=true&private=true&key={self.api_key}"
        else:
            # Keyless requests default to Sana
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

            for attempt in range(1, 6):
                try:
                    async with session.get(url, headers=headers, timeout=30, ssl=False) as response:
                        if response.status == 200:
                            content = await response.read()
                            with open(filepath, "wb") as f:
                                f.write(content)
                            return {"uid": uid, "status": "success", "file": filepath}
                        elif response.status == 429:
                            err_msg = "HTTP 429 (Rate Limited)"
                            # Wait and backoff with random jitter to break request cycles
                            await asyncio.sleep(backoff_delay + random.uniform(1.0, 3.0))
                            backoff_delay *= 2.0
                            continue
                        else:
                            err_msg = f"HTTP {response.status}"
                except Exception as e:
                    err_msg = f"{type(e).__name__}: {str(e)}"

                # Wait 2 seconds before retrying on general errors
                if attempt < 5:
                    await asyncio.sleep(2.0 + random.uniform(0.5, 1.5))

            # Append URL to error message for debugging
            err_msg_with_url = f"{err_msg} (URL: {url})"
            return {"uid": uid, "status": "failed", "error": err_msg_with_url}

    async def generate_faces_async(self, players_to_generate, prompt_template, progress_callback=None):
        """
        Takes a list of player dicts, generates prompts, and generates/downloads their faces.
        """
        from src.parser import PromptBuilder

        self._resolved_checkpoint = None
        async with aiohttp.ClientSession() as session:
            # For ComfyUI, resolve which checkpoint to use once for the whole batch
            checkpoint = None
            if self.provider == "comfyui":
                checkpoint = await self._resolve_checkpoint(session)

            tasks = []
            for player in players_to_generate:
                uid = player["uid"]
                # Build the prompt
                prompt = PromptBuilder.build_prompt(player, prompt_template)
                # Queue the task
                tasks.append(self.download_face(session, uid, prompt, checkpoint))

            results = []
            for count, future in enumerate(asyncio.as_completed(tasks), 1):
                res = await future
                results.append(res)
                if progress_callback:
                    # Trigger UI update
                    progress_callback(count, len(tasks), res)

            return results