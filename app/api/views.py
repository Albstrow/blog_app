from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.models import Room
from .serializers import RoomSerializer

@api_view(['GET'])
def getRoutes(requeset):
    routes = [
        'GET /api'
        'GET /apirooms',
        'GET /api/rooms/:id'
    ]
    return Response(routes)

@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serialzer=RoomSerializer(rooms,many=True)
    return Response(serialzer.data)

@api_view(['GET'])
def getRoom(request,pk):
    room = Room.objects.get(id=pk)
    serialzer=RoomSerializer(room,many=False)
    return Response(serialzer.data)
