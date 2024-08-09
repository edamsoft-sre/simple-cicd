# A Simple CICD
### Fast API end to end Build, Deploy on Kubernetes

## Build

1. Commit latest changes to FastAPI webapp
2. Run shell build script:
    
       ./build.sh <build_number> 
3. This will generate a new AMD64/Linux image and push it to github.io by default.
   The timestamp and build_number are saved in builds/ directory for reference.

## Deploy

1. Set environment variables:

* KUBE_CONFIG_PATH
* GITHUB_TOKEN
* Login to github in shell using the same personal access token with rights to repo and PR

2. Install deploy script dependencies:

       poetry add typer 

3. Run the deploy Python script:

        ./deploy_version.py <image_tag> <PR feature name>



> 



* Pull the latest main from Github. 
  * For future can use clone_repo method to create a standalone repo. This is not 
    used since I have Terraform state file locally in my repo copy.
* Creates a new branch with default prefix. 
  * This can be changed with CLI param
* Updates the Terraform variable **image_name** in **deploy.tfvars**
* Push the new branch with changes
* Run Terraform Plan
* If plan is successful, create a PR with the plan output
* Print the Github PR URL


## Finalize Deploy 

Currently, an operator must pull the latest changes after PR merge to and run terraform apply sinc the TF state is 
local in this example.


     git checkout main
     git pull
     terraform apply -auto-approve
