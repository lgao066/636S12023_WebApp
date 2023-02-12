# COMP636 S1 2023 Library Web App 

This project is created for COMP636 Summer School 2022 Web Application Final Assessment. A web-based library management system is created for Waikirikiri Library, which can be used to manage books, borrowers and loans.

## Contact

- Author: Li Gao
- Student ID: 1155084
- Email: Li.Gao@lincolnuni.ac.nz

## Getting Started

Instructions on how to install and set up the project on a local machine for development and testing purposes.

### Prerequisites

Code management - Code is stored in different locations
1. Local machine: where the code development mainly happens
2. GitHub Repo: where the code is mainly stored and distributed
3. Pythonanywhere: production envrionment, code stored there is stable; DB connection file is different from GitHub

### Installation

Steps:
0. Navigate to folder 636S12023_WebApp

1. Create virtual environment using the following commands
        py -3 -m venv .venv
        .venv\\Scripts\\activate or navigate to .venv folder and run Scripts\\activate
2. Install the packages
        navigate to the main folder 636S12023_WebApp, and run the following command
        pip install -r requirements.txt

3. Use the virtualenv as python interpreter (otherwise not able to pick up the packages installed inside this virtualenv)

4. Navigate to folder librarywebapp (where app.py is located), and run the following commands
        flask run
        Webapp running on http://127.0.0.1:5000

## Project Report: 

### Structure of routes & functions. 

This should be brief, but be sure to indicate how your routes and templates relate to each other and what data is being passed between them, do not just give a list of your routes.

Page Template Hiarachy:
base.html => booklist.html

          => basebooksearch.html => publicsearch.html
                                 => staffsearch.html

          => publicbase.html

          => staffbase.html      => addloan.html
                                 => borowerlist.html
                                 => currentloans.html

### Assumptions and Design Decisions

For example, did you share a page template between public and staff or use two separate pages? Did you detect GET or POST method to determine what page displays? If so, how and why? Note these types of decisions and assumptions as you work.

Assumptions:

1. Physical copies: Hardcover, Paperback, Illustrated; Digital copies (eBooks, Audio Books).
2. Users cannot add a loan for a non-digital copy when another borrower still has that copy (I cannot borrow a particular paperback when another borrower still has it at her house).
3. Users can add a loan for a digital copy any time (regardless of whether it is marked as returned or not returned)
4. All loans have a due date, and can be 'returned', regardless of copy format.

### A discussion that outlines what changes would be required if your application was to support multiple library branches

#### Changes required to database tables (new tables and modifications to existing tables) 

1. Library Branch Information Table: This table will store the information of all branches of the library, such as branch name, address, phone number, etc.

2. Book Information Table: This table will store the information of all books available in the library, such as book title, author, ISBN number, publication date, etc.

3. Member Information Table: This table will store the information of all members who have registered with the library, such as member name, address, phone number, etc.

4. Book Inventory Table: This table will store the information about the availability of books in each branch, such as book title, branch name, availability status, etc.

#### Changes required to the design and implementation of your web app.

1. Branch Selection: A new feature will be added to the web app to allow the users to select the branch from which they want to borrow a book. The app will fetch the data from the "Book Inventory Table" to display the availability of books in the selected branch.

2. Book Request: Members can request books from different branches. The request will be forwarded to the selected branch, and the branch will then update the availability status in the "Book Inventory Table".

3. Book Transfer: A new feature will be added to the app to allow the transfer of books between branches. The app will fetch the data from the "Book Inventory Table" to display the availability of books in different branches.

4. Branch Report: A new report will be added to the app to display the book inventory of each branch. The report will show the total number of books available, total number of books borrowed, and the total number of books requested in each branch.

5. Member Report: A new report will be added to the app to display the borrowing history of each member. The report will show the books borrowed by the member, the date of borrowing, and the date of return.

## Error Encountered

1. Virtual envrionment cannot be activated
Error messages: Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system. For more information, see about_Execution_Policies at https:/go.microsoft.com/fwlink/?LinkID=135170.
Solution: 
https://www.sharepointdiary.com/2014/03/fix-for-powershell-script-cannot-be-loaded-because-running-scripts-is-disabled-on-this-system.html


Questions:
When we are searching the catalogue and returning the loan information, it is possible for each of digital copies having mutiple loan records (given the they can be borrowed while on loan). Should we display all the loan records for digital copies or just the most recent one?