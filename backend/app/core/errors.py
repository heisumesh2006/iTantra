class ApplicationError(Exception):
    def __init__(self, message: str, code: str = "invalid_request", status: int = 400):
        super().__init__(message)
        self.message, self.code, self.status = message, code, status
