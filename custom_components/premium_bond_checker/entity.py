"""Base entity for Premium Bond Checker."""

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PremiumBondCoordinator


class PremiumBondCheckerEntity(CoordinatorEntity[PremiumBondCoordinator]):
    """Common entity behavior for Premium Bond Checker sensors."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: PremiumBondCoordinator) -> None:
        """Initialize the entity and associate it with the config entry's device."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.holder_number)},
            name=f"Premium Bond Checker {coordinator.holder_number}",
            manufacturer="NS&I",
            model="Premium Bond Checker",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def available(self) -> bool:
        """Return True if the coordinator's last update succeeded."""
        return self.coordinator.last_update_success
