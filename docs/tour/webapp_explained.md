# Web Application High Level Explained

Delivering diverse tasks to analyze the phenotypic characteristics of non-human primates, as well as their complex nervous systems, necessitates distinct configurations of both hardware and software, each tailored to the specific requirements of the task.

For this reason, combined with the flexibility of the GPIO on the Raspberry Pi system, which enables reconfigurable peripherals, we have designed the web application system with the idea of modularity to allow scalability of the experiments.

The idea is to use the Django framework to gain access to functions such as authentication, information retrieval from a database, and cookie management.

# Overview

<img src="https://raw.githubusercontent.com/BeACoN-Lab-Med-Chula/PrimatesBehaviorWebApp/refs/heads/gh-pages/images/WebAppDiagram.jpg" alt="webappdiagram" />

The web application is devided into three sections.

- Server: Host the web application logic as well as the database server.
- User Clients: Researcher devices that access the web application's functions via a web browser.
- Device Clients: A cage-based device embedded with a Python script to automate the web browser for accessing the experimental application, manipulate the GPIO of the integrated system, and invoke API calls to the server backend to perform CRUD operations on the database.


# Server 

## Database

To centalize the system and allow mutiple intruments to work simutinueously. We have stored the state of the entire system in the database server.

For instance, we reference each cage-based device in the RPIBOARDS table, storing its name, IP address, and other relevant information. We can define this using a Django model like this:

```
class RPiBoards(models.Model):
    board_name = models.CharField(max_length=255, default="")  
    ip_address = models.GenericIPAddressField(protocol='IPv4') 
    ssid = models.CharField(max_length=32 , blank=True , null=True) 
    ssid_password = models.CharField(max_length=255, blank=True , null=True)  
    def __str__(self)-> str:
	    return self.board_name

```

We also have the RPISTATES table for each device, which allows the instrument to track whether or not to run or end a task. This table also stores the state of the GPIO, enabling the edge device (the Raspberry Pi, in this case) to manipulate the peripherals.

```
class RPiStates(models.Model):
    rpiboard = models.OneToOneField(RPiBoards, on_delete=models.CASCADE)
    is_occupied =  models.BooleanField(default=False)
    game_instance_running = models.IntegerField(default=None,  blank=True , null=True) 
    start_game =  models.BooleanField(default=False)
    stop_game =  models.BooleanField(default=False)
    motor = models.BooleanField(default=False)
    def __str__(self)-> str:
	    return self.rpiboard.board_name
```

When it comes to the tasks, each device runs a different experiment instance (which may also involve different tasks). It is crucial to keep track of these states to manage the simultaneous operation of multiple instruments.

An example of the GAMEINSTANCE table allows us to keep track of each task's information, such as which instrument is being used, which task is being performed, which primate is involved, the configuration profile, and other relevant details.

```
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
```

Another crucial part is the experiment result of each task. This web application platform supports report generation, so we need to design the database carefully to ensure that the results of each task instance are stored properly.

One way we can do this is by creating a REPORT table to separate each task's report. We would then create two additional tables based on the task: one table for the instance of the report and another table to store the actual result of the task.

```
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

```
## Web application 
The web application is powered by the Django framework. The reason for this is that having a clear separation between the different parts allows the system to scale for various tasks. By separating application servers, we can create the logic for multiple tasks without interfering with each other. Another benefit is that Django promotes the grouping of related functionality into reusable "applications" and, at a lower level, organizes related code into modules.

The core components of this project are listed as follows:

- Web appplication logic
- API server
- User authentication/authorization application (via djoser and Django REST framework)
- Tasks application

## User Clients

User clients are researchers and observers who can access the web application remotely to start or stop the experiment on each device, monitor the status of the experiment, or download reports.

With the convenience of the Django template language, the web application's front end can update content dynamically from the database.

The Django Template Language (DTL) is a built-in templating system in Django used to generate dynamic HTML content. It allows developers to embed Python-like expressions inside HTML files while maintaining separation between logic and presentation.

Some of the core function of the Web application platform on user clients side:

- User authentication/authorization with tokenization, session management.</br>
<img src="https://raw.githubusercontent.com/BeACoN-Lab-Med-Chula/PrimatesBehaviorWebApp/refs/heads/gh-pages/images/login.png" alt="login" width="300"/>

- Remotely controlled experiments on the edge device with customized configurations for each task.
<img src="https://raw.githubusercontent.com/BeACoN-Lab-Med-Chula/PrimatesBehaviorWebApp/refs/heads/gh-pages/images/startgame.png" alt="startgame" />

- Dynamically update the state of each device in real-time, observe the experiment results, and end the session.
<img src="https://raw.githubusercontent.com/BeACoN-Lab-Med-Chula/PrimatesBehaviorWebApp/refs/heads/gh-pages/images/state1.png" alt="state1" />
<img src="https://raw.githubusercontent.com/BeACoN-Lab-Med-Chula/PrimatesBehaviorWebApp/refs/heads/gh-pages/images/state2.png" alt="state2" />

- Report generation: Support filtering by date, tasks, and optionally by instruments and primates.
<img src="https://raw.githubusercontent.com/BeACoN-Lab-Med-Chula/PrimatesBehaviorWebApp/refs/heads/gh-pages/images/reportgeneration.png" alt="reportgeneration" />


## Device Clients

Device clients, also known as cage-based devices in this project, are Raspberry Pi-based systems that also gain access to the web application, but as RPiClients users. The token from this user allows the server to grant permission for each device client to perform CRUD operations via APIs.

<img src="https://raw.githubusercontent.com/BeACoN-Lab-Med-Chula/PrimatesBehaviorWebApp/refs/heads/gh-pages/images/userclientflow.png" alt="userclientflow" />

The device clients are installed with Python scripts that leverage Selenium to automate the Chromium web browser.

When the system is booted, it is automatically logged in with its own credentials, connects to the web application, and enters power-saving mode, waiting for instructions.

The Python script keeps querying its own status at fixed intervals. When the user client makes an experiment request, the device switches to the corresponding task.

Also, the GPIOs are manipulated according to status updates from the database, and when the task sends an update request for each GPIO, the system sends a PATCH operation to update its own state.