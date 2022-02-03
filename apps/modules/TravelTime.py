import hassapi as hass


class TravelTime(hass.Hass):
    def initialize(self):
        self.listen_state(self.get_travel_time, self.args["travel_time_entity"])

    def get_travel_time(self, entity, attribute, old, new, kwargs):
        if int(new) > 0 and int(new) <= 10 and int(new) < int(old):
            self.notify_travel_time(new)

    def notify_travel_time(self, time):
        message = f"Elisa will be home in {time} minutes."
        self.notify(
            message,
            title=f"Elisa will be home soon.",
            name="mobile_app_phone_lucas",
            data={"tag": "travel_time_elisa"},
        )
