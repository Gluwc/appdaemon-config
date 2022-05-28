import hassapi as hass


class Animal(hass.Hass):
    def initialize(self):
        self.listen_state(self.get_humidity, self.args["humidity_entity"])

    def get_humidity(self, entity, attribute, old, new, kwargs):
        if "triggers" in self.args:
            for t in self.args["triggers"]:
                if float(new) > float(old) and float(old) < t["humidity_low"] and float(new) > t["humidity_low"]:
                    self.notify_humidity(config=t, humidity=new, low_high="restored")
                elif float(new) <= t["humidity_low"]:
                    self.notify_humidity(config=t, humidity=new, low_high="low")
                elif float(new) >= t["humidity_high"]:
                    self.notify_humidity(config=t, humidity=new, low_high="high")

    def notify_humidity(self, config, humidity, low_high):
        if low_high == "low":
            message = f"{self.args['animal']}'s humidity is too {low_high} ({humidity}%)."
            data = {
                "tag": "animal_" + self.args["animal"] + "_humidity",
                "color": "red",
                "persistent": True,
                "sticky": True,
                "notification_icon": "mdi:snake",
                "channel": "Medium Priority",
            }
        elif low_high == "restored":
            message = f"{self.args['animal']}'s humidity has been restored to {humidity}%."
            data = {
                "tag": "animal_" + self.args["animal"] + "_humidity",
                "color": "#54D157",
                "notification_icon": "mdi:snake",
                "channel": "Medium Priority",
            }
        for ma in config["notify"]:
            self.notify(message, title=f"{low_high.capitalize()} Humidity", name=ma, data=data)
