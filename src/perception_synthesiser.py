#!/usr/bin/env python
import roslib; roslib.load_manifest('dmitry_tracker')
import rospy
import math
import threading
import tf
from std_msgs.msg import Float64
from std_msgs.msg import UInt16MultiArray
from dmitry_tracker.msg import Thingies, Thingy
from geometry_msgs.msg import Point

class PerceptionSynthesiser():
    def __init__(self):
        rospy.init_node('perception_synthesiser')
        self.rate = rospy.Rate(10)
        self.users_lock = threading.Lock()
        self.users = []
        self.users_sub = rospy.Subscriber('openni_tracker/users', UInt16MultiArray, self.users_changed)
        self.thingies_pub = rospy.Publisher(rospy.get_name() + '/thingies', Thingies)

        self.tl = tf.TransformListener()

    def users_changed(self, users):
        self.users_lock.acquire()
        if len(users.data) > 0:
            self.users = users.data
            print("USERS %s" % str(self.users))
        self.users_lock.release()

    def run(self):
        while not rospy.is_shutdown():
            self.users_lock.acquire()
            time = rospy.Time(0)
            msg = Thingies()

            for user in self.users:
                try:
                    print("USER %s" % str(user))
                    tf_user_id = '/head_' + str(user)
                    (trans, rot) = self.tl.lookupTransform('/camera_depth_frame', tf_user_id, time)
                    thingy = Thingy()
                    thingy.id = tf_user_id

                    point = Point()
                    point.x = trans[0]
                    point.y = trans[1]
                    point.z = trans[2]
                    thingy.position = point
                    msg.thingies.append(thingy)

                except (tf.LookupException, tf.ConnectivityException):
                    continue

            self.users_lock.release()
            self.thingies_pub.publish(msg)
            self.rate.sleep()

if __name__ == '__main__':    
    ps = PerceptionSynthesiser()
    ps.run()
