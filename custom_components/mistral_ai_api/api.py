import logging
import requests
import aiofiles
from homeassistant.core import HomeAssistant
import asyncio
import os
import json
from .const import (
    DOMAIN,
    ATTR_LAST_PROMPT,
    ATTR_LAST_RESPONSE,
    ATTR_IDENTIFIER,
    ATTR_TIMESTAMP,
    STATE_IDLE,
    STATE_PROCESSING,
    EV_PROVIDE_RESPONSE,
    ROLE_USER,
    ROLE_ASSISTANT,
    CONVERSATIONS_PATH,
    KEY_MESSAGES,
    KEY_CONTENT,
    KEY_ROLE,
    URL_AGENTS_CHAT,
    URL_TEXT_CHAT,
    KEY_SENSOR,
    CONVERSATION_FILE_EXT
)

_LOGGER = logging.getLogger(__name__)

async def write_messages_to_conversation_with_id(messages: [str], conversation_id: str):
    file_path = os.path.join(CONVERSATIONS_PATH,f"{conversation_id}.{CONVERSATION_FILE_EXT}")
    res = json.dumps(messages)
    _LOGGER.debug(res)

    async with aiofiles.open(file_path, mode='w') as f:
        await f.write(res)

async def load_conversation_with_id(conversation_id: str) -> any:
    directory_path = CONVERSATIONS_PATH
    file_path = os.path.join(directory_path,f"{conversation_id}.{CONVERSATION_FILE_EXT}")

    content = {}
    content[KEY_MESSAGES] = []

    if os.path.exists(file_path):

        async with aiofiles.open(file_path, 'r') as file:
            content[KEY_MESSAGES] = json.loads(await file.read())
            return content
    else:
        return content

async def send_prompt_command(
    hass: HomeAssistant,
    api_key: str,
    prompt: str,
    agent_id: str,
    identifier: str,
    model: str,
    timeout_in_seconds: int,
    conversation_id: str
):
    sensor = hass.data[DOMAIN].get(KEY_SENSOR)
    if sensor:
        sensor.set_state(STATE_PROCESSING)
        sensor.last_prompt = prompt
        sensor.identifier = identifier
        sensor.refresh_timestamp()
        sensor.async_write_ha_state()
    else:
        _LOGGER.error("Sensor instance not found in hass.data")

    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
    }

    url = (
        URL_AGENTS_CHAT
        if agent_id
        else URL_TEXT_CHAT
    )

    content = {}
    content[KEY_MESSAGES] = []

    if conversation_id:
        content = await load_conversation_with_id(conversation_id)
    
    content[KEY_MESSAGES].append({KEY_ROLE: ROLE_USER, KEY_CONTENT: prompt})    

    if agent_id:
        payload = {
            "agent_id": agent_id,
            "messages": content[KEY_MESSAGES],
        }
    else:
        payload = {
            "model": model,
            "messages": content[KEY_MESSAGES],
        }

    _LOGGER.debug(payload)

    def make_request():
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        return response

    prompt_response = ""

    timeout_to_use = timeout_in_seconds if timeout_in_seconds else 60

    try:
        response = await asyncio.wait_for(
            hass.async_add_executor_job(make_request), timeout=timeout_to_use
        )
        response.raise_for_status()
        response_data = response.json()
        _LOGGER.debug(response_data)

        if "choices" in response_data and "message" in response_data["choices"][0]:
            prompt_response = response_data["choices"][0]["message"]["content"]

            if sensor:
                sensor.set_state(STATE_IDLE)
                sensor.last_response = prompt_response
                sensor.refresh_timestamp()
                sensor.async_write_ha_state()

            event_data = {
                "response": prompt_response,
                "identifier": identifier,
                "agent_id": agent_id if agent_id else "",
            }

            hass.bus.async_fire(EV_PROVIDE_RESPONSE, event_data)

            if conversation_id:
                ai_response = {}
                ai_response[KEY_ROLE] = ROLE_ASSISTANT
                ai_response[KEY_CONTENT] = prompt_response
                content[KEY_MESSAGES].append(ai_response)

                await write_messages_to_conversation_with_id(content[KEY_MESSAGES], conversation_id)                

    except asyncio.TimeoutError:
        _LOGGER.error("REST command timed out")
    except requests.exceptions.RequestException as e:
        _LOGGER.error(f"REST command error: {e}")
    except KeyError as e:
        _LOGGER.error(f"KeyError: {e}")

async def retrieve_last_prompt(hass: HomeAssistant): 
    sensor = hass.data[DOMAIN].get(KEY_SENSOR)
    if sensor:

        response = {
            ATTR_IDENTIFIER: sensor.identifier,
            ATTR_LAST_PROMPT: sensor.last_prompt,
            ATTR_LAST_RESPONSE: sensor.last_response,
            ATTR_TIMESTAMP: sensor.timestamp                        
        }

        return response

    return {}