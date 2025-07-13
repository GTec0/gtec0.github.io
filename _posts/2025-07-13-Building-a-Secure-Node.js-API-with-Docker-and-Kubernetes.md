---
layout: post
title: Building a Secure Node.js API with Docker and Kubernetes
comments: true
tags: [Node.js, Docker, Kubernetes, API Security]
author: Asahluma Tyika
---

Imagine you're building a social media app.  You need a robust, scalable backend API to handle user authentication, post creation, and interactions.  This tutorial will guide you through creating a secure Node.js API, containerizing it with Docker, and deploying it to a Kubernetes cluster. We’ll focus on securing the API using environment variables and basic authentication.


## Setting up the Node.js API

We'll start by building a simple Node.js API using Express.js.  This API will have a single endpoint that requires basic authentication.  This is a foundational step in establishing a secure foundation for larger applications.

First, create a new project directory and navigate into it using your terminal:

```bash
mkdir node-api && cd node-api
```

Next, initialize a Node.js project:

```bash
npm init -y
```

Install the necessary packages:

```bash
npm install express basic-auth
```

Now, create an `index.js` file with the following code:

{% highlight javascript linenos %}
const express = require('express');
const basicAuth = require('basic-auth');

const app = express();
const port = 3000;

const users = {
  'admin': 'password'
};

const authenticate = (req, res, next) => {
  const credentials = basicAuth(req);
  if (!credentials || !users[credentials.name] || users[credentials.name] !== credentials.pass) {
    res.setHeader('WWW-Authenticate', 'Basic realm="example"');
    return res.status(401).send('Authentication required.');
  }
  next();
};

app.get('/api/data', authenticate, (req, res) => {
  res.json({ message: 'Protected data' });
});

app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
{% endhighlight %}

This code sets up a simple Express.js server with a protected `/api/data` endpoint.  The `authenticate` middleware function performs basic authentication, checking against a hardcoded username and password in the `users` object.  For a production application, you'd store credentials securely, for example, using environment variables or a secrets management service.


## Containerizing the API with Docker

Next, we'll containerize our Node.js API using Docker.  This allows us to package our application and its dependencies into a single, portable unit.  This greatly simplifies deployment and improves consistency across environments.

Create a `Dockerfile` in the project root directory:

{% highlight dockerfile linenos %}
FROM node:16

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

ENV PORT=3000
ENV USERNAME=admin
ENV PASSWORD=password

EXPOSE 3000

CMD [ "node", "index.js" ]
{% endhighlight %}

This Dockerfile uses a Node.js 16 base image, copies the necessary files, installs dependencies, sets environment variables for the port and authentication credentials, exposes the port, and runs the application.  Note the use of environment variables for security;  never hardcode sensitive information directly into your Dockerfile.

Build the Docker image:

```bash
docker build -t node-api .
```

Run the container:

```bash
docker run -p 3000:3000 node-api
```


## Deploying to Kubernetes

Now, we'll deploy our Dockerized API to a Kubernetes cluster.  Kubernetes is a container orchestration platform that automates deployment, scaling, and management of containerized applications. This allows for easier scaling and management of your API as the application grows.

For this tutorial, we'll assume you have a Kubernetes cluster running (e.g., using Minikube or a cloud provider like Google Kubernetes Engine, Amazon Elastic Kubernetes Service, or Azure Kubernetes Service). You will need kubectl installed and configured to communicate with your cluster.

First, create a Kubernetes deployment YAML file (e.g., `deployment.yaml`):

{% highlight yaml linenos %}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: node-api-deployment
spec:
  replicas: 1
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
        image: node-api:latest
        ports:
        - containerPort: 3000
        env:
        - name: PORT
          value: "3000"
        - name: USERNAME
          value: "admin"
        - name: PASSWORD
          valueFrom:
            secretKeyRef:
              name: node-api-credentials
              key: password
{% endhighlight %}


Then, create a Kubernetes service YAML file (e.g., `service.yaml`):

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
  type: LoadBalancer # Or NodePort depending on your cluster setup
{% endhighlight %}


Create a secret to store the password (replace 'password' with a stronger password):

```bash
kubectl create secret generic node-api-credentials --from-literal=password=password
```

Finally, deploy the application:

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

After applying the YAML files,  check the pods and services status using `kubectl get pods` and `kubectl get services`. You should be able to access your API via the external IP address provided by the Kubernetes service (if using LoadBalancer type).  If using NodePort, you’ll need to access it via the node IP address and the NodePort.


## Securing your Kubernetes Deployment

Remember that this example uses basic authentication, which is not suitable for production environments.  For robust security, consider using OAuth 2.0, JWT (JSON Web Tokens), or other industry-standard authentication and authorization mechanisms.  This is crucial for production-level applications.  Furthermore, explore using Ingress controllers for more advanced routing and security features within your Kubernetes deployment.  Implementing robust security practices is a key aspect of a well-architected DevSecOps pipeline.


## Conclusion

In this tutorial, we built a secure Node.js API, containerized it using Docker, and deployed it to a Kubernetes cluster.  We used environment variables for secure credential management.  Remember to always prioritize security best practices when developing and deploying applications.  Learn more about Kubernetes by checking out [our comprehensive Kubernetes tutorial](https://example.com/kubernetes-tutorial) (replace with actual link if available). Feel free to share your feedback and experiences in the comments below!
