# Installation Windows

Use Python 3.10+ and Node 22+. Run scripts/setup.ps1 -WithModels. Use -ExecutionPolicy Bypass only on the named project scripts if local policy requires it. Models are separate explicit downloads; no API key is needed. The imageio-ffmpeg wheel supplies its own Windows FFmpeg with libopus. `-X utf8` avoids Windows console corruption for Indic diagnostics. Run start-dev.ps1 for hidden background processes or start-backend/start-frontend in separate terminals. Server ports are 8000 and 5173. Keep services local; there is no authentication for network exposure. The existing build-machine environment uses system-site-packages to reuse CPU torch, but the setup script creates an isolated environment on a fresh machine.


Kannada CTC: explicit `scripts/download-models.py --kannada-asr`, set `ITANTRA_KANNADA_STT=vakyansh`, restart backend. start-dev records exact process birth identities; stop-dev targets only those PIDs and avoids recycled PID matches. Existing ports produce an actionable conflict rather than killing unrelated processes.
