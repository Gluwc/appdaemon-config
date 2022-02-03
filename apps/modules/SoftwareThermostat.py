import hassapi as hass


class SoftwareThermostat(hass.Hass):
    def initialize(self):
        climate_entity = self.args["climate_entity"]
        self.listen_state(self.set_setpoint, climate_entity, attribute="all")

    def set_setpoint(self, entity, attribute, old, new, kwargs):
        setpoint_temperature_high = self.args["setpoint_temperature_high"]
        setpoint_temperature_low = self.args["setpoint_temperature_low"]
        temperature = new["attributes"]["temperature"]
        current_temperature = new["attributes"]["current_temperature"]
        old_temperature = old["attributes"]["current_temperature"]

        if current_temperature == old_temperature:
            return
        if current_temperature < temperature:
            self.log(f"set_high")
            self.call_service("opentherm_gw/set_control_setpoint", gateway_id="otgw", temperature=setpoint_temperature_high)
        elif current_temperature >= temperature:
            self.log(f"set_low")
            self.call_service("opentherm_gw/set_control_setpoint", gateway_id="otgw", temperature=setpoint_temperature_low)