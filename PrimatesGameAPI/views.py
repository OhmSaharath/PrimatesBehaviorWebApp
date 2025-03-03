
from django.shortcuts import render
from rest_framework import generics
from .models import RPiBoards, RPiStates, Primates, Games, GameInstances ,GameConfig, FixationGameConfig , Reports , FixationGameReport ,  FixationGameResult
from .permissions import IsResearcher , IsRPiClient , IsAdmin ,  IsResearcherOrAdmin 
from rest_framework.permissions import IsAuthenticated , AllowAny 
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User, Group
from .serializers import PrimatesSerializer , UserSerializer , UserNamePOSTSerializer , RPiBoardsSerializer , RPiStatesSerializer , GamesSerializer , GamesInstancesSerializer, GameConfigSerializer, FixationGameConfigSerializer, ReportsSerializer, FixationGameReportSerializer, FixationGameResultSerializer

# Create your views here.

# Primates views
class PrimatesView(generics.ListCreateAPIView):
    queryset = Primates.objects.all()
    serializer_class = PrimatesSerializer
    # Define permission classes for different methods
    def get_permissions(self):
        if self.request.method == 'GET':
            # Return permission classes for GET request
            return [AllowAny()]
        elif self.request.method == 'POST':
            # Return permission classes for POST request
            return [IsResearcherOrAdmin()]
        return super().get_permissions()

class SinglePrimatesView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Primates.objects.all()
    serializer_class = PrimatesSerializer
    # Define permission classes for different methods
    def get_permissions(self):
        if self.request.method == 'GET':
            # Return permission classes for GET request
            return [AllowAny()]
        elif self.request.method == 'PUT' or self.request.method == 'PATCH' or self.request.method == 'DELETE':
            # Return permission classes for POST request
            return [IsResearcherOrAdmin()]
        return super().get_permissions()
    
    
# RPi views

class RPiBoradsView(generics.ListCreateAPIView):
    queryset = RPiBoards.objects.all()
    serializer_class = RPiBoardsSerializer
    # Define permission classes for different methods
    def get_permissions(self):
        if self.request.method == 'GET':
            # Return permission classes for GET request
            return [AllowAny()]
        elif self.request.method == 'POST':
            # Return permission classes for POST request
            return [IsResearcherOrAdmin()]
        return super().get_permissions()

class SingleRPiBoardView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RPiBoards.objects.all()
    serializer_class = RPiBoardsSerializer
    # Define permission classes for different methods
    def get_permissions(self):
        if self.request.method == 'GET':
            # Return permission classes for GET request
            return [AllowAny()]
        elif self.request.method == 'PUT' or self.request.method == 'PATCH' or self.request.method == 'DELETE':
            # Return permission classes for POST request
            return [IsAuthenticated()]
        return super().get_permissions()
    
class RPiStatesView(generics.ListCreateAPIView):
    queryset = RPiStates.objects.all()
    serializer_class = RPiStatesSerializer
    permission_classes = (IsAuthenticated|IsAdmin|IsResearcher,)
    
class SingleRPiStateViews(generics.RetrieveUpdateDestroyAPIView):
    queryset = RPiStates.objects.all()
    serializer_class = RPiStatesSerializer
    permission_classes = (IsAuthenticated|IsAdmin|IsResearcher|IsRPiClient,)
    
class GamesView(generics.ListCreateAPIView):
    queryset = Games.objects.all()
    serializer_class = GamesSerializer
    permission_classes = (IsAuthenticated|IsAdmin|IsResearcher,)

class SingleGameView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Games.objects.all()
    serializer_class = GamesSerializer
    permission_classes = (IsAuthenticated|IsAdmin|IsResearcher,)
    
class GameInstancesView(generics.ListCreateAPIView):
    queryset = GameInstances.objects.all()
    serializer_class = GamesInstancesSerializer
    permission_classes = (IsAuthenticated|IsAdmin|IsResearcher,)

class SingleGameInstanceView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GameInstances.objects.all()
    serializer_class = GamesInstancesSerializer
    permission_classes = (IsAuthenticated|IsAdmin|IsResearcher|IsRPiClient,)
    
class GameConfigView(generics.ListCreateAPIView):
    queryset = GameConfig.objects.all()
    serializer_class = GameConfigSerializer
    permission_classes = (IsAuthenticated|IsAdmin|IsResearcher,)
class SingleGameConfigView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GameConfig.objects.all()
    serializer_class = GameConfigSerializer
    permission_classes = (IsAuthenticated|IsAdmin|IsResearcher,)
    
class FixationGameConfigView(generics.ListCreateAPIView):
    queryset = FixationGameConfig.objects.all()
    serializer_class = FixationGameConfigSerializer
    permission_classes = (IsAuthenticated|IsAdmin|IsResearcher,)
    
class SingleFixationGameConfigView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FixationGameConfig.objects.all()
    serializer_class = FixationGameConfigSerializer
    permission_classes = (IsAuthenticated|IsAdmin|IsResearcher,)
    
class ReportView(generics.ListCreateAPIView):
    queryset = Reports.objects.all()
    serializer_class = ReportsSerializer
    permission_classes = (IsAuthenticated|IsAdmin|IsResearcher,)
    
class SingleReportView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reports.objects.all()
    serializer_class = ReportsSerializer
    permission_classes = (IsAuthenticated|IsAdmin|IsResearcher,)
    
class FixationGameReportView(generics.ListCreateAPIView):
    queryset = FixationGameReport.objects.all()
    serializer_class = FixationGameReportSerializer
    permission_classes = (IsAuthenticated|IsAdmin|IsResearcher,)
    
class FixationGameResultView(generics.ListCreateAPIView):
    queryset = FixationGameResult.objects.all()
    serializer_class = FixationGameResultSerializer
    permission_classes = (IsAuthenticated|IsAdmin|IsResearcher,) # PERMISSION CLASS TO BE EDIT -> ONLT RPI INSTANCE CAN POST NEW RESULT


##### Group management views

class ResercherGroupManangeView(generics.ListCreateAPIView):
    #  filter by "Researcher" group.
    researcher_group = Group.objects.get(name='Researcher')
    queryset = User.objects.filter(groups=researcher_group)
    permission_classes = (IsAuthenticated|IsAdmin|IsResearcher,)
    
    # override get_serializer_class to define each serailizer in each Method
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        elif self.request.method == 'POST':
            return UserNamePOSTSerializer

    # overide post method
    def post(self, request):
        # deserialization
        serialize_item = self.get_serializer(data=request.data)
        serialize_item.is_valid(raise_exception=True)
        username = serialize_item.validated_data['username']
        try:
            # assign user to manager grouop
            user = User.objects.get(username=username)
            researcher_group = Group.objects.get(name='Researcher')
            user.groups.add(researcher_group)
            return Response({'message': f'{user.username} added to group {researcher_group.name}'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
    

class ResercherDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated|IsAdmin|IsResearcher,)
    
    def delete(self,request,pk):
        try:
            user = User.objects.get(pk=pk)
            researcher_group = Group.objects.get(name='Researcher')
						# if user does not in Researcher group -> Raise 400_BAD_REQUEST
						# Othwise delete user from group -> retrun 200
            if researcher_group in user.groups.all():
                user.groups.remove(researcher_group)
                return Response({'message': f'{user.username} removed from group {researcher_group.name}'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User is not in the specified group'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
