from fastapi import HTTPException


class ExceptionBase(HTTPException):
    pass


class NotFoundException(ExceptionBase):
    def __init__(self, detail):
        super().__init__(status_code=404, detail=detail)


class BadRequestException(ExceptionBase):
    def __init__(self, detail):
        super().__init__(status_code=400, detail=detail)
