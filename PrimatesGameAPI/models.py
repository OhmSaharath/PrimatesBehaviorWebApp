
from django.db import models

# Create your models here.
class RPiBoards(models.Model):
    board_name = models.CharField(max_length=255, default="")  # used to indicated board rather that id
    ip_address = models.GenericIPAddressField(protocol='IPv4')  # 'both' allows both IPv4 and IPv6 addresses
    ssid = models.CharField(max_length=32 , blank=True , null=True)  # SSID lengths can vary but typically limited to 32 characters
    ssid_password = models.CharField(max_length=255, blank=True , null=True)  
    def __str__(self)-> str:
	    return self.board_name
    

class RPiStates(models.Model):
    rpiboard = models.OneToOneField(RPiBoards, on_delete=models.CASCADE)
    is_occupied =  models.BooleanField(default=False)
    game_instance_running = models.IntegerField(default=None,  blank=True , null=True) 
    start_game =  models.BooleanField(default=False)
    stop_game =  models.BooleanField(default=False)
    gp17 = models.BooleanField(default=False)
    def __str__(self)-> str:
	    return self.rpiboard.board_name
 
class Primates(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self)-> str:
	    return self.name
    

class Games(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self)-> str:
	    return self.name


class GameConfig(models.Model):
    name = models.CharField(max_length=255)
    gameid = models.ForeignKey(Games,on_delete=models.CASCADE)
    def __str__(self)-> str:
	    return self.name


class GameInstances(models.Model):
    game = models.ForeignKey(Games, on_delete=models.PROTECT)
    config = models.ForeignKey(GameConfig, on_delete=models.PROTECT, related_name="gameconfig")
    rpiboard = models.ForeignKey(RPiBoards, on_delete=models.PROTECT , related_name="rpiboard")
    primate = models.ForeignKey(Primates, on_delete=models.PROTECT , related_name="primate")
    login_hist = models.DateTimeField()
    logout_hist = models.DateTimeField(blank=True , null=True)


class FixationGameConfig(models.Model):
    configtype = models.ForeignKey(GameConfig, on_delete=models.PROTECT)
    instance = models.OneToOneField(GameInstances, on_delete=models.CASCADE,related_name="gameinstance")
    interval_correct = models.IntegerField()
    interval_incorrect = models.IntegerField()
    interval_absent = models.IntegerField()
