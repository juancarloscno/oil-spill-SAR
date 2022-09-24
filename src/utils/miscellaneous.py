import os
import zipfile

import requests
import typer


def download_url(url, output_dir=None):
    """Download a resource as chunks from web."""
    # Get filename of url
    filename = url.split("/")[-1]
    if output_dir is None:
        filepath = os.path.join(os.getcwd(), filename)
    else:
        filepath = os.path.join(output_dir, filename)
    with requests.get(url, stream=True) as response:
        # Check if the request was successfully received, understood, and accepted
        if response.status_code == 200:
            # If the request is OK, then open it in write binary mode
            with open(filepath, "wb") as file:
                # If the file size is greater than 1024 bytes, then split it into a few chunks
                with typer.progressbar(
                    response.iter_content(chunk_size=1024),
                    label="Downloading {}...".format(filename),
                ) as progress:
                    for chunk in progress:
                        if chunk:
                            file.write(chunk)
                    print("Downloading is done!")
                    return file.name
        else:
            response.raise_for_status()

    return filename


def extract_all_files(filepath, output_dir=None):
    """Extract all files from a zipfile to root or specific directory."""
    if is_zip(filepath):
        with zipfile.ZipFile(filepath) as file:
            print("Extracting files from {}...".format(os.path.basename(filepath)))
            file.extractall(path=output_dir)
            print("Extraction has been completed successfully!")
    else:
        raise Exception("This file is not a zip file.")


def is_zip(filepath):
    """Test if is a ZIP file."""
    ext = os.path.splitext(filepath)[-1][1:]
    if ext == "zip":
        return True
    else:
        return False
