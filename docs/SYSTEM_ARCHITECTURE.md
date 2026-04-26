# System Architecture

React/Vite/TypeScript presents nine pages and a typed API boundary. FastAPI handles validation and offloads long transmissions to a single worker, with durable SQLite job events. A shared inference lock serializes model calls. Each provider owns its resampling boundary. The packet/DSP subsystem is independent of speech inference; receiver decoders accept only recovered bytes. SQLite schema v1 migrates on startup and interrupts orphaned active jobs. Media files are controlled UUID names under storage/media. See the README Mermaid diagram.
