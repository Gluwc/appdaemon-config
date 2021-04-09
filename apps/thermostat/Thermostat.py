import hassapi as hass


class Thermostat(hass.Hass):
    def initialize(self):
        # Set up contact_sensors
        self.contact_sensors = self.args["contact_sensors"]
        if "contact_sensors" in self.args:
            for trigger in self.args["contact_sensors"]:
                if "entity" in trigger:
                    self.listen_state(self.TriggerContactSensor, trigger["entity"], config=trigger)

        self.listen_state(self.TriggerEntity, self.args["entity"])

    def TriggerContactSensor(self, entity, attribute, old, new, kwargs):
        if self.EvaluateContactSensors():
            self.select_option("input_select.area_home", "Heating")
        else:
            self.select_option("input_select.area_home", "Cooling")

    def TriggerEntity(self, entity, attribute, old, new, kwargs):
        if new == "Home":
            if self.EvaluateContactSensors():
                self.select_option("input_select.area_home", "Heating")
            else:
                self.select_option("input_select.area_home", "Cooling")

    def EvaluateContactSensors(self):
        sensor_states = []
        for sensor in self.contact_sensors:
            sensor_states.append(self.get_state(sensor["entity"]))
        if "on" in sensor_states:
            return False
        elif "on" not in sensor_states:
            return True
