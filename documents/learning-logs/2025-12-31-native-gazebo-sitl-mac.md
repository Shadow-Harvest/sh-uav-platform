# Native Gazebo + ArduPilot SITL on M1 Mac

**Date:** 2025-12-31
**Session:** Hybrid Mac Setup - Native Simulation

## What I Learned

- Docker Gazebo on Mac uses software rendering (slow) - native Gazebo uses Metal GPU (5x faster)
- ArduPilot has multiple SITL backends with different protocols
- macOS doesn't support Docker `--network host`, making UDP bidirectional communication problematic
- `AHRS_EKF_TYPE 10` is the key for Gazebo SITL on Mac - bypasses GPS requirements

## The Journey

### Initial Goal
Run Gazebo natively on Mac for GPU acceleration, with SITL in Docker.

### What Didn't Work

1. **Docker SITL + Native Gazebo via UDP relay**
   - Docker bridge NAT prevents Gazebo from replying to Docker's internal IP
   - UDP relay scripts couldn't solve the bidirectional issue
   - Disabling macOS firewall didn't help

2. **`-f gazebo-iris` alone**
   - Uses old `SIM_Gazebo.cpp` with simple protocol (no magic number)
   - Gazebo plugin expects magic number `18458`
   - Error: `Incorrect protocol magic 0 should be 18458`

3. **`-f JSON` alone**
   - Correct protocol but wrong frame parameters
   - Missing GPS caused EKF failures

4. **Enabling SIM_GPS1_TYPE/ENABLE**
   - Gazebo doesn't send lat/lon in JSON - only position
   - Simulated GPS never got a fix
   - `GPS 1: not healthy` and `EKF attitude is bad` errors persisted

5. **SIM_IMU_COUNT adjustments**
   - Reducing to 1 IMU caused "3D Accel calibration needed"
   - Not the right approach

### What Worked

**Final working commands (3 terminals):**

```bash
# Terminal 1 - Gazebo Server
gz sim -v4 -s -r ~/Robotics/ardupilot_gazebo/worlds/iris_runway.sdf

# Terminal 2 - Gazebo GUI
gz sim -g

# Terminal 3 - ArduPilot SITL
cd ~/Robotics/ardupilot
sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --console --out=udp:127.0.0.1:14550
```

**Note:** If you get Ruby/RVM conflicts with `gz` command, ensure Homebrew's Ruby is used:
```bash
/opt/homebrew/bin/ruby /opt/homebrew/bin/gz sim -g
```
**Optional: Gazebo aliases that bypass RVM**
```
alias gz-server='/opt/homebrew/opt/ruby/bin/ruby /opt/homebrew/bin/gz sim -s'
alias gz-gui='/opt/homebrew/opt/ruby/bin/ruby /opt/homebrew/bin/gz sim -g'
```


**Critical parameters:**
```
param set AHRS_EKF_TYPE 10    # SITL mode - uses sim position directly
param set SIM_GPS1_ENABLE 0   # Disable simulated GPS
param set GPS1_TYPE 0         # Disable GPS driver
param save
```

## Key Commands / Code Snippets

```bash
# Install ArduPilot SITL on Mac
cd ~/Robotics
git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git
cd ardupilot
Tools/environment_install/install-prereqs-mac.sh
./waf configure --board sitl
./waf copter

# Add to ~/.zshrc
export PATH="$HOME/Robotics/ardupilot/Tools/autotest:$PATH"
```

## Gotchas / Mistakes Made

1. **Protocol mismatch**: `-f gazebo-iris` uses different protocol than Gazebo Harmonic plugin
2. **Need BOTH flags**: `-f gazebo-iris --model JSON` - frame params + correct protocol
3. **GPS red herring**: Spent hours trying to fix GPS when `AHRS_EKF_TYPE 10` was the answer
4. **Clean eeprom**: Delete `ArduCopter/eeprom.bin` when params get corrupted

## Architecture Summary

```
┌─────────────────────┐     UDP 9002/9003      ┌─────────────────────┐
│   Native Gazebo     │◄────────────────────►  │   Native SITL       │
│   (Metal GPU)       │   JSON + magic 18458   │   (ArduCopter)      │
│   iris_runway.sdf   │                        │   -f gazebo-iris    │
│   ArduPilotPlugin   │                        │   --model JSON      │
└─────────────────────┘                        └─────────────────────┘
                                                        │
                                                        │ UDP 14550
                                                        ▼
                                               ┌─────────────────────┐
                                               │   Docker Container  │
                                               │   - MAVROS          │
                                               │   - ROS2 nodes      │
                                               │   - uav_control     │
                                               └─────────────────────┘
```

## Resources

- [ardupilot_gazebo README](https://github.com/ArduPilot/ardupilot_gazebo)
- [ArduPilot SITL on Apple Silicon](https://discuss.ardupilot.org/t/how-to-use-gazebo-garden-for-sitl-simulation-of-ardupilot-on-apple-silicon/92390)

## Questions for Next Time

- Can we add GPS sensor to Gazebo model for more realistic simulation?
- Does MAVROS in Docker connect properly to native SITL on port 14550?
- Performance comparison: native Gazebo vs Docker Gazebo

## Next Steps

1. Test MAVROS in Docker connects to native SITL
2. Test uav_control nodes with the simulation
3. Document final setup in project README
