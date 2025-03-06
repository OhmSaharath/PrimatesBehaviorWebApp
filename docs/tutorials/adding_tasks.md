# Adding Tasks

When it comes to adding tasks, this platform aims to reduce the workload of researchers as much as possible.

There is still a need for some backend Django implementation, but most of it will be provided with template code, which you'll need to modify slightly to make it work.

So, simply speaking, the step that needs to be done is

- Get the project codebase on your local PC (fork the repository).
- Set up the enviroment for development.
- Create a feature branch to experiment with your ideas.
- Add new applications (tasks) to the web application.
- Implement the logic for the core function of the task in the Django view.
- Map the URL pattern.
- Implement the task logic.
- (To be update........)


## Requirement
- [Git](https://git-scm.com/)
- [Pipenv](https://pipenv.pypa.io/en/latest/)


## Step 1: Get The Project Codebase.

The first step is to get the project codebase on your local machine.

There are two scenarios, depending on whether or not you have access to the repository.

As an external contributor, you're contributing to an open-source project, so you don't have write access,follow these steps:

### Scenario 1: You Have Access to the Repository (Team Member)

If you are member of the organization, follow these steps.

#### Step 1: Clone the Repository

First, clone the repository to your local machine:

```
git clone <repository_url>

```

Then, navigate into the project directory:

```
cd PrimatesBehaviorWebApp
```

### Scenario 2: You Don't Have Push Access (External Contributor)

#### Step 1: Fork the Repository
- Go to the [project repository page](https://github.com/rsongphon/PrimatesBehaviorWebApp).
- Click the "Fork" button in the upper right corner of the screen. (this creates a copy of the repository under your account).

#### Step 2: Clone Your Fork
Copy the forked repository to your local machine:

```
git clone https://github.com/rsongphon/PrimatesBehaviorWebApp.git

```

Move into the project directory:

```
cd PrimatesBehaviorWebApp

```

### Step 3.1: Add the Original Repository as an Upstream
To keep your fork updated with the original repository:

```
git remote add upstream https://github.com/rsongphon/PrimatesBehaviorWebApp.git
```

#### Step 2: Create a New Branch

Before making changes, create a new branch for your work:

```
git checkout -b my-feature-branch
```

## Step 2: Set up the enviroment for development.

# (ตรงนี้ต้องเทสเยอะๆๆๆๆๆๆๆๆๆ)

This project reqired some packages and mock-up database in your local machine in order to make the whole web app running so you can experiment with your feature.

After you have pipenv in you system, install all dependencies for this project.

```
pipenv sync
```

After that, activate the environment.

```
pipenv shell
```

Create and imported MySQL database on the target machine

In the project directory, there is a file called database_backup.sql. This file will be used to create a mock-up database with the correct schema, ensuring that the web application runs properly.

First, install Mysql server with mysqlclient package, depending on machine. 

Refer to this [documentation](https://pypi.org/project/mysqlclient/) in the "Install" section for details on each operating system.

The MySQL server should run automatically after installation. If it doesn't, start the service manually, depending on your system.

##### Windows
Open Command Prompt as Administrator.
Run the following command:
```
net start mssqlserver
```

##### Linux (Ubuntu, CentOS, etc.):
Open a terminal and run the following command:
```
sudo systemctl start mssql-server
```

##### macOS (Homebrew):
```
brew services start mysql
```

Log in to the MySQL server on the target machine as root user:

This process requires administrative permissions, so you will need to grant them depending on your system (such as sudo for linux/mac).

##### macOS/Linux:
```
sudo mysql -u root -p
```

Password for root leaves as blank

### ตรงนี้ค้องสร้าง user admingame ด้วย <<--- เพิ่ม document

Create a new database

```
CREATE DATABASE PrimatesGameDB;
```

Import the database backup on the target machine.

Once the database is created, import the SQL data dump into the new database:

```
sudo mysql -u root -p PrimatesGameDB < database_backup.sql
```

This will restore the database on the target machine.

After the database is imported, you can run Django migrations to ensure the schema is up to date:

```
python3 manage.py migrate
```

Now, it's a good time to check the web application to see if it's running correctly, run the command.

```
python3 manage.py runserver 0.0.0.0:8000
```

This will run the web application on your local system.

Go to Site administration page by url http://127.0.0.1:8000/admin/

Login as admin (username and password are in user.txt in root directory of the project file)

Check if database has all table present.

<img src="/images/adminpage.png" alt="adminpage" width="400">


## Step 3: Create a feature branch.

Creating a feature branch allows you to experiment with your code and create tasks as you like. Once you've finished testing, you can merge your code back into the original main branch.

For more information about git branch [check](https://medium.com/amiearth/%E0%B8%A1%E0%B8%B2%E0%B8%97%E0%B8%B3%E0%B8%84%E0%B8%A7%E0%B8%B2%E0%B8%A1%E0%B8%A3%E0%B8%B9%E0%B9%89%E0%B8%88%E0%B8%B1%E0%B8%81-git-branch-560c23e67eb6)

```
git checkout -b name-of-your-branch
```

## Step 3: Add new applications (tasks) to the web application.

Now the important step, adding new application (task) to web app. 


```
python3 manage.py startapp PrimalGame_Your-Task-Name

```

Replace 'Your-Task-Name' with your preferred name.

You will see new directory with your app name in the root directory of the project. In this directory, you will see some scipts that need for your app. No need to do anything for these script now.

Now, add your new application in the project. All of the requirement app use in this project need to include in setting.py file in project level.

Go to setting.py located in project directory, in this case, under PrimatesGame

<img src="/images/settingpy.png" alt="settingpy" width="400">

Locate INSTALLED_APPS section and add new app at the last line (in square bracket) in the format like this.

```
'PrimalGame_Your-Task-Name',
```

Example of INSTALLED_APPS section after adding new application

```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'PrimalGameAPI',
    'rest_framework',
    'djoser',
    'PrimalGame_Your-Task-Name'
]

```

## Step 4 : Implement the logic for the core function.

Now we will implement some core function to make your application work.

First, your application need the HTML page as 