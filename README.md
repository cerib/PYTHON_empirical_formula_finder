# PYTHON_empirical_formula_finder
Finds and prints to a text file a list of formulas that have the empirical notation provided by the user.

# What's an empirical formula?
https://en.wikipedia.org/wiki/Empirical_formula
For example, take the chemical formula of glucose, C6-H12-O6. You can see that the proportion of Hydrogen to Oxygen and Carbon is 2 to 1. So the empirical formula would be C-H2-O

# Motive
This was a friend's old college assignment for his chemical engineering degree. I wanted to see if I was able to do the assignment, provided that I had never worked with python or SQLite before. I didn't solve this to help him, since he had already done it.

# How it works

It reads the orders.txt file and does things according to what is on the file
Example:
BASE_DADOS teste.db - creates database teste.db
CRIAR_TABELAS - creates database tables
CARREGAR compostos.txt - reads what's in compostos.txt and loads the data into the database
REPORT relatorio.txt - opens/ creates file relatorio.txt for appending text
LISTA CH;* - prints to file whatever chemical formula in the database has the empirical formula CH
