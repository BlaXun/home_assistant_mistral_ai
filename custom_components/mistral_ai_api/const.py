VERSION = "0.6.0"
DOMAIN = "mistral_ai_api"

ATTR_LAST_PROMPT = "last_prompt"
ATTR_LAST_RESPONSE = "last_response"
ATTR_TIMESTAMP = "timestamp"
ATTR_IDENTIFIER = "identifier"

STATE_PROCESSING = "processing"
STATE_IDLE = "idle"

EV_PROVIDE_RESPONSE = "mistral_ai_response"

ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"

CONVERSATIONS_PATH = "custom_components/mistral_ai_api/conversations"
CONVERSATION_FILE_EXT = "log"

KEY_MESSAGES = "messages"
KEY_CONTENT = "content"
KEY_ROLE = "role"
KEY_SENSOR = "sensor"

URL_TEXT_CHAT = "https://api.mistral.ai/v1/chat/completions"
URL_AGENTS_CHAT = "https://api.mistral.ai/v1/agents/completions"