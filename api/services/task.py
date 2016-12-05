from .base import BaseServiceClient

class TaskServiceClient(BaseServiceClient):
    def create(self, task):
        return self.request('post',
                            '/tasks',
                            json=task)
