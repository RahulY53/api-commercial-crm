from frappe.model.document import Document


class TargetMarket(Document):
	def validate(self):
		self.market_name = (self.market_name or "").strip()
		if self.market_code:
			self.market_code = self.market_code.strip().upper()
