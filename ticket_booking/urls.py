from django.contrib import admin
from django.urls import path, include
from api.views import UserRegistrationView, UserListView, BookTicketView, CancelTicketView, TicketStatusView, SearchTrainView, ORMExamplesView, PantryItemViewSet, BookingPantryViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'pantry-items', PantryItemViewSet)
router.register(r'booking-pantry', BookingPantryViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', UserListView.as_view(), name='user-view'),
    path('book/', BookTicketView.as_view()),
    path('cancel/<int:ticket_id>/', CancelTicketView.as_view(), name='cancel-ticket'),
    path('ticket/status/<str:pnr_number>/', TicketStatusView.as_view(), name='ticket-status'),
    path('search-trains/', SearchTrainView.as_view(), name='search-trains'),
    path('perform-orm/', ORMExamplesView.as_view()),
    path('api/', include(router.urls)),
]
   
