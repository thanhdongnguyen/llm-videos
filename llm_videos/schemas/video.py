
from marshmallow import Schema, fields, validate

class ProcessYoutubeSchema(Schema):
    youtube_url = fields.URL(required=True)



class SummarizeVideoSchema(Schema):
    video_id = fields.Int(required=True)