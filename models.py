from pydantic import BaseModel
from tortoise import Model, fields



class TXT(Model):
    class Meta:
        table = 'TXT'
    id = fields.IntField(pk=True, generated=True)
    name = fields.CharField(max_length=200, null=False, description='小说名')
    title = fields.TextField(max_length=200,null=False, description='章节标题')
    txt = fields.TextField( null=False, description='章节内容')
    nums = fields.IntField(null=True, description='章节数')

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'txt': self.txt,
            'nums': self.nums
        }
