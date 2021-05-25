import hassapi as hass
import time

class Notifications(hass.Hass):
    def initialize(self):
        return
        self.run_every(self.FindEntities, "now", 5)

    def FindEntities(self, kwargs):
        current_time = int(time.time())
        for entity in self.get_state():
            state = self.get_state(entity, attribute="all")
            if "yatbi" in state["attributes"]:
                if "notifications_entity" in state["attributes"]["yatbi"]:
                    notifications_entity = state["attributes"]["yatbi"]["notifications_entity"]
                    current_count = int(float(self.get_state(notifications_entity)))
                    entities = state["attributes"]["yatbi"]["entities"]
                    notification_count = 0
                    for entity in entities:
                        if not isinstance(entity, str):
                            selected_entity = entity["entity"]
                        else:
                            selected_entity = entity

                        if selected_entity.startswith("input_datetime.task"):
                            task_entity = self.get_state(selected_entity, attribute="all")
                            if "yatbi" in task_entity["attributes"]:
                                if "task_days" in task_entity["attributes"]["yatbi"]:
                                    task_time = int(task_entity["attributes"]["yatbi"]["task_days"]) * 3600
                                final_time = int(task_entity["attributes"]["timestamp"]) + task_time

                                if final_time < current_time:
                                    notification_count += 1

                                if notification_count != current_count:
                                    self.log(notification_count)
                                    self.call_service("input_number/set_value", entity_id=notifications_entity, value=notification_count)