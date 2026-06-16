# Rapid Automatic Segmentation

Automatically extract colored segmentations from RAPID perfusion maps as NIfTI masks, as used in:

H. Corbaz et al., "A comparative study of CT perfusion postprocessing tools in medium/distal vessel occlusion stroke," *American Journal of Neuroradiology*, vol. 46, pp. 900–907, 2025.

A. Anastasiou et al., "Mechanical thrombectomy and final infarct volume in medium or distal vessel occlusion stroke: A post hoc analysis of a randomized clinical trial," *JAMA Neurology*, vol. 83, pp. 537–543, 2026.

### Example

```bash
python3 main.py -i to_process/image_rapid.nii.gz -o images_segmented -p Tmax4s
` ``

## Installation

`````bash
uv pip install -r requirements.txt
` `` 

## Usage

````bash
python3 main.py -i <input_file> -o <output_directory> -p <map_type>
` ``


