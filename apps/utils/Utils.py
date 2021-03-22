import hassapi as hass

class Utils(hass.Hass):
  def initialize(self):
        return

  def SetEntities(self, states, state):
    for entity in states[state]:
      domain = entity['entity'].split('.')[0]
      if domain == 'input_select':
        self.call_service('input_select/select_option', entity_id=entity['entity'], option=entity['state'])
        self.log(f'Set {entity["entity"]} to {entity["state"]}.')
      elif domain == 'cover':
        self.call_service('cover/set_cover_position', entity_id=entity['entity'], position=entity['state'])
        self.log(f'Set {entity["entity"]} to {entity["state"]}.')
      elif domain == 'media_player':
        self.call_service('media_player/turn_'+entity['state'], entity_id=entity['entity'])
        self.log(f'Set {entity["entity"]} to {entity["state"]}.')
      elif domain == 'climate':
        self.call_service('climate/set_temperature', entity_id=entity['entity'], temperature=entity['state'])
        self.log(f'Set {entity["entity"]} to {entity["state"]}.')
      elif domain == 'switch':
        self.call_service('switch/turn_'+entity['state'], entity_id=entity['entity'])
        self.log(f'Set {entity["entity"]} to {entity["state"]}.')
      elif domain == 'fan':
        self.call_service('fan/turn_'+entity['state'], entity_id=entity['entity'])
        self.log(f'Set {entity["entity"]} to {entity["state"]}.')
      elif domain == 'light':
        brightness = entity["brightness"] if "brightness" in entity else 100
        if entity["state"] == 'on':
          self.call_service("light/turn_"+entity["state"], entity_id=entity['entity'], brightness_pct=brightness)
        elif entity["state"] == "off":
          self.call_service("light/turn_"+entity["state"], entity_id=entity['entity'])
        self.log(f'Set {entity["entity"]} to {entity["state"]}.')

  def isfloat(self, value):
    try:
      float(value)
      return True
    except ValueError:
      return False