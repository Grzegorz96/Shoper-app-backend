![shoperlogo](https://github.com/Grzegorz96/Shoper-app-backend/assets/129303867/7b68b20e-006b-47bc-8823-8c00e62282ca)
API for SHOPER.app

The API contains the necessary endpoints for the proper operation of the entire project. It supports the database and performs operations on multimedia files located on the server. Using functions, the user can perform all database-related operations. Thanks to extensive server-side validation, users will not be able to enter information in the database that does not meet the requirements. Validation also applies to files located on the server, an appropriate user directory is created for each file, and the file itself is validated in detail. In the project, I paid particular attention to the completeness of data and, in case of errors, returning an appropriate response with an appropriate status code. The program can be run on Windows and Linux.


## Description of the modules

The program contains four modules, the Database_connection.py module is responsible for creating a connection to the database, retrieves the necessary data placed in the environment variable and uses them to connect to the MySQL server. The Media_validator.py module contains a function validating the uploaded graphic file. The function takes the allowed extensions from the environment variable and checks whether the entered file meets the requirements. The Query_creator.py module contains two functions, one dynamically creates a database query, depending on what the user wants to search for, the other retrieves messages for a given conversation and converts DATETIME objects to a string. The API.py module is the most important module of this program, it is here that all operations related to the database and server are performed. It has the function of uploading, downloading and deleting multimedia files from the server. It is also possible to download photo paths and change the main ads photos. All database operations are wrapped in a try except clause, so in the event of an error, everything will be handled correctly and returned. The functions are also thoroughly validated in case of entering external data that should not be in the database. The transmitted parameters and request body of the request are also validated. Resource ids are converted at the endpoint level, which provides additional validation if someone would like to connect to the endpoint by entering a value other than integer as the resource or subresource id. Thanks to the calculated offset parameter, which receives data for calculations from information sent by the user, the program functions that retrieve data from the database can easily paginate records. The function for adding photos also has the option of changing the name of the added photo, which prevents the photos from being overwritten on the server. If the same user wants to add a photo with the same name, the program will check it and add _2, _3, etc. to the end of the file name. User folders on the server are also created automatically when a photo is added to the server for the first time.


## Features

- Database CRUD functions.
- Validation of data entered into the server.
- Handling various errors and returning the appropriate code status.
- Automatic creation of a user folder on the server.
- Automatic file renaming if required.
- Adding graphic files to the server.
- Deleting grahgic files from the server.
- Downloading graphic files from the server.
- Returning a collection of records in a pagination system.
- Intelligent creation of a query to the database when the user wants to download announcements with specific parameters.


## Technology used

**Server:** 
- Languages: Python, SQL
- Third Party Libraries: Flask, mysql-connector-python, python-dotenv, werkzeug
- Hosting for API: www.pythonanywhere.com
- Hosting for MySQL database: www.pythonanywhere.com


## Installation

### To run API on localhost:

#### Requirements:

##### Programs and libraries:
- Python 3.11.1
- MySQL Server 8.0
- Flask 2.3.2
- mysql-connector-python 8.1.0
- python-dotenv 1.0.0
- werkzeug 2.3.7

##### Environment Variables:

###### To run this project, you will need to add the following environment variables to your .env file:

`DATABASE_HOST`=IP or name of your host (127.0.0.1 or localhost).

`DATABASE_USER`=Your database username.

`DATABASE_PASSWORD`=Your database password.

`DATABASE_DATABASE`=The name of your database.

`UPLOAD_FOLDER`=Path to the created upload folder.

`ALLOWED_EXTENSIONS`=png,jpg,...


##### Tables for database:
- users
- categories
- announcements
- announcements_main_photo
- announcements_media
- conversations
- messages
- favorite_announcements
###### Login to your database and then copy and paste this text into your MySQL Workbench or MySQL Console.
```bash
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(45) NOT NULL,
  `last_name` varchar(45) NOT NULL,
  `email` varchar(100) NOT NULL,
  `login` varchar(45) NOT NULL,
  `password` varchar(45) NOT NULL,
  `date_of_birth` varchar(45) NOT NULL,
  `street` varchar(45) DEFAULT NULL,
  `zip_code` varchar(45) DEFAULT NULL,
  `city` varchar(45) DEFAULT NULL,
  `active_flag` tinyint NOT NULL,
  `creation_account_date` datetime NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email_UNIQUE` (`email`),
  UNIQUE KEY `login_UNIQUE` (`login`)
);
```

```bash
CREATE TABLE `categories` (
  `category_id` int NOT NULL AUTO_INCREMENT,
  `name_category` varchar(45) NOT NULL,
  PRIMARY KEY (`category_id`)
);

INSERT INTO `categories` VALUES (1,'Elektronika'),(2,'Do domu'),(3,'Do ogrodu'),(4,'Sport i turystyka'),(5,'Motoryzacja'),(6,'Zdrowie i uroda'),(7,'Dla dzieci'),(8,'Rolnictwo'),(9,'Nieruchomości'),(10,'Moda'),(11,'Kultura i rozrywka'),(12,'Oddam za darmo');
```

```bash
CREATE TABLE `announcements` (
  `announcement_id` int NOT NULL AUTO_INCREMENT,
  `seller_id` int NOT NULL,
  `category_id` int NOT NULL,
  `title` varchar(45) NOT NULL,
  `description` varchar(400) NOT NULL,
  `price` int NOT NULL,
  `location` varchar(45) NOT NULL,
  `active_flag` tinyint NOT NULL,
  `completed_flag` tinyint NOT NULL,
  `deleted_flag` tinyint NOT NULL,
  `state` varchar(10) NOT NULL,
  `creation_date` datetime NOT NULL,
  `mobile_number` varchar(17) DEFAULT NULL,
  PRIMARY KEY (`announcement_id`),
  KEY `an_sellers_is_users_user_id` (`seller_id`),
  KEY `an_cat_id_is_cat_cat_id` (`category_id`),
  CONSTRAINT `an_cat_id_is_cat_cat_id` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`),
  CONSTRAINT `an_sellers_is_users_user_id` FOREIGN KEY (`seller_id`) REFERENCES `users` (`user_id`)
);
```

```bash
CREATE TABLE `announcements_main_photo` (
  `main_photo_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `announcement_id` int NOT NULL,
  `path` varchar(200) NOT NULL,
  PRIMARY KEY (`main_photo_id`),
  UNIQUE KEY `announcement_id_UNIQUE` (`announcement_id`),
  UNIQUE KEY `path_UNIQUE` (`path`)
);
```

```bash
CREATE TABLE `announcements_media` (
  `media_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `announcement_id` int NOT NULL,
  `path` varchar(200) NOT NULL,
  PRIMARY KEY (`media_id`),
  UNIQUE KEY `path_UNIQUE` (`path`)
);
```

```bash
CREATE TABLE `conversations` (
  `conversation_id` int NOT NULL AUTO_INCREMENT,
  `announcement_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`conversation_id`)
);
```

```bash
CREATE TABLE `messages` (
  `message_id` int NOT NULL AUTO_INCREMENT,
  `conversation_id` int NOT NULL,
  `user_id` int NOT NULL,
  `customer_flag` tinyint NOT NULL,
  `content` varchar(100) NOT NULL,
  `date` datetime NOT NULL,
  PRIMARY KEY (`message_id`)
);
```

```bash
CREATE TABLE `favorite_announcements` (
  `favorite_announcement_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `announcement_id` int NOT NULL,
  PRIMARY KEY (`favorite_announcement_id`)
);
```


#### Instruction:
- Download MySQL Server 8.0, install it on your computer and create a database.
- Optional install mysql workbench for easier database work.
- Create the required tables and add categories into categories database.
- Download Shoper-app-backend repository:
```bash
 git clone https://github.com/Grzegorz96/Shoper-app-backend.git
```
- Create a folder for uploading multimedia in your Shoper-app-backend folder.
- Create .env file in your Shoper-app-backend folder.
- Add the required environment variables to the .env file.
- Install required packages on your venv:
```bash
  pip install -r requirements.txt
```
- or
```bash
  pip install Flask==2.3.2
  pip install mysql-connector-python==8.1.0
  pip install python-dotenv==1.0.0
  pip install werkzeug==2.3.7
```
- Run API.py on Windows:
```bash
 py .\API.py
```
- Run API.py on Linux:
```bash
 python3 API.py
```
- Now your program run on port localhost:5000 u can change port by:
```bash
 app.run(debug=True, port=(set your own port))
```
- If you want connect SHOPER.app program with local backend u need to change endpoints in [Shoper-app-frontend/Backend_requests.py](https://github.com/Grzegorz96/Shoper-app-frontend/blob/master/Backend_requests.py) on:
```bash
 url = "http://localhost:5000/endpoint"
```


## API Reference

#### HTTP GET METHODS:

```http
  GET /media/download
```
| Resource  | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `media`   | `string` | **Required** Getting a photo from the path included in request_body. |

```http
  GET /announcements/<int:announcement_id>/media/paths?main_photo_flag=
```
| Resource        | Type    | Description               | Resource id | Type    | Description                | Parameter | Type    | Description  |
| :--------       | :-------| :-------------------------| :--------   | :-------| :------------------------- | :-------  | :-------| :------------|
| `announcements` | `string`| **Required** Getting a photo paths to announcement from announcements_main_photo or announcements_media tables. | `announcement_id` | `int` | **Required** ID to specify the announcement. | `main_photo_flag` | `int` | **Required** Allowed values: 1/0, specifies whether to get paths from the announcements_media table or from the announcements_main_photo table. |

```http
  GET /users/login
```
| Resource  | Type    | Description                |
| :-------- | :-------| :------------------------- |
| `users`   | `string`| **Required** Getting user data from the users table, using data from the request body. |

```http
  GET /users/<int:user_id>/announcements?active_flag=&per_page=&page=
```
| Resource  | Type    | Description  | Resource id | Type    | Description | Sub-resource | Type    | Description | Parameter | Type | Description  | Parameter | Type | Description | Parameter | Type | Description |
| :-------- | :-------| :------------| :--------   | :-------| :-----------| :--------    | :------- | :----------| :-------- | :-------| :------------| :--------   | :-------| :-----------| :---| :--| :-------|
| `users`   | `string`| **Required** Reference to users resource. | `user_id`| `int`| **Required** ID to specify the user. | `announcements`| `string`| **Required** Getting user's announcements. | `active_flag`| `int`| **Required** Allowed values: 1/0, specifying whether to download active or completed announcements. | `per_page`| `int`| **Required** Allowed values: >0, specifying how many objects to return. | `page`| `int`| **Required** Allowed values: >0, specifying which page to return. |

```http
  GET /users/login-verification
```
| Resource  | Type    | Description                | 
| :-------- | :-------| :------------------------- | 
| `users`   | `string`| **Required** Verification whether the login sent in the request content is included in the data. | 

```http
  GET /users/<int:user_id>/favorite-announcements?active_flag=&per_page=&page=
```
| Resource  | Type | Description | Resource id | Type| Description  | Sub-resource | Type| Description | Parameter | Type | Description  | Parameter | Type | Description | Parameter | Type | Description |
| :--| :--| :-----| :---| :------| :-----| :--------    | :------- | :------| :--------    | :------- | :-----| :--------    | :------- | :-----| :--------    | :------- | :------------------------- |
| `users`   | `string`| **Required** Reference to users resource. | `user_id`| `int`| **Required** ID to specify the user. | `favorite-announcements`| `string`| **Required** Getting user's favorite announcements. | `active_flag`| `int`| **Required** Allowed values: 1/0, specifying whether to download active or completed announcements. | `per_page`| `int`| **Required** Allowed values: >0, specifying how many objects to return. | `page`| `int`| **Required** Allowed values: >0, specifying which page to return. |










































