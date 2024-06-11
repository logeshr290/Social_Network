# Social Network Application

This Django project implements a social networking application with features like user authentication, friend requests, Accept / Reject of friend requests, Searching of new friends.

## Installation

1. Clone the repository:

	git clone https://github.com/logeshr290/Social_Network.git

2. Navigate to the project directory:

	cd soc_network

3. Create a virtual environment (optional but recommended):

	python -m venv .venv

4. Activate the virtual environment:

	- On Windows:
  
 	 	.venv\Scripts\activate

	- On macOS/Linux:

	 	source .venv/bin/activate

5. Install the required packages:

	pip install -r requirements.txt

6. Apply migrations to set up the database:

	py manage.py makemigrations

	py manage.py migrate

7. Create a superuser to access the admin panel:

	python manage.py createsuperuser

	Email: your-email@gmail.com
	password: your-password

	Create the superuser as per your info.

8. Start the development server:

	python manage.py runserver

9. Access the application at http://127.0.0.1:8000/


## Required Packages

- Django==3.2.8
- djangorestframework==3.12.4
- drf-yasg==1.20.0
- django-filter==2.4.0

## Usage

1. Sign Up: Create a new account using the provided Sign Up form.
2. Log In: Log in with your credentials to access the application.
3. Search Users: Search for other users by email, username, or first name.
4. Send Friend Request: Send friend requests to other users.
5. Accept/Reject Friend Requests: Manage incoming friend requests.
6. List Friends: View your list of friends.
7. Logout: Log out from the application.

## API Endpoints

- `api/signup/`: User registration endpoint.
- `api/login/`: User login endpoint.
- `api/search/`: User search endpoint.
- `api/friends/`: List friends endpoint.
- `api/send-friend-request/`: Send friend request endpoint.
- `api/accept-friend-request/`: Accept friend request endpoint.
- `api/reject-friend-request/`: Reject friend request endpoint. 
