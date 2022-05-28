import hassapi as hass
from colorama import Fore, Style


class SoftwareThermostat(hass.Hass):
    def initialize(self):
        climate_entity = self.args["climate_entity"]
        self.listen_state(self.set_setpoint, climate_entity, attribute="all")

    def set_setpoint(self, entity, attribute, old, new, kwargs):
        setpoint_temperature_high = self.args["setpoint_temperature_high"]
        setpoint_temperature_low = self.args["setpoint_temperature_low"]
        temperature = new["attributes"]["temperature"]
        temperature_old = old["attributes"]["temperature"]
        current_temperature = new["attributes"]["current_temperature"]
        current_temperature_old = old["attributes"]["current_temperature"]

        if current_temperature == current_temperature_old and temperature == temperature_old:
            return
        if current_temperature < temperature:
            self.log(
                f"{Fore.CYAN}number.boiler_set_point{Style.RESET_ALL} > {Fore.GREEN}{setpoint_temperature_high}{Style.RESET_ALL}"
            )
            self.call_service("number/set_value", entity_id="number.boiler_set_point", value=setpoint_temperature_high)
        elif current_temperature >= temperature:
            self.log(
                f"{Fore.CYAN}number.boiler_set_point{Style.RESET_ALL} > {Fore.GREEN}{setpoint_temperature_low}{Style.RESET_ALL}"
            )
            self.call_service("number/set_value", entity_id="number.boiler_set_point", value=setpoint_temperature_low)