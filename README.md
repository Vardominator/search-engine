# Vardo's & Nick's Bada$$ Search Engine

## Python Set Up
### Install Python 3.5+
* Run the following:
  * sudo apt-get update
  * sudo apt-get install python3

### Install Necessary Packages
* Navigate to repository directory
* Run the following:
  * pip install -r requirements.txt

## GUI Set Up
### Install Semantic UI Dependencies
#### Install latest version of node.js
* Run the following:
  * sudo apt-get update
  * sudo apt-get install nodejs
  * sudo apt-get install npm

#### Install latest version of Semantic UI
* Navigate to repository directory
* Run the following:
  * npm install semantic-ui --save

* Select Express Install
* Include all modules
* Leave 'semantic/' as default directory
* Leave default output directory
* Navigate to 'semantic/'
* Run the following:
  * gulp build

#### Install a CORS plugin for your browser to enable local Http requests
* Search 'cors' plugin for you browser and install the most popular one

## Usage
* Run the following:
  * python3 searchengine.py
* Open index.html with favorite browser
* Enjoy a nice glass of rye

## TODOs
### Nick
* Fix Kgram: AND queries
* More phrase query unit test
* Milestone 2:
  * Ranked retrievals
  * Spelling correction
  * Kgram on disk
  * Calculate document weights
### Vardo
* Fix phrase queries
* Toggle modes (index and query) in GUI
* Milestone 2:
  * Build the index
  * Querying the index
  * B+ tree for vocabulary
  * Write index to disk
### Both
* Print ranked retrieval results
* Enjoy a nice glass of rye
