---
layout: post
title: Building a Secure Node.js API with Docker and Kubernetes
comments: true
tags: [Node.js, Docker, Kubernetes, API Security]
author: Asahluma Tyika
---

Imagine you're developing a Node.js application for a rapidly growing e-commerce platform.  You need to ensure scalability, reliability, and robust security for your API.  This tutorial demonstrates how to containerize your Node.js API using Docker and deploy it securely to a Kubernetes cluster, providing a foundation for a resilient and scalable backend.  We’ll cover building the Docker image, deploying to Kubernetes, and implementing basic security measures.

## Setting Up Your Node.js API

First, let's create a simple Node.js API. We'll use Express.js for this example.  This API will handle a single GET request to the `/api/hello` endpoint.

### Creating the Project

1.  Create a new directory for your project: `mkdir node-api-docker-k8s`
2.  Navigate into the directory: `cd node-api-docker-k8s`
3.  Initialize a Node.js project: `npm init -y`
4.  Install Express.js: `npm install express`

### Writing the API Code

Now, create a file named `index.js` with the following code:


{% highlight javascript linenos %}
const express = require('express');
const app = express();
const port = 3000;

app.get('/api/hello', (req, res) => {
  res.send('Hello from Dockerized Node.js API!');
});

app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
{% endhighlight %}

This simple API listens on port 3000 and responds with "Hello from Dockerized Node.js API!" when a GET request is made to `/api/hello`.

## Containerizing the API with Docker

Next, we'll create a Dockerfile to build a container image of our Node.js application. This ensures consistency across different environments.

### Creating the Dockerfile

Create a file named `Dockerfile` in the same directory as `index.js` with the following content:


{% highlight dockerfile linenos %}
FROM node:16

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD [ "node", "index.js" ]
{% endhighlight %}

This Dockerfile uses a Node.js 16 base image, copies the necessary files, installs dependencies, exposes port 3000, and starts the Node.js application.

### Building the Docker Image

Now, build the Docker image using the following command:


{% highlight bash linenos %}
docker build -t node-api-image .
{% endhighlight %}

This command builds the image and tags it as `node-api-image`.  You can verify the image is built by running `docker images`.


## Deploying to Kubernetes

Now that our API is containerized, let’s deploy it to a Kubernetes cluster.  This allows for easy scaling and management.  We'll use a Kubernetes deployment and service.

### Creating Kubernetes Deployment YAML

Create a file named `deployment.yaml` with the following content:


{% highlight yaml linenos %}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: node-api-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: node-api
  template:
    metadata:
      labels:
        app: node-api
    spec:
      containers:
      - name: node-api-container
        image: node-api-image
        ports:
        - containerPort: 3000
{% endhighlight %}

This YAML file defines a deployment with three replicas of our Node.js API container.

### Creating Kubernetes Service YAML

Next, create a file named `service.yaml` with the following content:


{% highlight yaml linenos %}
apiVersion: v1
kind: Service
metadata:
  name: node-api-service
spec:
  selector:
    app: node-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
{% endhighlight %}

This YAML file defines a service that exposes our deployment on port 80, using a LoadBalancer to provide external access (this requires a cloud provider that supports Load Balancers).

### Deploying to Kubernetes

Now, deploy the application to your Kubernetes cluster using the following commands:


{% highlight bash linenos %}
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
{% endhighlight %}

You can monitor the deployment status using `kubectl get pods` and `kubectl get services`.  You should see three pods running and the service's external IP address.

## Securing the Node.js API

While this example is basic, securing your API is crucial.  We'll explore some basic security measures. For a more comprehensive approach, consider exploring OAuth 2.0 or JWT for authentication and authorization.  [See our guide on securing Node.js applications](https://gtec0.github.io/node-security/).


### Input Validation

Always validate user inputs to prevent injection attacks (e.g., SQL injection).  Express.js middleware can be used for this.

### HTTPS

Use HTTPS to encrypt communication between your API and clients.  This can be achieved with a reverse proxy like Nginx or using a certificate manager in your Kubernetes setup.

### Rate Limiting

Implement rate limiting to prevent abuse and denial-of-service attacks.  Middleware packages are available for this in Node.js.


## Conclusion

In this tutorial, we built a simple Node.js API, containerized it using Docker, and deployed it to a Kubernetes cluster.  We also briefly touched upon fundamental security considerations. This provides a solid base for building a scalable and secure backend service.  Remember to implement more robust security measures for production environments.  Let us know in the comments if you have any questions or suggestions for future tutorials!
