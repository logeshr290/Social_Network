# LokiBook Social Network Application

This Django project implements a social networking application with features like user authentication, friend requests, Accept / Reject of friend requests, Searching of new friends.

## Installation

1. Clone the repository:

	git clone https://github.com/logeshr290/soc_network.git

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

## Project Overview and User Flow

1. **Starting the Server:**
   - Run the server to start the application.
   - Access the welcome page.

2. **Signing In:**
   - Click "Sign In" to go to the sign-in page.
   - Provide Email, Username, Password, and Confirm Password.
   - **API Request:** `POST /api/signup/`
     - Request Body: `{"email": "user@example.com", "username": "username", "password": "password", "confirm_password": "password"}`
     - **Response:** `{"message": "User signed up successfully."}`
   - Redirected to the welcome page after signing up.

3. **Logging In:**
   - Click "Log In" on the welcome page to go to the login page.
   - Enter Email and Password.
   - **API Request:** `POST /api/login/`
     - Request Body: `{"email": "user@example.com", "password": "password"}`
     - **Response:** `{"message": "User logged in successfully."}` or `{"error": "Invalid credentials."}`
   - Redirected to the home page (Friends Page) after successful login.

4. **Home Page (Friends Page):**
   - Perform various operations on the home page.

5. **Searching for Friends:**
   - Search friends by username or email ID.
   - **API Request:** `GET /api/search/?q=query`
     - **Response:** Paginated list of friends matching the search criteria.

6. **List Friends:**
   - View the list of friends.
   - **API Request:** `GET /api/friends/`
     - **Response:** Paginated list of friends.

7. **Sending Friend Requests:**
   - Click "Send Request" to send a friend request.
   - **API Request:** `POST /api/send-friend-request/`
     - Request Body: `{"receiver_email": "friend@example.com"}`
     - **Response:** `{"message": "Friend request sent."}` or `{"error": "Error message."}`

8. **Accepting Friend Requests:**
   - Click "Accept" for a pending request to accept it.
   - **API Request:** `POST /api/accept-friend-request/`
     - Request Body: `{"sender_id": "sender_id"}`
     - **Response:** `{"message": "Friend request accepted."}` or `{"error": "Error message."}`

9. **Rejecting Friend Requests:**
   - Click "Reject" for a pending request to reject it.
   - **API Request:** `POST /api/reject-friend-request/`
     - Request Body: `{"sender_id": "sender_id"}`
     - **Response:** `{"message": "Friend request rejected."}` or `{"error": "Error message."}`

10. **Logging Out:**
    - Click "Log Out" to log out and return to the welcome page.



