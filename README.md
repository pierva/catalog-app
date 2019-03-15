# Catalog App

## Get Started
Clone or download the repository, then navigate into the application folder.

Create and activate a virtualenv. The application is designed and tested in Python3. If using virtual machine with vagrant (suggested), jump to the next step:
```sh
$ python3.6 -m venv env
$ source env/bin/activate
```

Install the dependencies (first line for virtual env, second line for virtual machine):
```sh
(env)$ pip3 install -r requirements.txt
pip3 install -r requirements.txt
```
### Create app instance folder
From the downloaded folder (catalog) navigate inside the project folder (named same as the parent folder `catalog`)

```sh
$ cd catalog
```

You should be now in this location:

```sh
vagrant@vagrant:/vagrant/catalog/catalog$
```

Create an instance folder (where the google secret file will be stored):
```sh
$ mkdir instance
```

To enable Google Login:
- create the credentials in the [developer console](https://console.developers.google.com) (make sure to have the proper redirect URIs and javascript origins).
- Download the json file
- Rename it as `g_client_secrets.json`
- Move the file inside the `instance` folder previously created

The content of the file should look similar to this:

```
{
  "web":
    {
      "client_id": "YOUR-ID.apps.googleusercontent.com",
      "project_id": "your-app-name",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_secret": "YOUR-SECRET",
      "redirect_uris": [
          "http://localhost:5000/gCallback",
          "https://localhost:5000/gCallback",
          "http://localhost:5000/catalog"
          ],
      "javascript_origins": [
        "http://localhost:5000",
        "https://localhost:5000"
        ]
    }
}
```


### Set Environment Variables

```sh
$ export APP_SETTINGS="catalog.config.DevelopmentConfig"
```

or

```sh
$ export APP_SETTINGS="catalog.config.ProductionConfig"
```

### Update Settings in Production

1. `SECRET_KEY`
1. `SQLALCHEMY_DATABASE_URI`

### Create DB

```sh
$ python3 manage.py create_db
```

The file manage.py includes also the commands to migrate an existing db, if needed:
```sh
$ python3 manage.py db init
$ python3 manage.py db migrate
```

### Create Admin user (optional)
You can create an admin user by simply running this command:
```sh
$ python3 manage.py create_user
```

### Run the application

```sh
$ python3 manage.py runserver
```

The application in the home page shows a list of categories on the left and by default after opening, the list of recently added items (7) on the right.
To perform any operation other than read, the user needs to be authenticated.
CatalogApp offers two ways of authentication:

1. Local registration with bcrypt password hashing library
2. Google token sign in

The users have the possibility to have admin rights only when registering locally on the app.

### Be aware of
Registration can be done with email or username. It is recommended to use email in order to avoid potential conflicts with Google Login in case of subsequent authentication (for the same user) through Google.
The conflict can happen in case a locally registered user with admin rights, later, decides to use Google Login to access the app.
The user won't be recognized as admin because the search of the user in the database is made through the email address.
If a match is found, the user will have elevated rights (if registered as admin in the database).


Users authenticated with Google Sign In get temporary saved in the database with their username (Name Surname), therefore if they used a username to register to the app during the registration process and have admin rights, after login with Google the admin rights will be disabled.

## App features
The CatalogApp allows authenticated users to create new categories, edit categories, delete categories. All the categories CRUD operations are performed with AJAX calls.


For each category the user can add items, edit existing items and delete items.
Read and Delete items are made with AJAX calls.
Item details are shown in a modal, with the picture associated during the creation.
The buttons to Edit and Delete are visible only to the creator (or admin users) of the category/item. For all the categories and items not created by the current users (if not admin), the buttons are not visible.

The routes are also protected in case the CRUD operations are made from outside the application (i.e. through postman).

### !!! DELETING A CATEGORY !!!
When deleting a category, all the items associated with that category will be deleted as well.

______

## API Endpoints (GET method)

Get all the items in the database:

`/catalog/api/v1/all/JSON`
```javascript
{
Items: [
    {
      category_id: 1,
      category_name: "Electronics",
      description: "Custom made speakers for a crystal clear sound.",
      id: 1,
      name: "Speakers",
      picture: "https://images.unsplash.com/photo-1478145046317-39f10e56b5e9?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=634&q=80d",
      user_id: 1
    },
    {
      category_id: 2,
      category_name: "Racing",
      description: "The most beautiful leather gloves for the true bikers.",
      id: 2,
      name: "Gloves",
      picture: "https://images.unsplash.com/photo-1458642849426-cfb724f15ef7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80",
      user_id: 1
    }
  ]
}
```

Get the list of available categories

`/catalog/api/v1/categories/JSON`
```javascript
{
  Categories: [
    {
      id: 1,
      name: "Electronics",
      user_id: 1
    },
    {
      id: 2,
      name: "Racing",
      user_id: 1
    }
  ]
}
```

Get item details providing item id or item name (using like operator during the query)

`/catalog/api/v1/item/<int:itemId>/JSON` <br>
`/catalog/api/v1/item/<itemName>/JSON`

```javascript
{
  category_id: 2,
  category_name: "Racing",
  description: "The most beautiful leather gloves for the true bikers.",
  id: 2,
  name: "Gloves",
  picture: "https://images.unsplash.com/photo-1458642849426-cfb724f15ef7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80",
  user_id: 1
}
```
In case no item was found:
```javascript
{
  message: "No item found",
  status: 404
}
```

Get items belonging to a specific category
`/catalog/api/v1/items/<categoryName>/JSON`
```javascript
{
  Items: [
    {
      category_id: 2,
      category_name: "Racing",
      description: "dfadaab . dfadqae",
      id: 2,
      name: "Gloves",
      picture: "https://images.unsplash.com/photo-1458642849426-cfb724f15ef7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80",
      user_id: 1
    },
    {
      category_id: 2,
      category_name: "Racing",
      description: "This 4 pint buckle seat will keep you safe even in the toughest situations. Just made for your racing instinct.",
      id: 3,
      name: "4 Point Buckle Seat",
      picture: "https://images.unsplash.com/photo-1538563885443-a9d978f719d7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1365&q=80",
      user_id: 1
    }
  ]
}
```
If the category name doesn't exists, or it doesn't contain any item, it will be returned an empty list.

```javascript
{
  Items: [ ]
}
```

______
## Features to be added
For a better user experience it will be necessary to add the following features to the application:

* Users management page (i.e. Delete Users)
* Password change page
* Password reset page with emailed token (include SMTP)
* Enable POST/PUT/DELETE operations through API for authenticated users


## CatalogApp screenshots

#### Home Page without logged in user
![Alt - Home Page no user](https://drive.google.com/uc?export=download&id=1xq6rw4d9QnjbuH3hOEBOW56pBCHhkhlV)


#### Register User Page
![Alt - Register User Page](https://drive.google.com/uc?export=download&id=1q0eIdbhgi0YjX8S0H0qOXrRgnihnYDtU)


#### Login Page
![Alt - Login page](https://drive.google.com/uc?export=download&id=18d1vbl_0VPiStnr1p6-97uk4nevng97S)

#### Logged user (no admin)
![Alt - Home with no admin user](https://drive.google.com/uc?export=download&id=1WpzyqYmyllCVJXC3sfrEYM5BGl4HO2J-)

#### Add a category
![Alt - Add a category](https://drive.google.com/uc?export=download&id=1DiIIM02MocDo8UOZW67Obf90GuRCJVb9)


#### Add Item
![Alt - Add item](https://drive.google.com/uc?export=download&id=1jd0hG-q_E911eCy7EyczYFNJagvIAXOy)


#### Item Details
![Alt - Item details](https://drive.google.com/uc?export=download&id=1-eT0FZsiI-EnkRO2XBv5DkEKobxLmb4W)


#### Delete Item
![Alt - Delete Item](https://drive.google.com/uc?export=download&id=1Sw5n4QSVGtOoO_kHm_5mn7PpWBBHM904)
