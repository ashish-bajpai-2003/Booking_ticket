from rest_framework import serializers
from .models import CustomUser , Ticket, Train

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
    age = serializers.IntegerField(min_value=5, max_value=100)
    departure_date = serializers.DateField(required=True)
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['user','seat_number', 'status', 'pnr_number', 'available_seats']


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = '__all__'
