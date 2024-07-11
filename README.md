![shoperlogo](https://github.com/Grzegorz96/Shoper-app-backend/assets/129303867/7b68b20e-006b-47bc-8823-8c00e62282ca)
# API for SHOPER.app

The SHOPER API contains endpoints necessary for the proper operation of the entire project. It supports the database and performs operations on multimedia files located on the server. Using the function, the user can perform any operations related to databases. Thanks to extensive server-side validation, users will not be able to enter information into the database that does not meet the requirements. Files located on the server are also validated, an appropriate user directory is created for each file, and the file itself is verified in detail. In the project, I paid particular attention to the completeness of data and, in case of errors, to returning an appropriate response with an appropriate status code, as well as to optimizing the code related to graphic file management. The program can be run on Windows and Linux systems.


## Table of Contents

- [Description of folders and modules](#Description-of-folders-and-modules)
- [Features](#Features)
- [Technology used](#Technology-used)
- [Installation](#Installation)
- [Lessons learned](#Lessons-learned)
- [Authors](#Authors)
- [Contact](#Contact)
- [License](#License)
- [Screnshoots](#Screnshoots)


## Description of folders and modules

### Core:
/app.py:
- app.py file is the main script for a Flask web application. It first loads environment variables using dotenv, then creates a Flask application object and configures it using the Config class. It registers blueprints defined in the application through the register_blueprints function. Finally, it runs the Flask server on port 5000 in debug mode, which is useful during development.

### Routes:
#### Announcements
/routes/announcements/__init__.py:
- The __init__.py file defines the blueprint for Flask announcements. It imports various views (functions) responsible for operations on advertisements, such as adding, updating, deleting, restoring, marking as completed, and managing favorite advertisements. Then, the blueprint announcements_bp is created and assigned various URL rules that map to the appropriate view functions and specify the HTTP methods that can be used to invoke these functions.

There is a set of files in the /routes/announcements directory, each of which defines a function that handles a specific endpoint in the Flask application. Each of these files contains functions that respond to various ad operations:

##### /routes/announcements/add_announcement.py: Defines a function for adding new announcements.
##### /routes/announcements/add_announcement_to_favorites.py: Contains a function to add announcements to favorites.
##### /routes/announcements/complete_announcement.py: Supports marking announcements as completed.
##### /routes/announcements/delete_announcement.py: Defines a function to delete announcements.
##### /routes/announcements/delete_announcement_from_favorites.py: Contains a function to remove announcements from favorites.
##### /routes/announcements/get_announcements.py: Responsible for searching and returning announcements.
##### /routes/announcements/get_user_announcements.py: Handles retrieving user announcements.
##### /routes/announcements/get_user_favorite_announcements.py: Contains a function to retrieve a user's favorite announcements.
##### /routes/announcements/restore_announcement.py: Supports restoring deleted announcements.
##### /routes/announcements/update_announcement.py: Defines a function to update existing announcements.

#### Media:
/routes/media/__init__.py:
- The __init__.py file defines the blueprint for media operations in a Flask application. It imports various view functions responsible for media file operations, such as uploading, deleting, switching, and downloading media. The media_bp blueprint is then created and assigned various URL rules that map to the appropriate view functions and specify the HTTP methods that can be used to invoke these functions.

Files in the /routes/media directory define functions that handle specific endpoints related to media operations in the Flask application. Each of these files contains a function responsible for different media file operations:

##### /routes/media/delete_media.py: Defines a function for deleting media files.
##### /routes/media/download_media.py: Contains a function responsible for downloading media files.
##### /routes/media/switch_media: Supports the feature of replacing the main photo in the database.
##### /routes/media/switch_media: Defines a function for uploading new media files.

#### Messages:
/routes/messages/__init__.py:
- The __init__.py file defines the blueprint for message-related operations in a Flask application. It imports view functions responsible for getting messages, sending messages, and retrieving conversations. The messages_bp blueprint is created and various URL rules are assigned to it, mapping to the appropriate view functions and specifying the HTTP methods that can be used to invoke these functions.

Files in the /routes/messages directory define functions that handle specific endpoints related to messaging operations in the Flask application:

##### /routes/messages/get_conversations.py: Contains a function to retrieve conversations for a specific user.
##### /routes/messages/get_messages.py: Defines a function for retrieving messages for a specific user. 
##### /routes/messages/send_message.py: Contains a function for sending messages from a specific user.

#### Users:
/routes/users/__init__.py:
- The __init__.py file defines the blueprint for user-related operations in a Flask application. It imports various view functions responsible for functionalities such as user login, login verification, user registration, updating user details, and deleting user accounts. The users_bp blueprint is created and assigned different URL rules that map to the appropriate view functions and specify the HTTP methods that can be used to invoke these functions.

Within the /routes/users directory, each file handles specific endpoints related to user management:
##### /routes/users/delete_user.py: Defines a function for deleting a user account.
##### /routes/users/login_user.py: Contains a function for user login.
##### /routes/users/register_user.py: Defines a function for user registration.
##### /routes/users/update_user.py: Contains a function for updating user details.
##### /routes/users/verify_login.py: Checks whether a given login is free and whether the user can use it to create an account.

### Utils:
/utils/config.py:
- The config.py file defines a configuration object for the Flask application that sets configuration parameters:
##### UPLOAD_FOLDER: Defines where user media files are stored, fetched from environment variables.
##### MAX_CONTENT_LENGTH: Limits file uploads to 3 MB.
##### MAX_FILE_LENGTH: Restricts individual file size within ZIP archives to 200 KB.

/utils/database_connection.py:
- database_connection.py enables connecting to a MySQL database in a Flask application using environment variables for database configuration. It imports mysql.connector for database connectivity and os for accessing environment variables. The database_connect() function retrieves database credentials (DATABASE_HOST, DATABASE_USER, DATABASE_PASSWORD, DATABASE_DATABASE) from environment variables and establishes a connection to the MySQL database. It returns the database connection object for use throughout the application, ensuring secure and configurable database access. This approach centralizes database configuration, enhancing maintainability and security in the application's database interactions.

/utils/register_blueprints.py:
- register_blueprints.py is a script that organizes Flask application routes into modular blueprints for announcements, messages, users, and media. Each blueprint (announcements_bp, messages_bp, users_bp, media_bp) encapsulates related routes, enhancing code organization and scalability. Blueprints are registered with optional URL prefixes (/users, /media) to structure API endpoints logically within the application. This modular approach promotes maintainability and clarity in routing configuration for the Flask application.

/utils/helpers.py:
- The helpers.py file contains functions that support various operations in a Flask application. validation_file_extension validates the extension of uploaded graphic files based on allowed extensions defined in an environment variable. create_query_for_search_engine dynamically creates a database query for searching announcements using additional parameters. create_query_for_getting_messages constructs a query to retrieve messages for a specific conversation ID from the database, converting DATETIME objects to strings for easier handling. These functions facilitate data manipulation, database interaction, and file validation within the Flask application.

/utils/formating.py:
- The formating.py file provides a function to convert an image file to a base64-encoded string using Python's base64 module.

### Media
/media/media_root:
- The folder where all files added by application users are saved.


## Features

- Database CRUD functions.
- Validation of data entered into the server.
- Handling various errors and returning the appropriate code status.
- Automatic creation of a user folder on the server.
- Automatic file renaming if required.
- Adding graphic files to the server.
- Deleting graphic files from the server.
- Downloading graphic files from the server in the form of base 64 and zip file packages.
- Returning a collection of records in a pagination system.
- File upload size validation.
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
- IDE, for example Pycharm
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

`ALLOWED_EXTENSIONS`=jpg,jpeg,png


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
- Go to the Shoper-app-backend directory.
- Open the Shoper-app-backend on your IDE.
- Create a folder for uploading multimedia in your Shoper-app-backend directory.
- Create .env file in your Shoper-app-backend directory.
- Add the required environment variables to the .env file.
- Create virtual enviroment for the project (Windows):
```bash
 py -m venv venv
```
- Create virtual enviroment for the project (Linux):
```bash
 python3 -m venv venv
```
- Activate virtual enviroment (Windows):
```bash
 venv/Scripts/activate.bat
```
- Activate virtual enviroment (Linux):
```bash
 source venv/bin/activate
```
- Install required packages on your activated virtual enviroment:
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
- If you want connect desktop SHOPER.app program with local backend u need to change endpoints in [Shoper-app-frontend/utils/constants.py](https://github.com/Grzegorz96/Shoper-app-frontend/blob/master/utils/constants.py) on:
```bash
 url = "http://localhost:5000/endpoint"
```


## API Reference

#### HTTP GET METHODS:

##### 1. Endpoint to the function for downloading files from the server and returning them as a ZIP package using an announcement identifier from the URL.
```http
  GET /media/download/announcements/<int:announcement_id>
```
| Resource  | Type     | Description                | Sub-resource  | Type     | Description                | Sub-resource id  | Type     | Description  
| :-------- | :------- | :------------------------- | :------------ | :------- | :------------------------- | :--------------- | :------- | :------------------------- |
| `media`   | `string` | **Required**  Reference to media resource. | `announcements` | `string` | **Required**  Reference to annoucements sub-resource. |  `announcement_id` | `int` |  **Required** ID to specify the announcement. |

##### 2. Endpoint to the function that downloads data about user from the database. JSON={"login_or_email":string, "password":string}.
```http
  GET /users/login
```
| Resource  | Type    | Description                |
| :-------- | :-------| :------------------------- |
| `users`   | `string`| **Required**  Reference to users resource. |

##### 3. Endpoint to the function that downloads user's announcements from the database using information from url.
```http
  GET /announcements/users/<int:user_id>?active_flag=&per_page=&page=
```
| Resource  | Type    | Description  | Sub-resource | Type    | Description | Sub-resource id | Type    | Description | Parameter | Type | Description  | Parameter | Type | Description | Parameter | Type | Description |
| :-------- | :-------| :------------| :--------   | :-------| :-----------| :--------    | :------- | :----------| :-------- | :-------| :------------| :--------   | :-------| :-----------| :---| :--| :-------|
| `announcements`   | `string`| **Required** Reference to announcements resource. | `users`| `string`| **Required** Reference to users sub-resource. | `user_id`| `int`| **Required** ID to specify the user. | `active_flag`| `int`| **Required** Allowed values: 1/0, specifying whether to download active or completed announcements. | `per_page`| `int`| **Required** Allowed values: >0, specifying how many objects to return. | `page`| `int`| **Required** Allowed values: >0, specifying which page to return. |

##### 4. Endpoint to the function that informs the user whether a given login is available. JSON={"login":string}.
```http
  GET /users/login-verification
```
| Resource  | Type    | Description                | 
| :-------- | :-------| :------------------------- | 
| `users`   | `string`| **Required** Reference to users resource. | 

##### 5. Endpoint to the function that downloads user's favorite announcements from the database using information from url.
```http
  GET /favorite-announcements/users/<int:user_id>?active_flag=&per_page=&page=
```
| Resource  | Type | Description | Sub-resource | Type | Description  | Sub-resource id | Type| Description | Parameter | Type | Description  | Parameter | Type | Description | Parameter | Type | Description |
| :--| :--| :-----| :---| :------| :-----| :--------    | :------- | :------| :--------    | :------- | :-----| :--------    | :------- | :-----| :--------    | :------- | :------------------------- |
| `favorite-announcements`   | `string`| **Required** Reference to favorite-announcements resource. | `users`| `string`| **Required** Reference to users sub-resource. | `user_id`| `int` | **Required** ID to specify the user. | `active_flag`| `int`| **Required** Allowed values: 1/0, specifying whether to download active or completed announcements. | `per_page`| `int`| **Required** Allowed values: >0, specifying how many objects to return. | `page`| `int`| **Required** Allowed values: >0, specifying which page to return. |

##### 6. Endpoint to the function that downloads announcements from the database using information from parameters.
```http
  GET /announcements/search?per_page=&page=&q=&l=&c=
```
| Resource        | Type    | Description  | Parameter | Type | Description  | Parameter | Type | Description  | Parameter | Type | Description  | Parameter | Type | Description  | Parameter | Type | Description  |
| :--------       | :-------| :------------| :-------- | :----| :------------| :-------- | :----| :------------| :-------- | :----| :------------| :-------- | :----| :------------| :-------- | :----| :------------|
| `announcements` | `string`| **Required**  Reference to announcements resource. | `per_page` | `int`| **Required** Allowed values: >0, specifying how many objects to return. |  `page` | `int`| **Required** Allowed values: >0, specifying which page to return. | `q` | `string`| **Not Required** Specifying the phrase that must be included in the title of the announcements. | `l` | `string`| **Not Required** Specifying the location from which the announcements comes. |  `c` | `int`| **Not Required** Specifying the category number to which the announcements belongs. | 

##### 7. Endpoint to the function that downloads messages from the database for a given user when specifying conversation_id or announcement_id in request_body. JSON={"conversation_id":integer, "announcement_id":integer}.
```http
  GET /messages/users/<int:user_id>
```
| Resource  | Type    | Description                | Sub-resource  | Type    | Description                | Sub-resource id | Type    | Description            | 
| :-------- | :-------| :------------------------- | :--------     | :-------| :------------------------- | :--------       | :-------| :----------------------| 
| `messages`   | `string`| **Required** Reference to messages resource. | `users` | `string`| **Required** Reference to users sub-resource. | `user_id` | `int`| **Required** ID to specify the user.| 

##### 8. Endpoint to the function that downloads user's conversations from the database using information from url as a customer and seller.
```http
  GET /conversations/users/<int:user_id>?customer_flag=&per_page=&page=
```
| Resource  | Type    | Description | Resource id  | Type    | Description | Sub-resource | Type    | Description | Parameter | Type | Description  | Parameter | Type | Description  | Parameter | Type | Description  |
| :-------- | :-------| :-----------| :--------    | :-------| :-----------| :--------    | :-------| :-----------| :-------- | :----| :----------- | :-------- | :----| :----------- | :-------- | :----| :----------- |
| `conversations`   | `string`| **Required** Reference to conversations resource. | `users` | `string`| **Required** Reference to users sub-resource. | `user_id` | `int`| **Required** ID to specify the user. | `customer_flag` | `int`| **Required** Allowed values: 1/0, specifies whether the user wants to download conversations as a seller or as a customer. | `per_page` | `int`| **Required** Allowed values: >0, specifying how many objects to return. | `page` | `int`| **Required** Allowed values: >0, specifying which page to return. | 

#### HTTP POST METHODS:

##### 1. Endpoint to the function that validates, unpacks the zip package with graphic files and then adds them to the database and server. files={"file": ("images.zip", zip_buffer, "application/zip")}, DATA={"main_photo_index":integer, "announcement_id":integer}
```http
  POST /media/upload/users/<user_id> 
```
| Resource | Type    | Description                | Sub-resource | Type    | Description                | Sub-resource id | Type    | Description                 | 
| :--------| :-------| :------------------------- | :--------    | :-------| :------------------------- | :--------       | :-------| :-------------------------  |
| `media`  | `string`| **Required** Reference to media resource. | `users`| `string`| **Required** Reference to users sub-resource.| `user_id`| `int`| **Required** ID to specify the user. | 

##### 2. Endpoint to the function that adds a user to the database. JSON={"first_name":string, "last_name":string, "email":string, "login":string, "password":string, "date_of_birth:string, "street":string, "zip_code":string, "city":string}.
```http
  POST /users/register
```
| Resource  | Type    | Description                | 
| :-------- | :-------| :------------------------- | 
| `users`   | `string`| **Required** Reference to users resource.| 

##### 3. Endpoint to the function that adds announcements to the database for specific user. JSON={"title":string, "location":string, "state":string, "mobile_number":string, "description":string, "price":integer, "category_id":integer}.
```http
  POST /announcements/users/<int:user_id>
```
| Resource  | Type    | Description                | Sub-resource  | Type    | Description                | Sub-resource id | Type    | Description                | 
| :-------- | :-------| :------------------------- | :--------    | :-------| :------------------------- | :--------    | :-------| :------------------------- | 
| `announcements`   | `string`| **Required** Reference to announcements resource. | `users` | `string`| **Required** Reference to users sub-resource. | `user_id` | `int` |  **Required** ID to specify the user. |

##### 4. Endpoint to the function that adds favorite announcement to the database. JSON={"announcement_id":integer}.
```http
  POST /favorite-announcements/users/<int:user_id>
```
| Resource  | Type    | Description                | Sub-Resource | Type    | Description                | Sub-resource id | Type    | Description                | 
| :-------- | :-------| :------------------------- | :--------    | :-------| :------------------------- | :--------    | :-------| :------------------------- | 
| `favorite-announcements`   | `string`| **Required** Reference to favorite-announcements resource. | `users` | `string`| **Required** Reference to users sub-resource. | `user_id` | `int`| **Required** ID to specify the user. |

##### 5. Endpoint to the function that adds the user's messages to the database also creates conversations for the user if necessary. JSON={"conversation_id":integer, "announcement_id":integer, "customer_flag":bool, "content":string}.
```http
  POST /messages/users/<int:user_id>
```
| Resource  | Type    | Description                | Sub-Resource | Type    | Description                | Sub-resource id | Type    | Description                | 
| :-------- | :-------| :------------------------- | :--------    | :-------| :------------------------- | :--------    | :-------| :------------------------- | 
| `messages`| `string`| **Required** Reference to messages resource. | `users_id` | `int`|**Required** Reference to users sub-resource. | `user_id` | `int`| **Required** ID to specify the user. |

#### HTTP PATCH METHODS:

##### 1. Endpoint to the function that updates one value for the specific user. JSON={"column":string, "value":string}.
```http
  PATCH /users/<int:user_id>
```
| Resource  | Type    | Description                | Resource id  | Type    | Description                | 
| :-------- | :-------| :------------------------- | :--------    | :-------| :------------------------- |
| `users`   | `string`|  **Required** Reference users resource.  | `users_id` | `int`| **Required** ID to specify the user. | 

##### 2. Endpoint to the function that changes the specific announcement from active to completed. Updating the flag for a given announcement from active to completed.
```http
  PATCH /announcements/<int:announcement_id>/complete
```
| Resource        | Type    | Description                | Resource id  | Type    | Description                | 
| :--------       | :-------| :------------------------- | :--------    | :-------| :------------------------- |
| `announcements` | `string`| **Required** Reference announcements resource. | `announcement_id` | `int`| **Required** ID to specify the announcement. | 

##### 3. Endpoint to the function that changes the specific announcement from completed to active. Updating the flag for a given announcement from completed to active.
```http
  PATCH /announcements/<int:announcement_id>/restore
```
| Resource        | Type    | Description                | Resource id  | Type    | Description                | 
| :--------       | :-------| :------------------------- | :--------    | :-------| :------------------------- |
| `announcements` | `string`| **Required** Reference announcements resource. | `announcement_id` | `int`| **Required** ID to specify the announcement. | 

##### 4. Endpoint to the function that changes the specific announcement from completed to deleted. Updating the flag for a given announcement from completed to deleted.
```http
  PATCH /announcements/<int:announcement_id>/delete
```
| Resource        | Type    | Description                | Resource id  | Type    | Description                | 
| :--------       | :-------| :------------------------- | :--------    | :-------| :------------------------- |
| `announcements` | `string`| **Required** Reference announcements resource. | `announcement_id` | `int`| **Required** ID to specify the announcement. | 

#### HTTP PUT METHODS:

##### 1. Endpoint to the function that transfers the path from announcements_media to the announcements_main_photo table and vice versa for specific announcement. JSON={"main_photo_filename":string, "media_photo_filename":string, "announcement_id":integer}.
```http
  PUT /media/switch/users/<int:user_id>
```
| Resource  | Type    | Description                | Sub-resource | Type    | Description                | Sub-resource id | Type    | Description                |  
| :-------- | :-------| :------------------------- | :--------    | :-------| :------------------------- | :--------    | :-------| :------------------------- | 
| `media`   | `string`| **Required** Reference media resource.  | `users` | `string`| **Required** Reference users sub-resource. |  `user_id` | `int`|  **Required** ID to specify the user. |  

##### 2. Endpoint to the function that updates the entire announcement record in the database. JSON={"title":string, "location":string, "state":string, "mobile_number":string, "description":string, "price":integer}.
```http
  PUT /announcements/<int:announcement_id>
```
| Resource        | Type    | Description                | Resource id  | Type    | Description                |
| :--------       | :-------| :------------------------- | :--------    | :-------| :------------------------- |
| `announcements` | `string`| **Required** Reference announcements resource. | `announcement_id` | `int`| **Required** ID to define the announcement that is to be updated. | 

#### HTTP DELETE METHODS:

##### 1. Endpoint to the function that removes photos from the server and their paths from the database. JSON={"files": {"filename":string, "is_main_photo":bool}, ...}
```http
  DELETE /media/delete/users/<int:user_id>
```
| Resource        | Type    | Description                | Sub-resource  | Type    | Description                | Sub-resource id  | Type    | Description       |
| :--------       | :-------| :------------------------- | :--------  | :-------| :------------------------- | :--------  | :-------| :------------------------- |
| `media` | `string`| **Required** Reference media resource. | `users` | `string`|  **Required** Reference users sub-resource. | `user_id` | `int`| **Required** ID to specify the user. |

##### 2. Endpoint to the function that removes favorite announcements from the database for specific favorite announcement.
```http
  DELETE /favorite-announcements/<int:favorite_announcement_id>
```
| Resource                 | Type    | Description                | Resource id  | Type    | Description                | 
| :--------                | :-------| :------------------------- | :--------    | :-------| :------------------------- | 
| `favorite-announcements` | `string`| **Required** Reference favorite-announcements resource. | `favorite_announcement_id` | `int`| **Required** ID to define which favorite announcement to delete. |

##### 3. Endpoint to the function that sets a specific user's active flag to 0, resulting in their account being disabled.
```http
  DELETE /users/<int:user_id>
```
| Resource                 | Type    | Description                | Resource id  | Type    | Description                | 
| :--------                | :-------| :------------------------- | :--------    | :-------| :------------------------- | 
| `users` | `string`| **Required** Reference users resource. | `user_id` | `int`| **Required** ID to specify the user. |

## Lessons learned

Writing a backend for a Shoper project taught me a lot. I learned how to operate on multimedia files via the http protocol. I made sure to validate the entered data and handle each error appropriately. I improved my knowledge of the SQL language, designing tables and the relationships between them was a challenge for me. Initially, the front-end program worked without an API, I had to create the necessary functions and properly connect them to the second program. While writing the program, I had to solve many problems and it was from the Shoper program that I learned the most. I had to create a coherent program that operated on files on the server and data in the database. Any failure on the server should result in failure to perform the operation on the database and vice versa. Everything must work coherently. I had to redesign the logic of file operations on the server, the previous logic was too poorly optimized, which resulted in a very long waiting time for downloading and sending multimedia files in production. I have optimized it by reducing the number of queries, all graphic files are sent and received in a zip package and the main photos for advertisements are attached in the response along with the advertisements in base 64 format. I had to implement a backend application with database on a cloud server. It took me about 3 months to write a coherently functioning program (frontend + backend + database), during which time my skills and knowledge improved significantly.


## Features to be implemented
- Email verification function by sending a code to email.
- Password recovery and change function via a code sent to email.
- Hashing of user passwords in the database.
- JSON Web Tokens system.


## Authors

[@Grzegorz96](https://www.github.com/Grzegorz96)


## Contact

E-mail: grzesstrzeszewski@gmail.com


## License

[AGPL-3.0 license](https://github.com/Grzegorz96/Shoper-app-backend/blob/master/LICENSE.md)

## Screnshoots
##### Users table
![users](https://github.com/Grzegorz96/Shoper-app-backend/assets/129303867/3b2578d9-aa49-43b6-a0f1-146b41f43851)
##### Announcements table
![announcements](https://github.com/Grzegorz96/Shoper-app-backend/assets/129303867/5de0d0d4-0d70-4333-b139-a09881e523cb)
##### Categories table
![categories](https://github.com/Grzegorz96/Shoper-app-backend/assets/129303867/2f781a78-7133-44e8-b348-b2b142b3c070)
##### Favorite_announcements table
![fav_ann](https://github.com/Grzegorz96/Shoper-app-backend/assets/129303867/9d3d90bb-d93c-432f-b519-b52bf1bc4c72)
##### Conversations table
![conv](https://github.com/Grzegorz96/Shoper-app-backend/assets/129303867/fda14cc4-8947-4518-a51f-9969d252601e)
##### Messages table
![messeges](https://github.com/Grzegorz96/Shoper-app-backend/assets/129303867/e04c2e39-d997-47d6-8270-92c758712041)
##### Announcements_main_photo table
![main_photo](https://github.com/Grzegorz96/Shoper-app-backend/assets/129303867/986415d9-bfdb-4171-b7b5-6ec5b0af3aec)
##### Announcements_media table
![media](https://github.com/Grzegorz96/Shoper-app-backend/assets/129303867/7af51079-8906-4dc0-8093-c132a2d81153)
