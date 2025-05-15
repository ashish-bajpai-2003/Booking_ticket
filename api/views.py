from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from datetime import date
from django.shortcuts import get_object_or_404
from .models import Ticket, CustomUser, Train
from rest_framework.views import APIView
from .serializers import UserSerializer, TicketSerializer, TrainSerializer
from rest_framework.permissions import IsAuthenticated
from .permission import IsOwnerOnlyCanViewUsers
from .decorators import admin_required, normal_user_required


class UserRegistrationView(APIView):   #   user can Register here. 
    
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": "Invalid Payload!!!"}, status=status.HTTP_400_BAD_REQUEST)

class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOnlyCanViewUsers]   # Check the user is authenticated or not. 

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
from .models import generate_pnr
def calculate_partial_fare(train, source, destination, seat_class):
    # Fetching source and destination distances
    if source == train.source:
        from_dist = 0
    else:
        from_dist = next((s['distance'] for s in train.stoppages if s['station'] == source), None)

    if destination == train.destination:
        to_dist = train.distance
    else:
        to_dist = next((s['distance'] for s in train.stoppages if s['station'] == destination), None)

    # Ensure valid distance ranges
    if from_dist is None or to_dist is None or from_dist >= to_dist:
        return None

    km = to_dist - from_dist

    # Base fare per km rates for different seat classes
    base_fare_per_km = {
        '1AC': 5,
        '2AC': 2.5,
        '3AC': 1.8,
        'sleeper': 1.5,
    }

    # Train type multipliers
    train_type_multiplier = {
        'Vande Bharat': 2.5,
        'Rajdhani': 1.4,
        'Express': 1.2,
        'Superfast': 1.3
    }

    # Train type mapping (if payload has train number, map to train type)
    train_type_mapping = {
        "12520": "Vande Bharat",  # Here you can add other train numbers and their types
    }

    # Get train type from mapping (based on train_number)
    train_type = train_type_mapping.get(train.train_number, "Unknown")

    # Fetch multiplier for the train type
    multiplier = train_type_multiplier.get(train_type, 1)

    print(f"Train Type: {train_type}, Multiplier: {multiplier}")  # Debugging line
    print(f"Base Fare per km for {seat_class}: {base_fare_per_km.get(seat_class, 'Not Found')}")  # Debugging line
    
    # Fare calculation with multiplier
    fare = km * base_fare_per_km.get(seat_class, 1) * multiplier
    print(f"Fare Calculation: {fare}")  # Debugging line
    
    return fare



 



class BookTicketView(APIView):      #   User can book the ticket. 
    @normal_user_required       #   Check user authentication.
    # permission_classes = [IsAuthenticated]

    def post(self, request):

        if request.user.is_owner:      #   Check the type of user. 
            return Response({"error": "Only normal users can book tickets."}, status=status.HTTP_403_FORBIDDEN)

        train_number = request.data.get('train_number')      # Pass the train number.
        departure_date = request.data.get('departure_date')    # Pass the departure date.
        seat_class = request.data.get('seat_class')     # Pass the seat_class in which you want to travel(Like= 'Sleeper)
        number_of_seats = request.data.get('number_of_seats')   ## Pass the number of seats that you want to book.
        source = request.data.get('source')   ## Pass the Source station
        destination = request.data.get('destination')   # Pass the destination
        passengers = request.data.get('passengers', [])   # Pass the passenger name and his age here. 

        if not all([train_number, departure_date, seat_class, number_of_seats, source, destination]):
            return Response({"error": "Train number, departure date, seat class, number of seats, source and destination are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            number_of_seats = int(number_of_seats)
            if number_of_seats <= 0 or number_of_seats > 6:
                return Response({"error": "You can book between 1 to 6 seats only."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Number of seats must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        if len(passengers) != number_of_seats:
            return Response({"error": "Please provide name and age for each passenger."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            departure_date_obj = date.fromisoformat(departure_date)
            if departure_date_obj < date.today():
                return Response({"error": "You cannot book tickets for a past date."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Invalid departure date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            train = Train.objects.get(train_number=train_number)
        except Train.DoesNotExist:
            return Response({"error": "Train not found for the given number."}, status=status.HTTP_404_NOT_FOUND)

        if seat_class not in train.seat_info_array:
            return Response({"error": f"{seat_class} is not available for this train."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate fare per seat based on partial distance
        fare_per_seat = calculate_partial_fare(train, source, destination, seat_class)
        if fare_per_seat is None:
            return Response({"error": "Invalid source or destination station."}, status=status.HTTP_400_BAD_REQUEST)

        booked_tickets = Ticket.objects.filter(
            train_number=train_number,
            departure_date=departure_date,
            seat_class=seat_class,
            status='booked'
        )
        booked_count = booked_tickets.count()
        class_capacity = train.total_seats // len(train.seat_info_array)
        available_count = class_capacity - booked_count

        booked_seats_list = []      
        status_value = 'booked'

        if available_count >= number_of_seats:
            assigned_seats = set(booked_tickets.values_list('seat_number', flat=True))
            next_seat = 1
            while len(booked_seats_list) < number_of_seats:
                seat_label = f"{seat_class}-{next_seat}"
                if seat_label not in assigned_seats:
                    booked_seats_list.append(seat_label)
                next_seat += 1
        else:
            status_value = 'waiting'
            booked_seats_list = [None] * number_of_seats
            train.available_seats -= number_of_seats  # even for waiting
            train.save()

        group_pnr = generate_pnr()
        created_tickets = []

        for i, seat in enumerate(booked_seats_list):
            passenger_info = passengers[i]
            name = passenger_info.get('name')
            age = passenger_info.get('age')

            if not name or age is None:
                return Response({"error": "Each passenger must have a name and age."}, status=status.HTTP_400_BAD_REQUEST)

            total_fare = fare_per_seat  # Fare is per passenger now

            ## All the data of user's Ticket.
            ticket_data = {
                'user': request.user.id,
                'train_number': train_number,
                'departure_date': departure_date,
                'seat_class': seat_class,
                'seat_number': seat,
                'status': status_value,
                'event_name': f"Train {train_number} Ride",
                'source': source,
                'destination': destination,
                'number_of_seats': 1,
                'age': age,
                'name': name,
                'pnr_number': group_pnr,
                'fare': total_fare
            }

            serializer = TicketSerializer(data=ticket_data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                created_tickets.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if status_value == 'booked':
            train.booked_seats = (train.booked_seats or 0) + number_of_seats
            train.available_seats = (train.available_seats or train.total_seats) - number_of_seats
            train.save()

        return Response({
            "message": f"{len(created_tickets)} ticket(s) {'booked' if status_value == 'booked' else 'added to waiting list'} successfully.",
            "pnr": group_pnr,
            "tickets": created_tickets,
            "fare_per_passenger": fare_per_seat,
            "total_fare": fare_per_seat * number_of_seats
        }, status=status.HTTP_201_CREATED)
    
import logging
from django.db import transaction
logger = logging.getLogger(__name__)


###    User can cancel the ticket.
class CancelTicketView(APIView):
    @normal_user_required     # when user already loggedin.
    # permission_classes = [IsAuthenticated]

    def patch(self, request, ticket_id):
        # Start a transaction to ensure all operations are atomic
        with transaction.atomic():
            # Get the ticket that needs to be cancelled
            ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

            # Check if the ticket is already cancelled
            if ticket.status == 'cancelled':
                logger.info(f"User {request.user.username} tried to cancel an already cancelled ticket (Ticket ID: {ticket_id})")
                return Response({'message': 'Ticket already cancelled.'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the associated train for this ticket
            train = get_object_or_404(Train, train_number=ticket.train_number, departure_date=ticket.departure_date)

            # Cancel the current ticket
            ticket.status = 'cancelled'
            ticket.save()
            logger.info(f"User {request.user.username} cancelled ticket successfully (Ticket ID: {ticket_id})")

            # Update the booked seats and available seats in Train table
            train.booked_seats -= ticket.number_of_seats  # Decrease booked seats by the number of seats
            train.available_seats += ticket.number_of_seats  # Increase available seats by the number of seats
            train.save()

            logger.info(f"Updated Train {train.train_number}: Booked Seats: {train.booked_seats}, Available Seats: {train.available_seats}")

            # Check for the first waiting ticket and confirm it if there are any
            waiting_ticket = Ticket.objects.filter(status='waiting', train_number=ticket.train_number, departure_date=ticket.departure_date).first()

            if waiting_ticket:
                # Confirm the waiting ticket
                waiting_ticket.status = 'booked'
                waiting_ticket.save()

                # Update the train seat availability again for the confirmed waiting ticket
                train.booked_seats += waiting_ticket.number_of_seats  # Increase booked seats for confirmed waiting ticket
                train.available_seats -= waiting_ticket.number_of_seats  # Decrease available seats for confirmed waiting ticket
                train.save()

                logger.info(f"Waiting ticket with Ticket ID: {waiting_ticket.id} is now confirmed due to cancellation of Ticket ID: {ticket_id}")

            return Response({'message': 'Ticket cancelled successfully and waiting ticket confirmed if any.'}, status=status.HTTP_200_OK)


class TicketStatusView(APIView):  # Check the status of your ticket.
    # permission_classes = [IsAuthenticated]

    def get(self, request, pnr_number):
        try:
            ticket = Ticket.objects.get(pnr_number=pnr_number)
            serializer = TicketSerializer(ticket)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return Response({'error': 'Ticket not found or unauthorized.'}, status=status.HTTP_404_NOT_FOUND)




from datetime import date as today_date
from rest_framework.response import Response  # Isko import karna na bhulo

from datetime import date as today_date     # import Today Date
from django.db.models import Q
class SearchTrainView(APIView):   #   User can Search the train.
    def get(self, request):
        # Get parameters from the request
        source = request.query_params.get('source')   #   pass the Origin Station.
        destination = request.query_params.get('destination')   #   pass the your destination here. 
        train_number = request.query_params.get('train_number')  #    pass the train number.
        train_name = request.query_params.get('train_name')      #     pass the train name
        date = request.query_params.get('date') or today_date.today().isoformat()   # pass the journey date

        # Get all trains by default
        trains = Train.objects.all()

        # Filter trains based on train_number, if provided
        if train_number:
            trains = trains.filter(train_number__iexact=train_number)
        
        # Filter trains based on train_name, if provided
        if train_name:
            trains = trains.filter(train_name__icontains=train_name)

        # Filter trains based on source and destination
        if source and destination:
            trains = trains.filter(
                departure_date=date
            ).filter(
                Q(source__iexact=source) | Q(stoppages__station__iexact=source),
                Q(destination__iexact=destination) | Q(stoppages__station__iexact=destination)
            ).distinct()

        # If trains exist, serialize and return data
        if trains.exists():
            train_data = []
            for train in trains:
                # Check if the train has running days
                if train.running_days:
                    run_days = ", ".join(train.running_days)
                else:
                    run_days = "Daily"

                # Serialize the train data and add the running days information
                train_info = TrainSerializer(train).data
                train_info["running_days"] = run_days  # Add running_days info
                train_data.append(train_info)

            return Response(train_data)
        else:
            return Response({"error": "No trains found"}, status=404)


    # @admin_required
    # def post(self, request):
    
    #     # Admin-only POST request to add a new train
    #     # if not request.user.is_staff:
    #     #     return Response({"error": "Only admin can add train"}, status=403)

    #     # serializer = TrainSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=201)
    #     return Response(serializer.errors, status=400)
    
    @admin_required
    def post(self, request):
    # Train data ko serialize karna
        serializer = TrainSerializer(data=request.data)
    
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    










# # views.py
from django.db.models import Count, Q, Avg, Max
class ORMExamplesView(APIView):
    def get(self, request):
        data = {}
 
        # Retrieve all tickets with 'booked' status
        data['filter_tickets'] = list(Ticket.objects.filter(status='booked').values('pnr_number', 'status', 'fare', 'train_number'))

        # Retrieve all 'Vande Bharat' trains
        data['filter_trains'] = list(Train.objects.filter(train_type='Vande Bharat').values('train_name', 'train_number'))

        # Calculate the average fare of all tickets
        data['avg_fare'] = Ticket.objects.aggregate(avg_fare=Avg('fare'))

        # Find the maximum fare from all tickets
        data['max_fare'] = Ticket.objects.aggregate(max_fare=Max('fare'))

        # Tickets that are either 'booked' or 'waiting'
        data['q_tickets'] = list(
            Ticket.objects.filter(Q(status='booked') | Q(status='waiting')).values('pnr_number', 'status', 'fare')
        )

        # Trains that go from 'New Delhi' to 'Kanpur'
        data['q_trains'] = list(
            Train.objects.filter(Q(source='New Delhi') & Q(destination='Kanpur')).values('train_name', 'train_number')
        )

        # 5. select_related / prefetch_related
        # For Ticket with related user data (using select_related to optimize ForeignKey lookup)
        data['select_related_ticket'] = list(
            Ticket.objects.select_related('user').all().values('user__username', 'pnr_number', 'status')[:5]
        )

        # For Prefetching related tickets for each CustomUser (using prefetch_related for reverse relation)
        data['prefetch_related_user'] = list(
            CustomUser.objects.prefetch_related('ticket_set').annotate(ticket_count=Count('ticket')).values('username', 'ticket_count')[:5]
        )

        return Response(data)
 