import cv2
import threading
from django.conf import settings
import logging
import time
from queue import Queue, Empty
from .models import Video
import os

logger = logging.getLogger(__name__)

class VideoStreamThread:
    def __init__(self, video_path, buffer_size=30):
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        self.video_path = video_path
        self.buffer_size = buffer_size 
        self.frame_queue = Queue(maxsize=buffer_size)
        self.cap = None
        self.is_running = False # Flag to check if streaming is active
        self.thread = None # Background thread
        self.fps = 30
        self.viewers = 0
        self.lock = threading.Lock()# Prevents race conditions in multi-threading
        self._cap_lock = threading.Lock() # Lock for accessing video capture
        self.initialized = threading.Event() # Used to signal when streaming is ready

    def start(self):
        """Start video streaming thread"""
        try:
            with self._cap_lock:
                if self.cap is None:
                    self.cap = cv2.VideoCapture(self.video_path)
                    if not self.cap.isOpened():
                        raise ValueError(f"Failed to open video: {self.video_path}")

                    # Get video properties
                    self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
                    self.frame_delay = 1 / self.fps

                    # Pre-fill the queue with some frames
                    for _ in range(min(5, self.buffer_size)):
                        ret, frame = self.cap.read()
                        if ret:
                            frame = cv2.resize(frame, (1280, 720))
                            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                            self.frame_queue.put(buffer.tobytes())

            self.is_running = True
            self.thread = threading.Thread(target=self._stream_worker)
            self.thread.daemon = True
            self.thread.start()
            
            # Wait for initialization
            self.initialized.set()
            logger.info(f"Started streaming: {self.video_path}")
            return True
        except Exception as e:
            logger.error(f"Error starting stream: {str(e)}")
            self.cleanup()
            return False

    def _stream_worker(self):
        """Worker thread for video streaming"""
        try:
            while self.is_running and self.viewers > 0:
                if self.frame_queue.full():
                    time.sleep(self.frame_delay)
                    continue

                with self._cap_lock:
                    if self.cap is None:
                        break
                    ret, frame = self.cap.read()
                    if not ret:
                        # Video ended, restart
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue

                    # Process frame
                    try:
                        frame = cv2.resize(frame, (1280, 720))
                        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                        self.frame_queue.put(buffer.tobytes())
                    except Exception as e:
                        logger.error(f"Frame processing error: {str(e)}")
                        continue

                time.sleep(self.frame_delay)
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
        finally:
            self.cleanup()

    def get_frame(self):
        """Get next frame from queue"""
        try:
            # Wait for stream to initialize
            if not self.initialized.wait(timeout=2.0):
                logger.error("Stream initialization timeout")
                return None
                
            return self.frame_queue.get(timeout=0.5)
        except Empty:
            logger.warning("Frame queue empty")
            return None
        except Exception as e:
            logger.error(f"Error getting frame: {str(e)}")
            return None

    def add_viewer(self):
        """Add a viewer to the stream"""
        with self.lock:
            self.viewers += 1
            if self.viewers == 1:
                self.start()
            logger.info(f"Viewer added. Total viewers: {self.viewers}")

    def remove_viewer(self):
        """Remove a viewer from the stream"""
        with self.lock:
            if self.viewers > 0:
                self.viewers -= 1
                logger.info(f"Viewer removed. Total viewers: {self.viewers}")
                if self.viewers == 0:
                    self.stop()

    def stop(self):
        """Stop the stream"""
        self.is_running = False
        self.initialized.clear()
        self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        with self._cap_lock:
            if self.cap is not None:
                self.cap.release()
                self.cap = None
                
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except:
                pass
        logger.info(f"Cleaned up stream: {self.video_path}")

class StreamManager:
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        self._streams = {}
        self._streams_lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def get_stream(self, video_id, video_path):
        """Get or create a video stream"""
        with self._streams_lock:
            if video_id not in self._streams:
                stream = VideoStreamThread(video_path)
                self._streams[video_id] = stream
            stream = self._streams[video_id]
            stream.add_viewer()
            return stream

    def release_stream(self, video_id):
        """Release a stream"""
        with self._streams_lock:
            if video_id in self._streams:
                self._streams[video_id].remove_viewer()
                if self._streams[video_id].viewers == 0:
                    self._streams[video_id].cleanup()
                    del self._streams[video_id]
                logger.info(f"Released stream: {video_id}")