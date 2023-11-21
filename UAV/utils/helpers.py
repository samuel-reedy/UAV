__all__ = ['start_displays']

import time
from multiprocessing import Process
from typing import Dict
import cv2

try:
    from gstreamer import GstPipeline, GstVideoSource, GstContext, GstPipes
    import gstreamer.utils as gst_utils
    from gstreamer.gst_tools import GstBuffer
except:
    print("GStreamer is not installed")


def start_displays(display_type: str = 'gst',  # display type
                   decoder: str = 'h264',  # encoder type
                   num_cams: int = 1,  # number of cameras
                   names: list = None,  # cameras names
                   port: int = 5000,  # port number
                   _dict: Dict = None,  # cameras dict overides display_type (see below for example)
                    width=800, height=600
                   ) -> Process:  # encoder type
    """ Display video from one or more gst streams from drone in a separate process"""
    if names is None:
        names = [f'Cam {i}' for i in range(num_cams)]

    if decoder == 'h264':
        cmd = 'udpsrc port={port} ! application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96'
        avdec = 'avdec_h264'
        depay = 'rtph264depay'

    elif decoder == 'h265':
        cmd = 'udpsrc port={port} ! application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H265, payload=(int)96'
        avdec = 'avdec_h265'
        depay = 'rtph265depay'

    elif decoder == 'rtsp':
        cmd = 'rtspsrc location=rtsp://admin:admin@192.168.144.108:554/cam/realmonitor?channel=1&subtype=0 latency=100 '
        avdec = 'avdec_h265'
        depay = 'rtph265depay'
        #gst-launch-1.0 rtspsrc location="rtsp://admin:admin@192.168.144.108:554/cam/realmonitor?channel=1&subtype=0" latency=1000queue ! rtph265depay ! h265parse ! avdec_h265 ! autovideosink

    else:
        raise ValueError(f'Unknown decoder type {decoder}')

    if _dict is None:
        if display_type == 'gst':
            _dict = {
                'port': 5000, 'avdec': avdec, 'depay': depay,
                'pipeline': [
                    cmd,
                    'queue',
                    '{depay} ! {avdec}',
                    'videoconvert',
                    'fpsdisplaysink',
                ],
            }
        else:
            _dict = {
                'port': 5000, 'avdec': avdec, 'depay': depay,
                'pipeline': [
                    cmd,
                    'queue',
                    '{depay} ! {avdec}',
                    'videoconvert',
                    'capsfilter caps=video/x-raw,format=BGR ',
                    'appsink name=mysink emit-signals=true  sync=false ',
                    #
                    # 'appsink name=mysink emit-signals=True max-buffers=1 drop=True sync=false',
                ],
            }

    def gst_display(_num_cams: int, _port: int):
        """ Display video from one or more gst streams"""
        print(_dict)
        command_display = gst_utils.format_pipeline(**_dict)
        command_display = command_display.replace('port=5000', 'port={}')
        print(command_display)
        pipes = [GstPipeline(command_display.format(_port + i)) for i in range(_num_cams)]

        # if True:
        # with GstContext(loglevel=LogLevels.CRITICAL):  # GST main loop in thread
        # with GstPipes(pipes, loglevel=LogLevels.INFO) as gp:
        gp = GstPipes(pipes, loglevel=20).startup()
        while any(pipe.is_active for pipe in pipes):
            time.sleep(.5)
        gp.shutdown()

    def cv2_display(_num_cams: int, _port: int, width=width, height=height):
        """ Display video from one or more gst streams"""
        print(_dict)
        command_display = gst_utils.format_pipeline(**_dict)
        command_display = command_display.replace('port=5000', 'port={}')
        print(command_display)

        pipes = [GstVideoSource(command_display.format(_port + i)) for i in range(_num_cams)]
        for i in range(_num_cams):
            cv2.namedWindow(names[i], cv2.WINDOW_GUI_NORMAL)
            cv2.resizeWindow(names[i], width, height)

        with GstPipes(pipes, loglevel=10):
            # time.sleep(1)
            buffer = [GstBuffer for _ in range(_num_cams)]
            count = 0
            while any(pipe.is_active for pipe in pipes):
                count += 1
                for i, pipe in enumerate(pipes):
                    # buffer = pipe.pop()
                    buffer[i] = pipe.get_nowait()
                    if buffer[i]:
                        if count % 100 == 0:
                            print(f'buffer[{i}].data.shape = {buffer[i].data.shape}')

                        cv2.imshow(names[i], buffer[i].data)

                cv2.waitKey(10)
                if not any(buffer):
                    time.sleep(0.01)

        cv2.destroyAllWindows()

    target = gst_display if display_type == 'gst' else cv2_display
    _p = Process(target=target, args=(num_cams, port))
    _p.start()
    time.sleep(0.1)  # wait for display to start
    return _p


test_camera_dict = {
    'port': 5000,
    'width': 640,
    'height': 480,
    'fps': 30,  # Frames per second
    'pipeline': [
        'videotestsrc pattern=ball is-live=true',
        'capsfilter caps=video/x-raw,format=RGB,width={width},height={height},framerate={fps}/1',
        'videoconvert',
        'x264enc tune=zerolatency',
        'rtph264pay ! udpsink host=127.0.0.1 port={port}',
    ],
}

if __name__ == '__main__':
    width, height, fps, num_buffers = 1920, 1080, 30, 200
    caps_filter = 'capsfilter caps=video/x-raw,format=RGB,width={},height={},framerate={}/1'.format(width, height, fps)
    command = 'videotestsrc is-live=true num-buffers={} ! {} ! timeoverlay !  appsink emit-signals=True sync=false'.format(num_buffers, caps_filter)

    p = start_displays(display_type='cv2', num_cams=5)
    # command = gst_utils.format_pipeline(**test_camera_dict)
    with GstContext():
        with GstPipeline(command, loglevel=10):
            time.sleep(5)
    p.terminate()
