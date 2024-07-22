
from rest_framework import serializers
from .models import RPiBoards, RPiStates, Primates, Games, GameInstances
from django.contrib.auth.models import User , Group

class GroupSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Group
        fields = ['name',]

class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    class Meta:
        model = User
        fields = ['id', 'username','first_name','last_name','email','date_joined','groups']
        
class UserNamePOSTSerializer(serializers.Serializer):
    username = serializers.CharField()

class PrimatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Primates
        fields = ['id','name']
        
class RPiBoardsSerializer(serializers.ModelSerializer):
    ssid = serializers.CharField(required=False, allow_blank=True)
    ssid_password = serializers.CharField(write_only=True , required=False, allow_blank=True)
    class Meta:
        model = RPiBoards
        fields = ['id','board_name','ip_address','ssid', 'ssid_password']

        
class RPiStatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RPiStates
        fields = '__all__'
        
class GamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Games
        fields = '__all__'

class GamesInstancesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameInstances
        fields = ['id','game' , 'rpiboard' , 'login_hist' , 'primate', 'login_hist' , 'logout_hist']
