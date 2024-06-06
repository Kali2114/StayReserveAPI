# StayReserveAPI

## Introduction
StayReserveAPI allows users to register, log in, manage profiles, search for properties, make reservations, and add ratings and reviews. Property owners can add, edit, and delete their properties. The application also includes a payment system.

## Installation

### Requirements
- Docker
- Docker Compose
- PostgreSQL
- Python 3.8+
- pip

### Setup

1. **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/stayreserveapi.git
    cd stayreserveapi
    ```

2. **Environment Variables:**
    Create a `.env` file in the root directory and add the following environment variables:
    ```env
    SECRET_KEY=your_secret_key
    DEBUG=True
    DATABASE_NAME=your_database_name
    DATABASE_USER=your_database_user
    DATABASE_PASSWORD=your_database_password
    DATABASE_HOST=db
    DATABASE_PORT=5432
    ```

3. **Install Python dependencies:**
    Install the dependencies from `requirements.txt`:
    ```sh
    pip install -r requirements.txt
    ```

4. **Install development dependencies:**
    Install the development dependencies from `requirements.dev.txt`:
    ```sh
    pip install -r requirements.dev.txt
    ```

5. **Docker and Docker Compose:**
    Ensure you have Docker and Docker Compose installed. Then, build and start the containers:
    ```sh
    docker-compose up --build
    ```

6. **Run Migrations:**
    Once the containers are up, run the database migrations:
    ```sh
    docker-compose run --rm app sh -c "python manage.py makemigrations"
    docker-compose run --rm app sh -c "python manage.py migrate"
    ```

7. **Create a Superuser:**
    Create a superuser to access the Django admin:
    ```sh
    docker-compose run --rm app sh -c "python manage.py createsuperuser"
    ```

8. **Collect Static Files:**
    Collect static files for the admin panel:
    ```sh
    docker-compose run --rm app sh -c "python manage.py collectstatic"
    ```

## Running the Application
To start the application, run:
```sh
docker-compose up
```
The API will be available at http://localhost:8000.

## API Documentation

The API documentation is available at http://localhost:8000/api/docs/

## Code Formatting and Linting

This project uses black for code formatting and flake8 for linting.

### To format the code:
```
black .
```

### To lint the code:
```
flake8 .
```

## API Endpoints

### User Endpoints

Registration
- Method: POST
- Endpoint: '/api/register/'
- Parameters:
    - 'username' (string, required)
    - 'password' (string, required)
    - 'email' (string, required)
    - 
Login
- Method: POST
- Endpoint: '/api/login/'
- Parameters:
    - 'username' (string, required)
    - 'password' (string, required)

User Profile
- Method: GET
- Endpoint: '/api/user/profile/'
- Headers:
    - 'Authorization: Token <token>'

### Property Endpoints

Add Property
- Method: POST
- Endpoint: '/api/properties/'
- Parameters:
    - 'name' (string, required)
    - 'location' (string, required)
    - 'price' (float, required)
    - 'description' (string, optional)
    - 'owner' (int, required)

Edit Property
- Method: PUT
- Endpoint: '/api/properties/{id}/'
- Parameters:
    - 'name' (string, optional)
    - 'location' (string, optional)
    - 'price' (float, optional)
    - 'description' (string, optional)

Delete Property
- Method: DELETE
- Endpoint: '/api/properties/{id}/'

List Properties
- Method: GET
- Endpoint: '/api/properties/'

Filter and Search Properties
- Method: GET
- Endpoint: '/api/properties/?location={location}&price_min={min}&price_max={max}'
- Parameters:
    - 'location' (string, optional)
    - 'price_min' (float, optional)
    - 'price_max' (float, optional)

### Reservation Endpoints

Create Reservation
- Method: POST
- Endpoint: '/api/reservations/'
- Parameters:
    - 'property_id' (int, required)
    - 'user_id' (int, required)
    - 'start_date' (date, required)
    - 'end_date' (date, required)

Edit Reservation
- Method: PUT
- Endpoint: '/api/reservations/{id}/'
- Parameters:
    - 'start_date' (date, optional)
    - 'end_date' (date, optional)

Cancel Reservation
- Method: DELETE
- 'Endpoint: /api/reservations/{id}/'

List User Reservations
- Method: GET
- Endpoint: '/api/user/reservations/'
- Headers:
    - 'Authorization: Token <token>'

### Review Endpoints

Add Review
- Method: POST
- Endpoint: '/api/properties/{property_id}/reviews/'
- Parameters:
    - 'property_id' (int, required)
    - 'user_id' (int, required)
    - 'rating' (int, required)
    - 'comment' (string, optional)

List Reviews
- Method: GET
- Endpoint: '/api/properties/{id}/reviews/'

Edit Review
- Method: PUT
- Endpoint: '/api/properties/{property_id}/reviews/'
- Parameters:
    - 'property_id' (int, required)
    - 'user_id' (int, required)
    - 'rating' (int, required)
    - 'comment' (string, optional)

Delete Review
- Method: DELETE
- Endpoint: '/api/properties/{property_id}/reviews/'


### Payment Endpoints

Create Payment
- Method: POST
- Endpoint: /api/payments/'
- Parameters:

### Payment Endpoints

Payment Endpoints
- Method: POST
- Endpoint: '/api/reservations/{reservation_id}/payments/'
- Parameters:
    - 'reservation_id' (int, required)
    - 'amount' (float, required)
    - 'payment_method' (string, required)

List User Payments
- Method: GET
- Endpoint: '/api/user/payments/'
- Headers:
    - 'Authorization: Token <token>'

## Models

### User

- 'username' (string)
- 'password' (string)
- 'email' (string)

### Property

- 'name' (string)
- 'location' (string)
- 'price' (float)
- 'description' (string)
- 'owner' (ForeignKey to User)
 
### Reservation

- 'property' (ForeignKey to Property)
- 'user' (ForeignKey to User)
- 'start_date' (date)
- 'end_date' (date)

### Review

- 'property' (ForeignKey to Property)
- 'user' (ForeignKey to User)
- 'rating' (int)
- 'comment' (string)

### Payment

- 'reservation' (ForeignKey to Reservation)
- 'amount' (float)
- 'payment_method' (string)

## Deployment

The application uses Gunicorn as the WSGI HTTP Server and can be easily deployed using Docker. Ensure you have a Dockerfile and docker-compose.yml correctly set up in your project.

1. Build the Docker image:
```
docker-compose build
```
2. Run the application:
```
docker-compose up
```
3. Collect static files:
```
docker-compose run --rm app sh -c "python manage.py collectstatic"
```
4. Apply migrations:
```
docker-compose run --rm app sh -c "python manage.py migrate"
```
5. Create a superuser:
```
docker-compose run --rm app sh -c "python manage.py createsuperuser"
```
Now your application should be running and accessible at http://localhost:8000.

## License

This project is licensed under the GNU General Public License.
```
This `README.md` provides a comprehensive overview of your project, including setup instructions, API endpoints, and deployment guidelines. It also includes instructions for installing requirements from `requirements.txt` and `requirements.dev.txt`. Feel free to customize any part of it to better fit your project's specific details and requirements.
```