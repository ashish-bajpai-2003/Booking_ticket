from rest_framework import serializers
from .models import CustomUser , Ticket, Train

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser 
        fields = ['id', 'username', 'email', 'password', 'is_owner', 'role']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(  
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_owner=validated_data.get('is_owner', False), 
            role = validated_data.get('role'), 
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
        

from .models import  PantryItem, BookingPantry

class PantryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PantryItem
        fields = ['id', 'name', 'price']

class BookingPantrySerializer(serializers.ModelSerializer):
    item = serializers.CharField()  # Accept and return item name
    price = serializers.DecimalField(source='item_obj.price', read_only=True, max_digits=7, decimal_places=2)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = BookingPantry
        fields = ['id', 'booking', 'item', 'price', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()

    def validate(self, data):
        booking = data.get('booking')
        if booking and not booking.wants_pantry:
            raise serializers.ValidationError("Cannot order pantry items. This booking has not opted for pantry.")
        return data

    def create(self, validated_data):
        item_name = validated_data.pop('item')
        try:
            item_obj = PantryItem.objects.get(name__iexact=item_name)
        except PantryItem.DoesNotExist:
            raise serializers.ValidationError({'item': f"Pantry item '{item_name}' not found."})
        validated_data['item'] = item_obj
        return BookingPantry.objects.create(**validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['item'] = instance.item.name  # Show item name in response
        return rep