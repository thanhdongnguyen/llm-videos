

class VideoHandler:
    def __init__(self, video):
        self.video = video

    def process(self):
        self.video.processed = True
        self.video.save()