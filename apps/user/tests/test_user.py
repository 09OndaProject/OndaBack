# from django.contrib.auth import get_user_model
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from rest_framework_simplejwt.tokens import RefreshToken
#
# User = get_user_model()
#
#
# class UserAuthTests(APITestCase):
#     def setUp(self):
#         self.email = "test@example.com"
#         self.password = "Testpass123!"
#         self.user = User.objects.create_user(email=self.email, password=self.password)
#         self.user.is_active = True
#         self.user.save()
#
#     def get_tokens_for_user(self):
#         refresh = RefreshToken.for_user(self.user)
#         return str(refresh), str(refresh.access_token)
#
#     def test_register_user(self):
#         url = reverse("signup")  # name 설정 필요
#         data = {
#             "email": "newuser@example.com",
#             "password": "Newpass123!",
#             "password2": "Newpass123!",
#             "nickname": "newbie",
#         }
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertIn("verify_url", response.data)
#
#     def test_login_success(self):
#         url = reverse("token_login")  # SimpleJWT default
#         data = {"email": self.email, "password": self.password}
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("access_token", response.data)
#         self.assertIn("csrf_token", response.data)
#
#     def test_login_fail(self):
#         url = reverse("token_login")
#         data = {"email": self.email, "password": "wrongpass"}
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#
#     def test_refresh_token(self):
#         refresh_token, _ = self.get_tokens_for_user()
#         self.client.cookies["refresh_token"] = refresh_token
#         url = reverse("token_refresh")  # name 설정 필요
#         response = self.client.post(url, HTTP_X_CSRFTOKEN="test-csrf")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("access_token", response.data)
#
#     def test_logout(self):
#         refresh_token, _ = self.get_tokens_for_user()
#         self.client.cookies["refresh_token"] = refresh_token
#         url = reverse("token_logout")  # name 설정 필요
#         self.client.force_authenticate(user=self.user)
#         response = self.client.post(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#     def test_password_check(self):
#         url = reverse("password_check")  # name 설정 필요
#         self.client.force_authenticate(user=self.user)
#         response = self.client.post(url, {"password": self.password})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTrue(response.data["matched"])
#
#     def test_profile_retrieve(self):
#         url = reverse("profile")  # name 설정 필요
#         self.client.force_authenticate(user=self.user)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("message", response.data)
#
#     def test_profile_update(self):
#         url = reverse("profile")
#         self.client.force_authenticate(user=self.user)
#         response = self.client.patch(url, {"nickname": "updated"})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["nickname"], "updated")
#
#     def test_profile_delete(self):
#         url = reverse("profile")
#         self.client.force_authenticate(user=self.user)
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
