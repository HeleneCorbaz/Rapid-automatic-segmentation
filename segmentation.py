import numpy as np
import itk
import nibabel as nib
import os
import PIL
import argparse


class Rapid:
    def __init__(self, path):
        self.path = path

    def get_orientation(self):
        img = nib.load(self.path)
        return nib.aff2axcodes(img.affine)

    def img_readerRGB(self):
        Dimension = 3
        ComponentType = itk.UC
        InputPixelType = itk.RGBPixel[ComponentType]
        InputImageType = itk.Image[InputPixelType, Dimension]

        self.reader = itk.ImageFileReader[InputImageType].New()
        self.reader.SetFileName(self.path)
        self.reader.Update()

        return self.reader

    def segRapid(self, map_type='Tmax6s'):

        if map_type not in ['Tmax10s', 'Tmax8s', 'Tmax6s', 'Tmax4s', 'CBV', 'CBF', 'ADC', 'mismatch_tmax6s']:
            raise Exception("The map can only be 'Tmax10s', 'Tmax8s', 'Tmax6s', 'Tmax4s', 'CBV', 'CBF', 'ADC' or 'mismatch_tmax6s'")

        red    = (0,   255, 255)
        yellow = (42,  255, 255)
        green  = (85,  255, 255)
        blue   = (170, 255, 255)
        pink   = (220, 255, 220)

        arr = itk.GetArrayFromImage(self.reader.GetOutput())
        arr = np.swapaxes(arr, 0, 2)

        pil_im = PIL.Image.fromarray(arr.reshape(arr.shape[0], arr.shape[1] * arr.shape[2], arr.shape[3]))
        arr = np.array(pil_im.convert('HSV')).reshape(*arr.shape)

        dist = lambda x, y: ((x - y) ** 2).sum(axis=-1)

        grey_mask = arr[..., 1] == 0
        dists = np.stack([dist(arr[~grey_mask, :], c) for c in [red, yellow, green, blue, pink]], axis=-1)
        inds = np.zeros_like(grey_mask, dtype=np.uint8)
        inds[~grey_mask] = np.argmin(dists, axis=-1) + 1
        inds[grey_mask] = 0

        mask_red    = inds == 1
        mask_yellow = inds == 2
        mask_green  = inds == 3
        mask_blue   = inds == 4
        mask_pink   = inds == 5

        if map_type == 'Tmax10s':
            mask = mask_red
        if map_type == 'Tmax8s':
            mask = mask_red + mask_yellow
        if map_type == 'Tmax6s':
            mask = mask_red + mask_yellow + mask_green
        if map_type == 'Tmax4s' or map_type == 'CBF':
            mask = mask_red + mask_yellow + mask_green + mask_blue
        if map_type == 'CBV':
            mask = mask_yellow
        if map_type == 'ADC':
            mask = mask_pink
        if map_type == 'mismatch_tmax6s': # change cropping!
            mask = mask_green

        # remove the side barre and the annotations
       orientation = self.get_orientation()

        if orientation == ('L', 'P', 'S'):
            mask[:15, :, :] = 0
            mask[:, 500:, :] = 0
        elif orientation == ('L', 'A', 'S'):
            mask[:15, :, :] = 0
            mask[:, :215, :] = 0
            
        return self.mask


def parse_args():
    parser = argparse.ArgumentParser(description="Rapid Automatic Segmentation")

    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Path to the input file, as nifti file"
    )

    parser.add_argument(
        "--processing", "-p",
        type=str,
        required=True,
        choices=["Tmax10s", "Tmax8s", "Tmax6s", "Tmax4s", "CBV", "CBF", "ADC", "mismatch_tmax6s"],
        help="Type of map to extract"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        required=True,
        help="Path to the output file or directory"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    print(f"Input:      {args.input}")
    print(f"Map:        {args.processing}")
    print(f"Output:     {args.output}")

    path = args.input
    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)
    base_filename = os.path.basename(args.input)
    affine = nib.load(path).affine

    ra = Rapid(path=path)
    ra.img_readerRGB()
    mask = ra.segRapid(map_type=args.processing)
    arr_map = mask.astype('float32')

    filename = os.path.join(output_dir, f"{base_filename}_mask_{args.processing}.nii.gz")
    mask_nifti = nib.Nifti1Image(arr_map, affine=affine)
    nib.save(mask_nifti, filename)
    print(f"Saved mask to {filename}")


if __name__ == '__main__':
    main()
