from rest_framework.test import APITestCase, APIClient

class UserTests(APITestCase):
    def test_create_user(self):
        client = APIClient()

        response = client.post('/users', {}, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(list(response.data.keys()), ['id',
                                                      'name',
                                                      'email',
                                                      'last_login',
                                                      'created_at',
                                                      'updated_at',
                                                      'random_slugs'])

    def test_update_user(self):
      client = APIClient()

      create_response = client.post('/users', {}, format='json')

      self.assertEqual(create_response.status_code, 201)

      token = 'Bearer ' + create_response.data['random_slugs'][0]

      client.credentials(HTTP_AUTHORIZATION=token)

      update_response = client.put('/users/' + str(create_response.data['id']),
                                 {'email': 'foo@yahoo.com'},
                                 format='json')

      self.assertEqual(update_response.status_code, 200)
      self.assertEqual(update_response.data['email'], 'foo@yahoo.com')
      self.assertEqual(list(update_response.data.keys()), ['id',
                                                           'name',
                                                           'email',
                                                           'last_login',
                                                           'created_at',
                                                           'updated_at'])
