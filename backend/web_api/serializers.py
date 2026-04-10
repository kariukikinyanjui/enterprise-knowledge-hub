from rest_framework import serializers
from rag.models import Document


class DocumentSerializer(serializers.ModelSeiralizer):
    class Meta:
        model = Document
        fields = ['id', 'title', 's3_key', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']



class ChatQuerySerializer(serializers.Serializer):
    """
    Validates incoming user questions before they hit the LLM.
    """
    query = serializers.CharField(
        max_length=2000,
        help_text="The natural language question from the user."
    )
