import rclpy
from rclpy.node import Node
from mavros_msgs.srv import CommandBool, SetMode, CommandTOL
import time

class Week1Validator(Node):
    def __init__(self):
        super().init__('week1_validator')
        self.get_logger().info("Week 1 Validator starting...")
        
        # Create service clients
        self.arming_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.set_mode_client = self.create_client(SetMode, '/mavros/set_mode')
        self.takeoff_client = self.create_client(CommandTOL, '/mavros/cmd/takeoff')
        self.land_client = self.create_client(CommandTOL, '/mavros/cmd/land')
        
        # Wait for services to be available
        self.get_logger().info("Waiting for MAVROS services...")
        self.arming_client.wait_for_service()
        self.set_mode_client.wait_for_service()
        self.takeoff_client.wait_for_service()
        self.land_client.wait_for_service()
        self.get_logger().info("MAVROS services are available.")
        
    def set_mode(self, mode):
        req = SetMode.Request()
        req.custom_mode = mode
        future = self.set_mode_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        return future.result()
    
    def arm(self):
        req = CommandBool.Request()
        req.value = True
        future = self.arming_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        return future.result()
    
    def takeoff(self, altitude):
        req = CommandTOL.Request()
        req.altitude = altitude
        future = self.takeoff_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        return future.result()
    
    def land(self):
        req = CommandTOL.Request()
        future = self.land_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        return future.result()
    
    def run_validation(self):
        self.get_logger().info("Starting week 1 validaiton...")
        
        # Set mode to GUIDED
        self.get_logger().info("Setting mode to GUIDED...")
        if self.set_mode('GUIDED'):
            self.get_logger().info("Mode set to GUIDED.")
        else:
            self.get_logger().error("Failed to set mode to GUIDED.")
            return False
        
        time.sleep(1)
        
        # Arm the drone
        self.get_logger().info("Arming the drone...")
        if self.arm():
            self.get_logger().info("Drone armed.")
        else:
            self.get_logger().error("Failed to arm the drone.")
            return False
        
        time.sleep(2)
        
        # Takeoff to 10 meters
        self.get_logger().info("Taking off to 10 meters...")
        if self.takeoff(10.0):
            self.get_logger().info("Takeoff successful.")
        else:
            self.get_logger().error("Failed to takeoff.")
            return False
        
        # Hover for 10 seconds
        self.get_logger().info("Hovering for 10 seconds...")
        time.sleep(10)
        
        # Land the drone
        self.get_logger().info("Landing the drone...")
        if self.land():
            self.get_logger().info("Landing successful.")
        else:
            self.get_logger().error("Failed to land the drone.")
            return False    
        
        time.sleep(5)
        
        self.get_logger().info("Week 1 validation completed successfully.")
        return True
    
    def main():
        rclpy.init()
        validator = Week1Validator()
        
        try: 
            validator.run_validation()
        except KeyboardInterrupt:
            validator.get_logger().info("Validation interrupted by user.")
        finally:
            validator.destroy_node()
            rclpy.shutdown()
            
    if __name__ == '__main__':
        main()