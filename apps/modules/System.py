import hassapi as hass


class System(hass.Hass):
    def initialize(self):
        self.run_every(self.get_unavailable, "now", 60 * 60)
        self.exclude = []
        for entity in self.args["exclude"]:
            self.exclude.append(entity["entity"])

    def get_unavailable(self, kwargs):
        hass_state = self.get_state()
        unavailable_entities = []
        for entity in hass_state:
            if hass_state[entity]["state"] == "unavailable" and entity not in self.exclude:
                unavailable_entities.append(hass_state[entity])

        if len(unavailable_entities) > 1:
            message = f"You have {len(unavailable_entities)} unavailable entities."
            self.notify(
                message,
                title="System Notification",
                name="mobile_app_phone_lucas",
                data={"actions": [{"action": "URI", "title": "Show", "uri": "/lovelace/2"}], "tag":"unavailable_entities", "channel":"Low Priority"},
            )
        elif len(unavailable_entities) == 1:
            message = f"{unavailable_entities[0]} is unavailable."
            self.notify(
                message,
                title="System Notification",
                name="mobile_app_phone_lucas",
                data={"actions": [{"action": "URI", "title": "Show", "uri": "/lovelace/2"}], "tag":"unavailable_entities", "channel":"Low Priority"},
            )
