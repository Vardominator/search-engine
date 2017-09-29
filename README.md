# search-engine

# GUI
## Installing Semantic UI Dependencies
### Install latest version of node.js
* Run the following:
  * sudo apt-get update
  * sudo apt-get install nodejs
  * sudo apt-get install npm

### Install latest version of Semantic UI
* Go to repository directory
* Run the following:
  * npm install semantic-ui --save

* Select Express Install
* Include all modules
* Leave 'semantic/' as default directory
* Leave default output directory
* Navigate to 'semantic/'
* Run the following:
  * gulp build

### Install a CORS plugin for your browser to enable local Http requests
* Simply search 'cors' for you browser plugin and install the most popular one

### Test by opening semantictest.html
* There should be styled like and share buttons

### Features to add to GUI
* Print Terms button next to Build Index. List terms in left scroll box
* Check if term not in index and return term not found (print in modal)
* Print stem of word below query search bar
* Change Last Query/Documents found table to a horizontal table
* If time permits, seach term and return definition on right scroll box