import hassapi as hass

class Animal(hass.Hass):
    def initialize(self):
        self.listen_state(self.get_humidity, self.args["humidity_entity"])

    def get_humidity(self, entity, attribute, old, new, kwargs):
        if "triggers" in self.args:
            for t in self.args["triggers"]:
                if float(new) <= t["humidity_low"]:
                    self.notify_humidity(config=t, humidity=new, low_high="low")
                    self.log(t)
                elif float(new) >= t["humidity_high"]:
                    self.notify_humidity(config=t, humidity=new, low_high="high")
                    self.log(t)
        return

    def notify_humidity(self, config, humidity, low_high):
        message = f"{self.args['animal']}'s humidity is too {low_high} ({humidity}%)."
        for ma in config["notify"]:
            self.notify(
                message,
                title=f"{low_high.capitalize()} Humidity",
                name=ma,
                data={"tag":"animal_"+ self.args["animal"] +"_humidity"}
            )