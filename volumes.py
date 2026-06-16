import numpy as np
import nibabel as nib
import argparse

def measure_label_volume(filepath):
    img = nib.load(filepath)
    data = img.get_fdata()
    voxel_volume_mm3 = np.prod(img.header.get_zooms()[:3])

    return float(np.sum(data) * voxel_volume_mm3/1000)

def parse_args():
    parser = argparse.ArgumentParser(description="Measure the volume of a segmentation mask in mL")

    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Path to the segmentation mask as a NIfTI file"
    )

    return parser.parse_args()

def main():
    args = parse_args()
    volume = measure_label_volume(args.input)
    print(f"Volume: {volume:.2f} mL")

if __name__ == '__main__':
    main()