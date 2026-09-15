---
layout: post
title: Git Commit Message, How to Write Clear and Useful Commits
thumbnail-img: 
share-img: 
tags: [Git, GitHub, Version Control, Programming, Developer Tips]
author: Asahluma Tyika
---

When working on a software project, you will eventually need to save your changes using Git.

You might add a new feature, fix a bug, update documentation, or change the way an existing function works. Git allows you to record these changes in a commit.

However, saving changes is only part of the process. **Writing a clear commit message is just as important.**

A commit message helps you and other developers understand what changed in a project. A good message can make a project's history easier to read, simplify debugging, and improve collaboration.

In this guide, we will explore how to write useful Git commit messages, common commit types, practical examples, and mistakes to avoid.

## What Is a Git Commit?

A Git commit is a recorded snapshot of changes made to a repository.

For example, imagine you are building a website and add a login form.

After making your changes, you can stage them:

```bash
git add .
````

Then create a commit:

```bash
git commit -m "Add login form"
```

The `-m` option allows you to provide a commit message directly from the terminal.

The message:

```text
Add login form
```

briefly explains what the commit does.

Later, when you or another developer reviews the project's history, the message provides useful context.

## Why Are Good Commit Messages Important?

A commit message might look like a small detail, but it becomes valuable as a project grows.

### 1. They Make Project History Easier to Understand

Consider these commit messages:

```text
update
changes
fixed stuff
new code
```

They do not explain much about what actually happened.

Now compare them with:

```text
Add email validation to registration form
Fix incorrect total in shopping cart
Update installation instructions
Remove unused database connection
```

These messages communicate the purpose of each change much more clearly.

When reviewing a project months later, specific messages make it easier to understand how the code developed.

### 2. They Help With Debugging

Suppose a bug appears after several changes.

You can inspect the commit history to find when a particular part of the application was modified.

For example:

```bash
git log --oneline
```

Possible output:

```text
a12bc34 Fix incorrect total in shopping cart
b56de78 Add discount calculation
c90fa12 Create shopping cart page
d34ef56 Add product listing
```

The messages help you identify commits that may be related to the problem.

You can then inspect a specific commit:

```bash
git show a12bc34
```

This displays the changes associated with that commit.

Clear messages do not automatically identify the cause of a bug, but they make the investigation easier.

### 3. They Improve Collaboration

When multiple developers work on the same repository, everyone needs to understand what others have changed.

A message such as:

```text
Add password reset functionality
```

gives a team member a useful overview.

A message such as:

```text
stuff
```

does not provide the same information.

Clear commit messages reduce unnecessary confusion when reviewing project history.

## What Makes a Good Commit Message?

A useful commit message should generally be:

* **Clear:** Explain what changed.
* **Specific:** Avoid vague descriptions.
* **Concise:** Keep the main message short.
* **Relevant:** Describe the actual change.
* **Consistent:** Follow a format used by the project.

For example:

```text
Fix incorrect user total in checkout
```

This is more useful than:

```text
Fix bug
```

The first message identifies the affected part of the application and the problem being addressed.

## A Simple Commit Message Format

One straightforward format is:

```text
<type>: <description>
```

For example:

```text
feat: add user authentication
```

or:

```text
fix: prevent duplicate form submissions
```

The first part identifies the type of change.

The second part briefly describes the change.

This format is commonly used in projects that follow **Conventional Commits**, although teams may use their own conventions.

## Common Git Commit Types

Using a commit type can make a project's history more organized.

Here are some commonly used types.

### `feat` — New Feature

Use `feat` when adding a new feature or capability.

Example:

```bash
git commit -m "feat: add user registration"
```

Other examples:

```text
feat: add dark mode
feat: add search functionality
feat: allow users to upload profile images
```

### `fix` — Bug Fix

Use `fix` when correcting a problem in the application.

Example:

```bash
git commit -m "fix: prevent crash on empty search"
```

Other examples:

```text
fix: correct total price calculation
fix: resolve invalid login redirect
fix: handle missing profile image
```

### `docs` — Documentation Changes

Use `docs` when updating documentation.

Example:

```bash
git commit -m "docs: update installation instructions"
```

Other examples:

```text
docs: add API usage examples
docs: explain environment variables
docs: update project requirements
```

### `refactor` — Code Improvements Without Changing Behavior

Use `refactor` when restructuring code without intentionally changing its external behavior.

Example:

```bash
git commit -m "refactor: simplify user validation"
```

Other examples:

```text
refactor: extract database helper function
refactor: reorganize authentication module
refactor: remove duplicated validation logic
```

### `test` — Tests

Use `test` when adding or updating tests.

Example:

```bash
git commit -m "test: add tests for login validation"
```

Other examples:

```text
test: cover invalid email addresses
test: add tests for shopping cart totals
test: update user registration tests
```

### `chore` — Maintenance Tasks

Use `chore` for general maintenance that does not directly add a feature or fix a bug.

Example:

```bash
git commit -m "chore: update project dependencies"
```

Other examples:

```text
chore: update development tools
chore: remove unused configuration
chore: update build settings
```

## Good Commit Messages vs Bad Commit Messages

Let's compare some examples.

### Example 1: A New Feature

**Bad:**

```text
new stuff
```

**Better:**

```text
feat: add user authentication
```

The second message explains what was added.

### Example 2: Fixing a Bug

**Bad:**

```text
fixed it
```

**Better:**

```text
fix: prevent crash when search input is empty
```

The improved message identifies the problem being addressed.

### Example 3: Updating Documentation

**Bad:**

```text
README changes
```

**Better:**

```text
docs: add setup instructions for local development
```

The improved version explains what was changed in the documentation.

### Example 4: Refactoring Code

**Bad:**

```text
cleaned code
```

**Better:**

```text
refactor: move authentication logic into a helper
```

The improved message describes the actual restructuring.

## Keep Commit Messages Short and Specific

A commit message should communicate the main idea without unnecessary detail.

Compare these examples:

```text
fix: fix the issue where users sometimes cannot log in
```

and:

```text
fix: handle expired login sessions
```

The second message is more concise and identifies the likely area of the change.

A useful approach is to ask yourself:

> What changed in this commit?

For example:

```text
feat: add password reset emails
```

This tells the reader what was added.

You can add more detail when the change requires explanation.

## Use the Imperative Mood

Many Git projects recommend writing commit messages in the imperative mood.

This means describing the action as a command.

Examples:

```text
Add login form
Fix broken navigation
Update documentation
Remove unused imports
```

Instead of:

```text
Added login form
Fixed broken navigation
Updated documentation
Removed unused imports
```

Both styles can communicate the change, but using one consistent style makes the commit history easier to read.

A simple way to think about it is:

> If applied, this commit will **Add login form**.

This is why messages such as `Add`, `Fix`, and `Update` are commonly used.

## Avoid Combining Unrelated Changes

A commit should ideally represent one logical change.

For example, imagine you are working on a website and make all these changes:

* Add a login form.
* Change the website's colors.
* Update the README.
* Fix a database query.

You could place everything in one commit:

```text
Update website
```

However, this makes the commit difficult to understand.

A clearer approach is to create separate commits:

```text
feat: add login form
style: update website colors
docs: update README
fix: correct database query
```

This makes each change easier to review.

It also makes it easier to revert a particular change when necessary.

## How to Write a Commit Message in Git

Let's walk through a simple example.

Imagine you have created a new file called `login.html`.

First, check the status of your repository:

```bash
git status
```

You might see:

```text
Untracked files:
  login.html
```

Stage the file:

```bash
git add login.html
```

Now create a commit:

```bash
git commit -m "feat: add login page"
```

Git records the staged changes with that message.

You can confirm the commit using:

```bash
git log --oneline -1
```

Example output:

```text
a12bc34 feat: add login page
```

The short commit ID identifies the commit.

## Writing a Longer Commit Message

Sometimes a change needs more explanation than a short subject can provide.

For example, you might fix a complicated authentication problem.

A short message could be:

```text
fix: handle expired authentication tokens
```

You can add a longer description by creating a commit without using `-m`:

```bash
git commit
```

Git opens your configured text editor.

You can write something like:

```text
fix: handle expired authentication tokens

Refresh expired access tokens before making authenticated requests.
This prevents users from being logged out unnecessarily when their
session is still valid.
```

The first line is the subject.

The blank line separates the subject from the longer description.

The remaining lines explain the change in more detail.

A longer description is especially useful when the reason behind a change is not obvious from the code.

## Viewing Commit History

Git provides several commands for reviewing commits.

### View the Full Commit History

```bash
git log
```

This displays detailed information about previous commits.

### View a Short Summary

```bash
git log --oneline
```

Example:

```text
a12bc34 feat: add login page
b56de78 fix: correct registration validation
c90fa12 docs: update setup instructions
```

### View a Limited Number of Commits

To display the last five commits:

```bash
git log --oneline -5
```

This is useful when you only want a quick overview of recent changes.

### Inspect a Specific Commit

```bash
git show a12bc34
```

Replace `a12bc34` with the commit ID you want to inspect.

This displays information about the commit and the changes it introduced.

## Can You Change a Commit Message?

Yes. Git allows you to change the message of the most recent commit.

For example:

```bash
git commit --amend -m "feat: add login page"
```

This replaces the most recent commit message.

### Important Consideration

If you have already pushed the commit to a shared remote repository, changing it can rewrite commit history.

This may affect other developers who have already downloaded the original commit.

Before amending a published commit, consider whether the repository's workflow allows it.

For a commit that has not yet been shared, amending the message is usually straightforward.

## Common Mistakes to Avoid

### 1. Using Vague Messages

Avoid messages such as:

```text
update
changes
fix
stuff
```

These messages do not provide enough context.

Instead, describe the actual change:

```text
fix: handle missing user profile data
```

### 2. Writing Extremely Long Subject Lines

A commit subject should be easy to scan.

Instead of:

```text
fix: fix the problem that happens when a user submits the registration form without entering an email address and the application crashes
```

You could write:

```text
fix: handle missing email during registration
```

If necessary, add more information in the commit body.

### 3. Combining Too Many Unrelated Changes

A commit containing unrelated changes can be difficult to review.

Try to organize your work into logical commits.

### 4. Describing the Wrong Thing

Your commit message should match the actual changes.

For example, if you updated documentation, avoid writing:

```text
feat: add authentication
```

unless you actually added authentication functionality.

Accurate messages help keep project history trustworthy.

### 5. Using Inconsistent Formats

If one commit uses:

```text
feat: add search
```

and another uses:

```text
Added a search feature
```

the history may look inconsistent.

Choose a format and use it consistently within your project.

## A Practical Commit Message Checklist

Before creating a commit, ask yourself:

* Does the message explain what changed?
* Is it specific enough for someone else to understand?
* Is the message concise?
* Does it match the actual changes?
* Am I following the project's commit conventions?
* Have I avoided combining unrelated changes?

For example:

```text
fix: prevent duplicate checkout submissions
```

This message is short, specific, and describes a clear change.

## Frequently Asked Questions

### Should Every Commit Use a Type?

Not necessarily.

Git itself does not require prefixes such as `feat:` or `fix:`.

These prefixes are conventions used by many teams and projects.

You can write:

```text
Add user registration
```

instead of:

```text
feat: add user registration
```

The important thing is to follow the conventions used by your project.

### How Long Should a Commit Message Be?

There is no universal length requirement for commit messages.

A useful subject should be concise enough to understand quickly.

If a change needs more explanation, you can include a longer commit body.

### Is It Okay to Commit Small Changes?

Yes.

Small, logical commits can make changes easier to review and understand.

For example:

```text
feat: add search input
feat: display search results
test: add search tests
```

These commits each represent a specific part of the work.

### Can I Use Emojis in Commit Messages?

Yes, Git allows emojis in commit messages.

For example:

```text
✨ Add dark mode
🐛 Fix login validation
```

However, whether emojis are appropriate depends on your team's conventions.

For professional projects, a consistent text-based format may be easier to maintain.

## Final Thoughts

Good Git commit messages are simple, descriptive, and consistent.

You do not need to write a long explanation for every change. A short message such as:

```text
fix: handle empty search input
```

can be enough to communicate the purpose of a commit.

As your projects become larger, clear commit messages will make it easier to understand your work, review changes, and collaborate with other developers.

The next time you create a commit, avoid writing `update` or `changes`. Instead, take a moment to describe what you actually changed.

A useful commit history starts with useful commit messages.
