from storjtorrent import StorjTorrent
from bencode import bdecode
import time
import os
from shutil import move

class Torrenter():
    def __init__(self, data_dir, torrent_dir):
        self.data_dir = data_dir
        self.torrent_dir = torrent_dir
        self.full_names_by_truncated = dict()
        self.keys_by_name = dict()
        self.files_by_name = dict()
        self.st = StorjTorrent()

    def add(self, key, torrent_file):
        torrent_info = bdecode(open(torrent_file, 'rb').read())

        ## storjtorrent truncates names so we need to too if we want
        ## to be able to index of them
        full_torrent_name = torrent_info['info']['name']
        truncated_torrent_name = full_torrent_name[:40]

        print "Adding %s" % full_torrent_name

        self.keys_by_name[full_torrent_name] = key
        self.files_by_name[full_torrent_name] = torrent_file
        self.full_names_by_truncated[truncated_torrent_name] = full_torrent_name
        self.st.add_torrent(torrent_file, False)

    def done(self):
        while len(self.keys_by_name) > 0:
            time.sleep(5)

            os.system("clear")

            status = self.st.get_status()

            for truncated_torrent_name, torrent_status in status['torrents'].iteritems():
                if truncated_torrent_name in self.full_names_by_truncated:                    
                    torrent_name = self.full_names_by_truncated[truncated_torrent_name]
                    percent_done = torrent_status['progress']
                    seeds = torrent_status['num_seeds']
                    print "%s: %.2f%% (%d seeds)" % (torrent_name, percent_done * 100, seeds)

                    if percent_done >= 1:
                        print "%s finished" % torrent_name

                        torrent_file = self.files_by_name.pop(torrent_name)
                        key = self.keys_by_name.pop(torrent_name)
                        self.full_names_by_truncated.pop(truncated_torrent_name)

                        self.st.remove_torrent(path=torrent_file, delete_files=False)

                        move(torrent_name, self.data_dir)
                        move(torrent_file, self.torrent_dir)

                        yield key


