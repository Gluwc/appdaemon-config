import hassapi as hass


class Notify(hass.Hass):
	def initialize(self):
		self.listen_state(self.changed, 'persistent_notification')

	def changed(self, entity, attribute, old, new, kwargs):
		notifications = self.get_state('persistent_notification')
		for n in notifications:
			if notifications[n]['entity_id'] == entity:
				message = notifications[n]['attributes']['message']
				self.call_service("notify/mobile_app_phone_lucas", message=message)