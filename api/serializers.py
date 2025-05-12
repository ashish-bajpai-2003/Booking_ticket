from rest_framework import serializers
from .models import CustomUser , Ticket, Train, Stoppage

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser 
        fields = ['id', 'username', 'email', 'password', 'is_owner']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(  
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_owner=validated_data.get('is_owner', False),  
        )
        return user
    
class TicketSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(required=False, allow_null=True)
    departure_date = serializers.DateField(required=True)
    seat_number = serializers.CharField(required=False, allow_null=True)
    class Meta:
        model = Ticket
        fields = '__all__'
        extra_kwargs = {
            'pnr_number': {'required': False}  
        }
        read_only_fields = ['user', 'available_seats', 'de']


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = '__all__'


class StoppageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stoppage
        fields = '__all__'
