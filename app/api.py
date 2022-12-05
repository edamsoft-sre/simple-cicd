import asyncio
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse


app = FastAPI()
counter_lock = asyncio.Lock()
counter = 0
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# serve HTML template with per process counter
@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
async def index(request: Request):
    global counter
    async with counter_lock:
        counter += 1
    return templates.TemplateResponse("index.html", {"request": request, "counter": counter})


# serve static html file
@app.get("/page2")
async def read_index():
    return FileResponse('app/static/page2.html')


@app.get("/page1")
async def read_index():
    response = RedirectResponse(url='/page2')
    return response

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
