"""Tests for VehicleStateNode."""

import pytest
import rclpy
from rclpy.lifecycle import LifecycleState, TransitionCallbackReturn
from unittest.mock import MagicMock

from uav_control.vehicle_state_node import VehicleStateNode


@pytest.fixture(scope="module")
def rclpy_init():
    """Initialize rclpy once for all tests."""
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def node(rclpy_init):
    """Create a fresh node for each test."""
    node = VehicleStateNode()
    yield node
    node.destroy_node()


class TestVehicleStateNodeLifecycle:
    """Test lifecycle transitions."""
    
    def test_starts_unconfigured(self, node):
        """Node should start with FSM as None."""
        assert node.fsm is None

    def test_configure_creates_fsm(self, node):
        """on_configure should create the FSM."""
        result = node.on_configure(MagicMock())
        
        assert result == TransitionCallbackReturn.SUCCESS
        assert node.fsm is not None
        assert node.fsm.current_state.id == 'disarmed'

    def test_cleanup_destroys_fsm(self, node):
        """on_cleanup should destroy the FSM."""
        # First configure
        node.on_configure(MagicMock())
        assert node.fsm is not None
        
        # Then cleanup
        result = node.on_cleanup(MagicMock())
        
        assert result == TransitionCallbackReturn.SUCCESS
        assert node.fsm is None
        
class TestFsmStateMapping:
    """Test FSM state to message mapping."""
    
    def test_disarmed_maps_correctly(self, node):
        """Disarmed FSM state should map to STATE_DISARMED."""
        from uav_msgs.msg import VehicleState
        
        node.on_configure(MagicMock())
        
        result = node._fsm_state_to_msg()
        assert result == VehicleState.STATE_DISARMED
    
    def test_armed_maps_correctly(self, node):
        """Armed FSM state should map to STATE_ARMED."""
        from uav_msgs.msg import VehicleState
        
        node.on_configure(MagicMock())
        node.fsm.arm()
        
        result = node._fsm_state_to_msg()
        assert result == VehicleState.STATE_ARMED
    
    def test_unconfigured_returns_uninitialized(self, node):
        """When FSM is None, should return STATE_UNINITIALIZED."""
        from uav_msgs.msg import VehicleState
        
        # Don't configure - fsm stays None
        result = node._fsm_state_to_msg()
        assert result == VehicleState.STATE_UNINITIALIZED

