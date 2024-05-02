# ../myproject/subfile.py

# Save "hey" into myList
def stuff(threadname, mylist):
     # You have to make the module main available for the 
     # code here.
     # Placing the import inside the function body will
     # usually avoid import cycles - 
     # unless you happen to call this function from 
     # either main or subfile's body (i.e. not from inside a function or method)
     mylist.append("hey")