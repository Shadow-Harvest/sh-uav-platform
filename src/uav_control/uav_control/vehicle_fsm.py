"""
Vehicle Finite State Machine

States:
    DISARMED → ARMED → TAKING_OFF → HOVERING ←→ FLYING
        ▲                              │           │
        └────────── LANDING ◄──────────┴───────────┘
                       ▲
                   EMERGENCY

Transitions:
    arm:               DISARMED → ARMED
    disarm:            ARMED → DISARMED
    takeoff:           ARMED → TAKING_OFF
    takeoff_complete:  TAKING_OFF → HOVERING
    target_reached:    FLYING → HOVERING
    navigate:          HOVERING → FLYING
    land:              HOVERING → LANDING | FLYING → LANDING
    trigger_emergency: TAKING_OFF → EMERGENCY | HOVERING → EMERGENCY | FLYING → EMERGENCY | LANDING → EMERGENCY
    emergency_land:    EMERGENCY → LANDING
    touchdown:         LANDING → DISARMED
"""

from statemachine import StateMachine, State


class VehicleFSM(StateMachine):
    """Flight phase state machine for UAV."""
    
    # States
    disarmed = State(initial=True)
    armed = State()
    taking_off = State()
    hovering = State()
    flying = State()
    landing = State()
    emergency = State()
    
    # Transitions
    arm = disarmed.to(armed)
    disarm = armed.to(disarmed)
    takeoff = armed.to(taking_off)
    takeoff_complete = taking_off.to(hovering)
    target_reached = flying.to(hovering)
    navigate = hovering.to(flying)
    land = hovering.to(landing) | flying.to(landing)
    trigger_emergency = taking_off.to(emergency) | hovering.to(emergency) | flying.to(emergency) | landing.to(emergency)
    emergency_land = emergency.to(landing)
    touchdown = landing.to(disarmed)