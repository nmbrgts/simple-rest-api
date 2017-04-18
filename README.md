Simple REST API
--
### Project Background
This is a small REST API based off of the Flask REST API course project offered by [teamtreehouse.com](https://teamtreehouse.com/library/flask-rest-api). This is the final course in the Python and Flask track provided by team treehouse and was by far the most interesting for. This calss focused on the fundamentals of devoping a RESTful API such as design and implementation decissions through a code-along project which is the starting point for this project. Working through the projects in this course, I was introducted to: the Flask ecosystem, handling HTTP requests, RESTful design, user authentication methods, rate limiting and RDB management through ORM. This was my first experience with web application design and ORM (not counting SQLAlchemy's core module, which is not truely an ORM). So, there was a considerable amount for me to learn along the way.
### Design
The API is designed around a course review website. Users may create an account and use it to add courses to the existing list of courses and post reviews for these courses. The API has three main resources: **users**, **courses** and **reviews** of courses posted by users. Each of these resources has two endpoints **api/v1/[resource]** to access a full list of records and  **api/v1/[resource]/[id]** for accessing individual records.

All list resources allow users to view a full list of the respective resource through GET method and allow authenticated users to create new entries through POST method. POST methods on the course list and review list are reserved for authenticated users, but allowed on the user resource to provide users with a way to register their account. Individual record resources allow GET, PUT and DELETE methods for viewing, updating and removing entries. PUT and DELETE are reserved for authenticated users.

Authentication is handled through Basic HTTP Authentication with an option to use a time limited  token. This token can be obtained by a user through GET request at the **api/v1/users/token** and times out after 1 hour. Passwords are hashed for internal use and are only exposed to the user through the creation of their own account or updating their account information.
### Implementation
This projects uses Flask along with the Flask-RESTful and Flask-HTTPAuth extensions to create the minimal API which exposes a relational database containing user, course and review resources.  Database management is handled using peewee ORM and data is stored in a local SQLite database.

Resources and allowed methods are established through the creation of Flask-RESTful's Resource classes. Each resource field is made up of two classes representing the list resource and individual resource endpoints. These Resource class pairs are implemented in their own modules and provided to the main app module, **app.py**, through the use of Flask Blueprint objects.

Tables in the SQLite database are represented through peewee's Model classes. These classes are contained in the **models.py** module and are used by the Resource modules to query from and write to the database. User creation and authorization are closely coupled to the User Model class to keep these processes closely linked to user data storage and retrieval.

Client side authentication is handled through authentication decorator functions -- A feature provided by the Flask-HTTPAuth extension. These functions provide a thin wrapper to the authentication methods contained in the **models.py** module to reduce dependency on the Flask to provide server-side authentication methods.

### Improvements
Existing improvements to the project:

* The users resource has been expanded to allow for making requests to the individual user enpoint, **api/v1/users/[id]**. This also allows users to update or delete their accounts with POST and DELETE, respectively.
* The Review Model has been updated to share a foreign key with the User Model to connect users to the reviews they author. The user and review resources have been updated to reflect this. Users may only update thier own reviews.
*  The user resource provides a list of relative links to reviews written and the review resource provides a single relative link to the author's resource end point.
* Added Comment resource that allows users to comment on reviews as well as other comments.

Features that I would like to add:

* Put for reviews is broken
* Landing page for API to provide instructions and sign up form
* Category and provider fields for courses
* Up/down vote system for reviews and comments
* User profile and user "karma"
* Course recommendations using Non-negative Matrix Factorization

Other considerations:

I would like to eventually build a browser-side Javascript client to provide a user facing website for the API. But, this is still a long ways off and I have much to learn

Currently, all users can POST and DELETE course content. This is not desireable, but limiting these functions to the original authors is problematic as well. The best solution is an edit and approval system where users POST edits for courses and reviews for author approval. Edits would be stored in an inernal resource with limited access. Orphaned content would need special treatment, but this would fix most other possible issues.

> Written with [StackEdit](https://stackedit.io/).

