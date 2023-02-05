# Data Infra home assignment

The home assignment contains: 

1) a basic HTML frontend generating random purchase request and showing all requests made by
2) customer-facing API that receive:
 * POST requests with purchase json and send them to Kafka
 * GET request with userid that is forwarded to the customer-manager web server.
3) customer-manager web server that handles the purchase insertion and retrieval request using Mongo. 
* consume purchase events from Kafka and insert them to Mongo
* handle GET requests from the customer-facing API, retrieve the data from Mongo and return.

## prerequisite
* brew install kompose
* brew install minikube
minikube start --driver='hyperkit' && nminikube addons enable ingress && minikube addons enable ingress-dns

## Installation

Git clone this repository.

cd into it and into the /installation directory.

create "ironsource" namespace and set it as context
```bash
kubectl create ns ironsource
kubectl config set-context --current --namespace=ironsource
```

generate YAML files from the docker-compose file and apply them

```bash
kompose convert -f ../docker-compose.yaml
k apply -f .
```

### Access the Frontend 
To access the a small complication is needed, because I'm using minikube and not hosted kubernetes.

Edit the /etc/hosts file using sudo 
```bash
sudo vim /etc/hosts
```

And the line
```bash
127.0.0.1 customer-facing-api.com
```
to the end of the file


## Usage

To access the frontend:
to make the frontend accessbile:
```bash
minikube tunnel
kubectl port-forward service/frontend 8002:8002
```

Requests snippets:
```bash
curl --location --request POST "http://customer-facing-api.com/buy" \
--header "Content-Type: application/json" \
--data-raw "{
    \"username\": \"tom\",
    \"userid\": \"1\",
    \"price\": 100,
    \"timestamp\": 1675587178
}"

curl --location --request GET "http://customer-facing-api.com/getAllUserBuys/1"
```
