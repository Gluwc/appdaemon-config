import hassapi as hass
from colorama import Fore, Style


class InputSelect(hass.Hass):
    """
    Main module controlling most of the automation. Based on input_selects to define states of areas, people, animals, etc.
    """

    def initialize(self):
        self.timer = None
        self.Utils = self.get_app("utils")
        self.entity = self.args["entity"]

        self.listen_state(self.set_states, self.entity)

        if "triggers" in self.args:
            for trigger in self.args["triggers"]:
                if "entity" in trigger:
                    self.listen_state(self.entity_callback, trigger["entity"], config=trigger)
                elif "time" in trigger:
                    self.run_daily(self.time_callback, trigger["time"], config=trigger)
                elif "event" in trigger:
                    self.listen_event(self.event_callback, "deconz_event", id=trigger["event"], config=trigger)

        if "charger_entity" in self.args:
            self.listen_state(self.is_charging, self.args["charger_entity"])
            self.listen_event(self.set_awake, "mobile_app_notification_action", action="yes")

    # State callbacks
    def is_charging(self, entity, attribute, old, new, kwargs):
        if self.get_state(self.args["entity"]) == "Sleeping":
            if new == "none":
                identifier = self.args["entity"] + " > awake"
                self.call_service(
                    f"notify/{self.args['mobile_app']}",
                    message="Are you awake?",
                    data={
                        "tag": identifier,
                        "actions": [{"action": "yes", "title": "Yes"}, {"action": "no", "title": "No"}],
                    },
                )

    def entity_callback(self, entity, attribute, old, new, kwargs):
        config = kwargs["config"]
        if "state" in config:
            if new == config["state"] and self.Utils.evaluate_conditions(config):
                self.set_area(config, new)
        if "expression" in config:
            state = f'"{new}"' if not self.Utils.is_float(new) else new
            if eval(f'{state} {config["expression"]}') and self.Utils.evaluate_conditions(config):
                self.set_area(config, new)

    def event_callback(self, event, data, kwargs):
        config = kwargs["config"]
        if data["event"] == config["state"] and self.Utils.evaluate_conditions(config):
            self.set_area(config)

    def set_states(self, entity, attribute, old, new, kwargs):
        """
        Sets the entity states for each entity in the states list.
        """
        self.log(f"{Fore.CYAN}{entity}{Style.RESET_ALL} > {Fore.GREEN}{new}{Style.RESET_ALL}")
        if "states" in self.args:
            if new in self.args["states"]:
                self.log_trigger(entity, new)
                self.Utils.set_entities(self.args["states"], new)
                self.start_timeout(self.get_state(self.entity))
        if new == "Awake":
            self.run_in(self.set_home, 5)
        elif new == "Disabled" or new == "Idle":
            self.check_cancel_timer(self.timer)

    # Event callbacks
    def set_awake(self, event, data, kwargs):
        if "tag" in data:
            if data["tag"].split(" ")[0] == self.entity:
                self.select_option(self.entity, "Awake")

    # Scheduler callbacks
    def time_callback(self, kwargs):
        self.set_area(kwargs["config"])

    def set_home(self, kwargs):
        self.call_service("input_select/select_option", entity_id=self.entity, option="Home")

    def reset_to_idle(self, kwargs):
        """
        Resets input_select to "Idle" if there's no motion sensor active, otherwise loops until there's no motion active.
        """
        motion = False
        for trigger in self.args["triggers"]:
            if "entity" not in trigger:
                continue
            state = self.get_state(trigger["entity"], attribute="all")
            if "device_class" not in state["attributes"]:
                continue
            if state["attributes"]["device_class"] != "motion":
                continue
            if state["state"] == "off":
                continue
            motion = True
        if motion:
            self.log(
                f"Trigger state still {Fore.RED}on{Style.RESET_ALL} for {Fore.CYAN}{self.entity}{Style.RESET_ALL} looping."
            )
            self.timer = self.run_in(
                self.reset_to_idle,
                kwargs["time"],
                time=kwargs["time"],
            )
            return
        self.call_service("input_select/select_option", entity_id=self.entity, option="Idle")

    # Functions
    def set_area(self, config, state=None):
        """
        Sets input_select to defined 'set_state'.
        """
        call_service = self.call_service(
            "input_select/select_option",
            entity_id=self.entity,
            option=config["set_state"],
        )
        self.start_timeout(self.get_state(self.entity))
        if call_service is None:
            return
        if len(call_service) == 0:
            return
        if "expression" in config:
            self.log_trigger(config["entity"], f"{state} {config['expression']}")
        elif "time" in config:
            self.log_trigger(config["time"], config["set_state"])
        elif "event" in config:
            self.log_trigger(config["event"], state)
        else:
            self.log_trigger(config["entity"], state)

    def start_timeout(self, state):
        """
        Starts a timeout timer to reset input_select to 'Idle' if a timeout is defined.
        """
        if "timeout" in self.args.keys():
            if state in self.args["timeout"]:
                delay = self.args["timeout"][state]
                self.check_cancel_timer(self.timer)
                self.log(
                    f"{Fore.CYAN}{self.entity}{Style.RESET_ALL} timer {Fore.GREEN}{delay}{Style.RESET_ALL}"
                )
                self.timer = self.run_in(self.reset_to_idle, delay, time=delay)

    def log_trigger(self, entity, state):
        self.log(f"{Fore.LIGHTBLUE_EX}{entity}{Style.RESET_ALL} = {Fore.YELLOW}{state}{Style.RESET_ALL}")

    def check_cancel_timer(self, handle):
        scheduler_entries = self.get_scheduler_entries()
        for se in scheduler_entries:
            if handle in scheduler_entries[se].keys():
                self.cancel_timer(handle)
                self.log(f"{Fore.CYAN}{self.entity}{Style.RESET_ALL} timer {Fore.YELLOW}canceled{Style.RESET_ALL}")