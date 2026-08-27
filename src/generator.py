import os
import json
import uuid
import asyncio
import time
import urllib.parse
import ssl
try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    import certifi
    _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:
    _SSL_CONTEXT = ssl.create_default_context()

# Default negative prompt tuned for photorealistic SDXL face generation
DEFAULT_NEGATIVE_PROMPT = (
    "wrinkles, full body, crossed arms, hands, legs, lower body, background "
    "scenery, grass, soccer field, training pitch, trees, crowd, text, brand "
    "logos, badges, graphics, distorted logos, deformed crests, deformed "
    "apparel, waxy skin, CGI, 3D render, cartoon, illustration, drawing, "
    "digital art, makeup, smooth skin, airbrushed, blurred eyes, double chin, "
    "out of focus"
)

PROVIDER_NAMES = {
    "comfyui": "Local ComfyUI (SDXL)",
}


async def wait_for_comfyui(base_url, timeout=120, session=None, cancel_check=None):
    """
    Polls the ComfyUI /system_stats endpoint until it answers HTTP 200 or the
    timeout expires. ComfyUI can take a minute or two to boot (loading torch +
    the model), so generation should wait for it instead of failing instantly.
    ``cancel_check`` (optional) is polled every cycle; when it returns True the
    wait stops early and returns False.
    """
    base_url = base_url.rstrip("/")

    async def _up(s):
        try:
            async with s.get(f"{base_url}/system_stats", timeout=3) as r:
                return r.status == 200
        except Exception:
            return False

    async def _loop(s):
        while time.monotonic() < deadline:
            if cancel_check and cancel_check():
                return False
            if await _up(s):
                return True
            await asyncio.sleep(2)
        return False

    deadline = time.monotonic() + timeout
    if session is None:
        connector = aiohttp.TCPConnector(ssl=_SSL_CONTEXT)
        async with aiohttp.ClientSession(connector=connector) as s:
            return await _loop(s)
    return await _loop(session)


class FaceGenerator:
    def __init__(self, graphics_dir, concurrency_limit=1,
                 provider="comfyui", comfyui_base_url="http://127.0.0.1:8188",
                 comfyui_model="", negative_prompt=DEFAULT_NEGATIVE_PROMPT,
                 steps=25, cfg=6.0, sampler="euler_a", scheduler="karras",
                 width=896, height=1152):
        self.graphics_dir = graphics_dir
        self.semaphore = asyncio.Semaphore(max(1, concurrency_limit))
        self.provider = provider if provider in PROVIDER_NAMES else "comfyui"
        self.comfyui_base_url = comfyui_base_url.rstrip("/")
        self.comfyui_model = comfyui_model or ""
        self.negative_prompt = negative_prompt if negative_prompt else DEFAULT_NEGATIVE_PROMPT
        self.steps = int(steps) if steps else 25
        self.cfg = float(cfg) if cfg else 6.0
        self.sampler = sampler or "euler_a"
        self.scheduler = scheduler or "karras"
        self.width = int(width) if width else 896
        self.height = int(height) if height else 1152
        self._resolved_checkpoint = None
        os.makedirs(self.graphics_dir, exist_ok=True)

    @property
    def provider_name(self):
        return PROVIDER_NAMES.get(self.provider, self.provider)

    async def check_connection(self, wait_seconds=20):
        """
        Verifies the selected provider is reachable before generating.
        Gives a cold-starting ComfyUI up to wait_seconds to come online.
        Returns (ok, message) so the UI can log a friendly status.
        """
        if wait_seconds > 0:
            if await wait_for_comfyui(self.comfyui_base_url,
                                      timeout=wait_seconds):
                return (True, f"ComfyUI server reachable at "
                              f"{self.comfyui_base_url}")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.comfyui_base_url}/system_stats",
                                       timeout=10) as resp:
                    if resp.status == 200:
                        return True, f"ComfyUI server reachable at {self.comfyui_base_url}"
                    return False, f"ComfyUI server returned HTTP {resp.status}"
            except Exception as e:
                return False, (f"ComfyUI server NOT reachable at {self.comfyui_base_url} - "
                               f"is ComfyUI running? ({type(e).__name__})")

    async def download_face(self, session, uid, prompt, checkpoint=None):
        """
        Downloads a face using the configured provider.
        """
        ckpt = checkpoint or self._resolved_checkpoint or self.comfyui_model or "RealVisXL_V5.0_fp16.safetensors"
        return await self.download_face_comfy(session, uid, prompt, ckpt)

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
                  "inputs": {"width": self.width, "height": self.height, "batch_size": 1}},
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
                                        json=payload, timeout=60) as resp:
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
                                timeout=30) as resp:
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
                        async with session.get(view_url, timeout=60) as resp:
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
                    timeout=30) as resp:
                info = await resp.json()
            names = info["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
            checkpoint = names[0] if names else "RealVisXL_V5.0_fp16.safetensors"
        except Exception:
            checkpoint = "RealVisXL_V5.0_fp16.safetensors"

        self._resolved_checkpoint = checkpoint
        return checkpoint

    async def generate_faces_async(self, players_to_generate, prompt_template, progress_callback=None, cancel_check=None):
        """
        Takes a list of player dicts, generates prompts, and generates/downloads their faces.

        ``cancel_check`` is an optional zero-arg callable returning True when the
        caller wants to abort the batch. Pending tasks are cancelled and the
        results gathered so far are returned (completed faces stay on disk).
        """
        from src.parser import PromptBuilder

        self._resolved_checkpoint = None
        connector = aiohttp.TCPConnector(ssl=_SSL_CONTEXT)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Give an auto-started ComfyUI time to boot before submitting work.
            # The wait itself is cancellable so "Cancel Batch" works even during
            # a cold ComfyUI boot.
            if cancel_check and cancel_check():
                return [{"uid": p["uid"], "status": "cancelled",
                         "error": "Cancelled by user before generation started."}
                        for p in players_to_generate]
            if not await wait_for_comfyui(self.comfyui_base_url, timeout=180,
                                          session=session, cancel_check=cancel_check):
                if cancel_check and cancel_check():
                    return [{"uid": p["uid"], "status": "cancelled",
                             "error": "Cancelled by user while waiting for ComfyUI."}
                            for p in players_to_generate]
                return [{"uid": p["uid"], "status": "failed",
                         "error": ("ComfyUI did not start in time. Launch it "
                                   "manually or restart the app.")}
                        for p in players_to_generate]

            # Resolve which checkpoint to use once for the whole batch
            checkpoint = await self._resolve_checkpoint(session)

            tasks = []
            for player in players_to_generate:
                uid = player["uid"]
                # Build the prompt
                prompt = PromptBuilder.build_prompt(player, prompt_template)
                # Queue the task (as a real Task so it can be cancelled)
                tasks.append(asyncio.create_task(
                    self.download_face(session, uid, prompt, checkpoint)))

            results = []
            pending = set(tasks)
            try:
                while pending:
                    if cancel_check and cancel_check():
                        # Abort: cancel everything not yet finished, then stop.
                        for t in pending:
                            t.cancel()
                        await asyncio.gather(*pending, return_exceptions=True)
                        break
                    done_set, pending = await asyncio.wait(
                        pending, return_when=asyncio.FIRST_COMPLETED)
                    for future in done_set:
                        res = await future
                        results.append(res)
                        if progress_callback:
                            # Trigger UI update
                            progress_callback(len(results), len(tasks), res)
            finally:
                # Cancel anything still pending if we aborted mid-way.
                for t in pending:
                    t.cancel()

            return results