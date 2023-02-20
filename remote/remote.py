import sys
import os
import ftplib
import time
import subprocess
import shutil
import configparser

config = configparser.ConfigParser()
config.read('remote.ini')
# local_work_dir = config['dir']['local']
# remote_work_dir = config['dir']['remote']
ftp_work_dir = config['dir']['ftp']
ip = config['net']['ip']
username = config['net']['username']
password = config['net']['password']

def download_file(ftp, remote_file, localfile):
    with open(localfile, 'wb') as fp:
        print(ftp.retrbinary('RETR ' + remote_file, fp.write))
    fp.close() 

def uploadfile(ftp, remoteFile, localFile):
    with open(localFile, 'rb') as fp:
        print(ftp.storbinary('STOR ' + remoteFile, fp, 1024))
    fp.close() 

def run_codesign(codesign_dir):
    shutil.copyfile('001_run.bat', codesign_dir + '/001_run.bat')
    shutil.copyfile('002_move.bat', codesign_dir + '/002_move.bat')
    os.remove(codesign_dir + '/CodeSign.exe')
    os.remove(codesign_dir + '/CodeSign_Account.bat')
    shutil.copyfile('CodeSign.exe', codesign_dir + '/CodeSign.exe')
    shutil.copyfile('CodeSign_Account.bat', codesign_dir + '/CodeSign_Account.bat')
    p = subprocess.Popen('cmd.exe /c 001_run.bat', cwd=codesign_dir)
    stdout, stderr = p.communicate()
    print(p.returncode)
    # time.sleep(10)
    p = subprocess.Popen('cmd.exe /c 002_move.bat', cwd=codesign_dir)
    stdout, stderr = p.communicate()
    print(p.returncode)
    # time.sleep(2)

def monitor_tw_ftp(tw_ftp):
    res = None
    codesigns_flag = tw_ftp.nlst('flag')
    print(codesigns_flag)
    if len(codesigns_flag) != 0:
        flag = codesigns_flag[0].split('/')[1]
        download_file(tw_ftp, codesigns_flag[0], flag)
        with open(flag, 'r') as f:
            res = f.readline().split('\n')[0]
            print(res)
        if res != None:
            download_file(tw_ftp, 'codesign/' + res, res)
            codesign_dir = res.split('___')[0].split('.7z')[0]
            cmd = '"C:/Program Files/7-Zip/7z.exe" x ' + res + ' ' + codesign_dir
            os.system(cmd)
            bin_zip = 'ABC_bin___' + codesign_dir + '__' + res.split('___')[1] + '.zip'
            if os.path.exists(codesign_dir + '/a_all.bin'):
                run_codesign(codesign_dir)
                cmd = '"C:/Program Files/7-Zip/7z.exe" a ' + bin_zip + ' ' + codesign_dir + '/ABC_bin'
                os.system(cmd)
            else:
                subdir = os.listdir(codesign_dir)[0]
                run_codesign(codesign_dir + '/' + subdir)
                cmd = '"C:/Program Files/7-Zip/7z.exe" a ' + bin_zip + ' ' + codesign_dir + '/' + subdir + '/ABC_bin'
                os.system(cmd)
            uploadfile(tw_ftp, 'bin/' + bin_zip, bin_zip)
            os.system('echo done > done__' + res.split('___')[1])
            uploadfile(tw_ftp, 'done__' + res.split('___')[1], 'done__' + res.split('___')[1])
            tw_ftp.delete('codesign/' + res)
            tw_ftp.delete(codesigns_flag[0])
            # os.removedirs(codesign_dir)
            shutil.rmtree(codesign_dir, ignore_errors=True)
            os.remove(bin_zip)
            os.remove('done__' + res.split('___')[1])
            os.remove(flag)
            os.remove(res)

if __name__ == "__main__":
    ftp = ftplib.FTP_TLS()
    print(ftp.connect(ip, 21))
    print(ftp.login(username, password))
    print(ftp.prot_p())
    print(ftp.cwd(ftp_work_dir))

    while True:
        monitor_tw_ftp(ftp)
        time.sleep(2)
