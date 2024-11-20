"""
Creative Writing System Example

This script implements a multi-agent creative writing system using LangGraph.
It creates a team of specialized agents that collaborate to create stories:
1. Story Coordinator: Manages the writing process and maintains story coherence
2. Character Developer: Creates and develops character profiles and arcs
3. Scene Writer: Crafts individual scenes with vivid descriptions
4. Editor: Refines and polishes the written content

Key Features:
- Genre-specific writing prompts
- Character development focus
- Scene construction tools
- Collaborative story creation
- Editorial refinement
"""

import sys
import os
from typing import List, Dict, Optional

# Add parent directory to path to import agent_framework
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_framework import (
    AgentConfig,
    AgentRole,
    create_multi_agent_workflow
)

# Step 1: Define system messages for specialized writer roles
COORDINATOR_MESSAGE = """You are the lead writer coordinating the creative writing process.
Your responsibilities:
1. Understand the writing prompt and develop the main story outline
2. Coordinate with other writers for character development and scene details
3. Ensure consistency in tone, style, and narrative
4. Compile and refine the final piece

Keep the story engaging and coherent while incorporating input from other writers.
Provide clear direction that:
- Establishes story goals
- Defines narrative arcs
- Balances different elements
- Maintains consistent tone"""

CHARACTER_WRITER_MESSAGE = """You are a character development specialist.
Focus on:
1. Creating deep, believable characters with distinct personalities
2. Developing character backstories and motivations
3. Ensuring consistent character voices and behaviors
4. Adding character-driven conflict and growth

Make characters memorable and relatable while serving the story's needs.
Provide character details that:
- Feel authentic and deep
- Drive the story forward
- Create emotional connections
- Support the plot"""

SCENE_WRITER_MESSAGE = """You are a scene and description specialist.
Focus on:
1. Creating vivid, immersive settings
2. Writing engaging action sequences
3. Using sensory details effectively
4. Maintaining appropriate pacing
5. Building atmosphere and mood

Make scenes come alive while advancing the story.
Ensure each scene:
- Advances the plot
- Develops characters
- Creates imagery
- Engages readers"""

EDITOR_MESSAGE = """You are the editor reviewing and refining the story.
Focus on:
1. Story structure and pacing
2. Consistency in plot and character arcs
3. Language and style improvements
4. Dialogue authenticity
5. Overall impact and engagement

Provide specific suggestions for improvements while preserving the story's voice.
Focus on making the text:
- Clear and engaging
- Technically sound
- Stylistically strong
- True to the story"""

# Step 2: Define prompt generation function
def create_writing_prompt(genre: Optional[str] = None) -> str:
    """
    Generate a writing prompt based on genre.
    
    Each prompt is designed to:
    1. Establish a unique premise
    2. Suggest potential conflict
    3. Leave room for creative interpretation
    4. Support character development
    
    Args:
        genre: Optional genre specification (fantasy, scifi, mystery, romance)
    
    Returns:
        A genre-appropriate writing prompt
    """
    prompts = {
        "fantasy": "In a world where dreams become physical objects, a young collector discovers a nightmare that shouldn't exist.",
        "scifi": "A deep space maintenance worker receives an SOS signal from a ship that disappeared 50 years ago.",
        "mystery": "A detective investigates a series of impossible thefts where objects vanish from sealed rooms, only to appear in other sealed rooms.",
        "romance": "Two rival food critics are forced to collaborate on a series of restaurant reviews.",
        "general": "A mysterious package arrives at someone's doorstep, containing an object from their future."
    }
    return prompts.get(genre, prompts["general"])

def main():
    """
    Main function that runs the creative writing workflow.
    
    Process:
    1. Configure specialized writer agents
    2. Set up collaborative workflow
    3. Get genre selection from user
    4. Generate appropriate prompt
    5. Execute writing process
    6. Present final story
    """
    # Step 3: Create writer configurations
    writers = [
        AgentConfig(
            name="coordinator",
            role=AgentRole.COORDINATOR,
            system_message=COORDINATOR_MESSAGE
        ),
        AgentConfig(
            name="character_writer",
            role=AgentRole.CUSTOM,
            system_message=CHARACTER_WRITER_MESSAGE
        ),
        AgentConfig(
            name="scene_writer",
            role=AgentRole.CUSTOM,
            system_message=SCENE_WRITER_MESSAGE
        ),
        AgentConfig(
            name="editor",
            role=AgentRole.CRITIC,
            system_message=EDITOR_MESSAGE
        )
    ]
    
    # Step 4: Create the multi-agent workflow
    workflow = create_multi_agent_workflow(
        agent_configs=writers,
        communication_pattern="sequential"  # Writers work in sequence
    )
    
    # Step 5: Set up genre selection
    genres = ["fantasy", "scifi", "mystery", "romance", "general"]
    
    print("Creative Writing Demo")
    print("\nAvailable genres:")
    for i, genre in enumerate(genres, 1):
        print(f"{i}. {genre.title()}")
    
    # Step 6: Get user input and generate prompt
    choice = input("\nSelect a genre number (or press Enter for a general prompt): ").strip()
    try:
        selected_genre = genres[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(genres) else "general"
    except (ValueError, IndexError):
        selected_genre = "general"
    
    prompt = create_writing_prompt(selected_genre)
    
    print(f"\nGenre: {selected_genre.title()}")
    print(f"Prompt: {prompt}")
    print("\nGenerating story...")
    
    # Step 7: Prepare the writing request
    writing_request = f"""Please create a short story based on the following prompt:

Genre: {selected_genre}
Prompt: {prompt}

Requirements:
1. Story should be 500-1000 words
2. Include at least two main characters
3. Have a clear beginning, middle, and end
4. Incorporate descriptive scenes and meaningful dialogue
5. End with a satisfying resolution

Please collaborate to create an engaging and well-crafted story."""
    
    # Step 8: Execute the multi-agent writing workflow
    result = workflow.run(
        initial_message=writing_request,
        metadata={"max_turns": 15}  # Allow more turns for story development
    )
    
    # Step 9: Present the final story
    print("\nFinal Story:")
    print("=" * 80)
    for message in result["messages"]:
        if message.content.strip():
            print(f"\n{message.content}")
            print("-" * 80)

if __name__ == "__main__":
    main()
