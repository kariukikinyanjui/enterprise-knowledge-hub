from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from tenants.models import Tenant, User
from rag.models import Document


class MultiTenantSecurityTests(APITestCase):
    def setUp(self):
        # Create two distinct tenants (departments)
        self.hr_tenant = Tenant.objects.create(name="Human Resources")
        self.it_tenant = Tenant.objects.create(name="Information Technology")

        # Create users assigned to those tenants
        self.hr_user = User.objects.create_user(
            username="hr_admin", password="password123", tenant=self.hr_tenant
        )
        self.it_user = User.objects.create_user(
            username="it_admin", password="password123", tenant=self.it_tenant
        )

        # Create a highly sensitive HR document
        self.hr_document = Document.objects.create(
            tenant=self.hr_tenant,
            title="Q3 Layoff Strategy.pdf",
            s3_key="hr/layoffs_q3.pdf"
        )

        self.document_url = reverse('document-list')

    def test_tenant_data_isolation(self):
        """
        SECURITY BOUNDARY: Prove that IT cannot see HR's documents.
        """
        # Authenticate as the IT user
        self.client.force_authenticate(user=self.it_user)

        # IT User requests the list of all documents
        response = self.client.get(self.document_url)

        # Assert that the request was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert that the sensitive HR document is completely invisible to IT
        self.assertEqual(len(response.data['results']), 0)

    def test_tenant_data_access(self):
        """
        Prove that HR can successfully see their own documents.
        """
        # Authenticate as the HR user
        self.client.force_authenticate(user=self.hr_user)

        response = self.client.get(self.document_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], "Q3 Layoff Strategy.pdf")
