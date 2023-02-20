import hashlib
import os
import sys
import ftplib
import configparser
import time

config = configparser.ConfigParser()
config.read('local.ini')
ftp_work_dir = config['dir']['ftp']
ip = config['net']['ip']
username = config['net']['username']
password = config['net']['password']

def file_hash(file_path: str, hash_method) -> str:
    if not os.path.isfile(file_path):
        print('文件不存在。')
        return ''
    h = hash_method()
    with open(file_path, 'rb') as f:
        while b := f.read(8192):
            h.update(b)
    return h.hexdigest()

def file_sha256(file_path: str) -> str:
    return file_hash(file_path, hashlib.sha256)

def download_file(ftp, remote_file, localfile):
    with open(localfile, 'wb') as fp:
        print(ftp.retrbinary('RETR ' + remote_file, fp.write))
    fp.close() 

def uploadfile(ftp, remoteFile, localFile):
    with open(localFile, 'rb') as fp:
        print(ftp.storbinary('STOR ' + remoteFile, fp, 1024))
    fp.close() 

if __name__ == "__main__":
    ftp = ftplib.FTP_TLS()
    print(ftp.connect(ip, 21))
    print(ftp.login(username, password))
    print(ftp.prot_p())
    print(ftp.cwd(ftp_work_dir))

    if len(sys.argv) == 2:
        codesign_file = sys.argv[1]
        flag_file = file_sha256(codesign_file)
        os.system('echo ' + codesign_file + '___' + flag_file[0:8] + '>' + flag_file[0:8])
        uploadfile(ftp, 'codesign/' + codesign_file + '___' + flag_file[0:8], codesign_file)
        uploadfile(ftp, 'flag/' + flag_file[0:8], flag_file[0:8])

        print('please wait ......')
        # time.sleep(60)
        while not 'done__' + flag_file[0:8] in ftp.nlst('./'):
            time.sleep(2)
        bin_zip = 'ABC_bin___' + codesign_file.split('.7z')[0] + '__' + flag_file[0:8] + '.zip'
        download_file(ftp, 'bin/' + bin_zip, bin_zip)
        ftp.delete('bin/' + bin_zip)
        ftp.delete('done__' + flag_file[0:8])
        os.remove(flag_file[0:8])        
    else: 
        print('argument error!')

    ftp.close()