# ITEM-CATALOG (Costumes)
    In this project we can create own costumes as well as modify the created costumes based on the authorization.Google OAuth2 used for authenticating users.
#### Requirements:
* Vagrant
* Virtual box
* python 
**Note** All softwares are latest version

#### Procedure to run:
1. Install **virtualbox** and after successful install **vagrant**
2. clone or download [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm)
2. Open Git-bash from the location of **vagrantfile** and it is available inside **fullstack-nanodegree-vm** and give command as `vagrant up` and then `vagrant ssh`
3. Move to vagrant folder by `cd /vagrant`
4. Download the **Costumes** project and place this into vagrant folder and change directory to costumes by giving `cd Costumes`
3. Install the required libraries by running `pip install -r requirements.txt`
5. Run python file by command as `python3 costumes.py`
##### Project view:
* To explore running project by open **localhost:5000/** in google chrome or any browser
* To explore json points 
    [json point 1](http://localhost:5000/costumes/5.json)
    [json point 2](http://localhost:5000/costumes.json)
