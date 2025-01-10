from shutil import rmtree, copyfile
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers import modes, Cipher
from subprocess import run
from hashlib import md5
from os import path, mkdir, walk, remove, rename


def decrypt_file(file_data: bytes, key: bytes) -> bytes:
    cipher = Cipher(algorithms.AES128(key), modes.ECB())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(file_data) + decryptor.finalize()
    return decrypted_data

def encrypt_file(file_data: bytes, key: bytes) -> bytes:
    padding_data = md5(file_data).digest()
    cipher = Cipher(algorithms.AES128(key), modes.ECB())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(file_data+padding_data) + encryptor.finalize()
    return encrypted_data


def decompile():
    if not path.exists("temp"):
        mkdir("temp")
    run(["./tools/ildasm.exe", "/UTF8", "./Register.UI.dec.dll", "/OUT=./temp/Register.UI.il", "/NOBAR"])
    with open("./temp/Register.UI.il", "r+", encoding="utf-8") as f:
        content = f.read()
        content = content.replace("ldsfld     bool Wuyou.Exam.Encrypt.PersionVersionEncryptModuleEntry::'<IsActivation>k__BackingField'", "ldc.i4.1")
        f.seek(0)
        f.truncate()
        f.write(content)
    run([r"./tools/ilasm.exe", "/DLL", "/QUIET", "/OUTPUT=Register.UI.modified.dll", "./temp/Register.UI.il"])
    rmtree("./temp")
    for _,_, files in walk("./"):
        for name in files:
            if name.endswith('.resources'):
                remove(name)

if __name__ == '__main__':
    file_path = input(r"请输入程序安装路径(C:\WYKS2Python)：")
    with open(path.join(file_path, "Register.UI.dll"), "rb") as f:
        file_data = f.read()
    with open(path.join(file_path, "Exam.exe"), "rb") as f:
        key = md5(f.read()).digest()
    with open("./Register.UI.dec.dll", "wb") as f:
        f.write(decrypt_file(file_data, key))
    print("解密完成, 开始补丁")
    decompile()
    with open("./Register.UI.dll", "wb") as f:
        with open("./Register.UI.modified.dll", "rb") as f2:
            f.write(encrypt_file(f2.read(), key))
    rename(path.join(file_path, "Register.UI.dll"), path.join(file_path, "Register.UI.dll.bak"))
    copyfile("./Register.UI.dll", path.join(file_path, "Register.UI.dll"))
    print("补丁完成")
    remove("./Register.UI.dec.dll")
    remove("./Register.UI.modified.dll")
    remove("./Register.UI.dll")
    input("按任意键退出...")
