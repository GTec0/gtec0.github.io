---
layout: post
title: Automating Your Daily Tasks with Python
comments: true
tags: ['Python Automation', 'Productivity', 'Task Automation', 'Scripting']
author: Asahluma Tyika
---

Ever felt like you're spending too much time on repetitive, mundane tasks?  Things like renaming files, organizing your downloads, or even scheduling emails?  Wouldn't it be amazing to automate these chores, freeing up your valuable time for more creative and fulfilling work?  This post explores how to leverage Python's power to build simple yet effective automation scripts, transforming your daily workflow and boosting your productivity.  We'll specifically focus on automating file management, a common pain point for many users.


## Understanding the Power of Python for Automation

Python, with its extensive libraries and clear syntax, has become the go-to language for many automation projects. Its readability makes it easy to learn, even for beginners, while its versatility allows it to handle complex tasks with grace. We'll be using the `os` and `shutil` modules—powerful tools for interacting with the operating system's file system.  No prior Python experience is required, but a basic familiarity with programming concepts will be helpful.

### Setting up Your Environment

Before we dive into the scripts, make sure you have Python installed on your system.  Most operating systems offer straightforward installation procedures. You can verify your installation by opening your terminal or command prompt and typing `python --version`.  Once Python is installed, you can proceed to the next step.

## Building Your First File Management Script: Renaming Files

Let's build a Python script that automatically renames files within a specified directory.  This is particularly useful if you're downloading files with non-descriptive names and need to organize them for later use.  We'll add sequential numbering to the filenames, making it easy to keep track of them.

{% highlight python linenos %}
import os
import shutil

def rename_files(directory, prefix):
    files = os.listdir(directory)
    i = 1
    for file in files:
        base, ext = os.path.splitext(file)
        new_name = f"{prefix}{i:03}{ext}"  #Example: file1.txt, file002.jpg etc
        os.rename(os.path.join(directory, file), os.path.join(directory, new_name))
        i += 1

# Example Usage
directory_path = "/path/to/your/files" #Replace with your directory
file_prefix = "processed_"
rename_files(directory_path, file_prefix)
{% endhighlight %}

Remember to replace `/path/to/your/files` with the actual path to your files.  This script iterates through each file in the directory, extracts the extension, adds a sequential number, and then renames the file accordingly. Simple, yet effective!


## Advanced File Management: Moving and Deleting Files

Now, let's take it a step further.  This script moves files from one directory to another and optionally deletes files from the source directory after moving them. This is crucial for cleaning up after bulk downloads or processing.

{% highlight python linenos %}
import os
import shutil

def move_and_delete(source_dir, destination_dir, delete_source=False):
    for filename in os.listdir(source_dir):
        source_path = os.path.join(source_dir, filename)
        destination_path = os.path.join(destination_dir, filename)
        shutil.move(source_path, destination_path)
        if delete_source:
            os.remove(source_path)

#Example Usage
source_directory = "/path/to/source/files" #Replace with your source directory
destination_directory = "/path/to/destination/files" #Replace with your destination directory
move_and_delete(source_directory, destination_directory, delete_source=True) #set delete_source = False if you don't want to delete source files
{% endhighlight %}

The `delete_source` parameter offers flexibility—you can choose to keep the original files or remove them after moving them to the destination.  Always test your scripts with dummy files before applying them to important data!


## Automating Email Scheduling with Python

Beyond file management, Python excels at automating other repetitive tasks. Let's explore a simple script for scheduling emails using the `smtplib` library.  While this example uses Gmail's SMTP server, you can adapt it to other email providers.  Remember that you might need to enable "less secure app access" in your Gmail settings for this script to work (though this isn't considered best practice and you should explore more secure alternatives like app passwords).  See this GTec post on setting up secure email automation for more details [here](https://gtec0.github.io/secure-email-automation).

{% highlight python linenos %}
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime

def send_scheduled_email(sender_email, sender_password, recipient_email, subject, body, schedule_time):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    #check if current time is greater than or equal to schedule time
    if datetime.datetime.now() >= schedule_time:
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            server.close()
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")

# Example Usage: (replace with your email credentials and schedule time)
sender_email = "your_email@gmail.com"
sender_password = "your_password"
recipient_email = "recipient_email@example.com"
subject = "Scheduled Email"
body = "This email was sent automatically!"
schedule_time = datetime.datetime(2024, 3, 15, 10, 0, 0) #Example schedule time: March 15th, 2024 at 10:00 AM

send_scheduled_email(sender_email, sender_password, recipient_email, subject, body, schedule_time)
{% endhighlight %}


##  Error Handling and Best Practices

Robust error handling is crucial for any automation script.  Consider using `try-except` blocks to catch potential errors, such as file not found or network issues.  This prevents your script from crashing unexpectedly. Also, always thoroughly test your scripts in a safe environment before deploying them to your main system.

##  Expanding Your Automation Capabilities

The possibilities for automation with Python are vast. This introduction only scratches the surface. Consider exploring libraries like `requests` for web scraping and interacting with APIs, `schedule` for task scheduling, or `selenium` for browser automation. The key is to identify repetitive tasks in your workflow and leverage Python's powerful tools to streamline your processes.


## Conclusion: Embrace the Power of Automation

Automating your daily tasks with Python isn't just about saving time; it's about improving your efficiency, reducing errors, and ultimately, freeing you up to focus on the tasks that truly matter.  Try these scripts, adapt them to your specific needs, and share your results in the comments!  Let's build a more efficient and automated future together.
