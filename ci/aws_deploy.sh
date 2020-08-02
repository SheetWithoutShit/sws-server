# install aws cli
pip install awscli
export PATH=$PATH:$HOME/.local/bin

# install aws cli dependency
add-apt-repository ppa:eugenesan/ppa
apt-get update
apt-get install jq -y

# install ecs-deploy
curl https://raw.githubusercontent.com/silinternational/ecs-deploy/master/ecs-deploy | \
  sudo tee -a /usr/bin/ecs-deploy
sudo chmod +x /usr/bin/ecs-deploy

# login AWS ECR
eval $(aws ecr get-login --no-include-email --region $AWS_DEFAULT_REGION)

# build docker images and push to ECR
docker build -t sws-server .
docker tag sws-server:latest $AWS_ECR:latest
docker push $AWS_ECR:latest

# update an AWS ECS service with the new image
ecs-deploy -c $AWS_ECS_CLUSTER -n $AWS_ECS_SERVICE -i $AWS_ECR:latest
