from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from rag.models import Document
from .serializers import DocumentSerializer, ChatQuerySerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """
    Handles uploading and listing tenant-specific documents.
    """
    serializzer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    # Accept file uploads (PDFs)
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """
        SECURITY BOUNDARY: Force query scoping to the user's tenant.
        This prevents cross-tenant data spillage.
        """
        user = self.request.user
        if not user.tenant:
            return Document.objects.none()
        return Document.objects.filter(tenant=user.tenant).order_by('-uploaded_at')

    def perform_create(self, serializer):
        """
        Inject the tenant ID automatically upon creation.
        """
        document = serializer.save(tenant=self.request.user.tenant)

        # TODO: Trigger the RAG Extension Service here.

        return document


class ChatAPIView(APIView):
    """
    The main orchestration endpoint for Retrieval_Augmented Generation.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChatQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_query = serializer.validated_data['query']
        tenant = request.user.tenant

        if not tenant:
            return Response(
                {"error": "User is not assigned to a tenant."},
                status=status.HTTP_403_FORBIDDEN
            )

            # TODO: Trigger the RAG Generation Service here.
            # Embed user_query
            # Vector search pgvector for tenant's DocumentChunks
            # Call Amazon Bedrock with prompt + context

            mock_response = {
                "answer": f"This is a mock AI response to: '{user_query}'",
                "sources": []
            }

            return Response(mock_response, status=status.HTTP_200_OK)
