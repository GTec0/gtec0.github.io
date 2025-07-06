---
layout: post
title: Building a Secure Node.js API with Docker and Kubernetes
comments: true
tags: [Node.js, Docker, Kubernetes, API Security]
author: Asahluma Tyika
---

Imagine you're building a social media app. You've got a fantastic Node.js backend, but deploying it and ensuring its security are causing headaches.  This tutorial will guide you through building a secure Node.js API, containerizing it with Docker, and deploying it to a Kubernetes cluster.  We'll focus on securing the API and automating its deployment using readily available tools. Let's get started!


## Setting up the Node.js API

Our API will be a simple RESTful service with a single endpoint to demonstrate the core concepts.  We'll use Express.js for the framework and a basic authentication mechanism.  We'll also incorporate best practices for security from the start.

First, let's create a new project directory and initialize a Node.js project:

```bash
mkdir node-api
cd node-api
npm init -y
```

Next, install Express.js and a JSON Web Token (JWT) library for authentication:


```bash
npm install express jsonwebtoken
```

Now, let's create a simple `server.js` file:

{% highlight javascript linenos %}
const express = require('express');
const jwt = require('jsonwebtoken');

const app = express();
const port = 3000;

const secretKey = 'your-secret-key'; // **Replace with a strong, randomly generated key in production**

app.use(express.json());

app.post('/login', (req, res) => {
  const { username, password } = req.body;
  // **In a real app, verify credentials against a database**
  if (username === 'user' && password === 'password') {
    const token = jwt.sign({ username }, secretKey);
    res.json({ token });
  } else {
    res.status(401).json({ message: 'Unauthorized' });
  }
});

app.get('/data', (req, res) => {
  const { authorization } = req.headers;
  if (authorization) {
    const token = authorization.split(' ')[1];
    try {
      const decoded = jwt.verify(token, secretKey);
      res.json({ message: 'Protected data', user: decoded.username });
    } catch (error) {
      res.status(401).json({ message: 'Unauthorized' });
    }
  } else {
    res.status(401).json({ message: 'Unauthorized' });
  }
});

app.listen(port, () => console.log(`API listening on port ${port}`));
{% endhighlight %}

Remember to replace `'your-secret-key'` with a strong, randomly generated secret key for production. This simple example illustrates basic JWT authentication.  In a real application, you'd integrate this with a database for user management and authorization.


## Containerizing with Docker

Next, we'll containerize our Node.js API using Docker.  This allows for consistent deployment across different environments.  We'll create a `Dockerfile` in the project root:


{% highlight dockerfile linenos %}
FROM node:16

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD [ "node", "server.js" ]
{% endhighlight %}

This Dockerfile defines a container image based on a Node.js 16 base image, copies our application code, installs dependencies, and sets the port.  Building the image is straightforward:


```bash
docker build -t node-api .
```

Now, run the container to test:

```bash
docker run -p 3000:3000 node-api
```


## Deploying to Kubernetes

Kubernetes provides a robust platform for managing containerized applications.  We'll create a Kubernetes deployment YAML file to automate deployment.  Create a file named `deployment.yaml`:

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
        image: node-api:latest
        ports:
        - containerPort: 3000
{% endhighlight %}

This YAML file defines a deployment of three replicas of our Node.js API container.  Before applying this, make sure you have a Kubernetes cluster running.  Then, apply the deployment:


```bash
kubectl apply -f deployment.yaml
```

Next, expose the deployment using a Kubernetes service:

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

Apply the service definition:


```bash
kubectl apply -f service.yaml
```

This creates a load balancer that distributes traffic across your three API replicas. You'll get an external IP address, which you can use to access your secured Node.js API.  Remember to check your Kubernetes cluster’s documentation for load balancer specifics.  This setup enhances availability and scalability.



## Securing Your Kubernetes Deployment

While Docker provides containerization, securing your Kubernetes deployment is crucial.  Network policies are essential for controlling access within your cluster. Consider implementing Role-Based Access Control (RBAC) to manage user permissions.  Regularly update your Kubernetes components and images to patch security vulnerabilities.  Implement monitoring and logging to detect and respond to security incidents.  Employ secrets management to store sensitive information such as API keys and database credentials securely. This comprehensive approach will solidify your application's security within its deployment environment.


## Conclusion

In this tutorial, we built a secure Node.js API, containerized it using Docker, and deployed it to a Kubernetes cluster.  We covered essential security measures throughout the process, from secure coding practices to Kubernetes-specific security features.  Remember, security is an ongoing process that requires constant vigilance and adaptation.  For more advanced Kubernetes concepts, see our guide on [advanced Kubernetes features](link-to-another-GTEC-post-here).  Share your experiences and ask any questions in the comments below!
