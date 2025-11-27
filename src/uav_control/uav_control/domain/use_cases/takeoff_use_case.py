class TakeoffUseCase:
    def __init__(self, controller):
        self._controller = controller

    def execute(self, altitude: float):
        if altitude <= 0:
            raise ValueError("Altitude must be a positive value.")
        
        return True