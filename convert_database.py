"""
converting the input database of still images in the 16 bit TIFF format to
the output database in the JPEG format

the database was taken from Fluovisor app, okt 2019, Obninsk, Russia

Author: Alex A.Telnykh
Date: 16.10.2020

input database stucture:
path_root
    folder1
        Full
            image1_0.tiff
            image1_400.tiff
            image1_660.tiff
            image1_740.tiff
            image1_superposition_400.tiff
            image1_superposition_600.tiff
            image2_0.tiff
            image2_400.tiff
            image2_660.tiff
            image2_740.tiff
            image2_superposition_400.tiff
            image2_superposition_600.tiff
            .
            .
            .
            .
            imageN_0.tiff
            imageN_400.tiff
            imageN_660.tiff
            imageN_740.tiff
            imageN_superposition_400.tiff
            imageN_superposition_600.tiff
    folder2
        Full
            image1_0.tiff
            image1_400.tiff
            image1_660.tiff
            image1_740.tiff
            image1_superposition_400.tiff
            image1_superposition_600.tiff
            image2_0.tiff
            image2_400.tiff
            image2_660.tiff
            image2_740.tiff
            image2_superposition_400.tiff
            image2_superposition_600.tiff
            .
            .
            .
            .
            imageN_0.tiff
            imageN_400.tiff
            imageN_660.tiff
            imageN_740.tiff
            imageN_superposition_400.tiff
            imageN_superposition_600.tiff
    .
    .
    .
    .
    folderK
        Full
            image1_0.tiff
            image1_400.tiff
            image1_660.tiff
            image1_740.tiff
            image1_superposition_400.tiff
            image1_superposition_600.tiff
            image2_0.tiff
            image2_400.tiff
            image2_660.tiff
            image2_740.tiff
            image2_superposition_400.tiff
            image2_superposition_600.tiff
            .
            .
            .
            .
            imageN_0.tiff
            imageN_400.tiff
            imageN_660.tiff
            imageN_740.tiff
            imageN_superposition_400.tiff
            imageN_superposition_600.tiff

output dtabase structure:
root
    trcck1
        0000.jpg
        0001.jpg
        .
        .
        .
        xxxx.jpg
    track2
        0000.jpg
        0001.jpg
        .
        .
        .
        xxxx.jpg
    .
    .
    .
    trackK
        0000.jpg
        0001.jpg
        .
        .
        .
        xxxx.jpg
"""
import os
import numpy as np
import cv2
import argparse

track_count = 0
file_count = 0
out_dir = ''
def bytescaling(data, cmin=None, cmax=None, high=255, low=0):
    """
    Converting the input image to uint8 dtype and scaling
    the range to ``(low, high)`` (default 0-255). If the input image already has
    dtype uint8, no scaling is done.
    :param data: 16-bit image data array
    :param cmin: bias scaling of small values (def: data.min())
    :param cmax: bias scaling of large values (def: data.max())
    :param high: scale max value to high. (def: 255)
    :param low: scale min value to low. (def: 0)
    :return: 8-bit image data array
    """
    if data.dtype == np.uint8:
        return data

    if high > 255:
        high = 255
    if low < 0:
        low = 0
    if high < low:
        raise ValueError("`high` should be greater than or equal to `low`.")

    if cmin is None:
        cmin = data.min()
    if cmax is None:
        cmax = data.max()

    cscale = cmax - cmin
    if cscale == 0:
        cscale = 1

    scale = float(high - low) / cscale
    bytedata = (data - cmin) * scale + low
    return (bytedata.clip(low, high) + 0.5).astype(np.uint8)

def getPictTrue(filename, wl):
    """
    Subtracts a background  frame ("filename_0.tiff") from a fluorescent frame on a given wavelength ("filename_wl.tiff")

    :param filename: the full filename of a fluorescent frame
    :param wl:       a wavelength of a fluorescent frame

    :return: the true fluorescent picture
    """
    if filename.find('_' + str(wl)) != -1:
        pictFluo = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
        pictNull = cv2.imread(filename.replace('_' + str(wl), '_0'), cv2.IMREAD_UNCHANGED)
        pictFluo = (pictFluo - pictNull) * (pictFluo > pictNull) # cut the pixels where pictNull > pictFluo somehow
        return pictFluo
    print("ERROR: wrong filename")
    return None

def process_directory(dirName, dst_):
    global track_count
    global file_count
    global out_dir
    for f in sorted(os.listdir(dirName)):
        f = os.path.join(dirName, f)
        baseName, ext = os.path.splitext(f)
        if ext == '.tiff':
            if f.find('_740') != -1:
                print("Copy [" + baseName + "]")
                image = getPictTrue(f, wl=740)
                img8 = bytescaling(image)
                cv2.imwrite(os.path.join(out_dir, "{:05d}".format(file_count) + '.jpg'), img8)
                file_count = file_count + 1
        elif os.path.isdir(f):
            print("\nDescending into directory " + f)
            if f.find('Full') != -1:
                track_count = track_count + 1
                file_count = 0
                dst_track_path = os.path.join(dst_, 'track' + "{:05d}".format(track_count))
                if not os.path.isdir(dst_track_path):
                    os.mkdir(dst_track_path)
                out_dir = dst_track_path
            process_directory(os.path.join(dirName, f), dst_)

def ConvertDatabase(path_, dst_):
    if not os.path.isdir(dst_):
        print("make dir" + dst_)
        os.mkdir(dst_)
    process_directory(path_, dst_)


if __name__ == '__main__':
    cmdParser = argparse.ArgumentParser(
        description='converting the input database of still images in the 16 bit TIFF format to'
                    'the output database in the JPEG.\n'
                    'Author: Alex A.Telnykh\n'
                    'Date: 16.10.2020\n',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    cmdParser.add_argument('path', help='the input data base directory')
    cmdParser.add_argument('dst',  help='the output data base directory')
    cmdArgs     = cmdParser.parse_args()

    # convert database
    # path = "G:\\database\\Fluo from Obninsk\\"
    # dst = "G:\\database\\fluovisor\\"
    path = cmdArgs.path
    dst = cmdArgs.dst
    ConvertDatabase(path, dst)
