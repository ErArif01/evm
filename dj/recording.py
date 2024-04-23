import cv2
import pyaudio
import wave
import threading
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Video recording function
class VideoRecorder:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.is_recording = False
        self.out = None

    def start_recording(self):
        self.is_recording = True
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))
        while self.is_recording:
            ret, frame = self.video.read()
            if ret:
                self.out.write(frame)
                cv2.imshow('Recording', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        cv2.destroyAllWindows()
        self.out.release()
        self.video.release()

    def stop_recording(self):
        
        self.is_recording = False

# Voice recording function
class VoiceRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.is_recording = False

    def _audio_callback(self, in_data, frame_count, time_info, status):
        self.frames.append(in_data)
        return in_data, pyaudio.paContinue

    def start_recording(self):
        self.is_recording = True
        stream = self.audio.open(format=pyaudio.paInt16,
                                 channels=1,
                                 rate=44100,
                                 input=True,
                                 frames_per_buffer=1024,
                                 stream_callback=self._audio_callback)
        stream.start_stream()
        while self.is_recording:
            time.sleep(0.1)
        stream.stop_stream()
        stream.close()
        self.audio.terminate()
        wf = wave.open("output.wav", 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def stop_recording(self):
        self.is_recording = False

# Google Drive upload function
def upload_to_google_drive(file_path):
    # Authenticate and create the service
    # You need to set up the credentials properly
    drive_service = build('drive', 'v3', credentials=YOUR_CREDENTIALS_HERE)

    file_metadata = {'name': 'RecordedVideo.avi'}
    media = MediaFileUpload(file_path, mimetype='video/avi')
    file = drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    print('File ID: %s' % file.get('id'))

if __name__ == "__main__":
    video_recorder = VideoRecorder()
    voice_recorder = VoiceRecorder()

    start_video_thread = threading.Thread(target=video_recorder.start_recording)
    start_voice_thread = threading.Thread(target=voice_recorder.start_recording)

    start_video_thread.start()
    start_voice_thread.start()

    input("Press Enter to start recording...")
    
    start_video_thread.join()
    start_voice_thread.join()

    # Once recording stops, upload the video to Google Drive
    upload_to_google_drive('output.avi')
