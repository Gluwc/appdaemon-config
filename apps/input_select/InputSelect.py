import hassapi as hass


class InputSelect(hass.Hass):
    def initialize(self):
        # Define self variables
        self.handle = None
        self.Utils = self.get_app("utils")
        self.entity = self.args["entity"]

        # Set up triggers
        if "triggers" in self.args:
            for trigger in self.args["triggers"]:
                if "entity" in trigger:
                    self.listen_state(self.EntityCallback, trigger["entity"], config=trigger)
                elif "time" in trigger:
                    self.run_daily(self.TimeCallback, trigger["time"], config=trigger)
                elif "event" in trigger:
                    self.listen_event(self.EventCallback, "deconz_event", id=trigger["event"], config=trigger)

        # Listen to input_select.
        self.listen_state(self.SetEntities, self.entity)

        # Listen to charging entity.
        if "charger_entity" in self.args:
            self.listen_state(self.IsCharging, self.args["charger_entity"])
            self.listen_event(self.SetAwake, "mobile_app_notification_action", action="yes")

    # Callbacks
    def SetAwake(self, event, data, kwargs):
        if "tag" in data:
            if data["tag"].split(" ")[0] == self.entity:
                self.select_option(self.entity, "Awake")

    def IsCharging(self, entity, attribute, old, new, kwargs):
        if self.get_state(self.args["entity"]) == "Sleeping":
            if new == "none":
                identifier = self.args["entity"] + " > awake"
                self.call_service(
                    f"notify/{self.args['mobile_app']}",
                    message="Are you awake?",
                    data={
                        "tag":identifier,
                        "actions": [{"action": "yes", "title": "Yes"}, {"action": "no", "title": "No"}],
                    },
                )

    def EntityCallback(self, entity, attribute, old, new, kwargs):
        try:
            self.RunTrigger(kwargs["config"])
        except Exception as e:
            message = f"Trigger failed for {self.entity} with error: {e}"
            self.call_service("notify/persistent_notification", message=message)

    def EventCallback(self, event, data, kwargs):
        self.log(data["event"])
        if data["event"] == kwargs["config"]["state"]:
            try:
                self.RunTrigger(kwargs["config"])
            except Exception as e:
                message = f"Trigger failed for {self.entity} with error: {e}"
                self.call_service("notify/persistent_notification", message=message)

    def TimeCallback(self, kwargs):
        try:
            self.RunTrigger(kwargs["config"])
        except Exception as e:
            message = f"Trigger failed for {self.entity} with error: {e}"
            self.call_service("notify/persistent_notification", message=message)

    def SetEntities(self, entity, attribute, old, new, kwargs):
        if "automation_boolean" in self.args:
            if self.get_state(self.args["automation_boolean"]) == "off":
                return

        self.StartTimeout(self.get_state(self.entity))
        if "states" in self.args:
            if new in self.args["states"]:
                self.Utils.SetEntities(self.args["states"], new)
        if new == "Awake":
            self.run_in(self.SetHome, 5)
        elif new == "Disabled":
            self.cancel_timer(self.handle)

    def SetHome(self, kwargs):
        self.call_service("input_select/select_option", entity_id=self.entity, option="Home")

    def ResetToIdle(self, kwargs):
        motion_list = []
        for trigger in self.args["triggers"]:
            if "entity" in trigger:
                state = self.get_state(trigger["entity"], attribute="all")
                if "device_class" in state["attributes"]:
                    if state["attributes"]["device_class"] == "motion":
                        if state["state"] == "on":
                            motion_list.append(True)
                        else:
                            motion_list.append(False)
        if True not in motion_list:
            self.call_service("input_select/select_option", entity_id=self.entity, option="Idle")
        else:
            self.cancel_timer(self.handle)
            self.log(f"Trigger state still `on` for {self.entity} looping.")
            self.handle = self.run_in(
                self.ResetToIdle,
                kwargs["time"],
                time=kwargs["time"],
            )

    # Functions
    def RunTrigger(self, config):
        state_list = []
        if "condition" in config:
            for condition in config["condition"]:
                if "state" in condition:
                    if self.get_state(condition["entity"]) == condition["state"]:
                        state_list.append(True)
                    else:
                        state_list.append(False)
                elif "expression" in condition:
                    entity_state = self.get_state(condition["entity"])
                    entity_state = f'"{entity_state}"' if not self.Utils.isfloat(entity_state) else entity_state
                    if eval(f'{entity_state} {condition["expression"]}'):
                        state_list.append(True)
                    else:
                        state_list.append(False)
        if False not in state_list:
            if "entity" in config:
                state = self.get_state(config["entity"])
                if "state" in config:
                    if config["state"] == state:
                        self.SetArea(config)
                elif "expression" in config:
                    state = f'"{state}"' if not self.Utils.isfloat(state) else state
                    if eval(f'{state} {config["expression"]}'):
                        self.SetArea(config)
            else:
                self.SetArea(config)

    def SetArea(self, config):
        self.call_service(
            "input_select/select_option",
            entity_id=self.entity,
            option=config["set_state"],
        )

    def StartTimeout(self, state):
        if "timeout" in self.args.keys():
            if state in self.args["timeout"]:
                delay = self.args["timeout"][state]
                if self.handle != None:
                    self.cancel_timer(self.handle)
                self.log(f"Resetting {self.entity} to Idle in {delay} seconds.")
                self.handle = self.run_in(self.ResetToIdle, delay, time=delay)
