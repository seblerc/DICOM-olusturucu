# create_dicom.py
import sys, os, json
from PIL import Image
import numpy as np
import pydicom
from pydicom.uid import ExplicitVRLittleEndian, generate_uid

def load_patient_data(json_path="patient.json"):
    if not os.path.exists(json_path):
        print(f"❌ {json_path} bulunamadı. Lütfen aynı klasörde oluşturun.")
        sys.exit(1)
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def png_to_dicom(input_path, output_path):
    im = Image.open(input_path).convert("L")  # RGB istiyorsan "RGB"
    arr = np.asarray(im)

    ds = pydicom.Dataset()
    ds.file_meta = pydicom.Dataset()
    ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    ds.is_little_endian = True
    ds.is_implicit_VR = False

    # DICOM temel tanımlar
    ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.7"  # Secondary Capture
    ds.SOPInstanceUID = generate_uid()
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.Modality = "SC"

    # Hasta bilgilerini JSON'dan yükle
    meta = load_patient_data()
    ds.PatientName = meta["PatientName"]
    ds.PatientID = meta["PatientID"]
    ds.PatientBirthDate = meta["PatientBirthDate"]
    ds.PatientSex = meta["PatientSex"]
    ds.StudyDate = meta["StudyDate"]
    ds.StudyTime = meta["StudyTime"]
    ds.StudyID = meta["StudyID"]
    ds.AccessionNumber = meta["AccessionNumber"]
    ds.StudyDescription = meta["StudyDescription"]
    ds.SeriesDescription = meta["SeriesDescription"]
    ds.ReferringPhysicianName = meta["ReferringPhysicianName"]

    # Görüntü özellikleri
    if arr.ndim == 2:
        ds.Rows, ds.Columns = arr.shape
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.BitsAllocated = 8; ds.BitsStored = 8; ds.HighBit = 7
        ds.PixelRepresentation = 0
        ds.PixelData = arr.tobytes()
        ds.WindowCenter = 128; ds.WindowWidth = 256
    else:
        h, w, c = arr.shape
        assert c == 3
        ds.Rows = h; ds.Columns = w
        ds.SamplesPerPixel = 3
        ds.PhotometricInterpretation = "RGB"
        ds.PlanarConfiguration = 0
        ds.BitsAllocated = 8; ds.BitsStored = 8; ds.HighBit = 7
        ds.PixelRepresentation = 0
        ds.PixelData = arr.tobytes()

    pydicom.dcmwrite(output_path, ds, write_like_original=False)
    print(f"✅ DICOM hazır: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Kullanım: python create_dicom.py input.png output.dcm")
        sys.exit(1)
    png_to_dicom(sys.argv[1], sys.argv[2])