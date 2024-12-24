import logging
import voluptuous as vol
import os

from homeassistant.const import CONF_API_KEY, CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.util.json import JsonObjectType
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse

from .api import send_prompt_command, retrieve_last_prompt
from .const import (
    ATTR_IDENTIFIER,
    ATTR_LAST_PROMPT,
    ATTR_LAST_RESPONSE,
    ATTR_TIMESTAMP,
    DOMAIN,
)
from .sensor import MistralAiSensor

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {vol.Required(CONF_NAME): cv.string, vol.Required(CONF_API_KEY): cv.string}
        ),
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: dict):
    hass.data.setdefault(DOMAIN, {})

    # Exclude attributes from being recorded in history
    _entity_component_unrecorded_attributes = frozenset(
        (ATTR_TIMESTAMP, ATTR_LAST_PROMPT, ATTR_LAST_RESPONSE, ATTR_IDENTIFIER)
    )

    # Create directory for storing conversations
    directory_path = 'custom_components/mistral_ai_api/conversations'
    os.makedirs(directory_path,exist_ok=True)

    # Initialize MistralAiSensor
    sensor = MistralAiSensor(
        hass, {"state": "idle", "response": "", "prompt": "", "identifier": ""}
    )
    sensor.async_write_ha_state()

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config, "sensor")
    )

    hass.data[DOMAIN]["sensor"] = sensor

    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]
    return await setup_common(hass, conf)


async def setup_common(hass: HomeAssistant, conf: dict) -> bool:
    api_key = conf[CONF_API_KEY]

    async def send_prompt(call: ServiceCall):
        prompt = call.data.get("prompt")
        agent_id = call.data.get("agent_id")
        identifier = call.data.get("identifier")
        model = call.data.get("model")
        timeout_in_seconds = call.data.get("timeout_in_seconds")
        conversation_id = call.data.get("conversation_id")
        
        await send_prompt_command(
            hass, api_key, prompt, agent_id, identifier, model, timeout_in_seconds, conversation_id
        )

    hass.services.async_register(DOMAIN, "send_prompt", send_prompt)

    async def retrieve_last_command(call: ServiceCall) -> ServiceResponse:        
        return await retrieve_last_prompt(hass)

    hass.services.async_register(DOMAIN, "retrieve_last", retrieve_last_command, supports_response=SupportsResponse.ONLY)
    
    return True


async def async_unload_entry(hass, entry):
    hass.services.async_remove(DOMAIN, "send_prompt")
    return True
