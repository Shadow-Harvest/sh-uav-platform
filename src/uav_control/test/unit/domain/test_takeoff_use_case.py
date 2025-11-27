import pytest
from unittest.mock import Mock
from uav_control.domain.use_cases.takeoff_use_case import TakeoffUseCase

class TestTakeoffUseCase:
    def test_takeoff_rejects_negative_altitude(self):
        """Test that the takeoff use case rejects negative altitude values."""
        
        mock_controller = Mock()
        use_case = TakeoffUseCase(mock_controller)
        
        with pytest.raises(ValueError, match="(?i)altitude"):
            use_case.execute(altitude=-5)
