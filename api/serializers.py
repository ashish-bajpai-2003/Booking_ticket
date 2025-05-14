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
    age = serializers.IntegerField(required=False, allow_null=True)
    # departure_date = serializers.DateField(required=True)
    # departure_time = serializers.TimeField(required=True)
    seat_number = serializers.CharField(required=False, allow_null=True)
    class Meta:
        model = Ticket
        fields = '__all__'
        extra_kwargs = {
            'pnr_number': {'required': False}  
        }
        read_only_fields = ['user', 'available_seats']




class TrainSerializer(serializers.ModelSerializer):
    train_name = serializers.SerializerMethodField()
    class Meta:
        model = Train
        fields = '__all__'
        # read_only_fields = ["train_name"]

    def get_train_name(self, obj):
        try:
            train = Train.objects.get(train_number=obj.train_number)
            return train.train_name
        except Train.DoesNotExist:
            return None