# narrative_engine/ai_generator.py

import os
import redis
from openai import OpenAI  # Updated import from the latest SDK
import logging
import hashlib
from .narrative_memory import NarrativeMemory  # Import the memory module
from models.narrative_prompt import NarrativePrompt

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


def get_prompt_template(prompt_name):
    """
    Retrieve a prompt template and parameters from the database by name.
    """
    prompt_obj = NarrativePrompt.query.filter_by(name=prompt_name).first()
    if not prompt_obj:
        raise ValueError(f"NarrativePrompt '{prompt_name}' not found in database.")
    return prompt_obj.prompt_template, prompt_obj.to_dict()

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

def generate_dynamic_narrative(location_type, tone, required_elements, memory: NarrativeMemory = None, prompt_name="location_description"):
    """
    Generate narrative content dynamically using a prompt template from the database.
    """
    # Fetch template and metadata
    try:
        template_str, prompt_meta = get_prompt_template(prompt_name)
    except Exception as e:
        logger.error("Error fetching prompt template: %s", e)
        # fallback to default template string
        template_str = (
            "{memory_log}"
            "Generate a detailed description of a {location_type} environment, "
            "using a {tone} tone. Be sure to include the following elements: {required_elements}."
        )
        prompt_meta = {"max_tokens": 500, "temperature": 0.7}

    memory_log = memory.get_log() if memory else ""

    prompt = build_prompt(
        template_str,
        memory_log=memory_log,
        location_type=location_type,
        tone=tone,
        required_elements=required_elements
    )

    cache_key = hashlib.sha256(prompt.encode('utf-8')).hexdigest()

    if CACHING_ENABLED and redis_client:
        cached_narrative = redis_client.get(cache_key)
        if cached_narrative:
            logger.info("Using cached narrative for prompt: %s", prompt)
            narrative = cached_narrative.decode('utf-8')
        else:
            narrative = generate_narrative_with_params(prompt, prompt_meta)
    else:
        narrative = generate_narrative_with_params(prompt, prompt_meta)

    if not validate_narrative(narrative, required_elements):
        logger.warning("Generated narrative failed validation. Using fallback narrative.")
        narrative = fallback_narrative(location_type, tone, required_elements)

    if CACHING_ENABLED and redis_client:
        try:
            redis_client.set(cache_key, narrative)
        except Exception as cache_error:
            logger.error("Error storing narrative in Redis: %s", cache_error)

    if memory:
        memory.add_event(narrative)

    return narrative

def generate_narrative_with_params(prompt, prompt_meta):
    """
    Generate narrative using OpenAI API with parameters from prompt metadata.
    """
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a creative narrative generator for a text-based adventure game."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=prompt_meta.get("max_tokens", 500),
            temperature=prompt_meta.get("temperature", 0.7)
        )
        return response.choices[0].message.content.strip()
    except Exception as error:
        logger.error("Error during API call: %s", error)
        return fallback_narrative("unknown", "neutral", "unspecified")
