Redmine Gamification & Report Tool
--------------------------------------

As most issue trackers Redmine works best if all project participants update their issues on a regular basis. This repository contains a solution to use the python-redmine (https://github.com/maxtepkeev/python-redmine) tool and generate a report on how often and how well users are doing it. All on "somewhat" gamification principles.

How to install?
---------------

The application has a "data gathering" Python script and an Angular.js front-end. You should schedule to run the data gathering script as often as you prefer. It can be ran like this:

    python/python runner.py --url https://redmine.url/ --user admin --password admin --project project --days=25 app/data/data.json

In order to run the Angular.js app which uses the app/data/data.json file to serve content, you should:

     npm install
     
It can run like this:

     npm run
     
How does it work?
-----------------

You will see reports like this:

![History]:(https://raw.githubusercontent.com/wther/redmine-gamification/master/docs/RedminePointHistory.png "History")

and

![Velocity]:(https://raw.githubusercontent.com/wther/redmine-gamification/master/docs/RedmineVelocity.png "Velocity")


