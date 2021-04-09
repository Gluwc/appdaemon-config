import hassapi as hass
import math


class Utils(hass.Hass):
    def initialize(self):
        self.timer = None
        return

    def SetEntities(self, states, state):
        for entity in states[state]:
            domain = entity["entity"].split(".")[0]
            if domain == "input_select":
                self.call_service(
                    "input_select/select_option",
                    entity_id=entity["entity"],
                    option=entity["state"],
                )
                self.log(f'Set {entity["entity"]} to {entity["state"]}.')
            elif domain == "cover":
                self.call_service(
                    "cover/set_cover_position",
                    entity_id=entity["entity"],
                    position=entity["state"],
                )
                self.log(f'Set {entity["entity"]} to {entity["state"]}.')
            elif domain == "media_player":
                self.call_service("media_player/turn_" + entity["state"], entity_id=entity["entity"])
                self.log(f'Set {entity["entity"]} to {entity["state"]}.')
            elif domain == "climate":
                self.call_service(
                    "climate/set_temperature",
                    entity_id=entity["entity"],
                    temperature=entity["state"],
                )
                self.log(f'Set {entity["entity"]} to {entity["state"]}.')
            elif domain == "switch":
                self.call_service("switch/turn_" + entity["state"], entity_id=entity["entity"])
                self.log(f'Set {entity["entity"]} to {entity["state"]}.')
            elif domain == "fan":
                self.call_service("fan/turn_" + entity["state"], entity_id=entity["entity"])
                self.log(f'Set {entity["entity"]} to {entity["state"]}.')
            elif domain == "light":
                brightness = entity["brightness"] if "brightness" in entity else 100
                transition = entity["transition"] if "transition" in entity else 0
                from_brightness = (
                    int(self.get_state(entity["entity"], attribute="brightness") / 2.56)
                    if self.get_state(entity["entity"], attribute="brightness")
                    else 0
                )
                supported_features = self.get_state(entity["entity"], attribute="supported_features")
                if entity["state"] == "on":
                    # if supported_features == 33:
                    #     self.cancel_timer(self.timer)
                    #     self.timer = self.run_every(
                    #         self.CustomTransition,
                    #         "now",
                    #         1,
                    #         entity=entity["entity"],
                    #         state="on",
                    #         brightness=brightness,
                    #         transition=transition,
                    #         from_brightness=from_brightness,
                    #     )
                    # else:
                    self.call_service(
                        "light/turn_" + entity["state"],
                        entity_id=entity["entity"],
                        brightness_pct=brightness,
                        # transition=transition,
                    )
                elif entity["state"] == "off":
                    # if supported_features == 33:

                    #     self.cancel_timer(self.timer)
                    #     self.timer = self.run_every(
                    #         self.CustomTransition,
                    #         "now",
                    #         1,
                    #         entity=entity["entity"],
                    #         state="off",
                    #         transition=transition,
                    #         from_brightness=from_brightness,
                    #     )
                    # else:
                    self.call_service(
                        "light/turn_" + entity["state"],
                        entity_id=entity["entity"],
                        # transition=transition,
                    )
                self.log(f'Set {entity["entity"]} to {entity["state"]}.')

    def isfloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def Notify(self, target, message, title=None, data=None):
        self.call_service(f"notify/{target}", message=message)

    def CustomTransition(self, kwargs):
        transition = kwargs["transition"]
        brightness = kwargs["brightness"] if "brightness" in kwargs else 0
        from_brightness = kwargs["from_brightness"] if kwargs["from_brightness"] else 0
        current_brightness = self.get_state(kwargs["entity"], attribute="brightness")
        if current_brightness is not None:
            current_brightness_pct = int(current_brightness / 2.56)
        else:
            current_brightness_pct = 0

        if transition > 0:
            if kwargs["state"] == "on":
                if brightness < from_brightness:
                    delta = (from_brightness - brightness) / transition
                    brightness_pct = int(current_brightness_pct - delta)
                    if brightness_pct <= brightness:
                        self.cancel_timer(self.timer)
                        brightness_pct = brightness
                    else:
                        self.log(brightness_pct)
                        self.call_service("light/turn_on", entity_id=kwargs["entity"], brightness_pct=brightness_pct)
                elif brightness > from_brightness:
                    delta = (brightness - from_brightness) / transition
                    brightness_pct = int(current_brightness_pct + delta)
                    if brightness_pct >= brightness:
                        self.cancel_timer(self.timer)
                        brightness_pct = brightness
                    else:
                        self.log(brightness_pct)
                        self.call_service("light/turn_on", entity_id=kwargs["entity"], brightness_pct=brightness_pct)
            elif kwargs["state"] == "off":
                delta = (from_brightness - brightness) / transition
                brightness_pct = int(current_brightness_pct - delta)
                if brightness_pct <= brightness:
                    self.cancel_timer(self.timer)
                    self.call_service("light/turn_off", entity_id=kwargs["entity"])
                else:
                    self.log(brightness_pct)
                    self.call_service("light/turn_on", entity_id=kwargs["entity"], brightness_pct=brightness_pct)
