class TakeoffUseCase:
    def __init__(self, controller):
        self._controller = controller

    def execute(self, altitude: float) -> bool:
        if altitude <= 0:
            raise ValueError("Altitude must be a positive value.")
        
        if altitude > 100:
            raise ValueError("Altitude exceeds maximum limit of 100 meters.")
        
        return True