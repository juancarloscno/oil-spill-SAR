"""
Pre-processing scheme
Script for Sentinel-1 Ground Range Detected pre-processing with Sentinel Application Platform (SNAP).
Each function had been using in this script follow the scheme used in the paper:
    Krestenitis, M., et al. (2019). Oil spill identification from satellite images using deep neural networks.
        Remote Sensing, 11(15), 1762. DOI: 10.3390/rs11151762

Copyright (c) 2020 Juan Carlos Cedeño.
Licensed under the MIT License (see LICENSE for details)
Written by Juan Carlos Cedeño.
"""

import glob
import os
import shutil
import time
import zipfile
from multiprocessing import Pool

import typer
from pyroSAR import identify
from pyroSAR.snap.auxil import gpt
from pyroSAR.snap.auxil import groupbyWorkers
from pyroSAR.snap.util import parse_node, parse_recipe

from src.utils.miscellaneous import extract_all_files
from src.utils.definitions import UNPROCESSED_DATA_DIR, PROCESSED_DATA_DIR, TMP_DIR

# Root directory of the project
ROOT_DIR = os.path.abspath("../")
DATASET_DIR = os.path.join(ROOT_DIR, "dataset")
RAW_DATASET_DIR = os.path.join(DATASET_DIR, "raw")
INFER_DATASET_DIR = os.path.join(DATASET_DIR, "infer", "images")


class SARPreprocessor:
    def __init__(
        self,
        input_safe_file,
        output_dir,
        memory_allocation_min="2G",
        memory_allocation_max="32G",
    ):
        self.safe_file = input_safe_file
        self.output_folder = output_dir
        self.tmp_dir = TMP_DIR  # All XML files will be in the temporary folder (it will remove later)
        self.xms = memory_allocation_min
        self.xmx = memory_allocation_max
        os.environ["_JAVA_OPTIONS"] = "-Xms{} -Xmx{}".format(self.xms, self.xmx)
        os.environ["JAVA_TOOL_OPTIONS"] = "-Xms{} -Xmx{}".format(self.xms, self.xmx)

    def __call__(self, subset=None):
        filename = self.get_filename(self.safe_file)
        if subset is not None:
            subset_index = "{}_{}_{}_{}".format(
                subset[0], subset[1], subset[2], subset[3]
            )
            filename = filename + "_" + subset_index
            self.tmp_dir = os.path.join(self.tmp_dir, subset_index)
        if not os.path.exists(self.tpm_dir):
            os.mkdir(self.tpm_dir)
        xml_filepath = os.path.join(self.tpm_dir, "{}.xml".format(filename))
        work = self.preprocessing_chain(subset)
        work.write(xml_filepath)

        start = time.time()
        gpt(xml_filepath, self.tpm_dir, groupbyWorkers(xml_filepath, 6))
        end = time.time()
        # Remove XML folder and its files
        shutil.rmtree(self.tpm_dir)
        print("Preprocessing has completed successfully at {}s!".format(end - start))

    @staticmethod
    def prepare_subset(safe_file: str):
        """Helper function to split a scene into 4 subsets with an overlap of 2%. This is useful for run faster
        preprocessing (~4min)."""
        scene = identify(safe_file)
        h = scene.lines  # Subset height
        w = scene.samples  # Subset width
        w1 = int(w * 0.52)
        w2 = w - w1
        h1 = int(h * 0.52)
        h2 = h - h1
        del scene
        t1 = (0, 0, w1, h1)  # Upper-left subset coordinates
        t2 = (w2, 0, w, h1)  # Upper-right subset coordinates
        t3 = (0, h2, w1, h)  # Above-left subset coordinates
        t4 = (w2, h2, w, h)  # Above-right subset coordinates
        return [t1, t2, t3, t4]

    @staticmethod
    def get_filename(safe_file: str):
        """Returns the input filename without its extension."""
        return os.path.basename(safe_file).replace(".SAFE", "")

    def preprocessing_chain(self, subset: tuple = None):
        """Create a Direct Acyclic Graph (DAG) XML specification for use in GPT's SNAP.

        Arguments
        ---------
        subset: tuple (optional)
            Subset in (x, y, w, h) format used to for split image.

        Returns
        -------
            A Workflow object with all XML representations parsed for the nodes.
        """
        filename = self.get_filename(self.safe_file)
        filepath = os.path.join(self.output_folder, "{}_sigma0_VV_dB".format(filename))

        g = parse_recipe("blank")

        # Read file
        op = parse_node("Read")
        op.parameters["file"] = self.safe_file
        op.parameters["formatName"] = "SENTINEL-1"
        g.insert_node(op)
        # Overwrite source id with newer operator
        source_id = op.id

        # Subset
        if subset is not None:
            assert isinstance(subset, tuple), "{} should be a tuple object.".format(
                subset
            )
            x, y, w, h = subset
            filepath = filepath + "_{}_{}_{}_{}".format(x, y, w, h)
            op = parse_node("Subset")
            op.parameters["region"] = "{}, {}, {}, {}".format(x, y, w, h)
            op.parameters["copyMetadata"] = "true"
            g.insert_node(op, source_id)
            # Overwrite source id with newer operator
            source_id = op.id

        # Apply Orbit File: During the acquisition of S1 data the satellite position is recorded by GNSS. For fast
        # delivery, the orbit information generated are stored within the S1 products. The orbit positions are later
        # fined and made available as restituted (< 10cm accuracy) or precise (< 5cm accuracy) orbit files by
        # Copernicus Precise Orbit Determination (POD) Service. Precise orbit information can have a high influence
        # on several preprocessing steps like the geo-referencing of the data. Therefore, it's always preferable to
        # use most accurate orbit information available.
        op = parse_node("Apply-Orbit-File")
        op.parameters["continueOnFail"] = "true"
        g.insert_node(op, source_id)
        # Overwrite source id with newer operator
        source_id = op.id

        # Remove Border Noise: PyroSAR use its own implementation for remove the border noise in GRD products.
        op = parse_node("Remove-GRD-Border-Noise")
        op.parameters["selectedPolarisations"] = "VV"
        g.insert_node(op, source_id)
        # Overwrite source id with newer operator
        source_id = op.id

        # Calibration: All S1 products are not radiometric corrected by default. Calibration is used to perform the
        # conversion of digital numbers (DN) to radar backscatter (physical units). In this case, the output radar
        # backscatter is calibrated in sigma naught.
        op = parse_node("Calibration")
        op.parameters["selectedPolarisations"] = "VV"
        g.insert_node(op, source_id)
        # Overwrite source id with newer operator
        source_id = op.id

        # Speckle filter: A characteristic of images acquired by a SAR system is the visibility of random noise which
        # look like "salt and pepper" within the image and is called speckle. The appearance of speckle is caused by
        # the interferences of coherent echoes from individual scatterers within one pixel. The presence of speckle
        # degrades the quality of the image. The usage of speckle filter is an essential part of the preprocessing
        # chain.
        op = parse_node("Speckle-Filter")
        op.parameters["filter"] = "Median"
        op.parameters["windowSize"] = "7x7"
        g.insert_node(op, source_id)
        # Overwrite source id with newer operator
        source_id = op.id

        # Convert from sigma naught units to decibel scale
        op = parse_node("LinearToFromdB")
        g.insert_node(op, source_id)
        # Overwrite source id with newer operator
        source_id = op.id

        # Ellipsoid Correction Range-Doppler
        op = parse_node("Ellipsoid-Correction-RD")
        op.parameters["pixelSpacingInMeter"] = "10"
        g.insert_node(op, source_id)
        # Overwrite source id with newer operator
        source_id = op.id

        # Scale values to 8-unsigned integer (Linear scaled)
        op = parse_node("Convert-Datatype")
        op.parameters["targetDataType"] = "uint8"
        op.parameters["targetScalingStr"] = "Linear (slope and intercept)"
        g.insert_node(op, source_id)
        # Overwrite source id with newer operator
        source_id = op.id

        # Write GeoTIFF
        op = parse_node("Write")
        op.parameters["formatName"] = "GeoTIFF"
        op.parameters["file"] = filepath
        g.insert_node(op, source_id)

        return g


cli = typer.Typer()


@cli.command()
def calibrate(
    dataset: str = typer.Option(
        RAW_DATASET_DIR,
        "--input",
        "-in",
        metavar="/path/to/dataset",
        help="Path of the dataset with uncalibrated files. Either zip or .SAFE extension.",
    ),
    results_dir: str = typer.Option(
        INFER_DATASET_DIR,
        "--output",
        "-out",
        metavar="/path/to/results",
        help="Path of output folder to " "save results.",
    ),
    limit: int = typer.Option(None, help="Limit"),
):
    """Preprocessing Sentinel-1 Ground Range Detected SAR images."""
    # Walk files
    zip_filepaths = []
    for root, _, filenames in os.walk(dataset):
        for filename in filenames:
            if filename.endswith(".zip"):
                # Verify is file already exists using regex pattern based on scene ID
                pattern = os.path.join(results_dir, filename.replace(".zip", "*"))
                if glob.glob(pattern):
                    # Skip if the file already exists in the output folder
                    continue
                zip_filepath = os.path.join(root, filename)
                zip_filepaths.append(zip_filepath)
    # Limit files
    zip_filepaths = zip_filepaths[:limit]

    typer.echo("\nSentinel-1 SAR GRD Preprocessing\n")
    # List of tuples: Output dataset dir, zip filepath, safe filepath
    args = [
        (dataset, zip_filepath, zip_filepath.replace(".zip", ".SAFE"))
        for zip_filepath in zip_filepaths
    ]
    count = 0
    with typer.progressbar(args, label="Preprocessing") as progress:
        for arg in progress:
            dataset, zip_filepath, safe_filepath = arg
            typer.echo(
                "\nInput file: {}".format(
                    os.path.basename(zip_filepath).replace(".zip", "")
                )
            )
            try:
                # Try to extract files from zip
                extract_all_files(zip_filepath, dataset)
            except zipfile.BadZipfile:
                # But, if this is corrupted, then skip it.
                typer.echo(
                    "Skipping this BadZipFile: {}".format(
                        os.path.basename(zip_filepath)
                    )
                )
                continue
            # Instance graph
            preprocessing = SARPreprocessor(
                input_safe_file=safe_filepath, output_dir=results_dir
            )
            subsets = preprocessing.prepare_subset(safe_filepath)
            start = time.time()
            with Pool(4) as pool:
                pool.map(preprocessing, subsets)
                pool.close()
                pool.join()
            end = time.time()
            typer.echo("Batch preprocessing time: {}s!".format(end - start))
            count += 1
            typer.echo("\n{} images have already preprocessed.".format(count))
            # Remove .SAFE file because it's larger than .zip file
            shutil.rmtree(safe_filepath)
    typer.echo("\nIn total, {} SAR images have been preprocessed.".format(count))


if __name__ == "__main__":
    # Run CLI
    cli()
