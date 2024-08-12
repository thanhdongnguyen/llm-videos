from marshmallow import Schema, fields, validate


class ChatSchema(Schema):
    query = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    video_id = fields.Int(required=True)