This is just a script I wrote for studyng so that I can create VPCs on the fly without clicking like a mad man.  Might expand it later to include EC2 boxes.  We will see.

All you have to do now is just run 

    python create_from_yaml.py -y .\networks_to_create.yaml

to create the networks listed in the yaml file.

To delete the networks just run

    python auto_delete_vpc_file.py -j .\{{JSON_FILE_TO_LOAD}}.json

This deletion file is created automatically from the first script.  If you get 200s for the output of the deletion file then it worked.  

Assumes you have AWS creds already setup.

