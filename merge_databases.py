import os
import shutil
import logging
import argparse

logging.basicConfig(level=logging.INFO)

def merge_directories(full_process_path, full_dest_path):
    """ Merges two directories with tracks

    :param full_process_path: full path of directory of tracks to be copied. Only tracks with existing JPEG files inside are copied.
    :param full_dest_path: full copying destination path.

    If dest_dir_name doesn't exist, being created. If exists, being cleared of empty tracks.
    If any tracks numbers missed, processing tracks are copied under these numbers firstly.
    """
    if not os.path.isdir(full_process_path):
        return

    tracks_count = 0
    full_paths_missed_numbers = []
    if os.path.isdir(full_dest_path):
        track_dirs = sorted([d for d in os.listdir(full_dest_path)                   # All names will be processed
                             if (os.path.isdir(os.path.join(full_dest_path, d)) and  # which are directories
                                 len(d) == 10 and                                    #
                                 d[:5] == 'track' and                                # and are named as
                                 d[5:].isdigit()                                     # 'trackN', N - 5-digit number
                                 )
                             ])
        while track_dirs: # Checking the existing directories
            tracks_count = tracks_count + 1
            curr_track = 'track' + "{:05d}".format(tracks_count)
            full_curr_track = os.path.join(full_dest_path, curr_track)
            if track_dirs[0] == curr_track:                              # track with current number exists
                track_dirs = track_dirs[1:]
                if not os.listdir(full_curr_track):                      # totally empty track
                    os.rmdir(full_curr_track)
                    full_paths_missed_numbers.append(full_curr_track)
                elif not [f for f in os.listdir(full_curr_track)         # track without images??
                          if os.path.splitext(f)[1] == '.jpg'            # Still be preserved as not empty
                          ]:
                    logging.warning('There are no JPEG (.jpg) images in ' + curr_track)
            else:   # current number missed
                full_paths_missed_numbers.append(full_curr_track)
    else:   # dest_dir_name doesn't exist
        os.mkdir(full_dest_path)
    logging.info("Total tracks in destination: " + str(tracks_count - len(full_paths_missed_numbers)))

    full_processing_tracks = sorted([os.path.join(full_process_path, d) for d in os.listdir(full_process_path)  # All names will be copied
                                     if (os.path.isdir(os.path.join(full_process_path, d)) and                  # which are directories,
                                         d.find('track') != -1 and                                              # are named as "*track*"
                                         [f for f in os.listdir(os.path.join(full_process_path, d))             # and have any
                                          if os.path.splitext(f)[1] == '.jpg']                                  # JPEG files inside
                                         )
                                     ])
    logging.info("Tracks to process: " + str(len(full_processing_tracks)))

    full_processing_tracks.reverse() # just to pop() in increasing order
    full_paths_missed_numbers.reverse()
    while full_paths_missed_numbers and full_processing_tracks:   # Copy as tracks under all missed numbers first
        curr_track = full_processing_tracks.pop()
        logging.info("  Processing: " + curr_track)
        shutil.copytree(curr_track, full_paths_missed_numbers.pop())
    while full_processing_tracks:                                 # Then - the remaining tracks
        tracks_count = tracks_count + 1
        curr_track = full_processing_tracks.pop()
        logging.info("  Processing: " + curr_track)
        shutil.copytree(curr_track, os.path.join(full_dest_path, 'track' + "{:05d}".format(tracks_count)))
    logging.info("Total tracks now: " + str(tracks_count - len(full_paths_missed_numbers)))

def mergeAllDirectories(path_to_all_track_dirs, dst_):
    """ Merges all DataBase directories within given path into destination directory

    :param path_to_all_track_dirs: full path from where all directories which have tracks within will be merged
    :param dst_: full destination merging path
    """
    if not os.path.isdir(path_to_all_track_dirs):
        logging.warning('Bad processing directory')
        return
    for src in sorted([os.path.join(path_to_all_track_dirs, d) for d in os.listdir(path_to_all_track_dirs) # Processing all names
                       if (  os.path.isdir(os.path.join(path_to_all_track_dirs, d)) and                    # which are directories
                             [t for t in os.listdir(os.path.join(path_to_all_track_dirs, d))               # and have tracks inside:
                              if (   os.path.isdir(os.path.join(path_to_all_track_dirs, d, t)) and         # tracks are directories
                                     t.find('track') != -1 and                                             # which are named as "*track*"
                                     [f for f in os.listdir(os.path.join(path_to_all_track_dirs, d, t))    # and have any
                                      if os.path.splitext(f)[1] == '.jpg']                                 # JPEG files inside
                                        )
                                     ]
                                 )
                              ]):
        merge_directories(src, dst_)

if __name__ == '__main__':
    cmdParser = argparse.ArgumentParser(
        description='Script merges all the directories which contain tracks into one dataBase directory\n'
                    'Author: Orest Chura\n'
                    'Date: 29.11.2020\n',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    cmdParser.add_argument('path', help='path where all the directories with tracks lies')
    cmdParser.add_argument('dst',  help='the output data base directory')
    cmdArgs     = cmdParser.parse_args()

    # merge
    # path = "G:\\database\\Fluo from Obninsk\\"
    # dst = "G:\\database\\fluovisor\\"
    path = cmdArgs.path
    dst = cmdArgs.dst
    mergeAllDirectories(path, dst)
