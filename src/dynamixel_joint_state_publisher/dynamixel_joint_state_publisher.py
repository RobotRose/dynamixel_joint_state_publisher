#!/usr/bin/env python

"""
    Publish the dynamixel_controller joint states on the /joint_states topic

    Version 1.1 2015-04-15

    Created packaged version 1.1 by Okke Hendriks
    
    Version 1.0 2010-12-28

    Created for the Pi Robot Project: http://www.pirobot.org
    Copyright (c) 2010 Patrick Goebel.  All rights reserved.

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details at:
    
    http://www.gnu.org/licenses/gpl.html
"""

import rospy

from sensor_msgs.msg import JointState
from dynamixel_msgs.msg import JointState as JointStateDynamixel

class JointStateMessage():
    def __init__(self, name, position, velocity, effort):
        self.name = name
        self.position = position
        self.velocity = velocity
        self.effort = effort

class JointStatePublisher():
    def __init__(self):
        rospy.init_node('dynamixel_joint_state_publisher', anonymous=True)
        
        rate = rospy.get_param('~rate', 20)
        r = rospy.Rate(rate)
        
        joint_controllers = rospy.get_param('~joint_controllers', '')

        if joint_controllers:
            rospy.loginfo("Joints: {0}".format(joint_controllers))
        else:
            rospy.logfatal("No joint controllers configured. This node needs to have rosparam ~joint_controllers be set to a list of dynamixel joint controllers. Please see dynamixel_joint_state_publisher/launch/example.launch")
            exit(1)
                                                                
        self.servos = list()
        self.controllers = list()
        self.joint_states = dict({})
        
        for joint_controller in sorted(joint_controllers):
            joint_name = rospy.get_param("/"+joint_controller+'/joint_name', '')
            self.joint_states[joint_name] = JointStateMessage(joint_name, 0.0, 0.0, 0.0)
            self.controllers.append(joint_controller)

        # Start controller state subscribers
        [rospy.Subscriber(c + '/state', JointStateDynamixel, self.controller_state_handler) for c in self.controllers]
     
        # Start publisher
        self.joint_states_pub = rospy.Publisher('/joint_states', JointState)
       
        rospy.loginfo("Starting Dynamixel Joint State Publisher at " + str(rate) + "Hz")
       
        while not rospy.is_shutdown():
            self.publish_joint_states()
            r.sleep()
           
    def controller_state_handler(self, msg):
        js = JointStateMessage(msg.name, msg.current_pos, msg.velocity, msg.load)
        self.joint_states[msg.name] = js
       
    def publish_joint_states(self):
        # Construct message & publish joint states
        msg = JointState()
        msg.name = []
        msg.position = []
        msg.velocity = []
        msg.effort = []
       
        for joint in self.joint_states.values():
            msg.name.append(joint.name)
            msg.position.append(joint.position)
            msg.velocity.append(joint.velocity)
            msg.effort.append(joint.effort)
        
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = 'base_link'
        self.joint_states_pub.publish(msg)
        
if __name__ == '__main__':
    try:
        s = JointStatePublisher()
        rospy.spin()
    except rospy.ROSInterruptException: pass
