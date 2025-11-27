from uav_control.domain.entities.position import Position

class TakeoffUseCase:
    """Use case for executing UAV takeoff to specified altitude"""
    
    def __init__(self, controller):
        self._controller = controller

    def execute(self, altitude: float) -> bool:
        """Execute takeoff to specified altitude.
          
          Args:
              altitude: Target altitude in meters
              
          Returns:
              True if takeoff successful, False otherwise
              
          Raises:
              ValueError: If altitude is invalid
          """

        if altitude <= 0:
            raise ValueError("Altitude must be a positive value.")
        
        if altitude > 100:
            raise ValueError("Altitude exceeds maximum limit of 100 meters.")
        
        position = Position(x=0.0, y=0.0, z=altitude)
        return self._controller.set_position(position)