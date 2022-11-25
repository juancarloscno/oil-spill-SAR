# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from src.data.dataset.mklab import from_mklab_to_coco_format


@click.command()
@click.argument("input_filepath", type=click.Path(exists=True))
@click.argument("output_filepath", type=click.Path())
def main(input_filepath, output_filepath):
    """Runs data processing scripts to turn raw data from (../unprocessed) into
    cleaned data ready to be analyzed (saved in ../processed).
    """
    print("Making dataset...")
    print("(1/2) Oil Spill Dataset (train)...")
    from_mklab_to_coco_format(input_filepath, output_filepath, "train")
    print("(2/2) Oil Spill Dataset (test)...")
    from_mklab_to_coco_format(input_filepath, output_filepath, "test")
    logger = logging.getLogger(__name__)
    logger.info("making final data set from raw data")


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]
    print(project_dir)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
