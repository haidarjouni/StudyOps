from rest_framework import serializers

from subject.models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = (
            "id",
            "user",
            "name",
            "code",
            "semester",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "created_at",
            "updated_at",
        )
        
    def validate_code(self, code):
        request = self.context["request"]
        queryset = Subject.objects.filter(user=request.user, code=code)
        
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "You already have a subject with this code."
            )
            
        return code.upper()  # Convert the code to uppercase before saving
        