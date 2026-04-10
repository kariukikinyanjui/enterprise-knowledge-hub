from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from rag.models import Document
from rag.services import IngestionService, ChatOrchestrationService
from .serializers import DocumentSerializer, ChatQuerySerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """
    Handles uploading and listing tenant-specific documents.
    """
    serializzer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    # Accept file uploads (PDFs)
    parser_classes = [MultiPartParser, FormParser]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

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

        # Trigger the Ingestion Service
        uploaded_file = self.request.FILES.get('file')
        if uploaded_file:
            ingestion_service = IngestionService()
            ingestion_service.process_document(document, uploaded_file)

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

            # Execute the Chat Orchestration Service
            chat_service = ChatOrchestrationService()
            response_data = chat_service.answer_query(user_query, tenant)

            return Response(response_data, status=status.HTTP_200_OK)
