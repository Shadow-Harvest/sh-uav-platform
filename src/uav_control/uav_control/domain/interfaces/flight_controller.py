from abc import ABC, abstractmethod
from uav_control.domain.entities.position import Position

class FlightControllerInterface(ABC):
    """Interface for flight controller operations."""
    
    @abstractmethod
    def set_position(self, position: Position) -> None:
        """Set the desired position of the UAV.
        
        Implementation should handle all platform-specific operations:
          - Publishing setpoints
          - Mode changes (GUIDED/OFFBOARD/etc)
          - Arming procedure
          
        Args:
            position: Target position to reach
            
        Returns:
            True if successful, False otherwise
        """
        
        pass