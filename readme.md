# Spyke distributed pipeline with Dramatiq

## Motivation

This project is a proof of concept for a distributed pipeline. The pipeline is composed of a set of tasks that are executed in a distributed way. The tasks are executed by a set of workers that are connected to a broker. The broker is responsible for distributing the tasks to the workers. The backend responsible for storing the results of the tasks.

**We want to demonstrate that we can package the pipeline as single docker image and run it in a distributed way.**

The main benefits of this approach are:

- We can easily scale the pipeline by adding more workers
- We can easily update the pipeline by updating the docker image


The pipeline chains the following dummy tasks:
    - double: receives a number and returns the double of it
    - square: receives a number and returns the square of it

In real life this are inference tasks and we want to execute them in a distributed way on different machines.

## Architecture

### main.py

This is the entry point of the pipeline. It is a simple python script that setup the inference pipeline and execute it.

```python
    #for each x send a message to double actor and pipe the result to square actor
    jobs = dramatiq.group(double.message(int(x)) | square.message() for x in arguments.xs).run()  
```

### plumbing.py

Setups the broker, the results backend, how the tasks are serialized and deserialized.
In this spyke we use redis as broker and backend. In real life we can use a more robust broker and backend like RabbitMQ or AWS SQS and Postgres. For message serialization we use JSON but pickle is also supported.

```python
def setup():
    encoder = JSONEncoder()
    backend = RedisBackend(url="redis://127.0.0.1:6379/1", encoder=encoder)
    broker = RedisBroker(url="redis://127.0.0.1:6379/0")
    broker.add_middleware(Results(backend=backend))
    dramatiq.set_broker(broker)
    dramatiq.set_encoder(encoder)
```

### Dockerfile and docker-compose.yml

The dockerfile is responsible for packaging the pipeline. It installs the dependencies and copy the source code to the image.
**Note that we package all the pipeline code in a single docker image.**

The docker-compose.yml defines the services and it not ment to be used in production. In production we use Kubernetes or AWS ECS to manage to achieve the same results but in a more robust and scalable way. 

Each service defines it's own entrypoint. This is because we want to run the same image in different ways. For example, we can run the image as actor "double" or as actor "squares". In production we can run the image as actor "double" on a machine with CPU and as actor "square" on a machine with GPU. 

Also for production we may want to have a base image that contains the dependencies and the source code and then build the actor images on top of it. This way we can have a base image that is shared between all the actors and we can update it easily.


## How to play with

### Setup

Open a terminal and run:

```bash
docker compose build
docker compose up
```

The expected output is:

```text
...
spyke-dramatiq-redis-1   | 1:M 17 Jul 2023 21:55:44.361 * Ready to accept connections
spyke-dramatiq-square-1  | [2023-07-17 21:55:44,852] [PID 1] [MainThread] [dramatiq.MainProcess] [INFO] Dramatiq '1.14.2' is booting up.
spyke-dramatiq-square-1  | [2023-07-17 21:55:44,851] [PID 7] [MainThread] [dramatiq.WorkerProcess(0)] [INFO] Worker process is ready for action.
spyke-dramatiq-square-1  | [2023-07-17 21:55:44,853] [PID 13] [MainThread] [dramatiq.ForkProcess(0)] [INFO] Fork process 'dramatiq.middleware.prometheus:_run_exposition_server' is ready for action.
spyke-dramatiq-double-1  | [2023-07-17 21:55:44,866] [PID 1] [MainThread] [dramatiq.MainProcess] [INFO] Dramatiq '1.14.2' is booting up.
spyke-dramatiq-double-1  | [2023-07-17 21:55:44,864] [PID 7] [MainThread] [dramatiq.WorkerProcess(0)] [INFO] Worker process is ready for action.
spyke-dramatiq-double-1  | [2023-07-17 21:55:44,871] [PID 13] [MainThread] [dramatiq.ForkProcess(0)] [INFO] Fork process 'dramatiq.middleware.prometheus:_run_exposition_server' is ready for action.
```

Open a second terminal and run:

```bash
conda env create -f environment.yml
conda activate spyke-dramatiq
python main.py 3 5 9
```

The expected output in this terminal is:

```text
3 doubled then squared is 36
5 doubled then squared is 100
9 doubled then squared is 324
```

The expected output in the first terminal is:

```text
spyke-dramatiq-double-1  | [2023-07-17 21:56:02,935] [PID 7] [Thread-5] [double] [INFO] the double of 9 is 18
spyke-dramatiq-double-1  | [2023-07-17 21:56:02,935] [PID 7] [Thread-4] [double] [INFO] the double of 5 is 10
spyke-dramatiq-double-1  | [2023-07-17 21:56:02,939] [PID 7] [Thread-4] [double] [INFO] the double of 3 is 6
spyke-dramatiq-square-1  | [2023-07-17 21:56:03,683] [PID 7] [Thread-4] [square] [INFO] The square of 6 is 36
spyke-dramatiq-square-1  | [2023-07-17 21:56:03,684] [PID 7] [Thread-5] [square] [INFO] The square of 18 is 324
spyke-dramatiq-square-1  | [2023-07-17 21:56:03,702] [PID 7] [Thread-5] [square] [INFO] The square of 10 is 100
```