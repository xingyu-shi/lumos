IMAGE_TO_TEXT = """
Please examine the provided image and generate a detailed description organized into the following numbered sections—no preamble, no closing remarks. Begin immediately with “1. Scene Overview.”

1. Scene Overview  
   - Describe overall setting (indoor/outdoor, urban/rural, time of day, weather, etc.).

2. Main Entities  
   - List key elements (people, animals, objects, buildings), specifying their positions and poses.

3. Relationships & Interactions  
   - Explain spatial relationships and any interactions or actions.

4. Visual Details  
   - Note colors, textures, lighting, focal points.

5. Mood & Atmosphere  
   - Describe the emotion or vibe of the scene.

6. Additional Inferences  
   - Infer time period, location, cultural context, or other clues.

Format your output in natural language, with each section numbered and titled. Keep each section concise but thorough.  Output only these six sections in order—nothing else.


Example output:

1. Scene Overview  
   Outdoor city street at dusk; the sky is a gradient of orange and purple, with a light breeze rustling the leaves.  

2. Main Entities  
   - A young man wearing a black baseball cap (on the right side of the frame), dressed in a dark blue jacket, looking down at his phone.  
   - Two bicycles parked on the left side, with a bouquet of yellow flowers in one basket.  

3. Relationships & Interactions  
   The young man stands next to the bicycle, his right foot resting on the frame as if he’s about to ride; the bicycles are about one meter from him.  

4. Visual Details  
   The focus is on the young man; light comes from the upper left, casting soft shadows on his face; overall warm color palette with clearly visible cobblestones.  

5. Mood & Atmosphere  
   The scene feels anticipatory, as if the young man is about to embark on a journey.  

6. Additional Inferences  
   The architecture and clothing suggest a modern European city in early autumn.
"""

IMAGE_TO_TEXT_SIMPLE = """
Please examine the provided image and generate a detailed description in plain text.
no closing remarks, no irrelevant information in your answers. 
Begin immediately:"""

RAG_QUERY = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} \nContext: {context} \nAnswer:"""
