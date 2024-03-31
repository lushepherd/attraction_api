# Lucy Shepherd T2A2 - API 

## Menu

- [API Setup and Installation](#api-setup-and-installation)
- [Software Development Plan](#software-development-plan)
- [Q1](#1---identification-of-the-problem-you-are-trying-to-solve-by-building-this-particular-app)
- [Q2](#2---why-is-it-a-problem-that-needs-solving)
- [Q3](#3---why-have-you-chosen-this-database-system-what-are-the-drawbacks-compared-to-others)
- [Q4](#4---identify-and-discuss-the-key-functionalities-and-benefits-of-an-orm)
- [Q5- Endpoint Documentation](#5---document-all-endpoints-for-your-api)<br><br>
         <b>USERS</b><br>

    - [Register user](#register-user-endpoint---create-a-new-user-account-with-details-provided-by-client)
    - [Login user](#login-user-endpoint---log-in-an-already-registered-user)
    - [View all users (as admin)](#view-all-users-admin-only)
    - [View one user account (account holder or admin)](#view-account)
    - [Update Account](#update-account)
    - [Delete Account (account holder or admin)](#delete-account)<br>

    <b>BOOKINGS</b>
    - [Create Booking](#create-new-booking)
    - [Admin Create Booking on behalf of User](#admin-create-booking-for-user)
    - [View My Bookings](#view-my-bookings)
    - [Update Booking (admin only)](#update-booking-admin-only)
    - [Delete Booking (admin only)](#delete-account)

    <b>ATTRACTIONS</b>

- [Q6](#6---an-erd-for-your-app)
- [Q7](#7---detail-any-third-party-services-that-your-app-will-use)
- [Q8](#8---describe-your-projects-models-in-terms-of-the-relationships-they-have-with-each-other)
- [Q9](#9---discuss-the-database-relations-to-be-implemented-in-your-application)
- [Q10](#10---describe-the-way-tasks-are-allocated-and-tracked-in-your-project)
- [Resources](#resources)

### API Setup and Installation

1. Navigate to the src folder.
2. Create a database and user with the necessary permissions. The user will need to have ownership rights.
3. Create a .env file based on the provided .env.sample file in the src folder.
4. Create and activate a virtual environment 
```
python3 -m venv .venv && source .venv/bin/activate
```
5. Install dependencies from requirements.txt
```
pip3 install -r requirements.txt
```
6. Start the Flask server
```
flask run
```
7. Create tables
```
flask db create
```
8. Seed tables
```
flask db seed
```

For further instructions on usage, please navigate to [Endpoints](#5---document-all-endpoints-for-your-api) below.

### Software Development Plan

![Plan page 1](./docs/images/asana1.png)
![Plan page 2](./docs/images/asana2.png)
![Plan page 3](./docs/images/asana3.png)

### 1 - Identification of the problem you are trying to solve by building this particular app.

Planning visits to various attractions usually means having to look through many different websites and platforms. Seeing this issue as an inconvenience for users, the creation of an API for a booking app is a solution aimed at making things easier for users in several ways.

This is designed to function as a centralised booking system. By bringing together the booking process for a range of attractions into one platform, it makes things simpler for users. This means users no longer need to waste time checking multiple sites to plan their visits, making the journey from being interested in an attraction to actually booking a smoother experience.

It allows real-time availability information ensuring that planning trips and visits is easier and more efficient, allowing for smooth scheduling.

Another important feature is a streamlined review system. Usually, potential visitors have to search through several platforms to find reviews about an attraction. This app puts all these reviews in one place, letting users access other users experiences and insights. This helps users make informed decisions quickly, improving the planning process.

Verified user feedback is another design feature. Users with confirmed bookings that have been completed are able to leave feedback in the form of reviews and ratings. This serves two purposes: it gives attractions valuable insights for improvement and helps future visitors make choices.

Communication between users and attractions is helpful for sorting out questions or issues related to bookings. The app addresses this by creating a direct line of communication, making it easy to get in touch. This makes solving booking-related issues more efficient and also improves the user experience by ensuring help is easy to seek out when required.

Lastly, the app can allow users to discover attractions they may not have heard of by viewing all attractions. This gives users more choices and may lead to them discovering new favourites.

This API tackles these challenges with a comprehensive set of features. It enhances the users journey with efficiency and access to a wider range of attractions. It can function as a key tool in making the planning of activities simpler and the booking process more enjoyable.

### 2 - Why is it a problem that needs solving?

 - Time Consumption: Users can waste time navigating multiple websites and platforms to find and book attractions. It is a disjointed approach that complicates the planning process and can increase the likelihood of missing out on better options or deals. This can eradicate extra time consumption and save users time and simplify the decision-making process.

- Attraction Information: With all attraction information in one location, users are able to check location and opening hour information and if there is availability for the number of people for their booking. 

- Decision-Making: The verified review system allows convenient access to user experiences from users with completed bookings. This can assist with informed decision making at the time of booking (and users can also add their own ratings and reviews after attending).

- Communication: Direct communication with attractions for inquiries or booking changes allows efficient communication between user and attraction. This can enhances user satisfaction and trust in the service.

- Attraction Visibility: By offering a platform that hosts a wide range of attractions, it can help diversify user choices and potentially support smaller or lesser-known attractions in gaining visibility.

- Expanding Range - As an admin has the ability to create new attractions, the available range of attraction choices can continue to expand. This means users can continue to discover new attractions and may be more likely to be repeat customers in the future.  

###  3 - Why have you chosen this database system. What are the drawbacks compared to others?

#### Why I chose SQLAlchemy

- Easy to Start: I have found it's a simple process to get it up and running. As a new and learning developer I found it great to get this project off the ground without a lot of fuss over database setup.

- Works Well with Python and Flask: Lets me define the database in terms I'm familiar with (like Python classes), which made working with it and adapting it to my needs a straightforward process.

- Saves Time Writing Code: I found SQLAlchemy took care of a lot of the complex/repetitiveness that comes with dealing with databases. It abstracts database operations you don't need to write raw SQL queries which means writing less code, and the code have written is cleaner and easier to understand.

- Good Easy-to-read Docs: I found the documentation really easy to follow and it seemed to be easy to find solutions to errors that popped up. It was also easy to find examples of different ways to accomplish a task.

- Good for Work Experience - This is more of a general reason rather than related to this application, but I have found looking at jobs in tech/IT a lot of them require proven experience in SQLAlchemy as it is such a popular choice even today.

#### Some Drawbacks of using SQLAlchemy
For this assignment I didn't experience many drawbacks so I did some research to find some reasons why others think it may not be the best choice. I have found the main complaint is slowing down your application so I looked into how/why this happens.

SQLAlchemy works by putting a layer called Object-Relational Mapping (ORM) between your app and the database. This layer changes the Python code you write into SQL commands for the database and then turns the database's answers back into Python. This is meant to make things easier and keep your code tidy.

This extra step can make things slower and give you less direct control over the database. Whether this is a big deal depends on project needs and how fast you need your app to run. I have seen it mentioned also you can use SQLAlchemy for general things and switch to direct SQL commands when you need things to be faster.

Another reason that can affect performance is broad queries that return a large amount of data when only a small amount is needed. I have seen fixes to this including utilising more specific queries to return only the column required instead of a whole table, or using lazy loading which will prevent an attribute from loading on object instantiation - this means it won't load related tables unless they required. 

Another potential drawback I have seen I actually listed as a pro above (for myself). For someone who already knows SQL well SQLAlchemy’s way of handling things might feel limiting as it hides some of the complexities of SQL.

### 4 - Identify and discuss the key functionalities and benefits of an ORM

An Object-Relational Mapping (ORM) tool allows developers to manage and interact with relational databases in a simpler way. It acts as a bridge between the application code and the database. 

<u>Some key functionalities are:</u> <br><br>
- Simplification: ORM abstracts the database schema and operations into objects. This hides the complexity of SQL queries and database schema details and assists with easier code management and understanding. This can also assist with reducing errors in database operations.

- CRUD Operations: ORM frameworks provide simple methods for performing Create, Read, Update, and Delete operations on databases. These operations are fundamental to managing database records, and ORM simplifies their execution without needing to use SQL queries.

- Data Type Mapping: ORMs automatically map database data types to programming language data types, ensuring seamless data conversion. This mapping eliminates the need for manual conversion, reducing errors and workload.

- Relationship Management: ORM frameworks manage relationships between different data models (ie one-to-one, one-to-many, many-to-many relationships) through object references. This makes it easier to navigate related data without complex SQL joins.

<u>Some Benefits of Using an ORM:</u><br>
- Increased Productivity: ORM's automate a lot of routine database operations which allows developers to focus more on business logic rather than database management.

- Code Maintainability: As an ORM handles a lot of the more complex queries code is much cleaner/simpler. This means changes to the database model or structure can be managed efficiently, making the codebase easier to maintain and evolve.

- Enhanced App Performance: Through features like lazy loading and caching, ORM frameworks can optimise databases and reduce the load on the database server, leading to improved application performance.

- Easier Transaction Management: ORM frameworks often provide simplified mechanisms for managing transactions, ensuring data integrity and consistency even across complex operations involving multiple tables.

### 5 - Document all endpoints for your API

### Users

#### Register User Endpoint - Create a new user account with details provided by client.

<b>HTTP Method</b>: POST<br>
<b>URL:</b>
http://localhost:8080/auth/register<br>
<b>Request body</b>: JSON object with the following keys:

- name: Users full name. Must contain only letters, spaces, and dashes.
- email: Users email address. Must be in a valid email format.
- phone: Users phone number. Must contain exactly 10 characters.
- password: Users desired password. Must contain a minimum of 8 characters.

Example:
```json
{
  "name": "John Smith",
  "email": "smith.john@email.com",
  "phone": "0412345600",
  "password": "password"
}
```
<b>Success Response</b>
- Code 201 (created)
- Returns created user object (without the password)

Example Success Response:
```json
{
  "id": 4,
  "name": "John Smith",
  "email": "smith.john@email.com",
  "phone": "0412345600",
  "is_admin": false,
  "bookings": [],
  "reviews": []
}
```
Error Responses
Validation Error
- Code: 400 Bad Request
- Content: Error message detailing missing or invalid fields.
Example Validation Error Response:
```json
  {
  "error": {
    "name": [
      "Name cannot be empty.",
    ],
    "email": [
      "Not a valid email address."
    ]
  }
}
```
Integrity Errors
- Code: 400 Bad Request 
 - Content: A message indicating that a required field is missing or invalid.
 - Example NOT NULL Violation Response and Validation Error Response:
```json
  {
  "error": {
    "email": [
      "Not a valid email address."
    ]
  }
}
```
```json
{
  "error": {
    "password": [
      "Password must be at least 8 characters long."
    ]
  }
}
```
Unique Violations
 - Code: 409 Conflict (for UNIQUE violations)
- Content: A message indicating that the provided email address or phone number is already in use.
 - Example UNIQUE Violation Response (Email, Phone):
```json
{
  "error": "Email address already in use"
}
```
```json
{
  "error": "Phone number already in use"
}
```

<b>Further Notes</b><br>
- All fields (name, email, phone, password) are required. If any are missing or don't meet the validation criteria, a 400 Bad Request error will be returned with details.
- The password is hashed for security before being stored in the database.
- The email address and phone number must be unique. Attempting to register with an email address or phone number that is already in use will result in a 409 Conflict error.

#### Login User Endpoint - Log in an already registered user

<b>HTTP Method</b>: POST<br>
<b>URL:</b> http://localhost:8080/auth/login
<br>
<b>Authentication Required:</b> No
<b>Request body</b>: JSON object with the following keys:

- email: The user's email address
- password: The user's password

Example:
```json
{
  "email": "smith.john@email.com",
  "password": "password"
}
```
<b>Success Response</b>
- Code 200 (OK)
- Returns email, token, and if the user is an admin or not

Example Success Response:
```json
{
  "email": "smith.john@email.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "is_admin": false
}
```
Error Response
1. Code: 401 Unauthorized (email or password incorrect)
    .
Example Validation Error Response:
```json
{
  "error": "401 Unauthorized: The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."
}
```
#### View All Users (admin only)

<b>HTTP Method</b>: GET<br>
<b>URL:</b> http://localhost:8080/auth/users
<br>
<b>Authentication Required:</b> Yes, a valid JWT token must be used in Authorisation header.
<b>Permissions:</b> Admin only.

<b>Success Response</b>
- Code 200 (OK)
- Returns list of all registered users, their bookings and their reviews.

Example Success Response:
```json
[
  {
    "id": 1,
    "name": "Admin One",
    "email": "admin@email.com",
    "phone": "0455555555",
    "is_admin": true,
    "bookings": [],
    "reviews": [
      {
        "attraction": {
          "name": "The Colosseum"
        },
        "rating": 10,
        "comment": "Best day of my life!",
        "created_at": "30/03/2024"
      }
    ]
  },
  {
    "id": 2,
    "name": "User One",
    "email": "userone@email.com",
    "phone": "0466666666",
    "is_admin": false,
    "bookings": [
      {
        "id": 1,
        "attraction": {
          "name": "The Great Wall of China"
        },
        "booking_date": "20/05/2024",
        "number_of_guests": 2,
        "total_cost": 300.0,
        "status": "Confirmed",
        "created_at": "30/03/2024"
      }  
```
Error Response
1. Code: 401 Unauthorized (user not authenticated or token is invalid)

Example Validation Error Response:
```json
{
    "error": "Not authorised. Admin access required."
}
```
#### View Account

<b>HTTP Method</b>: GET<br>
<b>URL:</b> http://localhost:8080/auth/users/3 (number user ID)
<br>
<b>Authentication Required:</b> Yes, a valid JWT token must be used in Authorisation header.
<b>Permissions:</b> Account user can view their own account, admin can view any account.

<b>Success Response</b>
- Code 200 (OK)

Example Success Response:

```json
{
  "id": 4,
  "name": "John Smith",
  "email": "smith.john@email.com",
  "phone": "0412345600",
  "is_admin": false,
  "bookings": [],
  "reviews": []
}
```
Error Responses

- Code: 401 Unauthorized (user is not authenticated or token is invalid)
- Code: 403 Forbidden (user is not account holder or admin)
- Code: 404 Not Found (user with specified ID doesn't exist)

Example:
```json
{
  "error": "403 Forbidden: You don't have the permission to access the requested resource. It is either read-protected or not readable by the server."
}
```

#### Update Account

<b>HTTP Method</b>: PUT<br>
<b>URL:</b> http://localhost:8080/auth/update 
<br>
<b>Authentication Required:</b> Yes, a valid JWT token must be used in Authorisation header.
<b>Permissions:</b> Only account user can update their account.

<b>Request Body:</b> JSON object containing any of the fields that the user wishes to update: name, email, phone, and password. Fields not provided will retain their existing values. Follows same data validation as "register user".

- name: Users full name. Must contain only letters, spaces, and dashes.
- email: Users email address. Must be in a valid email format.
- phone: Users phone number. Must contain exactly 10 characters.
- password: Users desired password. Must contain a minimum of 8 characters.

Example:
```json
{
  "email": "mrjohnsmith@email.com"
}
```
<b>Success Response</b>
- Code 200 (OK)
Example Success Response:
```json
{
  "id": 4,
  "name": "John Smith",
  "email": "mrjohnsmith@email.com",
  "phone": "0412345600",
  "is_admin": false,
  "bookings": [],
  "reviews": []
}
```
Error Responses

- Code: 401 Unauthorized (user is not authenticated or token is invalid)
- Code: 404 Not Found (user with specified JWT doesn't exist)
- Code: 400 Bad Request (detailed error message will indicate which fields are invalid or improperly formatted)

Example:
```json
{
    "error": "User not found"
}
```
```json
{
  "name": [
    "Name can't contain special characters."
  ]
}
```
#### Delete Account

<b>HTTP Method</b>: DELETE<br>
<b>URL:</b> http://localhost:8080/auth/delete/2 (number is user id of account to be deleted) 
<br>
<b>Authentication Required:</b> Yes, a valid JWT token must be used in Authorisation header.
<b>Permissions:</b> Admins can delete any user account, user can delete their own account.

<b>Success Response:</b>
Code 200 (OK)<br>
Example Success Response:
```json
{
    "message": "User deleted successfully"
}
```
Error Responses
- Code 401 Unauthorized: user is not authenticated or the token is invalid
- Code 403 Forbidden: requesting user is not authorised to delete the account.

Example:
```json
{
    "error": "Unauthorised"
}
```
- Code 404 Not Found: user with specified ID does not exist.

Example:
```json
{
  "error": "404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."
}
```
#### Unlock Account (as admin)

<b>HTTP Method</b>: POST<br>
<b>URL:</b> http://localhost:8080/auth/unlock_user/2 (number as user ID to unlock)
<br>
<b>Authentication Required:</b> Yes, a valid JWT token must be used in Authorisation header.<br>
<b>Permissions:</b> Only admin can unlock an account.

Admin can retrieve a user to see if their account is locked. is_locked_out will show as "true" or "false". 

```json
{
  "id": 3,
  "name": "John Smith",
  "email": "mrjohnsmith@email.com",
  "phone": "0417987696",
  "is_locked_out": true,
  "is_admin": false,
  "bookings": 
```
Success Response

Code 200 (OK)

Example success response:
```json
{
  "message": "User account 3 unlocked successfully"
}
```
Retrieving the user account should now show as is_locked_out = false.
```json
{
  "id": 3,
  "name": "John Smith",
  "email": "mrjohnsmith@email.com",
  "phone": "0417987696",
  "is_locked_out": false,
  "is_admin": false,
  "bookings":
```
Further notes:<br>
User will still be unable to create another booking if they have 5 bookings in "requested" status from the last 24hrs or exceed the $2500 limit in the same time period. They will need to wait 24hrs, have an admin confirm/cancel a booking or bookings, or have an admin create a booking on their behalf.

#### Create New Booking

<b>HTTP Method</b>: POST<br>
<b>URL:</b> http://localhost:8080/booking/new
<br>
<b>Authentication Required:</b> Yes, a valid JWT token must be used in Authorisation header.
<b>Permissions:</b> Only account user owner can create a booking.

<b>Request Body:</b> JSON object containing booking details. 
- id: Attraction ID as an integer.
- booking_date: Australian date format DD-MM-YYYY. Must be dated between today and 6 months from now.
- number_of_guests: as an integer - can only be between 1 and 20.

Example:
```json
{
  "id": 1, 
  "booking_date": "10-04-2024",  
  "number_of_guests": 2
    }
```

<b>Success Response</b>
- Code 201 (Created)
Example Success Response:
```json
{
  "id": 3,
  "attraction": {
    "name": "The Great Wall of China"
  },
  "booking_date": "30/05/2024",
  "number_of_guests": 5,
  "total_cost": 750.0,
  "status": "Requested",
  "created_at": "31/03/2024",
  "user": {
    "name": "John Smith",
    "email": "mrjohnsmith@email.com",
    "phone": "0417987696"
  }
}
```

Error Responses
- Code: 400 Bad Request (For invalid request parameters or booking constraints exceeded)
```json
{
  "message": "Invalid booking date format. Enter as DD-MM-YYYY."
}
```
```json
{
  "message": "For bookings greater than 20, please contact the attraction directly."
}
```
- Code: 403 Forbidden (When trying to create a booking over $1000 without admin permissions)
```json
{
  "message": "Bookings over $1000 require admin permission."
}
```
- Code: 429 Too Many Requests (When account is locked due to security reasons)
```json
{
  "message": "Account locked for security reasons. Please contact admin."
}
```

- Code: 404 Not Found (When the specified attraction ID does not exist)
Content: { "error": "Attraction not found" }

Example:
```json
{
    "error": "User not found"
}
```
```json
{
  "name": [
    "Name can't contain special characters."
  ]
}
```
Further notes:
- Bookings are subject to validation checks including date format, date range (booking must be within 6 months from today), and attraction slot availability.
- Security checks are in place to reduce instances of fraud. 
    - Users need admin permission for bookings of $1000 or more
    - Users accounts are locked if they create more than 5 bookings or exceed total cost of $2500 in a 24hr period. Account can only be unlocked by an admin (in a real life scenario, admin would verify the bookings then confirm them and unlock the account, or cancel the bookings and keep account locked)
    - If a user requires another booking, admin can confirm or cancel current bookings and unlock their account.
    - If a user requires a booking exceeding $1000,  admin can create a booking on their behalf.
    - Bookings for 20 or more people are not allowed.
- When bookings are created, the number of guests for the new booking is deducted from the attraction availability to avoid overbooking.

#### Admin Create Booking for User

<b>HTTP Method</b>: POST<br>
<b>URL:</b> http://localhost:8080/booking/new
<br>
<b>Authentication Required:</b> Yes, a valid JWT token must be used in Authorisation header.
<b>Permissions:</b> Only account user owner can create a booking.

<b>Request Body:</b> JSON object containing booking details. 
- id: Attraction ID as an integer.
- booking_date: Australian date format DD-MM-YYYY. Must be dated between today and 6 months from now.
- number_of_guests: as an integer - can only be between 1 and 20.

Follows the same logic as create a booking, however an admin can enter the user id and create a booking exceeding the $1000 limit on their behalf. Would also be used in a case where potentially users don't want to or aren't able to make their own bookings - they can phone/email and an admin can create a booking on their behalf.<br>
<b>Success Response</b>
- Code 201 (Created)
Example Success Response:
```json
{
  "id": 15,
  "attraction": {
    "name": "The Great Wall of China"
  },
  "booking_date": "30/06/2024",
  "number_of_guests": 10,
  "total_cost": 1500.0,
  "status": "Requested",
  "created_at": "31/03/2024",
  "user": {
    "name": "John Smith",
    "email": "mrjohnsmith@email.com",
    "phone": "0417987696"
  }
}
```
Error Response:
- Code: 400 Bad Request (missing required fields, JSON payload incorrectly configured)

Examples:
```json
{
  "error": "400 Bad Request: The browser (or proxy) sent a request that this server could not understand."
}
```
Code 403: Forbidden (non admin user attempting booking)
```json
{
  "error": "Not authorised. Admin access required."
}
```
Further Notes:
- Admin can't make bookings for someone with a locked account, account must be unlocked. If account was locked due to having 5 bookings in requested, admin must confirm or cancel one or more bookings to make an additional booking. Locked accounts will return the following error:

```json
{
  "message": "Account locked for security reasons. Please contact admin."
}
```
- Admin unlocking an account and then making a booking without changing a booking status will lock the account again.

#### View My Bookings

<b>HTTP Method</b>: GET<br>
<b>URL:</b> http://localhost:8080/booking/my_bookings
<br>
<b>Authentication Required:</b> Yes, a valid JWT token must be used in Authorisation header.<vr>
<b>Permissions:</b> Only account user owner can access this endpoint to view their own bookings.

Success Response
Code 200 (OK)

Example:
```json
{
    "id": 15,
    "attraction": {
      "name": "The Great Wall of China"
    },
    "booking_date": "30/06/2024",
    "number_of_guests": 10,
    "total_cost": 1500.0,
    "status": "Requested",
    "created_at": "31/03/2024",
    "user": {
      "name": "John Smith",
      "email": "mrjohnsmith@email.com",
      "phone": "0417987696"
    }
```
Error Responses:
Code: 401 Unauthorized

This error occurs if the JWT token is missing, expired, or invalid.

If a user has no bookings, it will return 
```json
[]
```
Further notes:<br>
If an admin needs to view all bookings for a user, they would view a user account via auth/user/2 (number is user id) or they can retrieve all user accounts and all bookings via auth/users.

#### Update Booking (admin only)

<b>HTTP Method</b>: PUT<br>
<b>URL:</b> http://localhost:8080/booking/6 (integer = booking id)<br>
<b>Authentication Required:</b> Yes - admin only.<vr>
<b>Permissions:</b> Admins can update bookings for any user.

Admin can update the booking date, number of guests, and booking status for a user. In a real life scenario - an admin would likely need permission from the attraction to confirm or cancel a booking, update the booking date or add/remove guests (or they would admin their own attractions for approvals and amendments directly). One or more fields below are required.<br>
If the number of guests are increased or decreased, the available slots on the attraction adjusts accordingly.

Request body:
- booking_date (optional): The new booking date in DD-MM-YYYY format.
- number_of_guests (optional): The updated number of guests for the booking.
- status (optional): The new status of the booking (one of "Requested", "Confirmed", or "Cancelled").

Success Response
Code 200 (OK)

Example:

```json
{
  "id": 17,
  "attraction": {
    "name": "The Great Wall of China"
  },
  "booking_date": "30/06/2024",
  "number_of_guests": 2,
  "total_cost": 300.0,
  "status": "Confirmed",
  "created_at": "31/03/2024",
  "user": {
    "name": "John Smith",
    "email": "mrjohnsmith@email.com",
    "phone": "0417987696"
  }
}
```
Error Responses:

- Code: 404 Not Found (booking doesn't exist)
```json
{
  "error": "404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."
}
```
- 400 Bad Request (invalid booking date format)
```json
{
  "message": "Invalid booking date format. Enter as DD-MM-YYYY."
}
```

Code: 400 Bad Request (not enough attraction availablility for booking)
```json
{
"error": "Not enough availability for the updated number of guests."
}
```
Code: 422 Unprocessable Entity (valid status wasn't provided)
```json
{
  "error": "Invalid status value",
  "message": "Status can only be 'Requested', 'Confirmed', or 'Cancelled'."
}
```
#### Delete Booking (admin only)
<b>HTTP Method</b>: DELETE<br>
<b>URL:</b> http://localhost:8080/booking/6 (integer = booking id)<br>
<b>Authentication Required:</b> Yes - admin only.<vr>
<b>Permissions:</b> Admins can delete bookings for any user.

Success Response: 
- Code 200 (ok)

Example:
```json
{
  "message": "Booking deleted successfully"
}
```
Error Response:
- Code 404 Not Found (Booking doesn't exist)
```json
{
  "error": "404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."
}
```
- Code 403 Forbidden (user trying to delete doesn't have admin privileges)
```json
{
  "error": "Not authorised. Admin access required."
}
```


#### Create Attraction (admin only)

#### Update Attraction (admin only)

#### Delete Attraction (admin only)

#### View All Attractions

#### View One Attraction

#### Create A Review

#### View My Reviews

#### Update Review

#### Delete Reviews

#### View All Reviews For a Particular Attraction

### 6 - An ERD for your app

### 7 - Detail any third party services that your app will use

### 8 - 	Describe your projects models in terms of the relationships they have with each other

### 9 - Discuss the database relations to be implemented in your application

### 10 - Describe the way tasks are allocated and tracked in your project

### Resources

- docs.sqlalchemy.org. (n.d.). SQLAlchemy Documentation — SQLAlchemy 2.0 Documentation. [online] Available at: https://docs.sqlalchemy.org/en/20/.

- Flask (n.d.). Welcome to Flask — Flask Documentation (3.0.x). [online] flask.palletsprojects.com. Available at: https://flask.palletsprojects.com/en/3.0.x/.

- marshmallow.readthedocs.io. (n.d.). marshmallow: simplified object serialization — marshmallow 3.17.1 documentation. [online] Available at: https://marshmallow.readthedocs.io/en/stable/.

- accounts.google.com. (n.d.). Sign in - Google Accounts. [online] Available at: https://ait.instructure.com/courses/5166/pages/conference-recordings-term-2

- Stack Overflow. (n.d.). how to keep order of sorted dictionary passed to jsonify() function? [online] Available at: https://stackoverflow.com/questions/54446080/how-to-keep-order-of-sorted-dictionary-passed-to-jsonify-function

- Stack Overflow. (n.d.). How is a unique constraint across three columns defined? [online] Available at: https://stackoverflow.com/questions/26895207/how-is-a-unique-constraint-across-three-columns-defined 

- Stack Overflow. (n.d.). Why is loading SQLAlchemy objects via the ORM 5-8x slower than rows via a raw MySQLdb cursor? [online] Available at: https://stackoverflow.com/questions/23185319/why-is-loading-sqlalchemy-objects-via-the-orm-5-8x-slower-than-rows-via-a-raw-my 

- Cao, B. (2022). ⭕️ Six Ways to Optimize SQLAlchemy. [online] Athelas Engineering. Available at: https://athelaseng.substack.com/p/-six-way-to-optimize-sqlalchemy



‌

‌
