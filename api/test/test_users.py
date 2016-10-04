from rest_framework.test import APITestCase, APIClient

class UserTests(APITestCase):
    user_get_update_keys = ['id',
                            'name',
                            'email',
                            'last_login',
                            'created_at',
                            'updated_at']

    user_create_keys = ['id',
                        'name',
                        'email',
                        'last_login',
                        'created_at',
                        'updated_at',
                        'random_slugs']

    def test_create_user(self):
        client = APIClient()

        response = client.post('/users', {}, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(list(response.data.keys()), self.user_create_keys)

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
        self.assertEqual(list(update_response.data.keys()), self.user_get_update_keys)

    def test_user_update_must_be_logged_in(self):
        client = APIClient()

        create_repsonse = client.post('/users', {}, format='json')

        update_response = client.put('/users/' + str(create_repsonse.data['id']),
                                     {'email': 'foo@yahoo.com'},
                                     format='json')

        self.assertEqual(update_response.status_code, 401)

    def test_cannot_update_other_user(self):
        client = APIClient()

        user1_repsonse = client.post('/users', {}, format='json')
        user2_response = client.post('/users', {}, format='json')

        user2_token = 'Bearer ' + user2_response.data['random_slugs'][0]

        client.credentials(HTTP_AUTHORIZATION=user2_token)

        update_response = client.put('/users/' + str(user1_repsonse.data['id']),
                                     {'email': 'foo@yahoo.com'},
                                     format='json')

        self.assertEqual(update_response.status_code, 403)

    def test_list_users(self):
        client = APIClient()

        user1_repsonse = client.post('/users', {}, format='json')
        user2_response = client.post('/users', {}, format='json')

        list_response = client.get('/users')

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list(list_response.data.keys()), ['count',
                                                           'next',
                                                           'previous',
                                                           'results'])
        self.assertEqual(len(list_response.data['results']), 2)
        self.assertEqual(list(list_response.data['results'][0].keys()), self.user_get_update_keys)
        self.assertEqual(list(list_response.data['results'][1].keys()), self.user_get_update_keys)

    def test_get_user(self):
        client = APIClient()

        user_create_response = client.post('/users', {}, format='json')

        self.assertEqual(user_create_response.status_code, 201)

        user_response = client.get('/users/' + str(user_create_response.data['id']))

        self.assertEqual(user_response.status_code, 200)
        self.assertEqual(list(user_response.data.keys()), self.user_get_update_keys)
