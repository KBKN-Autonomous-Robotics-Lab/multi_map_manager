#!/usr/bin/env python3
import rospy
import ruamel.yaml
from pathlib import Path
from std_msgs.msg import UInt16
from std_srvs.srv import Empty, Trigger
from nav_msgs.srv import LoadMap


NODE_NAME = "map_changer"


class MultiMapChanger:
    def __init__(self):
        yaml = ruamel.yaml.YAML()
        ## Read multimaps directory
        self.multimap_dir = rospy.get_param(NODE_NAME + "/multi_map_dir")
        self.multimap_dir = Path(self.multimap_dir).resolve()
        self.current_map_num = 0
        ## Read waypoints file and change point number
        self.change_point_num = []
        self.next_map_idx = []
        waypoints_path = rospy.get_param(NODE_NAME + "/waypoints_file")
        with open(waypoints_path) as file:
            waypoints_yaml = yaml.load(file)
        for i, data in enumerate(waypoints_yaml["waypoints"]):
            if "change_map" in data["point"]:
                self.change_point_num.append(i + 2)
                self.next_map_idx.append(data["point"]["change_map"])
        ## Service clients
        self.change_map = rospy.ServiceProxy("/change_map", LoadMap)
        self.amcl_update = rospy.ServiceProxy("/request_nomotion_update", Empty)
        self.stop_nav = rospy.ServiceProxy("/stop_wp_nav", Trigger)
        self.resume_nav = rospy.ServiceProxy("/resume_nav", Trigger)
        ## Subscribe current waypoint number
        self.waypoint_num = 0
        self.wp_num_sub = rospy.Subscriber(
            "/waypoint_num", UInt16, self.waypoint_num_callback
        )
        return

    def waypoint_num_callback(self, msg):
        if msg.data == self.waypoint_num:
            return
        try:
            idx = self.change_point_num.index(msg.data)
            self.current_map_num = self.next_map_idx[idx]
            self.change_map_service_call()
        except ValueError:
            pass

        self.waypoint_num = msg.data
        return

    def change_map_service_call(self):
        self.stop_nav()
        rospy.sleep(0.5)
        self.update_amcl_call()
        rospy.wait_for_service("/change_map")
        try:
            res = self.change_map(
                str(self.multimap_dir / Path("map{}.yaml".format(self.current_map_num)))
            )
            if res.result == 0:
                rospy.loginfo("Successfully changed the map")
                self.update_amcl_call()
                self.resume_nav()
                return True
            else:
                rospy.logerr("Failed to change the map: result=", res.result)

        except rospy.ServiceException:
            rospy.logerr("Change map service call failed")
        return False

    def update_amcl_call(self):
        rospy.wait_for_service("/request_nomotion_update")
        for i in range(0, 5):
            self.amcl_update()
            rospy.sleep(0.5)
        rospy.loginfo("Update amcl pose 5 times")


if __name__ == "__main__":
    rospy.init_node(NODE_NAME)
    mmc = MultiMapChanger()
    rospy.spin()
