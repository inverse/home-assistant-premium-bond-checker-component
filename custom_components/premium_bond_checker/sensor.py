from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

class PremiumBondCheckerSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, holder_number: str, bond_period: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        self._type = bond_period
        self._name = f"Premium Bond Checker {holder_number} {bond_period}"
        self._id = f"premiumbondchecker-{holder_number}-{bond_period}"

        
