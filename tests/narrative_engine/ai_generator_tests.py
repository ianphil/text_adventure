import pytest
from unittest import mock
from flask import Flask
import redis
import openai
from narrative_engine.ai_generator import (
    init_app, build_prompt, validate_narrative, 
    fallback_narrative, generate_narrative, 
    generate_dynamic_narrative, NARRATIVE_TEMPLATE
)
from narrative_engine.narrative_memory import NarrativeMemory

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = Flask(__name__)
    app.config['OPENAI_API_KEY'] = 'fake-api-key-for-testing'
    app.config['REDIS_URL'] = 'redis://localhost:6379/0'
    app.config['REDIS_CACHING_ENABLED'] = True
    app.config['TESTING'] = True
    
    yield app

@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    with mock.patch('narrative_engine.ai_generator.redis') as mock_redis_module:
        mock_instance = mock.MagicMock()
        mock_redis_module.Redis.from_url.return_value = mock_instance
        yield mock_redis_module.Redis.from_url

@pytest.fixture
def mock_openai():
    """Mock OpenAI API for testing."""
    with mock.patch('narrative_engine.ai_generator.OpenAI', autospec=True) as mock_openai_class:
        # Set up the mock client and response structure
        mock_client = mock_openai_class.return_value
        mock_chat = mock.MagicMock()
        mock_client.chat = mock_chat
        
        mock_completions = mock.MagicMock()
        mock_chat.completions = mock_completions
        
        mock_create = mock.MagicMock()
        mock_completions.create = mock_create
        
        # Create a mock response structure that matches the OpenAI client API
        mock_choice = mock.MagicMock()
        mock_choice.message.content = "This is a test narrative about a cave. There are stalactites and bats."
        
        mock_response = mock.MagicMock()
        mock_response.choices = [mock_choice]
        mock_create.return_value = mock_response
        
        yield mock_create

class TestAIGenerator:
    def test_init_app(self, app, mock_redis):
        """Test initialization of AI generator module with Flask app."""
        init_app(app)
        mock_redis.assert_called_once()
        
    def test_init_app_missing_api_key(self, app):
        """Test initialization fails when API key is missing."""
        app.config['OPENAI_API_KEY'] = None
        
        with pytest.raises(ValueError) as excinfo:
            init_app(app)
        assert "OpenAI API key is not set" in str(excinfo.value)
    
    def test_init_app_missing_redis_url(self, app):
        """Test initialization fails when Redis URL is missing."""
        app.config['REDIS_URL'] = None
        
        with pytest.raises(ValueError) as excinfo:
            init_app(app)
        assert "Redis URL is not set" in str(excinfo.value)
    
    def test_build_prompt(self):
        """Test building a prompt with dynamic variables."""
        template = "{memory_log}This is a {type} test with {tone} tone."
        result = build_prompt(
            template, 
            memory_log="Previous events:\nUser entered cave.\n",
            type="simple", 
            tone="neutral"
        )
        
        expected = "Previous events:\nUser entered cave.\nThis is a simple test with neutral tone."
        assert result == expected
    
    def test_validate_narrative_pass(self):
        """Test narrative validation when all required elements are present."""
        narrative = "This cave has stalactites hanging from the ceiling and bats flying around."
        required_elements = "stalactites, bats"
        
        result = validate_narrative(narrative, required_elements)
        assert result is True
    
    def test_validate_narrative_fail(self):
        """Test narrative validation when required elements are missing."""
        narrative = "This cave has stalactites hanging from the ceiling."
        required_elements = "stalactites, bats"
        
        result = validate_narrative(narrative, required_elements)
        assert result is False
    
    def test_fallback_narrative(self):
        """Test generation of fallback narrative."""
        result = fallback_narrative("cave", "spooky", "stalactites, bats")
        
        assert "cave" in result
        assert "spooky" in result
        assert "stalactites, bats" in result
    
    def test_generate_narrative(self, mock_openai):
        """Test generating narrative using the OpenAI API."""
        result = generate_narrative("Generate a description of a cave.")
        
        mock_openai.assert_called_once()
        assert result == "This is a test narrative about a cave. There are stalactites and bats."
    
    def test_generate_narrative_api_error(self, mock_openai):
        """Test generating narrative handles API errors gracefully."""
        mock_openai.side_effect = Exception("API Error")
        
        result = generate_narrative("Generate a description of a cave.")
        
        assert "ambiance" in result  # From fallback narrative
    
    @mock.patch('narrative_engine.ai_generator.redis_client')
    @mock.patch('narrative_engine.ai_generator.validate_narrative')
    @mock.patch('narrative_engine.ai_generator.generate_narrative')
    def test_generate_dynamic_narrative_with_cache(self, mock_gen, mock_validate, mock_redis):
        """Test generating dynamic narrative with cache hit."""
        # Setup the mocks
        mock_redis.get.return_value = b"Cached narrative about a cave."
        mock_validate.return_value = True  # Ensure validation passes
        
        result = generate_dynamic_narrative("cave", "spooky", "stalactites, bats")
        
        assert result == "Cached narrative about a cave."
        mock_gen.assert_not_called()  # Should not call generate_narrative when cache hit
    
    @mock.patch('narrative_engine.ai_generator.redis_client')
    @mock.patch('narrative_engine.ai_generator.CACHING_ENABLED', True)
    @mock.patch('narrative_engine.ai_generator.validate_narrative')
    @mock.patch('narrative_engine.ai_generator.generate_narrative')
    def test_generate_dynamic_narrative_without_cache(self, mock_gen, mock_validate, mock_redis):
        """Test generating dynamic narrative with cache miss."""
        mock_redis.get.return_value = None
        mock_gen.return_value = "New narrative about a cave with stalactites and bats."
        mock_validate.return_value = True  # Ensure validation passes
        
        result = generate_dynamic_narrative("cave", "spooky", "stalactites, bats")
        
        assert result == "New narrative about a cave with stalactites and bats."
        mock_gen.assert_called_once()
        mock_redis.set.assert_called_once()
    
    @mock.patch('narrative_engine.ai_generator.redis_client')
    @mock.patch('narrative_engine.ai_generator.CACHING_ENABLED', True)
    @mock.patch('narrative_engine.ai_generator.validate_narrative')
    @mock.patch('narrative_engine.ai_generator.generate_narrative')
    def test_generate_dynamic_narrative_validation_fail(self, mock_gen, mock_validate, mock_redis):
        """Test generating dynamic narrative with validation failure."""
        mock_redis.get.return_value = None
        mock_gen.return_value = "Narrative about a cave."
        mock_validate.return_value = False
        
        result = generate_dynamic_narrative("cave", "spooky", "stalactites, bats")
        
        assert "ambiance" in result  # From fallback narrative
    
    @mock.patch('narrative_engine.ai_generator.redis_client')
    @mock.patch('narrative_engine.ai_generator.validate_narrative')
    def test_generate_dynamic_narrative_with_memory(self, mock_validate, mock_redis):
        """Test generating dynamic narrative with memory integration."""
        with mock.patch('narrative_engine.ai_generator.generate_narrative') as mock_gen:
            # Setup all mocks properly
            mock_redis.get.return_value = None
            mock_gen.return_value = "Narrative about a cave with stalactites and bats."
            mock_validate.return_value = True  # Ensure validation passes
            
            memory = NarrativeMemory()
            memory.add_event("Player entered the cave entrance.")
            
            result = generate_dynamic_narrative("cave", "spooky", "stalactites, bats", memory)
            
            # Verify the narrative was generated with the expected parameters
            mock_gen.assert_called_once()
            call_args = mock_gen.call_args[0][0]
            assert "Player entered the cave entrance." in call_args
            
            # Check that the new narrative was added to memory
            assert "Narrative about a cave with stalactites and bats." in memory.events