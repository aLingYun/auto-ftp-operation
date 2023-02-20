# import sys
import os
import ftplib
import time
# import subprocess
# import shutil
import configparser

codesign_hash = ''

config = configparser.ConfigParser()
config.read('transfer.ini')
# local_work_dir = config['dir']['local']
# remote_work_dir = config['dir']['remote']
ftp_work_dir = config['dir']['ftp']
hf_ip = config['hf_net']['ip']
hf_username = config['hf_net']['username']
hf_password = config['hf_net']['password']
tw_ip = config['tw_net']['ip']
tw_username = config['tw_net']['username']
tw_password = config['tw_net']['password']

def download_file(ftp, remote_file, localfile):
    with open(localfile, 'wb') as fp:
        print(ftp.retrbinary('RETR ' + remote_file, fp.write))
    fp.close() 

def uploadfile(ftp, remoteFile, localFile):
    with open(localFile, 'rb') as fp:
        print(ftp.storbinary('STOR ' + remoteFile, fp, 1024))
    fp.close() 

def monitor_hf_ftp(hf_ftp, tw_ftp):
    global codesign_hash
    res = None
    codesigns_flag = hf_ftp.nlst('flag')
    while len(codesigns_flag) == 0:
        codesigns_flag = hf_ftp.nlst('flag')
        time.sleep(2)
    # if len(codesigns_flag) != 0:
    flag = codesigns_flag[0].split('/')[1]
    download_file(hf_ftp, codesigns_flag[0], flag)
    with open(flag, 'r') as f:
        res = f.readline().split('\n')[0]  # res means codesign files
        print(res)
    if res != None:
        codesign_hash = 'done__' + res.split('___')[1]
        download_file(hf_ftp, 'codesign/' + res, res)
        uploadfile(tw_ftp, 'codesign/' + res, res)
        uploadfile(tw_ftp, codesigns_flag[0], flag)
        hf_ftp.delete('codesign/' + res)
        hf_ftp.delete(codesigns_flag[0])
        os.remove(res)
        os.remove(flag)

def monitor_tw_ftp(hf_ftp, tw_ftp):
    global codesign_hash
    print('please wait ......')
    while not codesign_hash in tw_ftp.nlst('./'):
        time.sleep(2)
    abc_bin = tw_ftp.nlst('bin')[0]
    local_bin = abc_bin.split('/')[1]
    download_file(tw_ftp, codesign_hash, codesign_hash)
    download_file(tw_ftp, abc_bin, local_bin)
    uploadfile(hf_ftp, abc_bin, local_bin)
    uploadfile(hf_ftp, codesign_hash, codesign_hash)
    tw_ftp.delete(abc_bin)
    tw_ftp.delete(codesign_hash)
    os.remove(local_bin)
    os.remove(codesign_hash)

def while_monitor(hf_ftp, tw_ftp):
    while True:
        monitor_hf_ftp(hf_ftp, tw_ftp)
        monitor_tw_ftp(hf_ftp, tw_ftp)

if __name__ == "__main__":
    hf_ftp = ftplib.FTP_TLS()
    print(hf_ftp.connect(hf_ip, 21))
    print(hf_ftp.login(hf_username, hf_password))
    print(hf_ftp.prot_p())
    print(hf_ftp.cwd(ftp_work_dir))
    
    tw_ftp = ftplib.FTP_TLS()
    print(tw_ftp.connect(tw_ip, 21))
    print(tw_ftp.login(tw_username, tw_password))
    print(tw_ftp.prot_p())
    print(tw_ftp.cwd(ftp_work_dir))

    while_monitor(hf_ftp, tw_ftp)

    hf_ftp.close()
    tw_ftp.close()