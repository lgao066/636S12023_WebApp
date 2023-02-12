# COMP636 S1 2023 Library Web App 

This project is created for COMP636 Summer School 2022 Web Application Final Assessment. A web-based library management system is created for Waikirikiri Library, which can be used to manage books, borrowers and loans.

## Contact

- Author: Li Gao
- Student ID: 1155084
- Email: Li.Gao@lincolnuni.ac.nz

## Getting Started

Instructions on how to install and set up the project on a local machine for development and testing purposes.

### Prerequisites

Assumptions:

1. Physical copies: Hardcover, Paperback, Illustrated; Digital copies (eBooks, Audio Books).
2. Users cannot add a loan for a non-digital copy when another borrower still has that copy (I cannot borrow a particular paperback when another borrower still has it at her house).
3. Users can add a loan for a digital copy any time (regardless of whether it is marked as returned or not returned)
4. All loans have a due date, and can be 'returned', regardless of copy format.

Code management - Code is stored in different locations
1. Local machine: where the code development mainly happens
2. GitHub Repo: where the code is mainly stored and distributed
3. Pythonanywhere: production envrionment, code stored there is stable; DB connection file is different from GitHub

### Installation

Steps:
0. Navigate to folder 636S12023_WebApp

1. Create virtual environment using the following commands
        py -3 -m venv .venv
        source .venv\\Scripts\\activate or navigate to .venv folder and run Scripts\\activate
2. Install the packages
        navigate to the main folder 636S12023_WebApp, and run the following command
        pip install -r requirements.txt

3. Use the virtualenv as python interpreter (otherwise not able to pick up the packages installed inside this virtualenv)

4. Navigate to folder librarywebapp (where app.py is located), and run the following commands
        flask run
        Webapp running on http://127.0.0.1:5000

## Usage

Instructions on how to use the project, including examples of how to run it.


Include a brief project report: 
• Outlining the structure of your solution (routes & functions). This should be brief, but be sure to indicate how your routes and templates relate to each other and what data is being passed between them, do not just give a list of your routes.

• Detailing any assumptions and design decisions that you have made. For example, did you share a page template between public and staff or use two separate pages? Did you detect GET or POST method to determine what page displays? If so, how and why? Note these types of decisions and assumptions as you work.

• A discussion that outlines what changes would be required if your application was to support multiple library branches. This should include: o Changes required to database tables (new tables and modifications to existing tables) o Changes required to the design and implementation of your web app. o (Do not implement these changes in your app.)

This report must be created using GitHub Markdown and saved in the README.md file of your GitHub repository.


Questions:
When we are searching the catalogue and returning the loan information, it is possible for each of digital copies having mutiple loan records (given the they can be borrowed while on loan). Should we display all the loan records for digital copies or just the most recent one?


Error Encountered: 
1. Virtual envrionment cannot be activated
Error messages: Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system. For more information, see about_Execution_Policies at https:/go.microsoft.com/fwlink/?LinkID=135170.
Solution: 
https://www.sharepointdiary.com/2014/03/fix-for-powershell-script-cannot-be-loaded-because-running-scripts-is-disabled-on-this-system.html

Page Template Hiarachy:
base.html => booklist.html

          => basebooksearch.html => publicsearch.html
                                 => staffsearch.html

          => publicbase.html

          => staffbase.html      => addloan.html
                                 => borowerlist.html
                                 => currentloans.html