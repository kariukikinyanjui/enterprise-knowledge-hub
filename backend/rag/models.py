import uuid
from django.db import models
from pgvector.django import VectorField
from tenants.models import Tenant


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    s3_key = models.CharField(max_length=1024, help_text="Path to the raw PDF in S3")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.tenant.name}] {self.title}"


class DocumentChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Why link tenant here again? Performance. It allows us to filter chunks by tenant
    # without doing a costly SQL JOIN through the Document table during vector search.
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='document_chunks')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')

    content = models.TextField(help_text="The actual text chunk extracted from the document")
    chunk_index = models.IntegerField(help_text="The order of this chunk in the document")

    # The VectorField stores our embeddings.
    embedding = VectorField(dimensions=384)

    def __str__(self):
        return f"Chunk {self.chunk_index} of {self.document.title}"
