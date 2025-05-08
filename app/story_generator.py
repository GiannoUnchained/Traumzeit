import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict, Any

load_dotenv()

class StoryGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_story(self, data: Dict[str, Any]) -> str:
        # Konvertiere Monate in Jahre für die bessere Lesbarkeit
        years = data["child_age"] // 12
        months = data["child_age"] % 12
        age_description = f"{years} Jahre und {months} Monate alt"

        prompt = f"""
        Erstelle eine kindgerechte Gute-Nacht-Geschichte für ein Kind namens {data['child_name']},
        das {age_description} ist. Das Kind hat ein Stofftier namens {data['toy_name']},
        das {data['toy_description']} ist.

        Die Geschichte sollte:
        1. Im Stil von {data['story_style']} sein
        2. {data['story_length']} sein
        3. Ein einfaches, aber spannendes Abenteuer enthalten
        4. Mit einem positiven Schluss enden
        5. Einfache Wörter und kurze Sätze verwenden
        6. Keine Gewalt oder Angst erregende Inhalte enthalten

        Beginne die Geschichte mit "Einmal in einer schönen Nacht..."
        und ende mit "...und so schlief {data['child_name']} ein, während {data['toy_name']}
        wach blieb und über ihn/ihre Wache hielt."
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Du bist ein Experte für kindgerechte Gute-Nacht-Geschichten."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Es ist ein Fehler beim Generieren der Geschichte aufgetreten: {str(e)}"

    def generate_image_prompt(self, story: str) -> str:
        """Generiert eine Beschreibung für ein passendes Bild zur Geschichte"""
        try:
            prompt = f"""
            Basierend auf folgender Geschichte, erstelle eine kurze Beschreibung für ein passendes Bild:
            {story}

            Die Beschreibung sollte:
            1. Die wichtigsten Charaktere und Szenen beschreiben
            2. Farben und Stimmung berücksichtigen
            3. Kindgerecht und nicht zu komplex sein
            4. Einen ruhigen, friedlichen Moment einfangen
            """

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Du erstellst kurze, präzise Beschreibungen für Bilder."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Ein Baumhaus im Wald bei Nacht, beleuchtet von Mondlicht. {data['child_name']} sitzt darin und liest ein Buch über Abenteuer. {data['toy_name']} sitzt neben ihm/ihr und schaut neugierig zu."

    def generate_image_url(self, prompt: str) -> str:
        """Generiert ein Bild basierend auf der Beschreibung"""
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                style="vivid"
            )
            return response.data[0].url
        except Exception as e:
            return "https://via.placeholder.com/1024x1024?text=Bild+konnte+nicht+erstellt+werden"
