from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import VirtualAccount
from .models import Stock

class LikedStockListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        account = VirtualAccount.objects.get(user=request.user)
        liked = account.liked_stocks.all()
        data = [{"code": s.code, "name": s.name} for s in liked]
        return Response(data)