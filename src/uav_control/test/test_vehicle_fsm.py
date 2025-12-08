"""Tests for Vehicle FSM."""

import pytest
from statemachine.exceptions import TransitionNotAllowed

from uav_control.vehicle_fsm import VehicleFSM


class TestVehicleFSM:
    """Test cases for VehicleFSM."""
    
    def test_initial_state_is_disarmed(self):
        """FSM should start in disarmed state."""
        fsm = VehicleFSM()
        assert fsm.current_state.id == "disarmed"
    
    def test_arm_from_disarmed(self):
        """Should be able to arm from disarmed."""
        fsm = VehicleFSM()
        fsm.arm()
        assert fsm.current_state.id == "armed"
    
    # Add more tests...
