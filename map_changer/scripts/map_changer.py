#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import UInt16
from std_srvs.srv import Trigger
from nav2_msgs.srv import LoadMap
import ruamel.yaml
from pathlib import Path
import time


class MultiMapChanger(Node):
    def __init__(self):
        super().__init__("map_changer")

        # Parameters
        self.declare_parameter("multi_map_dir", "")
        self.declare_parameter("waypoints_file", "")

        self.multimap_dir = Path(
            self.get_parameter("multi_map_dir").get_parameter_value().string_value
        )
        self.waypoints_file = Path(
            self.get_parameter("waypoints_file").get_parameter_value().string_value
        )

        # Read waypoints file
        self.change_point_num = []
        self.next_map_idx = []
        yaml = ruamel.yaml.YAML()
        with open(self.waypoints_file) as file:
            waypoints_yaml = yaml.load(file)
        for i, data in enumerate(waypoints_yaml["waypoints"]):
            if "change_map" in data["point"]:
                self.change_point_num.append(i + 2)
                self.next_map_idx.append(data["point"]["change_map"])

        # Virables
        self.current_map_num = 0
        self.waypoint_num = 0
        self.response = None

        # Service clients
        self.change_map_client = self.create_client(LoadMap, "/map_server/load_map")
        self.stop_nav_client = self.create_client(Trigger, "/stop_wp_nav")
        self.resume_nav_client = self.create_client(Trigger, "/resume_nav")

        # Subscriber
        self.wp_num_sub = self.create_subscription(
            UInt16, "/waypoint_num", self.waypoint_num_callback, 10
        )
        return

    def waypoint_num_callback(self, msg: UInt16):
        if msg.data == self.waypoint_num:
            return
        if not msg.data in self.change_point_num:
            return
        idx = self.change_point_num.index(msg.data)
        self.current_map_num = self.next_map_idx[idx]
        self.change_map_service_call()
        self.waypoint_num = msg.data
        return

    def change_map_service_call(self):
        self.stop_nav_client.call_async(Trigger.Request())
        while not self.change_map_client.wait_for_service(5.0):
            self.get_logger().info("Waiting for map server service...")
        try:
            req = LoadMap.Request()
            req.map_url = str(
                self.multimap_dir / Path(f"map{self.current_map_num}.yaml")
            )
            self.response = self.change_map_client.call_async(req)
            self.response.add_done_callback(self.change_map_done_callback)

        except Exception as e:
            self.get_logger().error("Change map service call failed")
            self.get_logger().error(e)
        return False

    def change_map_done_callback(self, _):
        time.sleep(3.0)
        self.get_logger().info("Successfully changed the map")
        self.resume_nav_client.call_async(Trigger.Request())
        return


def main(args=None):
    rclpy.init(args=args)
    mmc = MultiMapChanger()
    try:
        rclpy.spin(mmc)
        mmc.destroy_node()
        rclpy.shutdown()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
