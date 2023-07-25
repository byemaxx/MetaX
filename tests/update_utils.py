import contextlib
import os
import shutil
import stat

def on_rm_error(func, path, exc_info):
    """
    处理删除目录时的错误
    """
    # 设置文件或目录的权限以便删除
    os.chmod(path, stat.S_IWRITE)
    # 删除文件或目录
    os.remove(path)
    
    
def force_remove_dir(dir_path):
    """
    强制删除文件夹，如果文件夹不存在则跳过
    """
    with contextlib.suppress(FileNotFoundError):
        shutil.rmtree(dir_path, onerror=on_rm_error)
    

def remove_pycache(dir_path):
    """
    删除文件夹及其子文件夹中所有名为 __pycache__ 的文件夹
    """
    for root, dirs, files in os.walk(dir_path):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                dir_path = os.path.join(root, dir_name)
                force_remove_dir(dir_path)
                

    
def update_desktop():

    # remove the utlis folder from the path
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    desktop_metax_path = os.path.join(desktop_path, 'MetaX_Suite/MetaX')
    desktop_metax_utils_path = os.path.join(desktop_path, 'MetaX_Suite/MetaX/MetaX/utils')
    # check if the utils folder exists
    if not os.path.exists(desktop_metax_utils_path):
        print(f'utils folder does not exist in {desktop_metax_utils_path}')
        print('Update Desktop failed!')
        return
    # remove the utlis folder from the path
    if os.path.exists(desktop_metax_utils_path):
        force_remove_dir(desktop_metax_utils_path)
        print(f'utils folder removed from {desktop_metax_utils_path}')

    # copy the utils folder to the path
    script_path = os.path.dirname(os.path.realpath(__file__))
    new_utils_path = os.path.join(script_path, '../utils')
    # copy the new utils folder to desktop_metax_utils_path
    print(f'utils folder copied from \n{new_utils_path} \nto \n{desktop_metax_utils_path}')
    shutil.copytree(new_utils_path, desktop_metax_utils_path)
    # remove all __pycache__ folder in the utils folder and its subfolders
    remove_pycache(desktop_metax_path)
    print('utils folder copied successfully!')

def update_z():
    # check if Z:/Qing/MetaX exists
    if not os.path.exists('Z:/Qing/MetaX'):
        print('Z:/Qing/MetaX does not exist!')
        return
    # get directory list of Z:/Qing/MetaX
    dir_list = os.listdir('Z:/Qing/MetaX')
    if old_dir := next((i for i in dir_list if i.startswith('Update')), None):
        force_remove_dir(f'Z:/Qing/MetaX/{old_dir}')
        os.remove(f'Z:/Qing/MetaX/{old_dir}')
        print(f'utils folder removed from Z:/Qing/MetaX/{old_dir}')

    # get Version number from ../utils/GUI.py
    script_path = os.path.dirname(os.path.realpath(__file__))
    gui_path = os.path.join(script_path, '../utils/GUI.py')
    with open(gui_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip("'")
            break
    new_dir_name = f'Update_{version}'

    # create new directory
    if not os.path.exists(f'Z:/Qing/MetaX/{new_dir_name}'):
        os.mkdir(f'Z:/Qing/MetaX/{new_dir_name}')
        if not os.path.exists(f'Z:/Qing/MetaX/{new_dir_name}/MetaX'):
            os.mkdir(f'Z:/Qing/MetaX/{new_dir_name}/MetaX')
    
    z_update_path = f'Z:/Qing/MetaX/{new_dir_name}/MetaX/utils'

    # copy the utils folder to the path
    new_utils_path = os.path.join(script_path, '../utils')
    # copy the new utils folder to desktop_metax_utils_path
    print(f'utils folder copied from \n{new_utils_path} to {z_update_path}')
    shutil.copytree(new_utils_path, z_update_path)
    # remove the __pycache__ folder in the utils folder
    remove_pycache(z_update_path)
    print('utils folder copied successfully!')
    
def create_zip_and_move():
    from zipfile import ZipFile

    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    desktop_metax_path = os.path.join(desktop_path, 'MetaX_Suite/MetaX')
    save_path = os.path.join(desktop_path, 'MetaX_Suite')
    print(f'Zipping {desktop_metax_path} to {save_path}/MetaX.zip')
    # Create a ZipFile Object
    with ZipFile(f'{save_path}/MetaX.zip', 'w', compression=8) as zipObj:
        # Iterate over all the files in directory
        for folderName, subfolders, filenames in os.walk(desktop_metax_path):
            for filename in filenames:
                #create complete filepath of file in directory
                filePath = os.path.join(folderName, filename)
                # Get the relative path of the file from the MetaX folder
                relPath = os.path.relpath(filePath, desktop_metax_path)
                # Add file to zip with the relative path as the arcname
                zipObj.write(filePath, arcname=relPath)
    print('Zip file created successfully!')
    
    # move the zip file to Z:/Qing/MetaX
    # delete the old zip file
    if os.path.exists('Z:/Qing/MetaX/MetaX.zip'):
        os.remove('Z:/Qing/MetaX/MetaX.zip')
        print('Z:/Qing/MetaX/MetaX.zip removed!')
    # move the new zip file
    shutil.move(f'{save_path}/MetaX.zip', 'Z:/Qing/MetaX/MetaX.zip')
    print('Z:/Qing/MetaX/MetaX.zip moved successfully!')
    
if __name__ == '__main__':
    update_desktop()
    update_z()
    create_zip_and_move()