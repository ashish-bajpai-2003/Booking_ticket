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


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOnlyCanViewUsers]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
from .models import generate_pnr
class BookTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_owner:
            return Response({"error": "Only normal users can book tickets."}, status=status.HTTP_403_FORBIDDEN)

        train_number = request.data.get('train_number')
        departure_date = request.data.get('departure_date')
        seat_class = request.data.get('seat_class')
        number_of_seats = request.data.get('number_of_seats')
        passengers = request.data.get('passengers', [])

        if not all([train_number, departure_date, seat_class, number_of_seats]):
            return Response({"error": "Train number, departure date, seat class and number of seats are required."}, status=status.HTTP_400_BAD_REQUEST)

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
            train = Train.objects.get(train_number=train_number, departure_date=departure_date)
        except Train.DoesNotExist:
            return Response({"error": "Train not found for the given date."}, status=status.HTTP_404_NOT_FOUND)

        if seat_class not in train.seat_info_array:
            return Response({"error": f"{seat_class} is not available for this train."}, status=status.HTTP_400_BAD_REQUEST)

        # Check booked seats in the class
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
            train.available_seats -= number_of_seats  # This will go negative for waiting list
            train.save()

        # Generate a single PNR for this group booking
        group_pnr = generate_pnr()

        created_tickets = []
        for i, seat in enumerate(booked_seats_list):
            passenger_info = passengers[i]
            name = passenger_info.get('name')
            age = passenger_info.get('age')

            if not name or age is None:
                return Response({"error": "Each passenger must have a name and age."}, status=status.HTTP_400_BAD_REQUEST)

            ticket_data = {
                'user': request.user.id,
                'train_number': train_number,
                'departure_date': departure_date,
                'seat_class': seat_class,
                'seat_number': seat,
                'status': status_value,
                'event_name': f"Train {train_number} Ride",
                'source': train.source,
                'destination': train.destination,
                'number_of_seats': 1,
                'age': age,
                'name': name,
                'pnr_number': group_pnr
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
            "tickets": created_tickets
        }, status=status.HTTP_201_CREATED)
    
import logging
from django.db import transaction
logger = logging.getLogger(__name__)

class CancelTicketView(APIView):
    permission_classes = [IsAuthenticated]

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


class TicketStatusView(APIView):
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

from datetime import date as today_date
class SearchTrainView(APIView):
    def get(self, request):
        source = request.query_params.get('source')
        destination = request.query_params.get('destination')
        train_number = request.query_params.get('train_number')
        date = request.query_params.get('date')

        if train_number:  # If train_number is provided, we ignore date
            trains = Train.objects.filter(train_number=train_number)

        else:
            if not all([source, destination]):
                return Response({"error": "Please provide source and destination"}, status=400)

            # Default date = today
            if not date:
                date = today_date.today().isoformat()  

            trains = Train.objects.filter(
                source__iexact=source,
                destination__iexact=destination,
                departure_date=date
            )

        # If trains are found, return them, otherwise show error message
        if trains.exists():
            serializer = TrainSerializer(trains, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No trains found"}, status=404)




        # Admin POST request — add train
    def post(self, request):
        if not request.user.is_staff:
            return Response({"error": "Only admin can add train"}, status=403)

        serializer = TrainSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)