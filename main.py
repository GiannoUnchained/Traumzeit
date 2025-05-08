from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import os
from app.story_generator import StoryGenerator

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

story_generator = StoryGenerator()

class StoryRequest(BaseModel):
    child_name: str
    child_age: int  # in months
    toy_name: str
    toy_description: str
    story_style: str
    story_length: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate", response_class=HTMLResponse)
async def generate_story(request: Request,
                        child_name: str = Form(...),
                        child_age: int = Form(...),
                        toy_name: str = Form(...),
                        toy_description: str = Form(...),
                        story_style: str = Form(...),
                        story_length: str = Form(...)):
    try:
        # Erstelle ein Daten-Dict
        data = {
            "child_name": child_name,
            "child_age": child_age,
            "toy_name": toy_name,
            "toy_description": toy_description,
            "story_style": story_style,
            "story_length": story_length
        }

        # Generiere die Geschichte
        story = story_generator.generate_story(data)

        # Generiere die Bildbeschreibung
        image_prompt = story_generator.generate_image_prompt(story)

        # Generiere das Bild
        image_url = story_generator.generate_image_url(image_prompt)

        return templates.TemplateResponse("story.html", {
            "request": request,
            "story": story,
            "child_name": child_name,
            "toy_name": toy_name,
            "image_url": image_url
        })
    except Exception as e:
        return templates.TemplateResponse("story.html", {
            "request": request,
            "story": f"Es ist ein Fehler aufgetreten: {str(e)}",
            "child_name": child_name,
            "toy_name": toy_name,
            "image_url": "https://via.placeholder.com/1024x1024?text=Fehler"
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
