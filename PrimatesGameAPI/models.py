
from django.db import models

# Create your models here.
class RPiBoards(models.Model):
    board_name = models.CharField(max_length=255, default="")  # used to indicated board rather that id
    ip_address = models.GenericIPAddressField(protocol='IPv4')  # 'both' allows both IPv4 and IPv6 addresses
    ssid = models.CharField(max_length=32 , blank=True , null=True)  # SSID lengths can vary but typically limited to 32 characters
    ssid_password = models.CharField(max_length=255, blank=True , null=True) 
    token = models.CharField(max_length=255, default=None , blank=True , null=True) 
    def __str__(self)-> str:
	    return self.board_name
    

class RPiStates(models.Model):
    rpiboard = models.OneToOneField(RPiBoards, on_delete=models.CASCADE)
    is_occupied =  models.BooleanField(default=False)
    game_instance_running = models.IntegerField(default=None,  blank=True , null=True) 
    start_game =  models.BooleanField(default=False)
    stop_game =  models.BooleanField(default=False)
    motor = models.BooleanField(default=False)
    def to_dict(self):
        return {
            'rpiboard': self.rpiboard.pk,
            'is_occupied': self.is_occupied,
            'game_instance_running': self.game_instance_running,
            'start_game': self.start_game,
            'stop_game': self.stop_game,
            'motor': self.motor,
        }
    def __str__(self)-> str:
	    return self.rpiboard.board_name



class Primates(models.Model):
    name = models.CharField(max_length=255)
    rfid_tag = models.CharField(max_length=255,default=None, blank=True , null=True)
    is_occupied =  models.BooleanField(default=False)
    #current_stage = models.ForeignKey("Games", on_delete=models.SET_NULL, null=True, blank=True)
    game_instance = models.ForeignKey("GameInstances", on_delete=models.SET_NULL, null=True, blank=True)
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
    name = models.CharField(max_length=255)
    game = models.ForeignKey(Games, on_delete=models.PROTECT)
    config = models.ForeignKey(GameConfig, on_delete=models.PROTECT, related_name="gameconfig")
    rpiboard = models.ForeignKey(RPiBoards, on_delete=models.PROTECT , related_name="rpiboard")
    primate = models.ForeignKey(Primates, on_delete=models.PROTECT , related_name="primate")
    login_hist = models.DateTimeField()
    logout_hist = models.DateTimeField(blank=True , null=True)
    def __str__(self)-> str:
	    return self.name
 


class FixationGameConfig(models.Model):
    configtype = models.ForeignKey(GameConfig, on_delete=models.PROTECT)
    instance = models.OneToOneField(GameInstances, on_delete=models.CASCADE,related_name="fixationgameinstance")
    interval_correct = models.IntegerField(default=2)
    interval_incorrect = models.IntegerField(default=5)
    interval_absent = models.IntegerField(default=60)
    button_holdDuration = models.IntegerField(default=200)

class Reports(models.Model):
    reportname =  models.CharField(max_length=50)
    game = models.ForeignKey(Games, on_delete=models.PROTECT)
    def __str__(self)-> str:
	    return self.reportname

class FixationGameReport(models.Model):
    report = models.ForeignKey(Reports, on_delete=models.PROTECT)
    instance = models.OneToOneField(GameInstances, on_delete=models.PROTECT,related_name="fixationreportgameinstance")
    gamereportname = models.CharField(max_length=50, blank=True , null=True)
    def __str__(self)-> str:
	    return self.gamereportname
    
class FixationGameResult(models.Model):
    fixationreport = models.ForeignKey(FixationGameReport, on_delete=models.PROTECT)
    timestamp = models.DateTimeField()
    feedback = models.BooleanField()
    feedbacktype = models.CharField(max_length=10)
    buttonsize = models.FloatField()
    def __str__(self)-> str:
	    return self.fixationreport.gamereportname
    