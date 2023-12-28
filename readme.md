# **Project Setup:**

The database files, templates used, project related documents are in folder named "info-docs"

## Setting up MySQL server

1. The database has been exported to the Required data folder in the project file.
2. Create a database by name "website\_tracking\_table" or simply import the database from the folder to MySQL server.
3. Add the following params to the environment variable file (". env").
  1. "DATABASE\_HOST"
  2. "DATABASE\_PORT"
  3. "DATABASE\_PASSWORD"
  4. "DATABASE\_USER"
  5. "DATABASE\_NAME"

## Setting up smtp email functionality

1. Use the "Less secure app" functionality in the account that needs to be used to send email from.
2. Or generate an app password in the account and use that password to operate the project.

1. And fill the following variable in the environment variable file (". env").

  1. "SEND\_EMAIL\_SERVER\_DOMAIN"
  2. "SEND\_EMAIL\_SERVER\_PORT"
  3. "SENDER\_EMAIL"
  4. "SENDER\_PASSWORD"

## Setting up stripe:

1. Create a stripe account.
2. Create 3 products with reoccurring payments. (plans including bronze, silver and gold)
3. Enter the price id in the redirection url in "pricing.html" template.

1. Enter the following variable from the stripe account to the environment variable file. (". env")

  1. "STRIPE\_PUBLIC\_KEY"
  2. "STRIPE\_SECRET\_KEY"

## A sample for what variables ". env" file should contain exists in the project itself by name "required\_env\_variables", copy the file and set the variables in the file.
## Run the project
  1. Create a virtual environment using python virtualenv library.
  2. Activate the environment using command "env\_name/Scripts/activate" (windows)
  3. Install the requirements.txt file ("pip install –r requirements.txt")
  4. Run the project.