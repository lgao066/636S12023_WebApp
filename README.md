# 636S12023_WebApp
COMP636 S1 2023 Library Web App 

Web Application Project Summer School, 2022

This is readme

Steps:
1. Create virtual environment using the following commands
        py -3 -m venv .venv
        source librarywebapp\\.venv\\Scripts\\activate
2. Install the packages
        pip install -r requirements.txt

3. Use the virtualenv as python interpreter (otherwise not able to pick up the packages installed inside this virtualenv)

Steps:

Create virtual environment using the following commands py -3 -m venv .venv .venv\Scripts\activate.bat
Install the packages pip install -r requirements.txt
Include a brief project report: • Outlining the structure of your solution (routes & functions). This should be brief, but be sure to indicate how your routes and templates relate to each other and what data is being passed between them, do not just give a list of your routes.

• Detailing any assumptions and design decisions that you have made. For example, did you share a page template between public and staff or use two separate pages? Did you detect GET or POST method to determine what page displays? If so, how and why? Note these types of decisions and assumptions as you work.

• A discussion that outlines what changes would be required if your application was to support multiple library branches. This should include: o Changes required to database tables (new tables and modifications to existing tables) o Changes required to the design and implementation of your web app. o (Do not implement these changes in your app.)

This report must be created using GitHub Markdown and saved in the README.md file of your GitHub repository.

First interface (public)
        [Done] List all books available in the library at the /booklist route
        Search Books - Search books by title and/or author
        See the availability of all copies of a book
        
Second interface (staff)

Added navigation panel for public and staff 04/02/2023

Code management - Code is stored in different locations
1. Local machine: where the code development mainly happens
2. GitHub Repo: where the code is mainly stored and distributed
3. Pythonanywhere: production envrionment, code stored there is stable; DB connection file is different from GitHub