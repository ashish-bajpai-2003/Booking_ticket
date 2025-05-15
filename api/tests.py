from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from datetime import date
User = get_user_model()

# class UserRegistrationTest(APITestCase):
#     def test_user_registration(self):
#         data = {
#             # "username": "naman",
#             "password": "123",
#             "email": "naman@gmail.com"
#         }
#         response = self.client.post("/register/", data, format="json")
#         data1 = response.json()
#         self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        # print(response.__dict__)

        # assert response.status_code == status.HTTP_201_CREATED


    # def test_registration_with_invalid_data(self):
    #     data = {"username": "", "password": "abc", "email" : "naman@.com"}
    #     response = self.client.post("/register/", data)
    #     assert response.status_code == status.HTTP_400_BAD_REQUEST


class UserLoginTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="naman", password="2341")

    def test_user_login(self):
        data = {
            "username": "naman",
            "password": "2341"
        }

        # 👇 Define headers
        headers = {
            "Content-Type": "application/json", 
            "Authorization" : "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ3MzkyMTU2LCJpYXQiOjE3NDczMDU3NTYsImp0aSI6IjliZDdhNTQyNjhlODRkMzk5YmQwYTdmOTc3MDk1ZjViIiwidXNlcl9pZCI6M30.unA915CUbR664gUacpscajlpG7zDlDEEQqhEeqtHb-s"
        }

        # 👇 Pass headers using HTTP_ prefix (Django-style headers)
        response = self.client.post(
        "/login/",
        data,
        format="json",
        headers = headers
)
        assert response.status_code == status.HTTP_200_OK
#     def test_login_with_invalid_data(self):
#         data = {
#             "username" : "naman",
#             "password" : ""
#         }
#         response = self.client.post("/login/", data)
#         assert response.status_code == status.HTTP_400_BAD_REQUEST


# class UserCanBookTicketTest(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username="Ashish", password="1234", is_role="NORMAL")
#         self.client.force_authenticate(user=self.user) 
#     def test_book_ticket(self):
#         data = {
#             "train_number": "12520",   
#             "seat_class": "3AC",
#             "number_of_seats": 1,
#             "source": "New Delhi",
#             "destination": "Kanpur",
#             "departure_date": "2025-05-17",
#             "passengers": [
#                 {"name": "Ashish", "age": 21}
#             ]
#         }
#         response = self.client.post("/book/", data, format="json")
#         assert response.status_code == status.HTTP_201_CREATED

#     def test_book_with_invalid_data(self):
#         data = {
#             "train_number"  : "12520",
#             "seat_class" : "",
#             "number_of_seats" : 1,
#             "source" : "",
#             "destination" : "Kanpur",
#             "departure_date" : "2025-05-17",
#             "passengers" : [
#                 {"name" : "Ashish", "age" : 21}
#             ]
#         }
#         response = self.client.post("/book/", data, format="json")
#         print("Status code:", response.status_code)
#         print("Response data:", response.data)
#         assert response.status_code == status.HTTP_400_BAD_REQUEST


# class TrainSearchTest(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username="Ashish", password="1234")
#         self.client.force_authenticate(user=self.user)

#     def test_search_train_test(self):
#         data = {
#             "source" : "New delhi",
#             "destination" : "Banaras",
#             "date" : date.today().isoformat()
#         }
#         response = self.client.post("/search-trains/", data)
#         assert response.status_code == status.HTTP_200_OK

#     def test_search_with_invalid_data(self):
#         data = {
#             "source" : "",
#             "destination" : "",
#             "date" : ""
#         }
#         response = self.client.post("/search-trains/", data)
#         assert response.status_code == status.HTTP_404_NOT_FOUND
