import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from app.core.errors import ApplicationError
from app.db import store
from app.schemas.requests import TransmissionRequest
from transceiver.pipeline import execute

LOGGER = logging.getLogger(__name__)
EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="itantra-inference")
LOCK = threading.Lock()
ACTIVE = {}


def submit(table: str, request):
    with LOCK:
        if len(ACTIVE) >= 8:
            raise ApplicationError("Processing queue is full; wait for an active job", "queue_full", 429)
        job = store.create_job(table, request.model_dump(mode="json"))
        event = threading.Event()
        ACTIVE[job["id"]] = event
    EXECUTOR.submit(run, table, job, request, event)
    return job


def run(table, job, request, event):
    def stage(name, detail=None):
        job["stages"].append({"name": name, "timestamp": store.now(), "detail": detail})
        store.save_job(table, job)

    job["status"] = "running"
    store.save_job(table, job)
    try:
        if event.is_set():
            raise ApplicationError("Cancelled", "cancelled", 409)
        if table == "transmissions":
            result = execute(request, stage, event.is_set)
        else:
            results = []
            for mode in request.modes:
                for snr in request.snr_values:
                    for repeat in range(request.repeats):
                        if event.is_set():
                            raise ApplicationError("Experiment cancelled", "cancelled", 409)
                        config = request.config.model_copy(
                            update={"snr_db": snr, "seed": (request.config.seed + repeat) % 2**32}
                        )
                        # Validate sweep values rather than bypassing Pydantic model_copy bounds.
                        config = type(config).model_validate(config.model_dump())
                        spec = TransmissionRequest(
                            media_id=request.media_id,
                            mode=mode,
                            language=request.language,
                            reference=request.reference,
                            channel_config=config,
                        )
                        stage("Experiment trial", {"mode": mode, "snr_db": snr, "repeat": repeat})
                        try:
                            entry = execute(spec, cancelled=event.is_set)
                            entry["repeat"] = repeat
                            results.append(entry)
                            with store.connection() as db:
                                import json
                                from uuid import uuid4

                                db.execute(
                                    "INSERT INTO experiment_results VALUES(?,?,?)",
                                    (str(uuid4()), job["id"], json.dumps(entry, ensure_ascii=False)),
                                )
                        except ApplicationError as error:
                            if error.code == "cancelled":
                                raise
                            results.append(
                                {
                                    "mode": mode,
                                    "snr_db": snr,
                                    "repeat": repeat,
                                    "status": "unavailable",
                                    "error": error.message,
                                }
                            )
            result = {"runs": results, "configuration": request.model_dump(mode="json")}
        job["result"], job["status"] = result, "completed"
    except ApplicationError as error:
        job["error"], job["status"] = error.message, "cancelled" if error.code == "cancelled" else "failed"
    except Exception:
        LOGGER.exception("Job %s failed", job["id"])
        job["error"], job["status"] = "Processing failed; see the local backend log for diagnostics", "failed"
    finally:
        store.save_job(table, job)
        with LOCK:
            ACTIVE.pop(job["id"], None)


def cancel(identifier):
    with LOCK:
        event = ACTIVE.get(identifier)
        if event:
            event.set()
            return True
    return False
