#!/usr/bin/env python

import roslib; roslib.load_manifest('qbo_manual_control')
import rospy

from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState
from sensor_msgs.msg import Joy

import time
import sys, tty, termios

head_tilt_pos = 0.0
head_pan_pos = 0.0
joy_prev = Joy()

def move(publisher,linear,ang):
	speed_command=Twist()
	speed_command.linear.x=linear
	speed_command.linear.y=0
	speed_command.linear.z=0
	speed_command.angular.x=0
	speed_command.angular.y=0
	speed_command.angular.z=ang
	publisher.publish(speed_command)
	

def move_head_tilt(publisher, speed_tilt, speed_pan):
	global joy_prev
	global head_tilt_pos
	global head_pan_pos
	servo_command=JointState()
	servo_command.name=['head_tilt_joint', 'head_pan_joint']
	tilt_pos = head_tilt_pos
	pan_pos = head_pan_pos

	if speed_tilt > 0:
		tilt_pos -= 0.2
	elif speed_tilt < 0:
		tilt_pos += 0.2

	if speed_pan > 0:
		pan_pos -= 0.2
	elif speed_pan < 0:
		pan_pos += 0.2

#	if joy_prev.axes[3] > speed_tilt:
#		tilt_pos -= 1
#	elif joy_prev.axes[3] < speed_tilt:
#		tilt_pos += 1
#	else:
#		tilt_pos = 0

	servo_command.position=[tilt_pos, pan_pos]

	publisher.publish(servo_command)

	

def cb_joint(data):
	global head_tilt_pos
	global head_pan_pos
	head_tilt_pos = data.position[3]
	head_pan_pos = data.position[2]

def callback(data):
	global joy_prev
	if (len(joy_prev.axes) == 0):
		joy_prev = data
	pub = rospy.Publisher('/cmd_vel', Twist)
	pub_joints = rospy.Publisher('/cmd_joints',JointState)
	move(pub, data.axes[1]*0.5, data.axes[0])
#	print data
	move_head_tilt(pub_joints, data.axes[3], data.axes[2])
	joy_prev = data

def main():
	print "Initializing..."
	rospy.init_node('qbo_manual_control')
	
	pub = rospy.Publisher('/cmd_vel', Twist)
	sub = rospy.Subscriber('/joy', Joy, callback)
	sub_joint = rospy.Subscriber('/joint_states', JointState, cb_joint)
	
	fd = sys.stdin.fileno()
	old_settings = termios.tcgetattr(fd)
	
	print "Start"
	while(not rospy.is_shutdown()):
		tty.setraw(sys.stdin.fileno())
		ch = sys.stdin.read(1)
	
		if ch=='w' or ch=='W': #Forewards
			move(pub,0.3,0)
		elif ch=='s' or ch=='S': #Backwards
			move(pub,-0.3,0)
		elif ch=='a' or ch=='A': #Left
			move(pub,0,1)
		elif ch=='d' or ch=='D': #Right
			move(pub,0,-1)
		else:
			move(pub,0,0) #Stop and quit loop
			break
		#Wait until read other keyboard, because for each message the robot will be move for a second
		time.sleep(0.5)
	
	termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
	main()