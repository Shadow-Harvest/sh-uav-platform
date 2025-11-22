#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, SetMode

class ControlNode(Node):
	def __init__(self):
		super().__init__('control_node')
		
		self.current_state = State()
		self.target_pose = PoseStamped()

		# Subscribers
		self.state_sub = self.create_subscription(
			State, '/mavros/state', self.state_callback, 10
		)

		# Publishers
		self.setpoint_pub = self.create_publisher(
			PoseStamped, '/mavros/setpoint_position/local', 10
		)

		# Service clients
		self.arming_client = self.create_client(CommandBool, '/mavros/cmd/arming')
		self.set_mode_client = self.create_client(SetMode, '/mavros/set_mode')

		# Timer
		self.timer = self.create_timer(0.05, self.publish_setpoint)

		self.get_logger().info('Control Node Ready')

	def state_callback(self, msg):
		self.current_state = msg

	def publish_setpoint(self):
		self.target_pose.header.stamp = self.get_clock().now().to_msg()
		self.target_pose.header.frame_id = 'map'
		self.setpoint_pub.publish(self.target_pose)

	def set_offboard_mode(self):
		if not self.set_mode_client.wait_for_service(timeout_sec=5.0):
			self.get_logger().error('SetMode service not available')
			return False

		req = SetMode.Request()
		req.custom_mode = 'OFFBOARD'
		future = self.set_mode_client.call_async(req)
		rclpy.spin_until_future_complete(self, future)

		if future.result() and future.result().mode_sent:
			self.get_logger.info('OFFBOARD mode set')
			return True
		
		return False
	
	def arm(self):
		if not self.arming_client.wait_for_service(timeout_sec=5.0):
			self.get_logger().error('Arming service not available')
			return False
		
		req = CommandBool.Request()
		req.value = True
		future = self.arming_client.call_async(req)
		rclpy.spin_until_future_complete(self, future)

		if future.result() and future.result().mode_sent:
			self.get_logger.info('VEHICLE armed')
			return True
		
		return False
	
	def takeoff(self, altitude=2.0):
		self.get_logger.info('Setting takeoff altitude: {altitude}m')
		self.target_pose.pose.position.z = altitude


def main(args=None):
	rclpy.init(args=args)
	node = ControlNode()

	# Wait for MAVROS
	node.get_logger.info('Waiting for MAVROS...')
	while rclpy.ok() and not node.current_state.connected:
		rclpy.spin_once(node, timeout_sec=1.0)

	node.get_logger.info('MAVROS connected')	

	# Send initial setpoints
	for i in range(100):
		rclpy.spin_once(node, timeout_sec=0.05)

	# Takeoff sequence
	node.takeoff(2.0)

	for _ in range(20):
		rclpy.spin_once(node, timeout_sec=0.05)

	if node.set_offboard_mode():
		if node.arm():
			node.get_logger.info('Takeoff! Hovering at 2m!')
		
	rclpy.spin(node)
		
if __name__ == 'main':
	main()

