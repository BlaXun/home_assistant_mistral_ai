from datetime import datetime
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.core import HomeAssistant
from .const import (
    DOMAIN,
    VERSION,
    ATTR_LAST_RESPONSE,
    ATTR_LAST_PROMPT,
    ATTR_TIMESTAMP,
    ATTR_IDENTIFIER,
)


class MistralAiSensor(Entity):
    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, data):
        self.entity_id = generate_entity_id(
            entity_id_format="sensor.{}", name=DOMAIN, hass=hass
        )

        self.hass = hass
        self._state = data.get("state")
        self._attributes = {
            ATTR_LAST_RESPONSE: data.get("response"),
            ATTR_LAST_PROMPT: data.get("prompt"),
            ATTR_TIMESTAMP: datetime.now().timestamp(),
            ATTR_IDENTIFIER: data.get("identifier"),
        }

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            name="MistralAiApi",
            sw_version=VERSION,
            identifiers={
                (
                    DOMAIN,
                    "mistral_ai",
                )
            },
        )

    def has_entity_name(self):
        return True

    @property
    def name(self):
        return self.device_info["name"]

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    @property
    def identifier(self):
        return self._attributes[ATTR_IDENTIFIER]

    @identifier.setter
    def identifier(self, value):
        self._attributes[ATTR_IDENTIFIER] = value

    @property
    def last_response(self):
        return self._attributes[ATTR_LAST_RESPONSE]

    @last_response.setter
    def last_response(self, value):
        self._attributes[ATTR_LAST_RESPONSE] = value

    @property
    def last_prompt(self):
        return self._attributes[ATTR_LAST_PROMPT]

    @last_prompt.setter
    def last_prompt(self, value):
        self._attributes[ATTR_LAST_PROMPT] = value

    @property
    def timestamp(self):
        return self._attributes[ATTR_TIMESTAMP]    

    def set_state(self, state: str):
        self._state = state

    def set_attribute(self, key: str, value: any):
        self._attributes[key] = value

    def refresh_timestamp(self):
        self.set_attribute(ATTR_TIMESTAMP, datetime.now().timestamp())
