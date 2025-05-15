import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict, Any

load_dotenv()

class StoryGenerator:
    def __init__(self):
        # Einfache Initialisierung ohne zusätzliche Parameter
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_story(self, data: Dict[str, Any]) -> str:
        # Konvertiere Monate in Jahre für die bessere Lesbarkeit
        years = data["child_age"] // 12
        months = data["child_age"] % 12
        age_description = f"{years} Jahre und {months} Monate alt"

        # Handle single toy case for backward compatibility
        if 'toy_name' in data and 'toy_description' in data:
            toys_text = f"ein Stofftier namens {data['toy_name']}, das {data['toy_description']} ist"
            end_text = f"während {data['toy_name']} wach blieb und über ihn/sie Wache hielt."
        # Handle multiple toys
        elif 'toys' in data and data['toys']:
            if len(data['toys']) == 1:
                toy = data['toys'][0]
                toys_text = f"ein Stofftier namens {toy['name']}, das {toy['description']} ist"
                end_text = f"während {toy['name']} wach blieb und über ihn/sie Wache hielt."
            else:
                toy_names = [toy['name'] for toy in data['toys']]
                toy_descriptions = [f"{toy['name']}, das {toy['description']}" for toy in data['toys']]
                toys_text = ", ".join(toy_descriptions[:-1]) + " und " + toy_descriptions[-1] if len(toy_descriptions) > 1 else toy_descriptions[0]
                end_text = f"während {toy_names[0]} wach blieb und über ihn/sie Wache hielt."
        else:
            toys_text = "liebgewonnene Stofftiere"
            end_text = "während die Stofftiere Wache hielten."

        prompt = f"""
        Erstelle eine kindgerechte Gute-Nacht-Geschichte für ein Kind namens {data['child_name']},
        das {age_description} ist. {data['child_name']} hat {toys_text}.

        Die Geschichte sollte:
        1. Im Stil von {data['story_style']} sein
        2. {data['story_length']} sein
        3. Ein einfaches, aber spannendes Abenteuer enthalten
        4. Mit einem positiven Schluss enden
        5. Einfache Wörter und kurze Sätze verwenden
        6. Keine Gewalt oder Angst erregende Inhalte enthalten

        Beginne die Geschichte mit "Einmal in einer schönen Nacht..."
        und ende mit "...und so schlief {data['child_name']} ein, {end_text}"
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
            print(f"Fehler bei der Geschichte-Generierung: {str(e)}")
            # Handle case where toy data might be in different formats
            toy_name = ""
            if 'toy_name' in data:
                toy_name = data['toy_name']
            elif 'toys' in data and data['toys']:
                toy_name = data['toys'][0]['name'] if 'name' in data['toys'][0] else "einem Stofftier"
                
            return f"Einmal in einer schönen Nacht... träumte {data['child_name']} zusammen mit {toy_name} von einem wunderbaren Abenteuer. Sie erlebten viele spannende Dinge und hatten viel Spaß. Am Ende des Abenteuers waren alle müde und glücklich. Und so schlief {data['child_name']} ein, während {toy_name} wach blieb und über ihn/sie Wache hielt."
