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


def patch(filename):
    if not path.exists("temp"):
        mkdir("temp")
    run(["./tools/ildasm.exe", "/UTF8", f"./{filename}.dec.dll", f"/OUT=./temp/{filename}.il", "/NOBAR"])
    with open(f"./temp/{filename}.il", "r+", encoding="utf-8") as f:
        content = f.read()
        content = content.replace("ldsfld     bool Wuyou.Exam.Encrypt.PersionVersionEncryptModuleEntry::'<IsActivation>k__BackingField'", "ldc.i4.1")
        f.seek(0)
        f.truncate()
        f.write(content)
    run(["./tools/ilasm.exe", "/DLL", "/QUIET", f"/OUTPUT={filename}.modified.dll", f"./temp/{filename}.il"])
    rmtree("./temp")
    for _,_, files in walk("./"):
        for name in files:
            if name.endswith('.resources'):
                remove(name)

if __name__ == '__main__':
    try:
        file_path = input(r"请输入程序安装路径(C:\WYKS2Python)：")
        if path.exists(path.join(file_path, "Register.UI.dll")):
            with open(path.join(file_path, "Register.UI.dll"), "rb") as f:
                file_data = f.read()
            if path.exists(path.join(file_path, "Register.UI.dll.bak")):
                with open(path.join(file_path, "Register.UI.dll.bak"), "rb") as f:
                    file_data_bak = f.read()
                if md5(file_data).hexdigest() == md5(file_data_bak).hexdigest():
                    remove(path.join(file_path, "Register.UI.dll.bak"))
                else:
                    print("检测到文件已被修改，可能已破解")
            with open(path.join(file_path, "Exam.exe"), "rb") as f:
                key = md5(f.read()).digest()
            decrypted_data = decrypt_file(file_data, key)
            if not decrypted_data.startswith(b'MZ'):
                print("解密失败: 生成的文件无效。")
                input("按任意键退出...")
                exit(1)
            
            with open("./Register.UI.dec.dll", "wb") as f:
                f.write(decrypted_data)
            print("解密完成, 开始补丁")
            patch("Register.UI")
            with open("./Register.UI.dll", "wb") as f:
                with open("./Register.UI.modified.dll", "rb") as f2:
                    f.write(encrypt_file(f2.read(), key))
            rename(path.join(file_path, "Register.UI.dll"), path.join(file_path, "Register.UI.dll.bak"))
            copyfile("./Register.UI.dll", path.join(file_path, "Register.UI.dll"))
            print("补丁完成")
            remove("./Register.UI.dec.dll")
            remove("./Register.UI.modified.dll")
            remove("./Register.UI.dll")
        elif path.exists(path.join(file_path, "Wuyou.Exam.Encrypt.dll")):
            with open(path.join(file_path, "Wuyou.Exam.Encrypt.dll"), "rb") as f:
                file_data = f.read()
            if path.exists(path.join(file_path, "Wuyou.Exam.Encrypt.dll.bak")):
                with open(path.join(file_path, "Wuyou.Exam.Encrypt.dll.bak"), "rb") as f:
                    file_data_bak = f.read()
                if md5(file_data).hexdigest() == md5(file_data_bak).hexdigest():
                    remove(path.join(file_path, "Wuyou.Exam.Encrypt.dll.bak"))
                else:
                    print("检测到文件已被修改，可能已破解")
            with open(path.join(file_path, "Exam.exe"), "rb") as f:
                key = md5(f.read()).digest()
            decrypted_data = decrypt_file(file_data, key)
            if not decrypted_data.startswith(b'MZ'):
                print("解密失败: 生成的文件无效。")
                input("按任意键退出...")
                exit(1)
            
            with open("./Wuyou.Exam.Encrypt.dec.dll", "wb") as f:
                f.write(decrypted_data)
            print("解密完成, 开始补丁")
            patch("Wuyou.Exam.Encrypt")
            with open("./Wuyou.Exam.Encrypt.dll", "wb") as f:
                with open("./Wuyou.Exam.Encrypt.modified.dll", "rb") as f2:
                    f.write(encrypt_file(f2.read(), key))
            rename(path.join(file_path, "Wuyou.Exam.Encrypt.dll"), path.join(file_path, "Wuyou.Exam.Encrypt.dll.bak"))
            copyfile("./Wuyou.Exam.Encrypt.dll", path.join(file_path, "Wuyou.Exam.Encrypt.dll"))
            print("补丁完成")
            remove("./Wuyou.Exam.Encrypt.dec.dll")
            remove("./Wuyou.Exam.Encrypt.modified.dll")
            remove("./Wuyou.Exam.Encrypt.dll")
        else:
            print("未找到目标文件")
            print("请确认：1. 安装路径是否正确;    2. 程序是否完整安装")
    except Exception as e:
        print(e)
        print("处理过程中出错，未完成补丁")
    
    input("按任意键退出...")
