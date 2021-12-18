import hassapi as hass

class Animal(hass.Hass):
    def initialize(self):
        self.listen_state(self.Humidity, self.args["humidity_entity"])

    def Humidity(self, entity, attribute, old, new, kwargs):
        if "triggers" in self.args:
            for t in self.args["triggers"]:
                self.log(t)
                if float(new) <= t["humidity_low"]:
                    self.Notify(config=t, humidity=new, low_high="low")
                elif float(new) >= t["humidity_high"]:
                    self.Notify(config=t, humidity=new, low_high="high")
        return

    def Notify(self, config, humidity, low_high):
        message = f"{self.args['animal']}'s humidity is too {low_high} ({humidity}%)."
        for ma in config["notify"]:
            self.notify(
                message,
                title=f"{low_high.capitalize()} Humidity",
                name=ma,
                data={"tag":"animal_"+ self.args["animal"] +"_humidity"}
            )