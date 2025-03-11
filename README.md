# Web Application Platform for Behavioral Experiments In Non-human Primates
####  **This project was conducted under the supervision of Dr. rer. nat. Lalitta Suriya-Arunroj at the Behavioral and Cognitive Neuroscience Lab, Chulalongkorn Hospital.**

This project aims to improve the Marmoset Experimental Behavioral Instrument (MXBI) Platform, building on the work conducted by A. Calapai et al. (2022).

[Flexible auditory training, psychophysics, and enrichment of common marmosets with an automated, touchscreen-based system (A. Calapai, J. Cabrera-Moreno, T. Moser & M. Jeschke)](https://www.nature.com/articles/s41467-022-29185-9)

## Project Explanation and Documentation avialable at 
https://beacon-lab-med-chula.github.io/PrimatesBehaviorWebApp/


## Project Overview

<img src="./img/device1.png" alt="device" width="400"/>


A modular, cage-based device designed for adaptability in various experiments focused on computer-based cognitive training and audio-visual association studies, to facilitate the investigation of non-human primates' behavioral traits and complex nervous systems.

Contribute to the development and optimization of cognitive and environmental enrichment strategies for non-human primates under human care.

Incorporated a web application platform for remote access and control, providing rapid prototyping speed and convenience for researchers.

### Key Features

- A cage-based device built on the Raspberry Pi platform.
- 3-tier architecture,  client / application server / database server.
- RESTful API.
- Animal tagging by means of radio-frequency identification 
- Capable of experiment on cognitive vision / auditory tasks
- Scalable to multiple instruments
- An open-architecture, scalable, and customizable experiment platform (Django, JavaScript).
- User authentication and authorization for enhanced security and management.
- Dynamic content updates allow users to observe each experiment's status in real time.


### Web Applocation Overview

<img src="./img/WebAppDiagram.jpg" alt="webappdiagram" />


The web application is devided into three sections.

- Server: Host the web application logic as well as the database server.
- User Clients: Researcher devices that access the web application's functions via a web browser.
- Device Clients: A cage-based device embedded with a Python script to automate the web browser for accessing the experimental application, manipulate the GPIO of the integrated system, and invoke API calls to the server backend to perform CRUD operations on the database.