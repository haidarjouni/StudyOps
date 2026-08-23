from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from subject.models import Subject
User = get_user_model()
class SubjectViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.subject = Subject.objects.create(
            user=self.user,
            name="Computer Science",
            code="CS101",
            semester=1,
        )
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        self.subject2= Subject.objects.create(
            user=self.user2,
            name="Physics",
            code="PH101",
            semester=1,
        )
    def test_subject_list_view(self):
        response = self.client.get(reverse('subject-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.subject.name)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Subject.objects.filter(user=self.user).count(), 1)
        
    def test_subject_create_view(self):
        data = {
            "name": "Mathematics",
            "code": "MATH101",
            "semester": 1,
        }
        response = self.client.post(reverse('subject-list'), data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Subject.objects.filter(user=self.user).count(), 2)
        subject = Subject.objects.get(name="Mathematics")
        self.assertEqual(subject.user, self.user)
        
    def test_anonymous_user_cannot_list_subjects(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(reverse("subject-list"))

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
    
    def test_delete_subject(self):
        response = self.client.delete(reverse('subject-detail', args=[self.subject.id]))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Subject.objects.filter(user=self.user).count(), 0)
        
    def test_update_subject(self):
        data = {
            "name": "Updated Computer Science",
            "code": "CS102",
            "semester": 2,
        }
        subject_id = self.subject.id
        response = self.client.put(reverse('subject-detail', args=[subject_id]), data)
        self.assertEqual(response.status_code, 200)
        updated_subject = Subject.objects.get(id=subject_id)
        self.assertEqual(updated_subject.name, "Updated Computer Science")
        self.assertEqual(updated_subject.code, "CS102")
        self.assertEqual(updated_subject.semester, 2)
        self.assertEqual(updated_subject.user, self.user)
    
    def test_updating_subject_of_another_user(self):
        self.client.force_authenticate(user=self.user2)
        data = {
            "name": "Updated Computer Science",
            "code": "CS102",
            "semester": 2,
        }
        subject_id = self.subject.id
        response = self.client.put(reverse('subject-detail', args=[subject_id]), data)
        self.assertEqual(response.status_code, 404)
        
    def test_retrieving_subject_of_another_user(self):
        self.client.force_authenticate(user=self.user2)
        subject_id = self.subject.id
        response = self.client.get(reverse('subject-detail', args=[subject_id]))
        self.assertEqual(response.status_code, 404)
    
    def test_deleting_subject_of_another_user(self):
        self.client.force_authenticate(user=self.user2)
        subject_id = self.subject.id
        response = self.client.delete(reverse('subject-detail', args=[subject_id]))
        self.assertEqual(response.status_code, 404)
    