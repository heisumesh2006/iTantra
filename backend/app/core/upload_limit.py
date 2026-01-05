from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from app.core.config import MAX_BYTES


class RequestSizeLimitMiddleware:
    """Count body bytes before multipart processing, including chunked requests."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        limit = MAX_BYTES + 65536
        headers = dict(scope.get("headers", []))
        declared = headers.get(b"content-length", b"0")
        if declared.isdigit() and int(declared) > limit:
            response = JSONResponse(
                {
                    "error": {
                        "code": "upload_too_large",
                        "message": "Request body exceeds the 15 MB upload limit",
                    }
                },
                status_code=413,
            )
            return await response(scope, receive, send)
        count = 0

        async def bounded_receive():
            nonlocal count
            item = await receive()
            count += len(item.get("body", b""))
            if count > limit:
                raise HTTPException(status_code=413, detail="Request body exceeds the upload limit")
            return item

        return await self.app(scope, bounded_receive, send)
