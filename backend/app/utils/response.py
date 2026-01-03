from fastapi.responses import JSONResponse

class ResponseWrapper:
    @staticmethod
    def success(data=None, msg="success", code=0):
        return JSONResponse(content={
            "code": code,
            "msg": msg,
            "data": data
        }, media_type="application/json; charset=utf-8")

    @staticmethod
    def error(msg="error", code=500, data=None):
        return JSONResponse(content={
            "code": code,
            "msg": str(msg),
            "data": data
        }, media_type="application/json; charset=utf-8")
