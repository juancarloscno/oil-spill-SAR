from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval


class COCOWrapper(COCO):
    """Wrapper for the pycocotools COCO class."""

    def __init__(self, dataset, detection_type="bbox"):
        """COCOWrapper constructor.
        See http://mscoco.org/dataset/#format for a description of the format.
        By default, the COCO class constructor reads from a JSON file.
        This class duplicates the same behavior but loads from a dictionary,
        allowing us to perform evaluation without writing to external storage.
        Args:
          dataset: a dictionary holding bounding box annotations in the COCO format.
          detection_type: type of detections being wrapped. Can be one of ['bbox',
            'segmentation']
        Raises:
          ValueError: if detection_type is unsupported.
        """
        supported_detection_types = ["bbox", "segm"]
        if detection_type not in supported_detection_types:
            raise ValueError(
                "Unsupported detection type: {}. "
                "Supported values are: {}".format(
                    detection_type, supported_detection_types
                )
            )
        self._detection_type = detection_type
        COCO.__init__(self)
        self.dataset = dataset
        self.createIndex()


class COCOEvalWrapper(COCOeval):
    def __init__(self, gt=None, dt=None, iou_type="segm"):
        """Initialize CocoEval using coco APIs for ground truth (gt) and detections (dt).

        Arguments
        ---------
        gt: coco object with ground truth annotations
        dt: coco object with detection results
        """
        super().__init__(cocoGt=gt, cocoDt=dt, iouType=iou_type)
