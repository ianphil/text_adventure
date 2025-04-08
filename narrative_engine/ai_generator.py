# narrative_engine/ai_generator.py

import os
import redis
from openai import OpenAI  # Updated import from the latest SDK
import logging
import hashlib
from .narrative_memory import NarrativeMemory  # Import the memory module

# Module-level variables to hold configuration settings
OPENAI_API_KEY = None
REDIS_URL = None
redis_client = None
CACHING_ENABLED = True  # Default to enabled; can be configured via app settings

# Set up a logger for this module
logger = logging.getLogger(__name__)

def init_app(app):
    """
    Initialize the AI generator module with settings from a Flask app.
    Expected configuration keys:
      - OPENAI_API_KEY
      - REDIS_URL
      - REDIS_CACHING_ENABLED (optional, defaults to True)
    """
    global OPENAI_API_KEY, REDIS_URL, redis_client, CACHING_ENABLED

    OPENAI_API_KEY = app.config.get('OPENAI_API_KEY', os.environ.get('OPENAI_API_KEY'))
    REDIS_URL = app.config.get('REDIS_URL', os.environ.get('REDIS_URL'))
    CACHING_ENABLED = app.config.get('REDIS_CACHING_ENABLED', True)
    
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please define it in your config or set the OPENAI_API_KEY environment variable.")
    if not REDIS_URL:
        raise ValueError("Redis URL is not set. Please define it in your config or set the REDIS_URL environment variable.")
    
    # No need to set openai.api_key as we're using the new client-based approach
    # which takes the API key directly in the client constructor
    try:
        redis_client = redis.Redis.from_url(REDIS_URL)
    except Exception as e:
        logger.error("Failed to connect to Redis: %s", e)
        raise
    
    app.logger.info("AI Generator module initialized with OpenAI API and Redis (Caching Enabled: %s).", CACHING_ENABLED)


def generate_narrative(prompt):
    """
    Generates narrative content using the OpenAI API based on the provided prompt.
    
    :param prompt: The string prompt, formatted with dynamic variables.
    :return: The generated narrative text.
    """
    try:
        # Initialize the OpenAI client using the module-level OPENAI_API_KEY.
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Use the client to generate narrative content
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a creative narrative generator for a text-based adventure game."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        
        # Extract and return the output text
        narrative_text = response.choices[0].message.content.strip()
        return narrative_text
    except Exception as error:
        logger.error("Error during API call: %s", error)
        # Trigger fallback narrative if an error occurs
        return fallback_narrative("unknown", "neutral", "unspecified")


# Update the narrative prompt template to include a memory log segment.
NARRATIVE_TEMPLATE = (
    "{memory_log}"
    "Generate a detailed description of a {location_type} environment, "
    "using a {tone} tone. Be sure to include the following elements: {required_elements}."
)

def build_prompt(template, **kwargs):
    """
    Inserts dynamic variables into the provided template.
    
    :param template: A narrative prompt template with placeholders.
    :param kwargs: A dictionary of dynamic values.
    :return: A formatted prompt.
    """
    return template.format(**kwargs)

def validate_narrative(narrative, required_elements):
    """
    Validates the generated narrative text by ensuring it contains all required elements.
    
    :param narrative: The AI-generated narrative text.
    :param required_elements: A comma-separated string of elements that must appear.
    :return: True if all elements are found; otherwise, False.
    """
    required_list = [element.strip().lower() for element in required_elements.split(',')]
    narrative_lower = narrative.lower()
    for element in required_list:
        if element and element not in narrative_lower:
            return False
    return True

def fallback_narrative(location_type, tone, required_elements):
    """
    Provides a fallback narrative snippet when the AI-generated content fails validation
    or the API call encounters an error.
    
    :param location_type: Type of the location.
    :param tone: Desired narrative tone.
    :param required_elements: Key elements that should be included.
    :return: A safe fallback narrative string.
    """
    return (
        f"In this {location_type}, the ambiance is decidedly {tone}. "
        f"While detailed descriptions elude capture, essential elements such as {required_elements} "
        "are subtly suggested by the surroundings."
    )

def generate_dynamic_narrative(location_type, tone, required_elements, memory: NarrativeMemory = None):
    """
    Combines prompt building, caching, API call, content validation, and narrative memory to generate narrative content dynamically.
    
    :param location_type: The type of location (e.g., 'dungeon', 'forest').
    :param tone: The desired tone (e.g., 'mysterious', 'whimsical').
    :param required_elements: A comma-separated string of key narrative elements.
    :param memory: (Optional) An instance of NarrativeMemory to incorporate previous narrative events.
    :return: AI-generated narrative text that meets validation criteria, or a fallback narrative.
    """
    # Retrieve memory log if a memory instance is provided
    memory_log = memory.get_log() if memory else ""
    
    # Build the prompt with dynamic variables and the current memory log
    prompt = build_prompt(
        NARRATIVE_TEMPLATE,
        memory_log=memory_log,
        location_type=location_type,
        tone=tone,
        required_elements=required_elements
    )

    # Create a unique cache key based on the prompt
    cache_key = hashlib.sha256(prompt.encode('utf-8')).hexdigest()

    # Check if caching is enabled and try to retrieve cached content
    if CACHING_ENABLED and redis_client:
        cached_narrative = redis_client.get(cache_key)
        if cached_narrative:
            logger.info("Using cached narrative for prompt: %s", prompt)
            narrative = cached_narrative.decode('utf-8')
        else:
            narrative = generate_narrative(prompt)
    else:
        narrative = generate_narrative(prompt)
    
    # Validate the generated narrative; if it fails, use the fallback
    if not validate_narrative(narrative, required_elements):
        logger.warning("Generated narrative failed validation. Using fallback narrative.")
        narrative = fallback_narrative(location_type, tone, required_elements)
    
    # Store the generated narrative in Redis if caching is enabled
    if CACHING_ENABLED and redis_client:
        try:
            redis_client.set(cache_key, narrative)
        except Exception as cache_error:
            logger.error("Error storing narrative in Redis: %s", cache_error)
    
    # Update narrative memory if provided
    if memory:
        memory.add_event(narrative)
    
    return narrative
