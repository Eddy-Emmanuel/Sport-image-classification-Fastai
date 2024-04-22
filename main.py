from fastapi import FastAPI, status
from fastapi.openapi.docs import get_swagger_ui_html

from database.session import Base, engine
from database_router.route import router
from backend_configuration.configuration import Config

app = FastAPI()
configuration = Config()

Base.metadata.create_all(bind=engine)

app.include_router(router=router)

@app.get(path="/", status_code=status.HTTP_200_OK, tags=["HomePage"])
def GetSwaggerUI():
    return get_swagger_ui_html(openapi_url=configuration.OPENAPI_URL, title=configuration.HOMEPAGE_TITLE)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)