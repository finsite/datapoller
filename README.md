# template
# Generic Template for Python Application

This is a template for a python application please update the details here.


## Getting Started

Insert a description here


### Prerequisites

Install

```
Each script will be able to do error logging (default) but is not a requirement. 

The option is there as a parameter for debugging if required.

Each script has example files that you all you have to do is type get-help (scriptname) to see examples.

```
## Installation

1. Clone the repository.
2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

## Environment Variables

- `STOCK_API_TYPE`: The stock API to use (e.g., `yfinance`, `alpha_vantage`, `polygon`). Default: `yfinance`
- `QUEUE_TYPE`: The type of queue to send data to (`sqs` or `rabbitmq`). Default: `sqs`
- `SQS_QUEUE_URL`: The URL of the SQS queue (required if `QUEUE_TYPE=sqs`).
- `RABBITMQ_HOST`: The RabbitMQ server address (default: `localhost`).
- `RABBITMQ_QUEUE_NAME`: The name of the RabbitMQ queue (default: `stock_queue`).

## Example .env File


## Running the tests

Write up how to run the tests.

## Deployment

Read through the descriptions all parameters are documented and as to how to run them.

## Built With

* [Visual Studio Code](https://code.visualstudio.com/)

## Contributing

Please feel free to comment and if you see opportunities for improvement I welcome working with people.

## Authors

* **Mark Quinn** - - [Mobious999](https://github.com/mobious999)
* **Jason Qualkenbush** - - [jasonqualkenbush](https://github.com/jasonqualkenbush)

## License

Apache 2.0

## Acknowledgments

* insert references here

