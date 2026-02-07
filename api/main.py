from fastapi import FastAPI, Depends, HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

import cache
from database import Database, get_db
from api.dto.links import CreateShortLinkRequest
from database.core import ShortLinkWithThatUrlAlreadyExists

app = FastAPI(lifespan=cache.cache_warmup)


@app.post("/api/v1/shorten", response_class=JSONResponse)
async def shorten(link: CreateShortLinkRequest, database: Database = Depends(get_db)):
    """
    Создает короткую ссылку для указанного URL.
    """
    try:
        link_id, short_url = database.create_link(link.url.__str__(), link.length)
        cache.set_short_link(short_url, link.url.__str__(), link_id)
    except ShortLinkWithThatUrlAlreadyExists:
        raise HTTPException(status_code=400, detail="Short link with that url already exists")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=503, detail="Technical troubles, please try again later")

    return JSONResponse(status_code=200, content={"url": short_url})


@app.get("/{short_url}", response_class=JSONResponse)
async def redirect_to_original_link(short_url: str, request: Request, database: Database = Depends(get_db)):
    """
    Перенаправляет по короткой ссылке на оригинальный URL.
    """
    try:
        short_link = cache.get_short_link(short_url)
        if not short_link:
            short_link = database.get_link_by_short_url(short_url)
        if not short_link:
            raise HTTPException(status_code=404, detail="Short link with that url does not exist")

        link_id = short_link.id
        original_url = short_link.original_url
    except:
        raise HTTPException(status_code=503, detail="Technical troubles, please try again later")


    metadata = "User-Agent: "+request.headers.get("User-Agent")+"\nIP: "+request.client.host
    database.add_click_on_link(link_id, metadata)
    return RedirectResponse(url=original_url)
