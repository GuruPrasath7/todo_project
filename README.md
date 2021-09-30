# ToDo list application 
ToDo List application APIs

Todo list application with simple CRUD and user management consists of Signup and Login APIs, and it is deployed in Heroku

# Setup Instructions
__Steps__

1. Install Required Packages for Server  
   
        sudo 	apt-get install python3  
        
        sudo 	apt-get install python3-pip python3-dev libpq-dev postgresql postgresql-contrib
        
        sudo 	pip3 install virtualenv
    
2. Setup Postgres on Server

    Create Postgresql database

        sudo su – postgres
          
        createdb <dbname>  
        
    Create PostgreSQL Roles  
    
        createuser <username> --pwprompt  
        
    Connect to psql Mode  
    
        psql  
        
    Connect to the Database  
    
        \c <dbname> 
        
    Grant all privileges on the table <dbname> to the user <username>
      
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO <dbuser>;

3. Django Environment Setup
    
        virtualenv -p python3 env_name 
        
        source env_name/bin/activate
        
        pip install -r requirements.txt

4. Run Server
    
        python manage.py migrate            # to migrate all the migrations
 
        python manage.py setup_backend      # to create an oauth application
                
        python manage.py runserver          # to run the server

5. API Explanation
    
        /api/signup/           POST        # Signup API
 
        /api/login/            POST        # Login API returns AccessToken.
                                           # The token has to be added in headers as Bearer token.

        /api/todo/             GET         # API to get the todo tasks with filters

        /api/todo/             POST        # API to add a todo task

        /api/todo/             DELETE      # API to delete todo tasks

        /api/todo/{todo_id}/   GET         # API to get details of a particular todo task

        /api/todo/{todo_id}/   PUT         # API to update details of a particular todo task

6. SWAGGER API Documentation Link:

         https://todo-project-django.herokuapp.com/api/swagger/api-doc/

7. DJANGO SUPER ADMIN CREDENTIALS:
   
         USERNAME: superadmin@gmail.com
         PASSWORD: password