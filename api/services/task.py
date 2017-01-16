from .base import BaseServiceClient

class TaskServiceClient(BaseServiceClient):
    def create(self, task):
        return self.request('post',
                            '/tasks',
                            json=task)

    def get(self, task_id):
      return self.request('get', '/tasks/' + str(task_id))
