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
