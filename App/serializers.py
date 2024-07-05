from rest_framework import serializers
from .models import User, Organisation


class RegisterUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
 
class OrganisationSerializers(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = Organisation
        fields = ['org_id', 'name', 'description', 'user']
    def get_user(self, obj):
        return [user.name for user in obj.user.all()]