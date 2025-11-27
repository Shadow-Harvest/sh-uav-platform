import pytest
from unittest.mock import Mock, call, ANY
from uav_control.domain.use_cases.takeoff_use_case import TakeoffUseCase


@pytest.mark.unit
class TestTakeoffUseCase:
    def test_takeoff_rejects_negative_altitude(self):
        """Test that the takeoff use case rejects negative altitude values."""
        
        mock_controller = Mock()
        use_case = TakeoffUseCase(mock_controller)
        
        with pytest.raises(ValueError, match="(?i)altitude"):
            use_case.execute(altitude=-5)
            
    def test_takeoff_rejects_excessive_altitude(self):
        """Test that the takeoff use case rejects excessively high altitude values. >100m"""
        
        mock_controller = Mock()
        use_case = TakeoffUseCase(mock_controller)
        
        with pytest.raises(ValueError, match="(?i)altitude"):
            use_case.execute(altitude=150)
            
    def test_takeoff_sets_correct_altitude_on_controller(self):
        """Test that the takeoff use case sets the correct altitude within valid range."""
        
        mock_controller = Mock()
        mock_controller.set_position.return_value = True
        use_case = TakeoffUseCase(mock_controller)
        
        result = use_case.execute(altitude=5)
        
        mock_controller.set_position.assert_called_once()
        call_args = mock_controller.set_position.call_args[0][0]
        assert call_args.z == 5
        assert call_args.x == 0
        assert call_args.y == 0
        assert result is True