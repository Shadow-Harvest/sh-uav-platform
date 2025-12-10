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
    
    # Invalid transitions
    
    def test_cannot_takeoff_from_disarmed(self):
        """Should not be able to takeoff from disarmed."""
        fsm = VehicleFSM()
        with pytest.raises(TransitionNotAllowed):
            fsm.takeoff()
            
    def test_cannot_arm_when_flying(self):
        """Should not be able to arm when flying."""
        fsm = VehicleFSM()
        fsm.arm()
        fsm.takeoff()
        fsm.takeoff_complete()
        fsm.navigate()
        with pytest.raises(TransitionNotAllowed):
            fsm.arm()
            
    def test_cannot_arm_when_taking_off(self):
        """Should not be able to arm when taking off."""
        fsm = VehicleFSM()
        fsm.arm()
        fsm.takeoff()
        with pytest.raises(TransitionNotAllowed):
            fsm.arm()
            
    def test_cannot_land_from_armed(self):
        """Should not be able to land from armed."""
        fsm = VehicleFSM()
        fsm.arm()
        with pytest.raises(TransitionNotAllowed):
            fsm.land()
    
    # Happy paths
    
    def test_full_mission_sequence(self):
        """Test a full mission sequence."""
        fsm = VehicleFSM()
        
        # Arm
        fsm.arm()
        assert fsm.current_state.id == "armed"
        
        # Takeoff
        fsm.takeoff()
        assert fsm.current_state.id == "taking_off"
        
        # Takeoff complete
        fsm.takeoff_complete()
        assert fsm.current_state.id == "hovering"
        
        # Navigate to flying
        fsm.navigate()
        assert fsm.current_state.id == "flying"
        
        # Target reached
        fsm.target_reached()
        assert fsm.current_state.id == "hovering"
        
        # Land
        fsm.land()
        assert fsm.current_state.id == "landing"
        
        # Touchdown
        fsm.touchdown()
        assert fsm.current_state.id == "disarmed"

    def test_emergency_during_flight(self):
        """Test emergency trigger during flight."""
        fsm = VehicleFSM()
        
        # Arm and takeoff
        fsm.arm()
        fsm.takeoff()
        fsm.takeoff_complete()
        fsm.navigate()
        
        # Trigger emergency
        fsm.trigger_emergency()
        assert fsm.current_state.id == "emergency"
        
        # Emergency land
        fsm.emergency_land()
        assert fsm.current_state.id == "landing"
        
        # Touchdown
        fsm.touchdown()
        assert fsm.current_state.id == "disarmed"