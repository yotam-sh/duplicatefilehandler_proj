import os
import argparse
import hashlib
from collections import defaultdict


def path_parser():
    parser = argparse.ArgumentParser(description='Please enter path')
    parser.add_argument('path', nargs='?', default=False)
    args = parser.parse_args()
    path = args.path
    return path


def duplicate_sorter(file_info_dict, order):
    # Data prep for sorting
    filename_size_dict = defaultdict(list)
    for filename, filesize in file_info_dict.items():
        filename_size_dict[filesize].append(filename)
    delete_keys_list = [size for size, filelist in filename_size_dict.items() if len(filelist) <= 1]
    for key_to_delete in delete_keys_list:
        del filename_size_dict[key_to_delete]
    # Data sorting
    sorted_list = (sorted(filename_size_dict.items(), key=lambda x: x[0], reverse=order))
    for size, files in sorted_list:
        files.sort(reverse=order)
    for k, v in sorted_list:
        print(f'\n{k} bytes')
        for i in v:
            print(i)
            # Below prints only sub-folder and file name in relation to parent dir
            # print(i.removeprefix(args.path + '\\'))
    return sorted_list


def hashed_dict_creator(sorted_list):
    # Create dict for hashed files with all info
    hash_dict = dict()
    for filesize, filelist in sorted_list:
        for file in filelist:
            md5_hash = hashlib.md5()
            with open(file, 'rb') as open_file:
                content = open_file.read()
                md5_hash.update(content)
                digest = md5_hash.hexdigest()
            if filesize in hash_dict:
                for subdict in hash_dict[filesize]:
                    if digest in subdict:
                        value_temp = subdict[digest]
                        subdict.update({digest: value_temp + [file]})
                    else:
                        subdict.update({digest: [file]})
            else:
                hash_dict[filesize] = [{digest: [file]}]

    filtered_dict, enum_dict = hashed_dict_filter(hash_dict)
    return filtered_dict, enum_dict


def hashed_dict_filter(created_dict):
    delete_keys_dict = dict()
    for filesize, sublist in created_dict.items():
        for subdict in sublist:
            for filehash, filelist in subdict.items():
                if len(filelist) <= 1:
                    delete_keys_dict[filehash] = filesize
    for filehash, filesize in delete_keys_dict.items():
        for subdict in created_dict[filesize]:
            del subdict[filehash]

    filtered_dict, enum_dict = hashed_dict_enumerator(created_dict)
    return filtered_dict, enum_dict


def hashed_dict_enumerator(filtered_dict):
    # Create dict for hashed files with all info
    enum_counter = 1
    enum_dict = dict()
    for filesize, sublist in filtered_dict.items():
        print(f'\n{filesize} bytes')
        for subdict in sublist:
            for filehash, filelist in subdict.items():
                print(f'Hash: {filehash}')
                for file in filelist:
                    print(f'{enum_counter}. {file}')
                    enum_dict[enum_counter] = [file, filesize]
                    enum_counter += 1

    return filtered_dict, enum_dict


def user_parameters():
    # Get format filter and sorting option
    file_format = input('\nEnter file format:')
    sorting_input = input('\nSize sorting options: \n'
                          '1. Descending \n'
                          '2. Ascending \n \n'
                          'Enter a sorting option:')

    sorting_options = ['1', '2']
    while sorting_input not in sorting_options:
        sorting_input = input('Wrong option \n\n'
                              'Enter a sorting option:')
    if sorting_input == '1':
        sort_order = True
    elif sorting_input == '2':
        sort_order = False
    return file_format, sort_order


def first_file_sort(f_format):
    filename_size = dict()
    for root, dirs, files in os.walk(os.getcwd(), topdown=False):
        for name in files:
            file_name = os.path.join(root, name)
            file_size = os.path.getsize(file_name)
            if not f_format:
                filename_size[file_name] = file_size
            else:
                if f_format == file_name[(len(f_format) * -1):]:
                    filename_size[file_name] = file_size
                else:
                    pass
    return filename_size


def optional_hash_sorter(sorted_list):
    check_loop = False
    while check_loop is False:
        hash_check = input('\nCheck for duplicates? ').lower()
        if hash_check == 'yes' or hash_check == 'no':
            if hash_check == 'yes':
                filtered_dict, enum_dict = hashed_dict_creator(sorted_list)
            check_loop = True
        else:
            print('Wrong option')
            check_loop = False
    return filtered_dict, enum_dict


def files_validation(enum_dict):
    valid_numbers = [i for i in range(1, len(enum_dict) + 1)]
    all_files_valid = False
    while all_files_valid is False:
        files_to_del = input('\nEnter file numbers to delete: ')

        if files_to_del == '':
            print('Wrong format')
            continue
        else:
            split_input = files_to_del.split()

        valid_files = []
        for file_num in split_input:
            try:
                int_file_num = int(file_num)
                if int_file_num in valid_numbers:
                    valid_files.append(1)
                else:
                    valid_files.append(0)
            except ValueError:
                valid_files.append(0)

        if 0 in valid_files:
            all_files_valid = False
            print('Wrong format')
        else:
            all_files_valid = True

    return split_input


def file_deleter(split_input, enum_dict):
    space_cleared = 0
    for file_num in split_input:
        for enum_number, file_name in enum_dict.items():
            if enum_number == int(file_num):
                space_cleared += file_name[1]
                os.remove(file_name[0])
    print(f'\nTotal freed up space: {space_cleared} bytes')


def optional_files_delete(enum_dict):
    delete_bool = False
    while delete_bool is False:
        delete_input = input('\nDelete files? ').lower()
        if delete_input == 'yes' or delete_input == 'no':
            delete_bool = True
        else:
            print('Wrong option')
            delete_bool = False

    if delete_input == 'no':
        pass
    else:
        # Check if all file number inputs are valid
        split_input = files_validation(enum_dict)
        # Delete files
        file_deleter(split_input, enum_dict)


def main(args_path):
    if args_path:
        os.chdir(args_path)

        file_format, sort_order = user_parameters()
        filename_size = first_file_sort(file_format)
        sorted_list = duplicate_sorter(filename_size, sort_order)
        filtered_dict, enum_dict = optional_hash_sorter(sorted_list)
        optional_files_delete(enum_dict)

    else:
        print('Directory is not specified')


main(path_parser())
