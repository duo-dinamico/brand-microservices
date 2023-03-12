# brand-microservices

![App Version](https://img.shields.io/github/v/tag/duo-dinamico/brand-microservices?label=API)
![Python Version](https://img.shields.io/badge/python-v3.11-blue)
![fastAPI Version](https://img.shields.io/badge/fastapi-v0.92.0-blue)
![CI Status](https://github.com/duo-dinamico/brand-microservices/actions/workflows/brand_ci.yml/badge.svg)
![Last Commit](https://img.shields.io/github/last-commit/duo-dinamico/brand-microservices)
![License](https://img.shields.io/github/license/duo-dinamico/brand-microservices)

Brand microservices is an API built with FastAPI and PostgreSQL to manage a collection of brands Made in Portugal.

The aim is to replace the currently used spreadsheet with a more robust system.

## Table of Contents

1. [Requirements](#requirements)
   1. [Install](#install)
   2. [Create](#create)
   3. [Run](#run)
2. [Using](#using-brand-microservices)
3. [Contribute](#contribute)
4. [Credits and Acknowledgments](#credits-and-acknowledgments)
   1. [Authors](#authors)
   2. [Thanks](#thanks)
5. [License](#license)

## Requirements

### Install

- Docker
- Python (3.7+)
- Poetry (to manage python versions and install dependencies)
- Make
- IDE of your preference

### Create

To run this project, you will need a **_.env_** file in the root so that docker can access the following environment variables:

```console
JWT_SECRET_KEY=password
JWT_REFRESH_SECRET_KEY=password
PSUSER=postgresuser
PSPASSWD=password
```

### Run

Clone the repository `git clone git@github.com:duo-dinamico/brand-microservices.git`

Move into the directory you've just cloned

And initiate Poetry `poetry init`

## Using brand microservices

Open your terminal and type `make up` to deploy the development.
You should now be able to visit [localhost:8000/docs](localhost:8000/docs) on your browser to use the documentation.

~~Create a user to use the protected routes.~~

### Authorize OpenAPI and start using the API.

Use the trial user account to use the protected routes:

- username: `trialUser`
- password: `TrialPassword1`

Alternatively, you can type `make utest` on your terminal to run the unit tests. We've tried as much as possible to make this a TDD (Test Driven Development).

Any other commands available you can check by typing `make` in the terminal.

## Contribute

Contributions to the development are welcome. Here's how you can contribute:

- [Submit bugs](https://github.com/duo-dinamico/brand-microservices/issues) and help us verify fixes.
- [Submit pull requests](https://github.com/duo-dinamico/brand-microservices/pulls) for bug fixes and features
  - For the submission of code, we follow a few simple rules:
    - We always branch off from `develop` and create pull requests against `develop`. Pull requests against `main` can only come from `develop`.
    - Branch naming should have as prefix the goal of the submission, for example if it is a new feature, it will be: `feat/<name-of-feature>`, or if related to documentation: `doc/<name-of-documentation>`. The following labels are available:
      ```
      enhancement: ["feature/*", "feat/*"]
      bug: ["fix/*", "bug/*"]
      documentation: ["doc/*", "documentation/*"]
      workflow: ["workflow/*", "ci/*"]
      refactor: ["refactor/*", "improve/*"]
      release: ["release/*", "version/*"]
      ```
    - The title of the pull request should also follow a similar system. We always begin with the label and then a short description like `feat: the title of this pull request`

## Credits and Acknowledgments

### Authors

[jcvsilva](https://github.com/jcvsilva)

[joaojesus81](https://github.com/joaojesus81)

### Thanks

[FastAPI Documentation and Sebastián Ramírez](https://fastapi.tiangolo.com/) - Which we read several times over and over and it was a pleasure to read.

[Maximilian Filtenbord - BiteStreams](https://bitestreams.com/blog/fastapi_template/) - We used this tutorial to start of our application and it was a great way to get started.

Family and friends for still putting up with us.

## License

This project is licensed under the terms of the [MIT](LICENSE) license.
