import os
import json
import google.generativeai as genai
from pydantic import BaseModel, Field, ValidationError
from typing import List
from dotenv import load_dotenv

print("Script started.")

# Load environment variables from .env
print("Loading .env file...")
load_dotenv() 
print(".env file loaded.")

# --- Pydantic Models for Structured Output ---

class ChordVoicing(BaseModel):
    chord_type: str = Field(..., description="The type of the chord, e.g., 'maj7', 'min9'")
    voicing: List[str] = Field(..., description="The notes in the voicing, e.g., ['C4', 'E4', 'G4', 'B4']")
    difficulty: str = Field(..., description="The difficulty of the voicing, e.g., 'beginner', 'intermediate', 'advanced'")
    description: str = Field(..., description="A brief description of the voicing's character and usage.")

class ChordProgression(BaseModel):
    name: str = Field(..., description="The name of the progression, e.g., 'Classic 2-5-1'")
    genre: str = Field(..., description="The genre this progression is common in, e.g., 'Jazz', 'Gospel'")
    chords: List[str] = Field(..., description="The chords in the progression, e.g., ['Dm7', 'G7', 'Cmaj7']")
    description: str = Field(..., description="A brief description of the progression and how it's used.")

# --- Gemini Generation ---

def generate_with_gemini(prompt: str, output_model):
    """
    Generates content with Gemini and validates it with a Pydantic model.
    """
    try:
        print("Configuring Gemini API...")
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("Error: GOOGLE_API_KEY environment variable not found.")
            return None
        genai.configure(api_key=api_key)
        print("Gemini API configured.")

        print("Generating content with Gemini...")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        print("Content generated.")
        
        print("Parsing and validating response...")
        # Extract the JSON from the response
        json_response = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(json_response)
        
        # Validate and parse the data
        if isinstance(data, list):
            validated_data = [output_model(**item) for item in data]
        else:
            validated_data = output_model(**data)
        
        print("Response parsed and validated successfully.")
        return validated_data
            
    except Exception as e:
        print(f"An error occurred during Gemini generation: {e}")
        if 'response' in locals():
            print("Raw response from Gemini:", response.text)
        return None

# --- Prompt Templates ---

def create_voicings_prompt(chord_types: List[str], count: int = 3):
    return f"""
    Generate {count} different common voicings for each of the following chord types: {', '.join(chord_types)}.
    For each voicing, provide a difficulty level (beginner, intermediate, advanced) and a brief description.
    Return the response as a JSON array of objects, where each object has the following keys: 'chord_type', 'voicing', 'difficulty', 'description'.
    
    Example response format:
    ```json
    [
      {{
        "chord_type": "maj7",
        "voicing": ["C4", "E4", "G4", "B4"],
        "difficulty": "beginner",
        "description": "A standard, root position major 7th chord."
      }},
      {{
        "chord_type": "maj7",
        "voicing": ["C4", "G4", "B4", "E5"],
        "difficulty": "intermediate",
        "description": "A spread voicing with the 3rd in the upper octave, creating a more open sound."
      }}
    ]
    """

def create_progressions_prompt(genre: str, count: int = 5):
    return f"""
    Generate {count} common chord progressions found in {genre} music.
    For each progression, provide a name and a brief description of its use and character.
    Return the response as a JSON array of objects, where each object has the following keys: 'name', 'genre', 'chords', 'description'.

    Example response format:
    ```json
    [
        {{
            "name": "The 'Amen' Cadence",
            "genre": "Gospel",
            "chords": ["Fmaj", "Cmaj"],
            "description": "A classic plagal cadence (IV-I) often used at the end of hymns."
        }}
    ]
    """

# --- Main Execution ---

if __name__ == "__main__":
    print("---" + " Starting Music Theory Data Generation " + "---")

    # --- Generate Chord Voicings ---
    print("\n---" + " Generating Chord Voicings " + "---")
    voicings_prompt = create_voicings_prompt(["maj7", "min7", "7"], count=2)
    generated_voicings = generate_with_gemini(voicings_prompt, ChordVoicing)

    if generated_voicings:
        print(f"\nSuccessfully generated {len(generated_voicings)} chord voicings.")
        
        # Example of how you might save this to a TS file:
        try:
            with open("generated_voicings.ts", "w") as f:
                f.write("import { ChordDefinition } from './theoryData';\n\n")
                f.write("export const GENERATED_VOICINGS: Record<string, ChordDefinition[]> = {\n")
                # This is a simplified example; you'd need to group by chord_type
                # for voicing in generated_voicings:
                #     pass # Implement grouping and writing logic here
                f.write("};\n")
            print("Saved a placeholder for generated voicings to 'generated_voicings.ts'")
        except IOError as e:
            print(f"Error writing to file: {e}")


    # --- Generate Chord Progressions ---
    print("\n---" + " Generating Chord Progressions " + "---")
    progressions_prompt = create_progressions_prompt("Gospel", count=3)
    generated_progressions = generate_with_gemini(progressions_prompt, ChordProgression)

    if generated_progressions:
        print(f"\nSuccessfully generated {len(generated_progressions)} chord progressions.")
            
        # Example of how you might save this to a TS file:
        try:
            with open("generated_progressions.ts", "w") as f:
                f.write("export const GENERATED_PROGRESSIONS = [\n")
                for progression in generated_progressions:
                    f.write(f"  {json.dumps(progression.dict())},\n")
                f.write("];\n")
            print("Saved generated progressions to 'generated_progressions.ts'")
        except IOError as e:
            print(f"Error writing to file: {e}")

    print("\n---" + " Data generation complete. " + "---")