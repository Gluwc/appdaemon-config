import hassapi as hass
from colorama import Fore, Back, Style


class Utils(hass.Hass):
    def initialize(self):
        return

    def set_entities(self, states, state):
        for entity in states[state]:
            if not self.evaluate_conditions(entity):
                continue
            domain = entity["entity"].split(".")[0]
            if domain == "input_select":
                self.call_service(
                    "input_select/select_option",
                    entity_id=entity["entity"],
                    option=entity["state"],
                )
            elif domain == "cover":
                self.call_service(
                    "cover/set_cover_position",
                    entity_id=entity["entity"],
                    position=entity["state"],
                )
            elif domain == "media_player":
                if "volume" in entity:
                    self.call_service(
                        "media_player/volume_set", entity_id=entity["entity"], volume_level=entity["volume"]
                    )
                    self.log(f'{Fore.CYAN}{entity["entity"]}:volume{Style.RESET_ALL} > {Fore.GREEN}{entity["volume"]}{Style.RESET_ALL}')
                else:
                    self.call_service("media_player/turn_" + entity["state"], entity_id=entity["entity"])
            elif domain == "climate":
                self.call_service(
                    "climate/set_temperature",
                    entity_id=entity["entity"],
                    temperature=entity["state"],
                )
            elif domain == "switch":
                self.call_service("switch/turn_" + entity["state"], entity_id=entity["entity"])
            elif domain == "fan":
                self.call_service("fan/turn_" + entity["state"], entity_id=entity["entity"])
            elif domain == "light":
                brightness = entity["brightness"] if "brightness" in entity else 100
                if entity["state"] == "on":
                    self.call_service(
                        "light/turn_" + entity["state"],
                        entity_id=entity["entity"],
                        brightness_pct=brightness,
                    )
                elif entity["state"] == "off":
                    self.call_service(
                        "light/turn_" + entity["state"],
                        entity_id=entity["entity"],
                    )
            self.log_action(entity)

    def log_action(self, entity):
        if "state" in entity:
            self.log(f'{Fore.CYAN}{entity["entity"]}{Style.RESET_ALL} > {Fore.GREEN}{entity["state"]}{Style.RESET_ALL}')

    def is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def evaluate_conditions(self, config):
        """
        Evaluates all trigger conditions.
        """
        if "condition" not in config:
            return True
        for condition in config["condition"]:
            if "state" in condition:
                if self.get_state(condition["entity"]) != condition["state"]:
                    return
            elif "expression" in condition:
                entity_state = self.get_state(condition["entity"])
                entity_state = f'"{entity_state}"' if not self.is_float(entity_state) else entity_state
                if not eval(f'{entity_state} {condition["expression"]}'):
                    return
        return True