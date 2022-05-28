import hassapi as hass


class MediaPlayer(hass.Hass):
    def initialize(self):
        self.entity = self.args["entity"]
        self.linked = self.args["linked"] if "linked" in self.args.keys() else None
        self.adjust_volume = (
            self.args["adjust_volume"] if "adjust_volume" in self.args.keys() else None
        )
        self.remote_device = (
            self.args["remote_device"] if "remote_device" in self.args.keys() else None
        )
        self.listen_state(self.changed, self.entity)
        if self.adjust_volume:
            self.run_daily(self.set_volume, "23:00:00", volume=0.2)
            self.run_daily(self.set_volume, "9:00:00", volume=0.4)
        if "set_volume" in self.args:
            self.listen_state(self.set_start_volume, self.entity, volume=self.args["set_volume"])

    def changed(self, entity, attribute, old, new, kwargs):
        if new == "off":
            self.run_in(self.turn_off_linked, 300)
        elif new == "playing":
            self.turn_on_linked()

    def set_start_volume(self, entity, attribute, old, new, kwargs):
        if new == "on":
            self.call_service("media_player/volume_set", entity_id=self.args["entity"], volume_level=kwargs["volume"])

    def turn_off_linked(self, kwargs):
        if "linked_source" in self.args.keys():
            source = self.get_state(entity_id=self.linked, attribute="source")
            if source != self.args["linked_source"]:
                return
        player_state = self.get_state(entity_id=self.entity)
        if player_state == "off":
            if self.remote_device:
                self.call_service(
                    "remote/send_command",
                    entity_id=self.linked,
                    device=self.remote_device,
                    command="PowerOff",
                )
            else:
                self.call_service("media_player/turn_off", entity_id=self.linked)
            self.log(f"{self.linked} turned off.")
        else:
            self.log(f"Ignoring {self.entity}, not off.")

    def turn_on_linked(self):
        if self.remote_device:
            self.call_service(
                "remote/send_command",
                entity_id=self.linked,
                device=self.remote_device,
                command="PowerOn",
            )

    def set_volume(self, kwargs):
        volume = kwargs["volume"]
        self.call_service(
            "media_player/volume_set", entity_id=self.entity, volume_level=volume
        )
        self.log(f"{self.entity} volume set to {volume}.")
