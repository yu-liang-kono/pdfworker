# standard library imports
import os
import os.path
import sys

cwd = os.path.dirname(getBundlePath())
print cwd
if cwd not in sys.path:
    sys.path.append(cwd)
 
# third party related imports

# local library imports
import preview
reload(preview)

def get_all_pdfs():
    """Get all pdfs in the specified directory."""
    
def main():

    preview.open_app()
    
if __name__ == "__main__":
    main()
