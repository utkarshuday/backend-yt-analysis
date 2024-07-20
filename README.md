# YouTube Analysis API

This is an API for analyzing YouTube data using Flask for the backend.

## Prerequisites

Ensure you have the following installed on your system:

- [Python 3.x](https://www.python.org/downloads/)
- [pipenv](https://pipenv.pypa.io/en/latest/)

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/utkarshuday/backend-yt-analysis.git
    cd backend-yt-analysis
    ```

2. **Install the dependencies:**

    ```sh
    pipenv install
    ```

3. **Create a `.env` file in the root directory and add your YouTube Data API key:**

    ```plaintext
    API_KEY=your_api_key_here
    ```

## Running the Application

1. **Activate the virtual environment:**

    ```sh
    pipenv shell
    ```

2. **Run the Flask application:**

    ```sh
    flask --app app.index --debug run
    ```

## Project Structure

- `app/`: Contains the Flask application code.
- `.env`: Environment file containing the YouTube Data API key.

## License

This project is licensed under the MIT License.

---

Happy coding!
