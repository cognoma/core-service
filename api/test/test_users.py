from rest_framework.test import APITestCase, APIClient

class UserTests(APITestCase):
    user_get_keys = ['id',
                     'name',
                     'created_at',
                     'updated_at',
                     'random_slugs',
                     'classifier_set']

    user_update_get_self_keys = ['id',
                                 'name',
                                 'email',
                                 'created_at',
                                 'updated_at',
                                 'random_slugs',
                                 'classifier_set']

    user_create_keys = ['id',
                        'name',
                        'email',
                        'created_at',
                        'updated_at',
                        'random_slugs',
                        'classifier_set']

    service_token = 'JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXJ2aWNlIjoiY29yZSJ9.HHlbWMjo-Y__DGV0DAiCY7u85FuNtY8wpovcZ9ga-oCsLdM2H5iVSz1vKiWK8zxl7dSYltbnyTNMxXO2cDS81hr4ohycr7YYg5CaE5sA5id73ab5T145XEdF5X_HXoeczctGq7X3x9QYSn7O1fWJbPWcIrOCs6T2DrySsYgjgdAAnWnKedy_dYWJ0YtHY1bXH3Y7T126QqVlQ9ylHk6hmFMCtxMPbuAX4YBJsxwjWpMDpe13xbaU0Uqo5N47a2_vi0XzQ_tzH5esLeFDl236VqhHRTIRTKhPTtRbQmXXy1k-70AU1FJewVrQddxbzMXJLFclStIdG_vW1dWdqhh-hQ'

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
        self.assertEqual(list(update_response.data.keys()), self.user_update_get_self_keys)

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

    # def test_update_from_internal_service(self):
    #     client = APIClient()

    #     create_response = client.post('/users', {}, format='json')

    #     self.assertEqual(create_response.status_code, 201)

    #     client.credentials(HTTP_AUTHORIZATION=self.service_token)

    #     update_response = client.put('/users/' + str(create_response.data['id']),
    #                                  {'email': 'foo@yahoo.com'},
    #                                  format='json')

    #     self.assertEqual(update_response.status_code, 200)
    #     self.assertEqual(update_response.data['email'], 'foo@yahoo.com')
    #     self.assertEqual(list(update_response.data.keys()), self.user_update_get_self_keys)

    def test_list_users(self):
        client = APIClient()

        user1_response = client.post('/users', {}, format='json')
        user2_response = client.post('/users', {}, format='json')

        list_response = client.get('/users')

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list(list_response.data.keys()), ['count',
                                                           'next',
                                                           'previous',
                                                           'results'])
        self.assertEqual(len(list_response.data['results']), 2)
        self.assertEqual(list(list_response.data['results'][0].keys()), self.user_get_keys)
        self.assertEqual(list(list_response.data['results'][1].keys()), self.user_get_keys)

    def test_get_user(self):
        client = APIClient()

        user_create_response = client.post('/users', {}, format='json')

        self.assertEqual(user_create_response.status_code, 201)

        user_id_response = client.get('/users/' + str(user_create_response.data['id']))

        self.assertEqual(user_id_response.status_code, 200)
        self.assertEqual(list(user_id_response.data.keys()), self.user_get_keys)

        user_slug_response = client.get('/users/' + str(user_create_response.data['random_slugs'][0]))

        self.assertEqual(user_slug_response.status_code, 200)
        self.assertEqual(list(user_slug_response.data.keys()), self.user_get_keys)

    def test_get_user_self(self):
        client = APIClient()

        user_create_response = client.post('/users', {}, format='json')

        self.assertEqual(user_create_response.status_code, 201)

        token = 'Bearer ' + user_create_response.data['random_slugs'][0]

        client.credentials(HTTP_AUTHORIZATION=token)

        user_id_response = client.get('/users/' + str(user_create_response.data['id']))

        self.assertEqual(user_id_response.status_code, 200)
        self.assertEqual(list(user_id_response.data.keys()), self.user_update_get_self_keys)

        user_slug_response = client.get('/users/' + str(user_create_response.data['random_slugs'][0]))

        self.assertEqual(user_slug_response.status_code, 200)
        self.assertEqual(list(user_slug_response.data.keys()), self.user_update_get_self_keys)
