#-*- coding: utf-8 -*-
"""
국토부3세부
SCOP에서 전송한 MQTT 정보를 Withpoints MQTT Broker에서 접속해 수신하는 프로그램

copyright KOCETI
"""

import json
import time
from datetime import datetime
from threading import Thread

import paho.mqtt.client as mqtt
import rclpy
from msg_gps_interface.msg import GPSMsg
from rclpy.node import Node
from roller_interfaces.msg import RollerStatus
from std_msgs.msg import String

# BROKER = 'withpoints.asuscomm.com'
# PORT = 50592
BROKER = 'localhost'
PORT = 1883
CLIENT_ID = "roller_cmd_recv_vib"
USERNAME = "roller"
PASSWORD = "roller"


class MQTTClientNode(Node):
    def __init__(self):
        super().__init__('mqtt_client_node')
        self.get_logger().info(f'MQTT Client to Scop via Withpoints broker started.')
        self.equip_data = self.make_equip_data()

        self.gps_msg_subscriber = self.create_subscription(
            msg_type=GPSMsg,
            topic='gps_msg',
            callback=self.recv_gpsmsg,
            qos_profile=10
        )
        self.roller_msg_subscriber = self.create_subscription(
            msg_type=RollerStatus,
            topic='roller_status',
            callback=self.recv_rlrstat,
            qos_profile=10
        )
        self.mqtt_client = mqtt.Client(client_id=CLIENT_ID)
        # self.mqtt_client.username_pw_set(USERNAME, PASSWORD)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.connect_thread = Thread(target=self.connect, daemon=True)
        self.connect_thread.start()

        self.send_mqtt_timer = self.create_timer(1, self.send_equip_data)

    # MQTT 함수
    def connect(self):
        while not self.mqtt_client.is_connected():
            try:
                self.get_logger().info('Connecting to MQTT Broker...')
                self.mqtt_client.connect(BROKER, PORT, 60)
                self.mqtt_client.loop_start()
                break
            except Exception as e:
                self.get_logger().error(f'Connection error: {e}')
                self.get_logger().info('Retrying in 5 seconds...')
                time.sleep(5)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.get_logger().info('Connected to MQTT Broker!')
            client.subscribe("command/workplan/roller")
        else:
            self.get_logger().error(f'Failed to connect, return code {rc}')

    def on_disconnect(self, client, userdata, rc):
        self.get_logger().info('Disconnected from MQTT broker')
        time.sleep(5)
        self.connect()

    # 콜백함수
    def on_message(self, client, userdata, msg):
        self.get_logger().info(f'Message received on topic {msg.topic}: {msg.payload.decode()}')

    def recv_gpsmsg(self, msg:GPSMsg):
        self.equip_data["rlr_drm_lttd"] = msg.lat
        self.equip_data["rlr_drm_lgtd"] = msg.lon
        self.equip_data["rlr_drm_attd"] = msg.alt
        self.equip_data["rlr_drm_z_pose"] = msg.heading
        self.equip_data["rlr_drm_vel"] = msg.speed
        self.equip_data["rlr_timestamp"] = msg.gpstime
        self.equip_data["evenDt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.equip_data["rlr_drum_posx"] = msg.tm_x
        self.equip_data["rlr_drum_posy"] = msg.tm_y

    def recv_rlrstat(self, msg:RollerStatus):
        self.equip_data["rlr_drum_steering"] = msg.steer_angle

    def send_equip_data(self):
        msg = String()
        msg.data = json.dumps(self.equip_data, ensure_ascii=False)

        if self.mqtt_client.is_connected():
            self.mqtt_client.publish("equipment/roller", msg.data)
            self.get_logger().info(f'Published data to MQTT topic: {msg.data}')

    # 유틸함수
    def make_equip_data(self):
        return {
            "prjId": "b703bf96-e305-48f9-bd7f-89d87053aca5",
            "userId": "01076257625",
            "assetId": "1ec3d361-48a2-4cdb-a39f-95116c5d67ed",
            "assetNm": "3세부자동화진동롤러",
            "planId": "45da8d5a1c3a156f940ec8fa59be6384",
            "targetId": "1234",
            "assetType": "02",
            "gpsType": "DUAL",
            "rlr_drm_lttd": "",
            "rlr_drm_lgtd": "",
            "rlr_drm_attd": "",
            "rlr_drm_z_pose": "",
            "rlr_drm_vel": "",
            "evenDt": "",
            "rlr_timestamp": "",
            "status": "1",
            "rlr_drm_x_pose": "",
            "rlr_drm_y_pose": "",
            "work_status": "",
            "rlr_drum_roll": "",
            "rlr_drum_pitch": "",
            "rlr_drum_posx": "",
            "rlr_drum_posy": "",
            "rlr_drum_posz": "",
            "rlr_drum_steering": "",
            "rlr_drum_vib": "",
            "rlr_CMV": ""
        }


def main(args=None):
    try:
        rclpy.init(args=args)
        node = MQTTClientNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        node.mqtt_client.disconnect()
        node.mqtt_client.loop_stop()
        node.destroy_node()


if __name__ == '__main__':
    main()
