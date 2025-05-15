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
    toy_names: list[str]
    toy_descriptions: list[str]
    story_style: str
    story_length: str
    
    def get_toys(self):
        """Return a list of dicts with toy data"""
        return [
            {"name": name, "description": desc} 
            for name, desc in zip(self.toy_names, self.toy_descriptions)
        ]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate", response_class=HTMLResponse)
async def generate_story(request: Request,
                        child_name: str = Form(...),
                        child_age: int = Form(...),
                        toy_names: list[str] = Form(...),
                        toy_descriptions: list[str] = Form(...),
                        story_style: str = Form(...),
                        story_length: str = Form(...)):
    try:
        # Validate that we have the same number of names and descriptions
        if len(toy_names) != len(toy_descriptions):
            raise ValueError("Anzahl der Stofftiernamen stimmt nicht mit der Anzahl der Beschreibungen überein")
            
        # Create a data dict with all toys
        data = {
            "child_name": child_name,
            "child_age": child_age,
            "toy_names": toy_names,
            "toy_descriptions": toy_descriptions,
            "toys": [{"name": name, "description": desc} for name, desc in zip(toy_names, toy_descriptions)],
            "story_style": story_style,
            "story_length": story_length
        }
        
        print(f"Eingabedaten: {data}")

        # Generiere die Geschichte
        story = story_generator.generate_story(data)
        print(f"Generierte Geschichte: {story[:100]}...")


        # Erstelle eine Fallback-Geschichte, falls die generierte Geschichte leer ist
        if not story or len(story.strip()) < 10:
            print("Verwende Fallback-Geschichte")
            toys_text = ", ".join(toy_names[:-1] + ["und " + toy_names[-1]] if len(toy_names) > 1 else toy_names)
            story = f"Einmal in einer schönen Nacht... träumte {child_name} zusammen mit {toys_text} von einem wunderbaren Abenteuer. Sie erlebten viele spannende Dinge und hatten viel Spaß. Am Ende des Abenteuers waren alle müde und glücklich. Und so schlief {child_name} ein, während {toy_names[0]} wach blieb und über ihn/sie Wache hielt."

        return templates.TemplateResponse("story.html", {
            "request": request,
            "story": story,
            "child_name": child_name,
            "toy_name": ", ".join(toy_names),  # For backward compatibility
            "toys": data["toys"]  # Pass all toys to the template
        })
    except Exception as e:
        return templates.TemplateResponse("story.html", {
            "request": request,
            "story": f"Es ist ein Fehler aufgetreten: {str(e)}",
            "child_name": child_name,
            "toy_name": toy_names[0] if toy_names else "",
            "toys": [{"name": name, "description": desc} for name, desc in zip(toy_names, toy_descriptions)] if toy_names and toy_descriptions else []
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
