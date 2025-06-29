---
layout: post
title: Building a Secure Node.js API with Docker and HTTPS
comments: true
tags: [Node.js, Docker, HTTPS, API Security]
author: Asahluma Tyika
---

Imagine this: you've painstakingly crafted a fantastic Node.js API, brimming with innovative features.  You're ready to deploy it to the world, but a nagging worry creeps in: security. How do you ensure your API remains robust against attacks and unauthorized access? This tutorial will guide you through building a secure Node.js API, containerizing it with Docker, and securing it with HTTPS using a self-signed certificate.  We'll cover the entire process, from setting up the API to deploying it in a secure manner.


## Setting up the Node.js API

First, let's create a basic Node.js API. We'll use Express.js, a popular framework for building web applications and APIs.  This will form the foundation of our secure application.

1.  Create a new project directory: `mkdir node-api-secure` and navigate into it: `cd node-api-secure`.
2.  Initialize a Node.js project: `npm init -y`.
3.  Install Express.js: `npm install express`.


Now, let's create our `server.js` file:

{% highlight javascript linenos %}
const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.send('Hello from a secure Node.js API!');
});

app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
{% endhighlight %}

This simple API responds with a "Hello" message to any GET request on the root path.  We will enhance its security significantly in the next steps.


## Containerizing with Docker

Next, we will containerize our Node.js API using Docker. This allows for consistent and reproducible deployments across various environments. Docker significantly simplifies deployment and enhances security by isolating our application.

1.  Create a `Dockerfile` in your project's root directory:

{% highlight dockerfile linenos %}
FROM node:18

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD [ "node", "server.js" ]
{% endhighlight %}

This `Dockerfile` sets up a Node.js 18 based image, copies our project files, installs dependencies, and exposes port 3000.


2.  Build the Docker image: `docker build -t node-api-secure .`.  The `. ` refers to the current directory.


3.  Run the Docker container: `docker run -p 3000:3000 node-api-secure`.  This maps port 3000 on your host machine to port 3000 in the container.  Now you should be able to access your API at `http://localhost:3000`.



## Securing with HTTPS using a Self-Signed Certificate

Currently, our API is accessible via HTTP, which is insecure. Let's secure it with HTTPS using a self-signed certificate.  While self-signed certificates are suitable for development and testing, for production environments, you should obtain a certificate from a trusted Certificate Authority (CA).

1.  Generate a self-signed certificate using OpenSSL:

```bash
openssl req -x509 -newkey rsa:4096 -nodes -keyout key.pem -out cert.pem -days 365 -subj "/C=US/ST=CA/L=SanFrancisco/O=MyOrg/CN=localhost"
```

This command generates a private key (`key.pem`) and a self-signed certificate (`cert.pem`).  Remember to replace the subject information (`/C=US/...`) with your own details.

2.  Modify the `server.js` file to use HTTPS:

{% highlight javascript linenos %}
const express = require('express');
const https = require('https');
const fs = require('fs');
const app = express();
const port = 3000;

const privateKey = fs.readFileSync('./key.pem', 'utf8');
const certificate = fs.readFileSync('./cert.pem', 'utf8');

const credentials = {
  key: privateKey,
  cert: certificate,
};

const httpsServer = https.createServer(credentials, app);

app.get('/', (req, res) => {
  res.send('Hello from a secure Node.js API!');
});

httpsServer.listen(port, () => {
  console.log(`HTTPS server listening on port ${port}`);
});
{% endhighlight %}

This revised code loads the private key and certificate, and uses the `https.createServer` method to start an HTTPS server.


3. Rebuild the Docker image and run the container again, mapping port 3000 as before.  You should now be able to access your API securely via HTTPS at `https://localhost:3000`.  Your browser might show a security warning about the self-signed certificate – that's expected.


##  Deployment and Further Enhancements: A DevSecOps Approach


Deploying your secured containerized Node.js application can be done in multiple ways—using Kubernetes for orchestration is highly recommended for production, but for now, `docker run` offers a simple setup.  For enhanced DevSecOps, consider adding automated testing and integration with tools like GitHub Actions for continuous integration and continuous deployment (CI/CD).   [See our guide on CI/CD](https://gtec0.github.io/cicd-guide/) for more details.


![Dockerized App Architecture](docker-architecture.png)


Remember that while a self-signed certificate is sufficient for development, for production, obtaining a certificate from a trusted Certificate Authority is crucial for user trust and security.  This entire process—from the development of the API to its secure deployment—demonstrates a vital component of a strong DevSecOps pipeline.


## Conclusion

This tutorial demonstrated how to build a secure Node.js API, containerize it using Docker, and protect it with HTTPS using a self-signed certificate.  We've touched upon the crucial aspects of securing your applications and deploying them in a secure environment.  Remember to always prioritize security throughout your development lifecycle.  Feel free to share your thoughts and experiences in the comments below!  For more advanced Docker and Kubernetes tutorials, please visit the GTEC homepage.
