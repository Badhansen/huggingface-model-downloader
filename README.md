# HuggingFace Model Downloader

## Overview

The HuggingFace Model Downloader is a PyQt6-based application that allows users to securely download models from Hugging Face with ease. The application provides a graphical user interface (GUI) for entering the repository ID of the model to be downloaded and managing the Hugging Face access token.

## Features

-   Securely download models from Hugging Face.
-   Specify the directory to save the downloaded models.

## Prerequisites

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/huggingface-model-downloader.git
    cd huggingface-model-downloader
    ```

2. Install the required dependencies using `uv`:

    ```bash
    uv run
    ```

## Usage

1. Run the application:

    ```bash
    uv run app/main.py
    ```

2. The main window of the application will appear. First, setup or update your Hugging Face access token, click the "Settings" button. A dialog will appear where you can enter your token and specify the directory to save the downloaded models.

3. Enter the Hugging Face repository ID of the model you want to download (e.g., `meta-llama/Llama-3.2-1B`).

4. Click the "Download Model" button to start the download process.

5. You can cancel an ongoing download by clicking the "Cancel Download" button.

## Project Structure

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
