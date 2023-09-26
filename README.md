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
A function that downloads a file from the server using the submitted path. JSON={"path":string}.
| Resource  | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `media`   | `string` | **Required** Getting a photo from the path included in request_body. |

```http
  GET /announcements/<int:announcement_id>/media/paths?main_photo_flag=
```
A function that downloads a file paths from the database using information from url.
| Resource        | Type    | Description               | Resource id | Type    | Description                | Parameter | Type    | Description  |
| :--------       | :-------| :-------------------------| :--------   | :-------| :------------------------- | :-------  | :-------| :------------|
| `announcements` | `string`| **Required** Getting a photo paths to announcement from announcements_main_photo or announcements_media tables. | `announcement_id` | `int` | **Required** ID to specify the announcement. | `main_photo_flag` | `int` | **Required** Allowed values: 1/0, specifies whether to get paths from the announcements_media table or from the announcements_main_photo table. |

```http
  GET /users/login
```
A function that downloads data about user from the database. JSON={"login_or_email":string, "password":string}.
| Resource  | Type    | Description                |
| :-------- | :-------| :------------------------- |
| `users`   | `string`| **Required** Getting user data from the users table, using data from the request body. |

```http
  GET /users/<int:user_id>/announcements?active_flag=&per_page=&page=
```
A function that downloads user's announcements from the database using information from url.
| Resource  | Type    | Description  | Resource id | Type    | Description | Sub-resource | Type    | Description | Parameter | Type | Description  | Parameter | Type | Description | Parameter | Type | Description |
| :-------- | :-------| :------------| :--------   | :-------| :-----------| :--------    | :------- | :----------| :-------- | :-------| :------------| :--------   | :-------| :-----------| :---| :--| :-------|
| `users`   | `string`| **Required** Reference to users resource. | `user_id`| `int`| **Required** ID to specify the user. | `announcements`| `string`| **Required** Getting user's announcements. | `active_flag`| `int`| **Required** Allowed values: 1/0, specifying whether to download active or completed announcements. | `per_page`| `int`| **Required** Allowed values: >0, specifying how many objects to return. | `page`| `int`| **Required** Allowed values: >0, specifying which page to return. |

```http
  GET /users/login-verification
```
A function that informs the user whether a given login is available. JSON={"login":string}.
| Resource  | Type    | Description                | 
| :-------- | :-------| :------------------------- | 
| `users`   | `string`| **Required** Verification whether the login transmitted in the request body isn't included in the database. | 

```http
  GET /users/<int:user_id>/favorite-announcements?active_flag=&per_page=&page=
```
A function that downloads user's favorite announcements from the database using information from url.
| Resource  | Type | Description | Resource id | Type| Description  | Sub-resource | Type| Description | Parameter | Type | Description  | Parameter | Type | Description | Parameter | Type | Description |
| :--| :--| :-----| :---| :------| :-----| :--------    | :------- | :------| :--------    | :------- | :-----| :--------    | :------- | :-----| :--------    | :------- | :------------------------- |
| `users`   | `string`| **Required** Reference to users resource. | `user_id`| `int`| **Required** ID to specify the user. | `favorite-announcements`| `string`| **Required** Getting user's favorite announcements. | `active_flag`| `int`| **Required** Allowed values: 1/0, specifying whether to download active or completed announcements. | `per_page`| `int`| **Required** Allowed values: >0, specifying how many objects to return. | `page`| `int`| **Required** Allowed values: >0, specifying which page to return. |

```http
  GET /announcements/search?per_page=&page=&q=&l=&c=
```
A function that downloads announcements from the database using information from parameters.
| Resource        | Type    | Description  | Parameter | Type | Description  | Parameter | Type | Description  | Parameter | Type | Description  | Parameter | Type | Description  | Parameter | Type | Description  |
| :--------       | :-------| :------------| :-------- | :----| :------------| :-------- | :----| :------------| :-------- | :----| :------------| :-------- | :----| :------------| :-------- | :----| :------------|
| `announcements` | `string`| **Required** Getting all announcements for specific parameters. | `per_age` | `int`| **Required** Allowed values: >0, specifying how many objects to return. |  `page` | `int`| **Required** Allowed values: >0, specifying which page to return. | `q` | `string`| **Not Required** Specifying the phrase that must be included in the title of the announcements. | `l` | `string`| **Not Required** Specifying the location from which the announcements comes. |  `c` | `int`| **Not Required** Specifying the category number to which the announcements belongs. | 

```http
  GET /users/<int:user_id>/messages
```
A function that downloads user's messages from the database. JSON={"conversation_id":integer, "announcement_id":integer}.
| Resource  | Type    | Description                | Resource id  | Type    | Description                | Sub-resource | Type    | Description                | 
| :-------- | :-------| :------------------------- | :--------    | :-------| :------------------------- | :--------    | :-------| :------------------------- | 
| `users`   | `string`| **Required** Reference to users resource. | `users_id` | `int`| **Required** ID to specify the user. | `messages` | `string`| **Required** Getting messages for a given user when specifying conversation_id or announcement_id in request_body. | 

```http
  GET /users/<int:user_id>/conversations?customer_flag=&per_page=&page=
```
A function that downloads user's conversations from the database using information from url.
| Resource  | Type    | Description | Resource id  | Type    | Description | Sub-resource | Type    | Description | Parameter | Type | Description  | Parameter | Type | Description  | Parameter | Type | Description  |
| :-------- | :-------| :-----------| :--------    | :-------| :-----------| :--------    | :-------| :-----------| :-------- | :----| :----------- | :-------- | :----| :----------- | :-------- | :----| :----------- |
| `users`   | `string`| **Required** Reference to users resource. | `users_id` | `int`| **Required** ID to specify the user. | `conversations` | `string`| **Required** Getting a user's conversation as a buyer or as seller. | `customer_flag` | `int`| **Required** Allowed values: 1/0, specifies whether the user wants to download conversations as a seller or as a buyer. | `per_page` | `int`| **Required** Allowed values: >0, specifying how many objects to return. | `page` | `int`| **Required** Allowed values: >0, specifying which page to return. | 

#### HTTP POST METHODS:

```http
  POST /media/upload/<user_id>?main_photo_flag=&announcement_id=
```
A function that adds a graphic file to the server and its path to the database. FILES={"file":file.jpg}
| Resource | Type    | Description                | Resource id | Type    | Description                | Parameter   | Type    | Description                | Parameter   |    Type |               Description  |
| :--------| :-------| :------------------------- | :--------   | :-------| :------------------------- | :--------   | :-------| :------------------------- | :--------   | :-------| :------------------------- |
| `media`  | `string`| **Required** Upload a graphic file sent in files to the server and save its path in the database. | `user_id`| `int`| **Required** ID to specify the user. |  `main_photo_flag`| `int`| **Required** Allowed values: 1/0, specifying whether the photo should be saved in the database as the main one or not. | `announcement_id`| `int`| **Required** Allowed values: >1, specifying which announcement the uploaded file refers to.|

```http
  POST /users/register
```
A function that adds a user to the database. JSON={"first_name":string, "last_name":string, "email":string, "login":string, "password":string, "date_of_birth:string, "street":string, "zip_code":string, "city":string}.
| Resource  | Type    | Description                | 
| :-------- | :-------| :------------------------- | 
| `users`   | `string`| **Required** Adding a new user to the users table. The data is downloaded from the request body. | 

```http
  POST /users/<int:user_id>/announcements
```
A function that adds announcements to the database. JSON={"title":string, "location":string, "state":string, "mobile_number":string, "description":string, "price":integer, "category_id":integer}.
| Resource  | Type    | Description                | Resource id  | Type    | Description                | Sub-resource | Type    | Description                | 
| :-------- | :-------| :------------------------- | :--------    | :-------| :------------------------- | :--------    | :-------| :------------------------- | 
| `users`   | `string`| **Required** Reference to users resource. | `users_id` | `int`| **Required** ID to specify the user. | `announcements` | `string`| **Required** Adding an announcement by a specific user, with data sent via request body. |

```http
  POST /users/<int:user_id>/favorite-announcements
```
A function that adds favorite announcement to the database. JSON={"announcement_id":integer}.
| Resource  | Type    | Description                | Resource id  | Type    | Description                | Sub-resource | Type    | Description                | 
| :-------- | :-------| :------------------------- | :--------    | :-------| :------------------------- | :--------    | :-------| :------------------------- | 
| `users`   | `string`| **Required** Reference to users resource. | `users_id` | `int`| **Required** ID to specify the user. | `favorite-announcements` | `string`| **Required** Adding the announcement sent in request data to the user's favorites. |

```http
  POST /users/<int:user_id>/messages
```
The function that adds the user's messages to the database also creates conversations for the user if necessary. JSON={"conversation_id":integer, "announcement_id":integer, "customer_flag":bool, "content":string}.
| Resource  | Type    | Description                | Resource id  | Type    | Description                | Sub-resource | Type    | Description                | 
| :-------- | :-------| :------------------------- | :--------    | :-------| :------------------------- | :--------    | :-------| :------------------------- | 
| `users`   | `string`| **Required** Reference to users resource. | `users_id` | `int`| **Required** ID to specify the user. | `messages` | `string`| **Required** Adding a message by a specific user with specific data sent in the request body. |

#### HTTP PATCH METHODS:

```http
  PATCH /users/<int:user_id>
```
A function that updates one value for the user. JSON={"column":string, "value":string}.
| Resource  | Type    | Description                | Resource id  | Type    | Description                | 
| :-------- | :-------| :------------------------- | :--------    | :-------| :------------------------- |
| `users`   | `string`| **Required** Updating a specific user field with data sent in the request body. | `users_id` | `int`| **Required** ID to specify the user. | 

```http
  PATCH /announcements/<int:announcement_id>/complete
```
A function that changes the announcement from active to completed.
| Resource        | Type    | Description                | Resource id  | Type    | Description                | 
| :--------       | :-------| :------------------------- | :--------    | :-------| :------------------------- |
| `announcements` | `string`| **Required** Updating the flag for a given announcement from active to completed. | `announcement_id` | `int`| **Required** ID to specify the announcement. | 

```http
  PATCH /announcements/<int:announcement_id>/restore
```
A function that changes the announcement from completed to active.
| Resource        | Type    | Description                | Resource id  | Type    | Description                | 
| :--------       | :-------| :------------------------- | :--------    | :-------| :------------------------- |
| `announcements` | `string`| **Required** Updating the flag for a given announcement from completed to active. | `announcement_id` | `int`| **Required** ID to specify the announcement. | 

```http
  PATCH /announcements/<int:announcement_id>/delete
```
A function that changes the announcement from completed to deleted.
| Resource        | Type    | Description                | Resource id  | Type    | Description                | 
| :--------       | :-------| :------------------------- | :--------    | :-------| :------------------------- |
| `announcements` | `string`| **Required** Updating the flag for a given announcement from completed to deleted. | `announcement_id` | `int`| **Required** ID to specify the announcement. | 

#### HTTP PUT METHODS:

```http
  PUT /media/switch/<int:user_id>?to_media_flag=&to_main_flag=
```
A function that transfers the path from the photo table to the main photo table and vice versa. JSON={"main_photo_path":string, "media_photo_path":string, "announcement_id":integer}.
| Resource        | Type    | Description                | Resource id  | Type    | Description                | Parameter  | Type    | Description                | Parameter  | Type    | Description                | 
| :--------       | :-------| :------------------------- | :--------    | :-------| :------------------------- | :--------  | :-------| :------------------------- | :--------  | :-------| :------------------------- |
| `media` | `string`| **Required** Deletes a record from one table and creates it in another table. Transferring paths between the announcements_main_photo table and the announcements_media. | `user_id` | `int`| **Required** ID to specify the user who owns the image files. |  `to_media_flag` | `int`| **Required** Allowed values: 1/0, determining whether the user wants to transfer the transmitted paths in request body from main_photo to media. | `to_main_flag` | `int`| **Required** Allowed values: 1/0, determining whether the user wants to transfer the transmitted paths in request_body from media to main_photo.| 

```http
  PUT /announcements/<int:announcement_id>
```
A function that updates the entire announcement record in the database. JSON={"title":string, "location":string, "state":string, "mobile_number":string, "description":string, "price":integer}.
| Resource        | Type    | Description                | Resource id  | Type    | Description                |
| :--------       | :-------| :------------------------- | :--------    | :-------| :------------------------- |
| `announcements` | `string`| **Required** Updating a specific announcement with data sent in the request body. | `announcement_id` | `int`| **Required** ID to define the announcement that is to be updated. | 

#### HTTP DELETE METHODS:

```http
  DELETE /media/delete?main_photo_flag=&path=
```
A function that removes photos from the server and their paths from the database.
| Resource        | Type    | Description                | Parameter  | Type    | Description                | Parameter  | Type    | Description                |
| :--------       | :-------| :------------------------- | :--------  | :-------| :------------------------- | :--------  | :-------| :------------------------- |
| `media` | `string`| **Required** Deleting the photo from the server and its path from the database using the information from the parameters. | `announcement_id` | `int`| **Required** ID to define the announcement that is to be updated. | `main_photo_flag` | `int`| **Required** Allowed values: 1/0, determines whether the user deletes the main photo or not. | `path` | `string`| **Required** Path to the saved photo on the server. |

```http
  DELETE /favorite-announcements/<int:favorite_announcement_id>
```
A function that removes favorite announcements from the database.
| Resource                 | Type    | Description                | Resource id  | Type    | Description                | 
| :--------                | :-------| :------------------------- | :--------    | :-------| :------------------------- | 
| `favorite-announcements` | `string`| **Required** Removing an announcement from the user's favorite announcements. | `favorite-announcement_id` | `int`| **Required** ID to define which favorite announcement to delete. |


## Lessons Learned

Writing a backend for a Shoper project taught me a lot. I learned how to operate on multimedia files via the http protocol. I made sure to validate the entered data and handle each error appropriately. I improved my knowledge of the SQL language, designing tables and the relationships between them was a challenge for me. Initially, the front-end program worked without an API, I had to create the necessary functions and properly connect them to the second program. While writing the program, I had to solve many problems and it was from the Shoper program that I learned the most. I had to create a coherent program that operated on files on the server and data in the database. Any failure on the server should result in failure to perform the operation on the database and vice versa. Everything must work coherently. It took me about 2 months to write a coherently functioning program (frontend + backend + database), during which time my skills and knowledge improved significantly.


## Features to be implemented
- Email verification function by sending a code to email.
- Password recovery and change function via a code sent to email.
- Hashing of user passwords in the database.
- JSON Web Tokens system.


## Authors

- [@Grzegorz96](https://www.github.com/Grzegorz96)


## Contact

E-mail: grzesstrzeszewski@gmail.com


## License

[MIT](https://github.com/Grzegorz96/Shoper-app-backend/blob/master/LICENSE.md)


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
