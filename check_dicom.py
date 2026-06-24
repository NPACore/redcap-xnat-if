import zipfile
import pydicom
import os

# unzip
zip_path = 'test_dicoms/1.3.12.2.1107.5.2.43.67078.2026062306222695826100749.0.0.0.dicom.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    for file in z.namelist():
        # get just the filename, strip any subdirectory structure
        filename = os.path.basename(file)
        if not filename:
            continue
        source = z.open(file)
        target_path = f'test_dicoms/localizer/{filename}'
        with open(target_path, 'wb') as target:
            target.write(source.read())

dicoms = [f for f in os.listdir('test_dicoms/localizer') if f.endswith('.dcm')]
print(f"Found {len(dicoms)} DICOM files")

ds = pydicom.dcmread(f'test_dicoms/localizer/{dicoms[0]}')
print(f"Patient ID:  {ds.PatientID}")
print(f"Study Date:  {ds.StudyDate}")
print(f"Series Desc: {ds.SeriesDescription}")
print(f"Modality:    {ds.Modality}")
print(f"Patient Name:    {ds.PatientName}")
print(f"Patient ID:      {ds.PatientID}")
print(f"Patient DOB:     {ds.get('PatientBirthDate', 'N/A')}")
print(f"Patient Sex:     {ds.get('PatientSex', 'N/A')}")
print(f"Institution:     {ds.get('InstitutionName', 'N/A')}")
print(f"Study Desc:      {ds.get('StudyDescription', 'N/A')}")
