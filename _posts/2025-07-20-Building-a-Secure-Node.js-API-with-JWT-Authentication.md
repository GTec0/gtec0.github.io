---
layout: post
title: Building a Secure Node.js API with JWT Authentication
comments: true
tags: [Node.js, JWT, API Security, Authentication]
author: Asahluma Tyika
---

Imagine you're developing a social media application.  User accounts, posts, and interactions are all critical data needing protection.  This tutorial will guide you through building a secure Node.js API using JSON Web Tokens (JWTs) for authentication, ensuring only authorized users can access your application's resources.  We'll combine Node.js with Express.js for the backend and Postman for testing.


## Setting up the Node.js Project

First, we'll create the foundation for our Node.js API.  This involves setting up a project directory, initializing it with npm, and installing the necessary packages.

1. Create a new directory for your project: `mkdir node-api-jwt` and navigate into it: `cd node-api-jwt`.

2. Initialize the project using npm: `npm init -y`. This creates a `package.json` file.

3. Install the required packages: `npm install express jsonwebtoken bcryptjs body-parser`.  We'll use Express.js for routing, jsonwebtoken for JWT generation and verification, bcryptjs for password hashing, and body-parser for parsing request bodies.

Now, let's create the server file.


## Creating the API Server with Express.js

We will now construct the core of our API using Express.js, handling user registration and login functionalities.

Create a file named `server.js` and add the following code:

{% highlight javascript linenos %}
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

const users = []; // In-memory user database (replace with a real database later)

app.post('/register', async (req, res) => {
  try {
    const { username, password } = req.body;
    const hashedPassword = await bcrypt.hash(password, 10);
    users.push({ username, password: hashedPassword });
    res.status(201).json({ message: 'User registered successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  const user = users.find(user => user.username === username);

  if (!user) {
    return res.status(401).json({ message: 'Authentication failed' });
  }

  const passwordMatch = await bcrypt.compare(password, user.password);
  if (!passwordMatch) {
    return res.status(401).json({ message: 'Authentication failed' });
  }

  const token = jwt.sign({ username }, 'your-secret-key'); // Replace with a strong secret key
  res.json({ token });
});

app.listen(3000, () => console.log('Server started on port 3000'));
{% endhighlight %}

Remember to replace `'your-secret-key'` with a strong, randomly generated secret key.  This key is crucial for JWT security.  Storing user details in an array is for simplicity; in a production environment, you'd use a robust database like PostgreSQL or MongoDB.


## Implementing JWT Authentication

Now we'll incorporate JWT authentication into our API to protect our routes.

We'll add a middleware function to verify tokens:

{% highlight javascript linenos %}
const authenticateJWT = (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (authHeader) {
    const token = authHeader.split(' ')[1];

    jwt.verify(token, 'your-secret-key', (err, user) => {
      if (err) {
        return res.sendStatus(403);
      }

      req.user = user;
      next();
    });
  } else {
    res.sendStatus(401);
  }
};
{% endhighlight %}

Then, we'll protect a route using this middleware:

{% highlight javascript linenos %}
app.get('/protected', authenticateJWT, (req, res) => {
  res.send('Protected resource accessed successfully');
});
{% endhighlight %}


## Testing the API with Postman

Postman is an excellent tool for testing APIs. You can use it to register users, log in, and access protected routes.

1.  Register a user by sending a POST request to `/register` with the username and password in the body.

2.  Login using a POST request to `/login` with the username and password.  The response will contain a JWT.

3.  Use the JWT in the `Authorization` header (as `Bearer <token>`) for requests to `/protected`.  If the token is valid, you should see the "Protected resource accessed successfully" message.  If not, you'll get a 401 or 403 error.  ![Postman Screenshot](postman.png)


## Securing the API Further

This tutorial provides a basic foundation for securing your Node.js API with JWT.  However, several enhancements are essential for production environments:

*   **Database Integration:** Replace the in-memory user database with a persistent database like PostgreSQL or MongoDB.
*   **Input Validation:** Add robust input validation to prevent common vulnerabilities like SQL injection.
*   **Rate Limiting:** Implement rate limiting to protect against brute-force attacks.
*   **HTTPS:** Always use HTTPS to encrypt communication between the client and the server.  [Learn more about HTTPS](https://www.example.com/https-tutorial) (replace with a relevant GTEC link).
*   **Stronger Secret Key Management:** Use a secure method for storing and managing your JWT secret key. Never hardcode it directly into your code.


## Conclusion

In this tutorial, we built a secure Node.js API using JWT authentication with Express.js, bcryptjs for password hashing, and jsonwebtoken for token management.  We tested the API using Postman and discussed critical steps for enhancing security in a production setting.  This provides a strong baseline for protecting sensitive data in your applications.  

Share your comments and questions below, and check out other helpful tutorials on GTEC!
