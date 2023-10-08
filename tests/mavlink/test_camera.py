# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/api/22_mavlink.camera.ipynb.

# %% auto 0
__all__ = ['NAN', 'CAMERA_INFORMATION', 'CAMERA_SETTINGS', 'STORAGE_INFORMATION', 'CAMERA_CAPTURE_STATUS',
           'CAMERA_IMAGE_CAPTURED', 'MAV_TYPE_GCS', 'MAV_TYPE_CAMERA', 'Cam1', 'Cam2', 'Cli', 'test_ack']

# %% ../../nbs/api/22_mavlink.camera.ipynb 6
import time
from UAV.mavlink.mavcom import MAVCom, time_since_boot_ms, time_UTC_usec, date_time_str
from UAV.mavlink.component import Component, mavutil, mavlink, MAVLink

from UAV.mavlink.camera_client import *
from UAV.mavlink.camera_server import *
from UAV.utils.display import *
from fastcore.test import *

# %% ../../nbs/api/22_mavlink.camera.ipynb 9
# from pymavlink.dialects.v20 import ardupilotmega as mav
# from pymavlink.dialects.v20.ardupilotmega import MAVLink


NAN = float("nan")

"""
MAV_CMD_REQUEST_CAMERA_CAPTURE_STATUS = 527 # https://mavlink.io/en/messages/common.html#MAV_CMD_REQUEST_CAMERA_CAPTURE_STATUS
MAV_CMD_REQUEST_CAMERA_INFORMATION = 521 # https://mavlink.io/en/messages/common.html#MAV_CMD_REQUEST_CAMERA_INFORMATION
MAV_CMD_REQUEST_CAMERA_SETTINGS = 522 # https://mavlink.io/en/messages/common.html#MAV_CMD_REQUEST_CAMERA_SETTINGS
MAV_CMD_REQUEST_STORAGE_INFORMATION = 525 # https://mavlink.io/en/messages/common.html#MAV_CMD_REQUEST_STORAGE_INFORMATION
MAV_CMD_STORAGE_FORMAT = 526 # https://mavlink.io/en/messages/common.html#MAV_CMD_STORAGE_FORMAT
MAV_CMD_SET_CAMERA_ZOOM = 531 # https://mavlink.io/en/messages/common.html#MAV_CMD_SET_CAMERA_ZOOM
MAV_CMD_SET_CAMERA_FOCUS = 532 # https://mavlink.io/en/messages/common.html#MAV_CMD_SET_CAMERA_FOCUS
MAV_CMD_IMAGE_START_CAPTURE = 2000  # https://mavlink.io/en/messages/common.html#MAV_CMD_IMAGE_START_CAPTURE
MAV_CMD_IMAGE_STOP_CAPTURE = 2001  # https://mavlink.io/en/messages/common.html#MAV_CMD_IMAGE_STOP_CAPTURE
MAV_CMD_REQUEST_VIDEO_STREAM_INFORMATION = 2504 # https://mavlink.io/en/messages/common.html#MAV_CMD_REQUEST_VIDEO_STREAM_INFORMATION
MAV_CMD_REQUEST_VIDEO_STREAM_STATUS = 2505 # https://mavlink.io/en/messages/common.html#MAV_CMD_REQUEST_VIDEO_STREAM_STATUS
MAV_CMD_VIDEO_START_CAPTURE = 2500 # https://mavlink.io/en/messages/common.html#MAV_CMD_VIDEO_START_CAPTURE
MAV_CMD_VIDEO_STOP_CAPTURE = 2501 # https://mavlink.io/en/messages/common.html#MAV_CMD_VIDEO_STOP_CAPTURE
MAV_CMD_SET_CAMERA_MODE = 530 # https://mavlink.io/en/messages/common.html#MAV_CMD_SET_CAMERA_MODE

"""
CAMERA_INFORMATION = mavlink.MAVLINK_MSG_ID_CAMERA_INFORMATION # https://mavlink.io/en/messages/common.html#CAMERA_INFORMATION
CAMERA_SETTINGS = mavlink.MAVLINK_MSG_ID_CAMERA_SETTINGS # https://mavlink.io/en/messages/common.html#CAMERA_SETTINGS
STORAGE_INFORMATION = mavlink.MAVLINK_MSG_ID_STORAGE_INFORMATION # https://mavlink.io/en/messages/common.html#STORAGE_INFORMATION
CAMERA_CAPTURE_STATUS = mavlink.MAVLINK_MSG_ID_CAMERA_CAPTURE_STATUS # https://mavlink.io/en/messages/common.html#CAMERA_CAPTURE_STATUS
CAMERA_IMAGE_CAPTURED = mavlink.MAVLINK_MSG_ID_CAMERA_IMAGE_CAPTURED # https://mavlink.io/en/messages/common.html#CAMERA_IMAGE_CAPTURED


# %% ../../nbs/api/22_mavlink.camera.ipynb 24
from UAV.mavlink.mavcom import MAVCom
from UAV.mavlink.component import Component, mavutil
import time

MAV_TYPE_GCS = mavutil.mavlink.MAV_TYPE_GCS
MAV_TYPE_CAMERA = mavutil.mavlink.MAV_TYPE_CAMERA

class Cam1(Component):
    def __init__(self, source_component, mav_type, debug=False):
        super().__init__(source_component=source_component, mav_type=mav_type,
                         loglevel=LogLevels.DEBUG)

class Cam2(Component):
    def __init__(self, source_component, mav_type, debug=False):
        super().__init__(source_component=source_component, mav_type=mav_type,
                         loglevel=LogLevels.DEBUG)
class Cli(Component):
    def __init__(self, source_component, mav_type, debug=False):
        super().__init__( source_component=source_component, mav_type=mav_type,
                         loglevel=LogLevels.DEBUG)

# %% ../../nbs/api/22_mavlink.camera.ipynb 25
def test_ack():
    # Test sending a command and receiving an ack from client to server
    with MAVCom("udpin:localhost:14445", source_system=111, loglevel=LogLevels.DEBUG) as client:
        with MAVCom("udpout:localhost:14445", source_system=222,loglevel=LogLevels.DEBUG) as server:
            client.add_component(Cli( mav_type=MAV_TYPE_GCS, source_component = 11))
            server.add_component(Cam1( mav_type=MAV_TYPE_CAMERA, source_component = 22))
            server.add_component(Cam1( mav_type=MAV_TYPE_CAMERA, source_component = 23))
            
            for key, comp in client.component.items():
                if comp.wait_heartbeat(target_system=222, target_component=22, timeout=0.1):
                    print ("*** Received heartbeat **** " )
            NUM_TO_SEND = 2
            for i in range(NUM_TO_SEND):
                client.component[11]._test_command(222, 22, 1)
                client.component[11]._test_command(222, 23, 1)
                
            client.component[11]._test_command(222, 24, 1)
    
        print(f"{server.source_system = };  {server.message_cnts = }")
        print(f"{client.source_system = };  {client.message_cnts = }")
        print()
        print(f"{client.source_system = } \n{client.summary()} \n")
        print(f"{server.source_system = } \n{server.summary()} \n")
    
        assert client.component[11].num_cmds_sent == NUM_TO_SEND * 2 + 1
        assert client.component[11].num_acks_rcvd == NUM_TO_SEND * 2
        assert client.component[11].num_acks_drop == 1
        assert server.component[22].num_cmds_rcvd == NUM_TO_SEND
        assert server.component[23].num_cmds_rcvd == NUM_TO_SEND
test_ack()
