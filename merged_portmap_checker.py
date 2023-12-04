#!/usr/bin/env python
# coding: utf-8
# In[1]:
import os
import pandas as pd
from tabulate import tabulate
import textfsm
import re
import numpy as np
# In[2]:
def remove_list_dups(lst):
    lst = lst
    temp_list = []
    for elem in lst:
        if elem not in temp_list:
            temp_list.append(elem)
    return temp_list
# In[ ]:
# In[3]:
def get_value(key):
    ''' gets variable values from settings file.
        MAKE SURE TO PUT THE RIGHT SETTINGS FILE PATH '''
    key = key
    plog(f'getting value {key}..')
    try:
        key = key
        with open("merged_portmap_checker_settings.txt") as settings_file:
                settings_file = settings_file.read()
        if '#' in settings_file.split(key)[0].split("\n")[-1]:
            msg = 'value is commented out'
            plog(msg)
            return None
        else:
            #var = settings_file.split(key)[1].split("\n")[0].strip(" ").strip("\"").strip("\'")
            #plog(key)
            unstriped = settings_file.split(key)[1].split("\n")[0].strip()
            #plog(unstriped[0])
            if unstriped.lower()[0] ==  '[' and unstriped.lower()[-1] == ']':
                var1 = unstriped.strip('[').strip(']').split(',')
                var = [e.strip().strip("'").strip('"') for e in var1]
                return var
            elif '"' == unstriped[0]  or '"' == unstriped[-1] or "'" == unstriped[0]  or "'" == unstriped[-1]:
                #plog("is string")
                var = unstriped.strip("\"").strip("\'")
                return var
            elif  unstriped.isnumeric():
                var = int(unstriped)
                return var
            elif unstriped.lower() == 'true':
                var = True
                return var
            elif unstriped.lower() ==  'false':
                var = False
                return var
            else:
                plog(f"{unstriped} -invalid variable set in settings")
    except Exception as e:
        try:
            plog(f'EXCEPTION ERROR - get_value() - {e}')
        except:
            plog(f'EXCEPTION ERROR - get_value() - {e}') 
def plog(string, log_only=False):
    """prints and logs string"""
    global session_id #so it wont have to create multiple text file for every plog call. this will ensure that only one text file will be generated for every session.
    string = str(string)
    if log_only == False: #prints if log_only is false default is false
        print(string)
    try:
        session_id = session_id # checks if session_id is defined 
    except:
        from datetime import datetime
        date_now = datetime.now().strftime("%m-%d-%y_%H%M%S")  # defines the session id
        session_id = str(date_now)
    output_folder = r'print_log\\'	# this is the log folder path
    try:
        if os.path.exists(output_folder): # checks if folder already exist, if not the it will create one
            pass
        else:	
            os.mkdir(output_folder)
    except:
        import os
        if os.path.exists(output_folder): 
            pass
        else:	
            os.mkdir(output_folder)
    with open(f'{output_folder}/plog_{session_id}.txt', 'a') as f: #saves the string in the text file 
        f.write(string)
        f.write('\n')
    return
# In[4]:
def current_dir_folder_lister(path):
    """lists the folders in a dir FIRST LEVEL ONLY"""
    plog('-------current_dir_folder_lister()')
    path = path 
    current_listdir = os.listdir(path)
    plog(f'listing files in folder {path}')
    #plog(current_dir_list)
    folder_list = []
    for obj in current_listdir: 
        obj_path = f'{path}\\{obj}'  
        if os.path.isdir(obj_path): 
            #plog(obj_path)
            folder_list.append(obj_path)
    return folder_list
def directory_folder_lister(root_path):
    """lists all the folder and subfolder in a directory"""
    plog('-------directory_folder_lister()')
    root_path = root_path
    list_of_folders = current_dir_folder_lister(root_path)    
    dir_map = [list_of_folders]
    for list_of_folders in dir_map:
        for folder in list_of_folders:
                #plog(current_dir_folder_lister(folder))
                dir_map.append(current_dir_folder_lister(folder))
    return dir_map
def get_file_dir_level(root_path, file_path):
    """gets the level of the directory relative to the root_path"""
    plog('-------get_file_dir_level()')
    root_path = root_path
    file_path = file_path
    return len(file_path.split(f'{root_path}\\')[1].split('\\')) - 1  
# In[5]:
def list_hostnames(switchcount_wb, portmap_type):
    """list hostnames from switchcoun work book"""
    plog(f'------list hostnames from switchcoun work book')
    switchcount_wb = switchcount_wb
    portmap_type = portmap_type.lower().strip()
    hostname_list = []
    for sheet in switchcount_wb:
        #plog(sheet)
        if portmap_type.strip().lower() == 'cmo':
            df =  switchcount_wb[sheet]
            try:
                hostname_l = get_CMO_hostname_from_sheet(df)
            except:
                continue
            #plog(sheet)
            #plog(hostname)
            for hostname in hostname_l:
                hostname_list.append(hostname.strip())
        if portmap_type.strip().lower() == 'fmo':
            df =  switchcount_wb[sheet]
            try:
                hostname = get_FMO_hostname_from_sheet(df)
            except:
                continue
            #plog(sheet)
            #plog(hostname)
            hostname_list.append(hostname.strip())
    return hostname_list
def get_text_log_files(device_outputs_folder):
    """gets all the text and log file's path from device_outputs_folder"""
    plog('-'*80)
    plog(f"---get_text_log_files()")
    device_outputs_folder = device_outputs_folder
    folders = []
    folders.append([[device_outputs_folder]])
    folders.append(directory_folder_lister(device_outputs_folder))
    folders_clean = []
    for folder_list in folders:
        for folder_l in folder_list:
            #plog(folder_l)
            for folder_path in folder_l:
                #plog(folder_path)
                folders_clean.append(folder_path)
    all_device_output_files = []
    for device_outputs_folder in folders_clean:
        device_output_files = os.listdir(device_outputs_folder)
        #plog(device_output_files)
        for file in device_output_files:
            file = f'{device_outputs_folder}\\{file}'
            if os.path.isfile(file):
                #plog(file)
                if 'log' in file.split('.') or 'txt' in file.split('.'):
                    all_device_output_files.append(file)
    return all_device_output_files
def get_hostname_from_output_text(file):
    '''get_hostname_from_output_text'''
    plog('-------get_hostname_from_output_text()')
    file = file
    plog(f'get_hostname_from_output_text')
    hostname = file.split('show')[0].split('\n')[-1].split('#')[0]
    plog(f'\t{hostname}')
    return hostname
def store_all_output_text_in_dict(device_outputfiles):
    '''store_all_output_text_in_dict'''
    plog('-'*80)
    plog(f'---store_all_output_text_in_dict()')
    output_dict = {}
    for file in device_outputfiles:
        with open(file) as f:
            file = f.read()
        hostname = get_hostname_from_output_text(file)
        output_dict[hostname.strip()] = file
    return output_dict
def get_device_os(hostname):
    """gets device os from output file"""
    plog(f'gets device os from output file')
    try:
        device_os = output_dict[hostname].split("show version")[1].split(hostname)[0].split(',')[0].split('\n')[-1]
        #plog(f'{hostname} -- {device_os}')
    except:
        pass
    device_os = ''
    return device_os
# In[6]:
def get_cmo_hostnames_from_portmap(path):
    """get_cmo_hostnames_from_portmap"""
    plog('-'*80)
    plog('---"get_cmo_hostnames_from_portmap()')
    path = path
    df = pd.read_excel(path)
    cmo_hostnames_list = df['CMO Hostname'].unique().tolist()
    temp_list = []
    for e in cmo_hostnames_list:
        if isinstance(e, str):
            if e.strip() == '':
                continue
            elif 'CMO Hostname' in e:
                continue
            else:
                #print(e)
                temp_list.append(e)
    cmo_hostnames_list = temp_list.copy()
    return cmo_hostnames_list
# In[7]:
def ios_show_interface(output_dict, hostname):
    """extracts the 'show interface' output"""
    output_dict = output_dict
    plog("    extracting the 'show interface' output",log_only=True)
    hostname = hostname
    x = re.split(f'{hostname}#\s*show\s+interface\s*\n+', output_dict[hostname])#[1].split(f'{hostname}#')[0]
    interface_ = x[1].split(f'{hostname}#')[0]
    return interface_
def ios_show_interface_status(output_dict, hostname):
    """extracts the 'show interface status' output"""
    output_dict = output_dict
    plog("    extracting the 'show interface status' output",log_only=True)
    hostname = hostname
    #interface_status_text = output_dict[hostname].split("show interface status")[1].split(f'{hostname}#')[0]
    interface_status_text = re.split(f'{hostname}#\s*show\s+interface\s+status\s*\n+', output_dict[hostname])[1].split(f'{hostname}#')[0]
    return interface_status_text
def ios_show_interface_description(output_dict, hostname):
    """extracts the 'show interface description' output"""
    output_dict = output_dict
    plog("    extracting the 'show interface description' output",log_only=True)
    hostname = hostname
    #plog(hostname)
    #show_interface_description = output_dict[hostname].split("show interface description")[1].split(f'{hostname}#')[0]
    show_interface_description = re.split(f'{hostname}#\s*show\s+interface\s+description\s*\n+', output_dict[hostname])[1].split(f'{hostname}#')[0]
    return show_interface_description
def ios_show_interface_switchport(output_dict, hostname):
    """extracts the 'show interface switchport' output"""
    output_dict = output_dict
    plog("    extracting the 'show interface switchport' output",log_only=True)
    hostname = hostname
    #interface_switchport_text = output_dict[hostname].split("show interface switchport")[1].split(f'{hostname}#')[0]
    interface_switchport = show_interface_description = re.split(f'{hostname}#\s*show\s+interface\s+switchport\s*\n+', output_dict[hostname])[1].split(f'{hostname}#')[0]
    return interface_switchport
def ios_show_vlan(output_dict, hostname):
    """extracts the 'show vlan' output"""
    output_dict = output_dict
    plog("    extracting the 'show vlan' output",log_only=True)
    hostname = hostname
    #show_vlan = output_dict[hostname].split("show vlan")[1].split(f'VLAN Type  SAID')[0]
    show_vlan = re.split(f'{hostname}#\s*show\s+vlan\s*\n+', output_dict[hostname])[1].split(f'{hostname}#')[0]
    return show_vlan
# In[8]:
def import_and_clean_portmap_df():
    """import_and_cleans_portmap_df"""
    cols = ['Origin','Existing/New','CMO Hostname','CMO Interface','CR','FMO_HOSTNAME',
     'FMO_INTERFACE','FMO_ADMIN','FMO_OPERATION','FMO_MODE','FMO_VLAN_IP','FMO_SPEED',
     'FMO_DUPLEX','FMO_MAC_ADDRESS','FMO_DESCRIPTION','FMO_LAST_UP','ISE','NATIVE_VLAN',
     'ADDITIONAL_COMMANDS','PORT_CHANNEL','EN_SWITCH','OUI_VENDOR']
    portmap_filename= get_value('merged_portmap=')
    plog('-'*80)
    plog('---import_and_clean_portmap_df()')
    if 'csv' == portmap_filename.split('.')[-1].strip():
        plog('portmap is csv')
        i = 0 
        while True:
            portmap_df = pd.read_csv(portmap_filename, skiprows= i)
            portmap_df = portmap_df.iloc[:, : 22].copy()
            plog(portmap_df.columns)
            original_cols_list = []
            for col in portmap_df.columns:
                original_cols_list.append(col)
            if cols == original_cols_list:
                break
            i = i + 1
            plog(i)
        portmap_df = portmap_df.iloc[:, : 22].copy()
    elif 'xlsx' == portmap_filename.split('.')[-1].strip():
        plog('portmap is xlsx')
        i = 0 
        while True:
            portmap_df = pd.read_excel(portmap_filename, skiprows= i)
            portmap_df = portmap_df.iloc[:, : 22].copy()
            portmap_df.columns = cols
            plog(portmap_df.columns)
            original_cols_list = []
            for col in portmap_df.columns:
                original_cols_list.append(col)
            if cols == original_cols_list:
                break
            i = i + 1
            plog(i)
        portmap_df = portmap_df.iloc[:, : 22].copy()
        """portmap_df = pd.read_excel(portmap_filename)
        portmap_df.columns = cols"""
    portmap_df = portmap_df.drop(portmap_df[portmap_df['FMO_HOSTNAME'] == 'FMO_HOSTNAME'].index)
    portmap_df = portmap_df.drop(portmap_df[portmap_df['FMO_HOSTNAME'] == 'HOSTNAME'].index) 
    #vlan_map_df['CMO VLAN'] = vlan_map_df['CMO VLAN'].map(str)
    for col in cols:
        portmap_df[col] = portmap_df[col].map(str)
    plog('\tsuccess')
    return portmap_df
def interface_to_shorcut_format(interface):
    """converts interface string to its shortcut form"""
    interface = interface
    port_types = {'Fa': 'FastEthernet',
                  'Tw': 'TwoGigabitEthernet','Fi': 'FiveGigabitEthernet','Te': 'TenGigabitEthernet',
                  'Twe': 'TwentyFiveGigE','Fo': 'FortyGigabitEthernet','Hu': 'HundredGigabitEthernet',
                  'Lo': 'Loopback','Vl': 'Vlan','Po': 'Port-channel',
                  'Tu': 'Tunnel','Nv': 'Nve','Ap': 'AppGigabitEthernet','Gi': 'GigabitEthernet','E': 'Ethernet'}
    for k,v in port_types.items():
        if v.strip().lower() in interface.strip().lower():
            #plog(v)
            suffix = interface.split(v)[1]
            interface_short = f'{k}{suffix}'
            break
    return  interface_short
def physical_interface_checker(interface):
    '''checks if interface physical'''
    interface = interface
    port_types = {'Fa': 'FastEthernet',
                  'Tw': 'TwoGigabitEthernet','Fi': 'FiveGigabitEthernet','Te': 'TenGigabitEthernet',
                  'Twe': 'TwentyFiveGigE','Fo': 'FortyGigabitEthernet','Hu': 'HundredGigabitEthernet',
                  'Ap': 'AppGigabitEthernet','Gi': 'GigabitEthernet','E': 'Ethernet'}
    for k,v in port_types.items():
        if v.strip() in interface:
            #plog(v)
            status = True
            return status
        else:
            status = False
    return status
# In[9]:
def store_connected_interfaces_details_in_dict(output_dict,cmo_hostname_list):
    """store_connected_interfaces_details_in_dict"""
    plog('-'*80)
    plog("---store_connected_interfaces_details_in_dict()")
    output_dict = output_dict
    cmo_hostname_list =cmo_hostname_list
    connected_interfaces_dict = {}
    for hostname in cmo_hostname_list:
        with open(r"textFSM_templates\\cisco_ios_show_interfaces_status.textfsm") as template: 
            re_table = textfsm.TextFSM(template)
            #plog(re_table)
        extracted_data = re_table.ParseText(ios_show_interface_status(output_dict, hostname))
        #print(extracted_data)
        upup_interface_list = []
        upup_interface_list = [dat for dat in extracted_data if dat[2] == 'connected']
        connected_interfaces_dict[hostname] = upup_interface_list
    return connected_interfaces_dict
# In[10]:
def verify_connected_interfaces_from_outputs(connected_interfaces_dict, portmap_df ):
    plog('-'*80)
    plog('---verify_connected_interfaces_from_outputs()')
    #merged_portmap_df = import_and_clean_portmap_df()
    merged_portmap_df = portmap_df
    data_list = []
    for hostname, value in connected_interfaces_dict.items():
        CMO_interfaces_upup_df1 = merged_portmap_df[merged_portmap_df['CMO Hostname'] == hostname]
        CMO_interfaces_upup_df2 = CMO_interfaces_upup_df1[CMO_interfaces_upup_df1['FMO_ADMIN'] == 'UP']
        CMO_interfaces_upup_df = CMO_interfaces_upup_df2[CMO_interfaces_upup_df2['FMO_OPERATION'] == 'UP']
        CMO_interfaces_upup_df = CMO_interfaces_upup_df.reset_index()
        CMO_interfaces_list = CMO_interfaces_upup_df['CMO Interface'].to_list()
        CMO_interfaces_short_list = []
        for CMO_interface in CMO_interfaces_list:
            CMO_interface_short = interface_to_shorcut_format(CMO_interface)
            CMO_interfaces_short_list.append(CMO_interface_short)
        #value['connected_interfaces'].append(['Gi1'])
        print(hostname)
        temp_list = []
        for line in value:
            #print(line[0])
            if line[0] in CMO_interfaces_short_list:
                #print(line[0] + '  match')
                temp_list.append([hostname, line[0], '-'])
            else:
                temp_list.append([hostname, line[0], 'no match in portmap'])
        data_list.append(temp_list)
        #print('_'*80)
    ###################
    #################
    #############
    sorted_data_list = []
    for lst in data_list:
        for dat in lst:
            if dat not in sorted_data_list:
                sorted_data_list.append(dat)
    if os.path.exists('reports'): 
        pass
    else:
        os.mkdir('reports')
    tabul = tabulate(sorted_data_list, headers = ["hostname", "interf", "stat"], tablefmt= "orgtbl")
    df_output = pd.DataFrame(sorted_data_list, columns = ["hostname", "interf", "stat"])
    df_output.to_csv('reports\\upup_interface_veification.csv', index=False)
    '''with open(f'reports\\upup_interface_veification.txt', 'w') as f:
        f.write(tabul)'''
    return sorted_data_list
# In[ ]:
# In[11]:
def sort_by_special(elem):
    """use as (key) parameter in list.sort(key=) """
    elem = elem
    vlan = elem.split(' ')[0].strip('<') # edit for situation
    #print(line)
    if vlan.isnumeric():
        return int(vlan)
    else:
        return 99999
# In[12]:
def ios_FMO_SPEED_check(portmap_df, output_dict):
    '''checks FMO_SPEED againts show interface status from output file'''
    plog('_'*80)
    plog("ios_FMO_SPEED_check")
    portmap_df = portmap_df
    output_dict = output_dict
    data = []
    all_interface_matched= True
    for hostname in portmap_df['CMO Hostname'].unique():
        if hostname in output_dict:
            pass
        else:
            continue
        #plog(hostname)
        portmap_df_filtered_by_hostname = portmap_df[portmap_df['CMO Hostname'] == hostname]
        for CMO_INTERFACE in portmap_df_filtered_by_hostname['CMO Interface']:
            #print(CMO_INTERFACE)
            data_temp = []
            if physical_interface_checker(CMO_INTERFACE) == False:
                continue
            else:    
                interface_df = portmap_df_filtered_by_hostname[portmap_df_filtered_by_hostname['CMO Interface'] == CMO_INTERFACE].reset_index()
                FMO_SPEED = str(interface_df.loc[0]['FMO_SPEED']).strip()
                if 'nan' == FMO_SPEED:
                    FMO_SPEED = ''
                CMO_INTERFACE_short = interface_to_shorcut_format(CMO_INTERFACE)
                ###########################################################
                with open(r"textFSM_templates\\cisco_ios_show_interfaces_status.textfsm") as template: 
                    re_table = textfsm.TextFSM(template)
                    #plog(re_table)
                extracted_data = re_table.ParseText(ios_show_interface_status(output_dict, hostname))
                FMO_SPEED_from_outputs = 'not found in output file'
                for split_line in extracted_data:
                    if split_line[0].lower().strip() == CMO_INTERFACE_short.lower().strip():
                        #plog(split_line)
                        FMO_SPEED_from_outputs = split_line[5].strip().lower()
                        break
                        #plog(split_line)
                ###################################################
                if FMO_SPEED_from_outputs == 'not found in output file':
                    ################################################ 
                    show_interface = ios_show_interface(output_dict, hostname)
                    show_interface_targeted = re.split(f'{CMO_INTERFACE}', show_interface)[1].split('\n')[:27]
                    for line in show_interface_targeted:
                        if 'duplex' in line:
                            #print(line)
                            duplex = line.split()[0].strip(',')
                            speed = line.split()[1].strip(',')
                    #print('%%%%%%%%%%%%%%%%%%%%%%%%%')
                    speed_num = re.split('\D+', speed)[0]
                    FMO_SPEED_from_outputs = f'a-{speed_num}'
                    #print(FMO_SPEED_from_outputs)
                #############################################################
                if FMO_SPEED.strip().lower() == FMO_SPEED_from_outputs.strip().lower():
                    if all_interface_matched:
                        all_interface_matched = True
                    data_temp = [hostname,CMO_INTERFACE,FMO_SPEED,FMO_SPEED_from_outputs,'-']
                    data.append(data_temp)
                else:
                    all_interface_matched = False
                    #plog(f'{hostname} -- {CMO_INTERFACE} -- {FMO_ADMIN} -- {FMO_ADMIN_from_outputs}')
                    data_temp = [hostname,CMO_INTERFACE,FMO_SPEED,FMO_SPEED_from_outputs,'MISMATCH']
                    data.append(data_temp)
    tabul = tabulate(data, headers = ["HOSTNAME","INTERFACE","FMO_SPEED","FROM OUTPUT","STAT"], tablefmt= "orgtbl")
    tabul_mismatch = tabulate([dat for dat in data if dat[-1] == 'MISMATCH'], headers = ["HOSTNAME","INTERFACE","FMO_SPEED","FROM OUTPUT","STAT"], tablefmt= "orgtbl")
    if all_interface_matched:
        plog('-ios_FMO_SPEED_check all matched')
        #plog(tabul)
    else:
        plog('-ios_FMO_SPEED_check  MISMATCH FOUND!')
        #plog(tabul_mismatch)
        plog('_'*80)
    return data
# In[13]:
def ios_FMO_DUPLEX_check(portmap_df, output_dict):
    '''checks FMO_DUPLEX againts show interface status from output file'''
    plog('_'*80)
    plog("ios_FMO_DUPLEX_check")
    portmap_df = portmap_df
    output_dict = output_dict
    data = []
    all_interface_matched= True
    for hostname in portmap_df['CMO Hostname'].unique():
        if hostname in output_dict:
            pass
        else:
            continue
        #plog(hostname)
        portmap_df_filtered_by_hostname = portmap_df[portmap_df['CMO Hostname'] == hostname]
        for CMO_Interface in portmap_df_filtered_by_hostname['CMO Interface']:
            data_temp = []
            if physical_interface_checker(CMO_Interface) == False:
                continue
            else:    
                interface_df = portmap_df_filtered_by_hostname[portmap_df_filtered_by_hostname['CMO Interface'] == CMO_Interface].reset_index()
                FMO_DUPLEX = str(interface_df.loc[0]['FMO_DUPLEX']).strip()
                if 'nan' == FMO_DUPLEX:
                    FMO_DUPLEX = ''
                CMO_Interface_short = interface_to_shorcut_format(CMO_Interface)
                ###########################################################
                with open(r"textFSM_templates\\cisco_ios_show_interfaces_status.textfsm") as template: 
                    re_table = textfsm.TextFSM(template)
                    #plog(re_table)
                extracted_data = re_table.ParseText(ios_show_interface_status(output_dict, hostname))
                FMO_DUPLEX_from_outputs = 'not found in output file'
                #found_in_show_interface_status = False
                for split_line in extracted_data:
                    if split_line[0].lower().strip() == CMO_Interface_short.lower().strip():
                        #plog(split_line)
                        FMO_DUPLEX_from_outputs = split_line[4].strip().lower()
                        #found_in_show_interface_status = True
                        break
                        #plog(split_line)
                if FMO_DUPLEX_from_outputs == 'not found in output file':
                    ################################################ 
                    show_interface = ios_show_interface(output_dict, hostname)
                    show_interface_targeted = re.split(f'{CMO_Interface}', show_interface)[1].split('\n')[:27]
                    for line in show_interface_targeted:
                        if 'duplex' in line:
                            #print(line)
                            duplex = line.split()[0].strip(',')
                            speed = line.split()[1].strip(',')
                    #FMO_DUPLEX_from_outputs = duplex
                    duplex_pre = re.split('-duplex', duplex)[0].lower()
                    FMO_DUPLEX_from_outputs = f'a-{duplex_pre}'
                    ################################################
                ###################################################
                #############################################################
                if FMO_DUPLEX.strip().lower() == FMO_DUPLEX_from_outputs.strip().lower():
                    if all_interface_matched:
                        all_interface_matched = True
                    data_temp = [hostname,CMO_Interface,FMO_DUPLEX,FMO_DUPLEX_from_outputs,'-']
                    data.append(data_temp)
                else:
                    all_interface_matched = False
                    #plog(f'{hostname} -- {CMO Interface} -- {FMO_ADMIN} -- {FMO_ADMIN_from_outputs}')
                    data_temp = [hostname,CMO_Interface,FMO_DUPLEX,FMO_DUPLEX_from_outputs,'MISMATCH']
                    data.append(data_temp)
    tabul = tabulate(data, headers = ["HOSTNAME","INTERFACE","FMO_DUPLEX","FROM OUTPUT","STAT"], tablefmt= "orgtbl")
    tabul_mismatch = tabulate([dat for dat in data if dat[-1] == 'MISMATCH'], headers = ["HOSTNAME","INTERFACE","FMO_DUPLEX","FROM OUTPUT","STAT"], tablefmt= "orgtbl")
    if all_interface_matched:
        plog('-ios_FMO_DUPLEX_check all matched')
        #plog(tabul)
    else:
        plog('-ios_FMO_DUPLEX_check MISMATCH FOUND!')
        #plog(tabul_mismatch)
        plog('_'*80)
    return data
# In[14]:
def ios_FMO_DESCRIPTION_check(portmap_df, output_dict):
    '''checks FMO_DESCRIPTION againts show interface status from output file'''
    plog('_'*80)
    plog("ios_FMO_DESCRIPTION_check")
    portmap_df = portmap_df
    output_dict = output_dict
    data = []
    all_interface_matched= True
    for hostname in portmap_df['CMO Hostname'].unique():
        if hostname in output_dict:
            pass
        else:
            continue
        #plog(hostname)
        portmap_df_filtered_by_hostname = portmap_df[portmap_df['CMO Hostname'] == hostname]
        for CMO_INTERFACE in portmap_df_filtered_by_hostname['CMO Interface']:
            data_temp = []
            if physical_interface_checker(CMO_INTERFACE) == False:
                continue
            else:    
                interface_df = portmap_df_filtered_by_hostname[portmap_df_filtered_by_hostname['CMO Interface'] == CMO_INTERFACE].reset_index()
                FMO_DESCRIPTION = str(interface_df.loc[0]['FMO_DESCRIPTION']).strip().lower()
                if 'nan' == FMO_DESCRIPTION:
                    FMO_DESCRIPTION = ''
                CMO_INTERFACE_short = interface_to_shorcut_format(CMO_INTERFACE)
                ###########################################################
                with open(r"textFSM_templates\\cisco_ios_show_interfaces_description.textfsm") as template: 
                    re_table = textfsm.TextFSM(template)
                    #plog(re_table)
                extracted_data = re_table.ParseText(ios_show_interface_description(output_dict, hostname))
                FMO_DESCRIPTION_from_outputs = 'not found in output file'
                for split_line in extracted_data:
                    if split_line[0].lower().strip() == CMO_INTERFACE_short.lower().strip():
                        #plog(split_line)
                        FMO_DESCRIPTION_from_outputs = split_line[-1].strip().lower()
                        break
                        #plog(split_line)
                ###################################################
                #############################################################
                if FMO_DESCRIPTION.strip().lower() == FMO_DESCRIPTION_from_outputs.strip().lower():
                    if all_interface_matched:
                        all_interface_matched = True
                    data_temp = [hostname,CMO_INTERFACE,FMO_DESCRIPTION,FMO_DESCRIPTION_from_outputs,'-']
                    data.append(data_temp)
                else:
                    all_interface_matched = False
                    #plog(f'{hostname} -- {CMO_INTERFACE} -- {FMO_ADMIN} -- {FMO_ADMIN_from_outputs}')
                    data_temp = [hostname,CMO_INTERFACE,FMO_DESCRIPTION,FMO_DESCRIPTION_from_outputs,'MISMATCH']
                    data.append(data_temp)
    tabul = tabulate(data, headers = ["HOSTNAME","INTERFACE","FMO_DESCRIPTION","FROM OUTPUT","STAT"], tablefmt= "orgtbl")
    tabul_mismatch = tabulate([dat for dat in data if dat[-1] == 'MISMATCH'], headers = ["HOSTNAME","INTERFACE","FMO_DESCRIPTION","FROM OUTPUT","STAT"], tablefmt= "orgtbl")
    if all_interface_matched:
        plog('-ios_FMO_DESCRIPTION_check all matched')
        #plog(tabul)
    else:
        plog('-ios_FMO_DESCRIPTION_check MISMATCH FOUND!')
        #plog(tabul_mismatch)
        plog('_'*80)
    return data
# In[15]:
def ios_NATIVE_VLAN_check(portmap_df, output_dict):
    '''checks NATIVE_VLAN againts show interface status from output file'''
    plog('_'*80)
    plog("ios_NATIVE_VLAN_check")
    portmap_df = portmap_df
    output_dict = output_dict
    data = []
    all_interface_matched= True
    for hostname in portmap_df['CMO Hostname'].unique():
        if hostname in output_dict:
            pass
        else:
            continue
        local_vlan_map = create_local_vlan_map(output_dict,hostname)
        #plog(hostname)
        portmap_df_filtered_by_hostname = portmap_df[portmap_df['CMO Hostname'] == hostname]
        for CMO_INTERFACE in portmap_df_filtered_by_hostname['CMO Interface']:
            data_temp = []
            if physical_interface_checker(CMO_INTERFACE) == False:
                continue
            else:    
                interface_df = portmap_df_filtered_by_hostname[portmap_df_filtered_by_hostname['CMO Interface'] == CMO_INTERFACE].reset_index()
                try:
                    NATIVE_VLAN = str(int(interface_df.loc[0]['NATIVE_VLAN'])).strip()
                except:
                    NATIVE_VLAN = str(interface_df.loc[0]['NATIVE_VLAN']).strip()
                if 'nan' == NATIVE_VLAN:
                    NATIVE_VLAN = ''
                CMO_INTERFACE_short = interface_to_shorcut_format(CMO_INTERFACE)
                ###########################################################
                #########################
                #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
                not_found = False
                if ios_show_interface_switchport(output_dict, hostname).find(f'{CMO_INTERFACE_short}\n') == -1:
                    plog(f"{hostname}-[{CMO_INTERFACE_short}] not found in output file's - 'show interfaces switchport' section")
                    NATIVE_VLAN_from_outputs = ''
                    not_found = True
                    interface_switchport_infos = """"""
                    interface_switchport_infos_lines = interface_switchport_infos.split('\n')
                else:
                    interface_switchport_infos = ios_show_interface_switchport(output_dict, hostname).split(f'{CMO_INTERFACE_short}\n')[1].split('Name:')[0]
                    interface_switchport_infos_lines = interface_switchport_infos.split('\n')
                for line in interface_switchport_infos_lines:
                    if not_found:
                        NATIVE_VLAN_from_outputs = ''
                        break
                    if 'Administrative Mode:' in line and 'trunk' in line:
                        for line in interface_switchport_infos_lines:
                            if 'Trunking Native Mode VLAN:' in line:
                                x = line.split('Trunking Native Mode VLAN:')[1].split()[0]
                                NATIVE_VLAN_from_outputs = line.split('Trunking Native Mode VLAN:')[1].strip().split()[0].strip()
                                NATIVE_VLAN_from_outputs = convert_vlan_to_FMO_vlan(local_vlan_map, NATIVE_VLAN_from_outputs)
                                break
                        break
                    else: #for none trunk
                        NATIVE_VLAN_from_outputs = ''
                #####################################################
                if str(NATIVE_VLAN).strip() == str(NATIVE_VLAN_from_outputs).strip():
                    data_temp = [hostname,CMO_INTERFACE,NATIVE_VLAN,NATIVE_VLAN_from_outputs,'-']
                    data.append(data_temp)
                    if all_interface_matched:
                        all_interface_matched = True
                else:
                    all_interface_matched = False
                    #plog(NATIVE_VLAN)
                    #plog(NATIVE_VLAN_from_outputs)
                    data_temp = [hostname,CMO_INTERFACE,NATIVE_VLAN,NATIVE_VLAN_from_outputs,'MISMATCH']
                    data.append(data_temp)
    tabul = tabulate(data, headers = ["HOSTNAME","INTERFACE","NATIVE_VLAN","FROM OUTPUT","STAT"], tablefmt= "orgtbl")
    tabul_mismatch = tabulate([dat for dat in data if dat[-1] == 'MISMATCH'], headers = ["HOSTNAME","INTERFACE","NATIVE_VLAN","FROM OUTPUT","STAT"], tablefmt= "orgtbl")
    if all_interface_matched:
        plog('-ios_NATIVE_VLAN_check all matched')
        #plog(tabul)
    else:
        plog('-ios_NATIVE_VLAN_check MISMATCH FOUND!')
        #plog(tabul_mismatch)  
    return data
# In[16]:
def result_main_report(results_dict):
    """formalize and output main report"""
    plog("result_main_report")
    results_dict = results_dict
    main_out_data = []
    FMO_ADMIN_clone = []
    for r in results_dict['FMO_SPEED']:
        FMO_ADMIN_clone.append(r)
    for row_main in FMO_ADMIN_clone: #main
        #plog('%%%%%%%%%%%%%%%')
        #plog(row_main[0])
        row_temp = row_main.copy()
        for k , v in results_dict.items():
            #plog(k)
            if k == 'FMO_SPEED':
                continue
            for row in v: #every new col
                if row_main[0] == row[0] and row_main[1] == row[1]:
                    row_temp.append(row[2])
                    row_temp.append(row[3])
                    row_temp.append(row[4])
                    break
        #plog(row_temp)
        main_out_data.append(row_temp)
        #return main_out_data
    df_out = pd.DataFrame(main_out_data, columns=['HOSTNAME', 'INTERFACE',
'FMO_SPEED','FROM_OUTPUTS','STATUS',
'FMO_DUPLEX','FROM_OUTPUTS','STATUS',
'FMO_DESCRIPTION','FROM_OUTPUTS','STATUS',
'NATIVE_VLAN','FROM_OUTPUTS','STATUS',
'FMO_VLAN_IP','FROM_OUTPUTS','STATUS'])
    ########### filtred
    mismatch_data_list = []
    hit = False
    for i in range(len(df_out)):
        if 'MISMATCH' in df_out.iloc[i, 4] or 'MISMATCH' in df_out.iloc[i, 7] or 'MISMATCH' in df_out.iloc[i, 10] or 'MISMATCH' in df_out.iloc[i, 13]or 'MISMATCH' in df_out.iloc[i, 16]:
            #plog(df_out.iloc[i].tolist())
            hit = True
            mismatch_data_list.append(df_out.iloc[i].tolist())
            mismatch_df = pd.DataFrame(mismatch_data_list, columns=['HOSTNAME', 'INTERFACE',
'FMO_SPEED','FROM_OUTPUTS','STATUS',
'FMO_DUPLEX','FROM_OUTPUTS','STATUS',
'FMO_DESCRIPTION','FROM_OUTPUTS','STATUS',
'NATIVE_VLAN','FROM_OUTPUTS','STATUS',
'FMO_VLAN_IP','FROM_OUTPUTS','STATUS'])
    if hit == False: # this means there are no mismatch
        plog('creating black df for mismatch filered report')
        mismatch_data_list = [["","","","","","","","","","","","","","","","",""]]
        mismatch_df = pd.DataFrame(mismatch_data_list, columns=['HOSTNAME', 'INTERFACE',
'FMO_SPEED','FROM_OUTPUTS','STATUS',
'FMO_DUPLEX','FROM_OUTPUTS','STATUS',
'FMO_DESCRIPTION','FROM_OUTPUTS','STATUS',
'NATIVE_VLAN','FROM_OUTPUTS','STATUS',
'FMO_VLAN_IP','FROM_OUTPUTS','STATUS'])
    ##################################################################
    report_main_name= get_value('report_main_name=')
    #print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    plog(report_main_name)
    plog(f'{report_main_name}.csv')
    if os.path.exists('reports'): 
        pass
    else:
        os.mkdir('reports')
    df_out.to_csv(f'reports\\{report_main_name}.csv', index = False)
    report_main_filtered_mismatch_name= get_value("report_main_filtered_mismatch_name=")
    plog(f'reports\\{report_main_filtered_mismatch_name}.csv')
    mismatch_df.to_csv(f'reports\\{report_main_filtered_mismatch_name}.csv', index = False)
    return df_out
# In[17]:
def result_MISMATCH_report(results_dict):
    plog("result_MISMATCH_report")
    mismatch_df_dict = {}
    mismatch_report_dict = {}
    for k , v in results_dict.items():
        temp_rows_list = []
        for row in v:
            row_clone = row.copy()
            #plog(row_clone)
            hostname = row_clone[0]
            if row_clone[4] == 'MISMATCH':
                #plog(row)
                temp_rows = []
                if k == 'FMO_DESCRIPTION':
                    ############### FMO_DESCRIPTION
                    interf_short = interface_to_shorcut_format(row_clone[1])
                    not_found = False
                    if ios_show_interface_status(output_dict, hostname).find(f'{interf_short} ') == -1:
                        plog(f"{hostname}-[{interf_short}] not found in output file's - 'show interfaces status' section")
                        output_info = 'data not found in outputs'
                        not_found = True
                    else:
                        output_info =  ios_show_interface_description(output_dict, row_clone[0]).split(f'{interf_short} ')[1].split('\n')[0]
                    ################## 
                elif k == 'NATIVE_VLAN':
                    ############### NATIVE_VLAN
                    interf_short = interface_to_shorcut_format(row_clone[1])
                    not_found = False
                    if ios_show_interface_switchport(output_dict, hostname).find(f'{interf_short}\n') == -1:
                        plog(f"{hostname}-[{interf_short}] not found in output file's - 'show interface switchport' section")
                        output_info = 'data not found in outputs'
                        not_found = True
                    else:
                        output_info =  ios_show_interface_switchport(output_dict, row_clone[0]).split(f'{interf_short}\n')[1].split('Name:')[0]
                    ##################
                    ################## 
                elif k == 'FMO_SPEED':
                    ############### FMO_OPERATION
                    interf_short = interface_to_shorcut_format(row_clone[1])
                    not_found = False
                    if ios_show_interface_status(output_dict, hostname).find(f'{interf_short} ') == -1:
                        plog(f"{hostname}-[{interf_short}] not found in output file's - 'show interfaces status' section")
                        output_info = "data not found in outputs 'show interface status'"
                        not_found = True
                    else:
                        output_info =  ios_show_interface_status(output_dict, row_clone[0]).split(f'{interf_short} ')[1].split('\n')[0]
                    ##################
                elif k == 'FMO_DUPLEX':
                    ############### FMO_OPERATION
                    interf_short = interface_to_shorcut_format(row_clone[1])
                    not_found = False
                    if ios_show_interface_status(output_dict, hostname).find(f'{interf_short} ') == -1:
                        plog(f"{hostname}-[{interf_short}] not found in output file's - 'show interfaces status' section")
                        output_info = "data not found in outputs 'show interface status'"
                        not_found = True
                    else:
                        output_info =  ios_show_interface_status(output_dict, row_clone[0]).split(f'{interf_short} ')[1].split('\n')[0]
                    ##################
                elif k == 'FMO_VLAN_IP':
                    ############### FMO_OPERATION
                    interf_short = interface_to_shorcut_format(row_clone[1])
                    not_found = False
                    output_info =  'THIS IS A SPECIAL CHECK'
                    ##################
                row_clone.append(output_info)
                temp_rows.append(row_clone)
                #plog(temp_rows)
                #mismatch_report_dict[k] = {}
                temp_rows_list.append(temp_rows)
                mismatch_report_dict[k] = temp_rows_list
    data_fin_list = []            
    for kk, vv in mismatch_report_dict.items():
        data_fin = []
        plog(kk)
        for row_ in vv:
            data_fin.append(row_[0])
        #data_fin_list.append(data_fin)
        #plog(data_fin)
        ####################################################################################
        #for data_fin in data_fin_list:
        try:
            df_temp = pd.DataFrame(data_fin, columns=['HOSTNAME', 'INTERFACE', 'FROM_PORTMAP', 'FROM_OUTPUT', 'STATUS', 'OUTPUT_INFO'])
            mismatch_df_dict[kk] = df_temp
        except Exception as e:
            plog('data_fin could be empty meaning no mismatch')
            plog(data_fin)
    if os.path.exists('reports'): 
        pass
    else:
        os.mkdir('reports')
    report_mismatch_summary_file_name= get_value("report_mismatch_summary_file_name=")
    with pd.ExcelWriter(f'reports\\{report_mismatch_summary_file_name}.xlsx') as excel_writer:
        sheet_not_found = True
        if  len(mismatch_df_dict ) > 0:
            for sheet_name, df in mismatch_df_dict.items():
                try:
                    df.to_excel(excel_writer, sheet_name=sheet_name, index=False)
                    sheet_not_found = False
                except Exception as e:
                    plog(f"'{e} possible sheet is empty\n\tcreating black sheet")
        else:
            data_fin = [['','','','','','']]
            df_nomatch = pd.DataFrame(data_fin, columns=['HOSTNAME', 'INTERFACE', 'FROM_PORTMAP', 'FROM_OUTPUT', 'STATUS', 'OUTPUT_INFO'])
            df_nomatch.to_excel(excel_writer, sheet_name='NO MISSMATCH', index=False)
    plog(f'{report_mismatch_summary_file_name}.xlsx')
    return 
# # SPECIAL ios_FMO_VLAN_IP_check FUNCTIONS
# 
# In[ ]:
# In[ ]:
# In[ ]:
# In[ ]:
# In[ ]:
# In[ ]:
# In[18]:
def vlan_range_converter(range_str):
    plog(f'vlan_range_converter({range_str})')
    plog(f'converting vlan range [{range_str}] to per individual vlan form')
    range_str = range_str
    first_no = range_str.split('-')[0].strip()
    second_no = range_str.split('-')[1].strip()
    if first_no.isnumeric() and second_no.isnumeric():
        first_no = int(first_no)
        second_no = int(second_no)
        vlan_list = []
        for vlan in range(first_no, second_no+1):
            #print(vlan)
            vlan_list.append(str(vlan))
        range_str_new = ','.join(vlan_list)
        return range_str_new
    else:
        return f'<can not convert [{range_str}] from range form to individual vlan form>'
# In[19]:
def import_cmo_to_fmo_vlan_df():
    vlan_map_df = pd.read_excel('cmo_to_fmo_vlanlist.xlsx')
    vlan_map_df['CMO VLAN'] = vlan_map_df['CMO VLAN'].replace(np.nan, 0)
    vlan_map_df['CMO VLAN'] = vlan_map_df['CMO VLAN'].map(str)
    #print(vlan_map_df)
    vlan_map_df['FMO VLAN'] = vlan_map_df['FMO VLAN'].replace('REMOVE', '')
    #vlan_map_df['FMO VLAN'] = vlan_map_df['FMO VLAN'].replace('REMOVE', '')
    for index in range(len(vlan_map_df)): # conver alphabeticals to numeric
        vlan = vlan_map_df.loc[index, 'CMO VLAN'].split('.')[0].strip()
        #print(vlan)
        #print(type(vlan))
        #print(vlan.isnumeric())
        if vlan.isnumeric():
            #print(index)
            vlan_map_df.loc[index, 'CMO VLAN'] = vlan
        else:
            vlan_map_df.loc[index, 'CMO VLAN'] = ''
    #vlan_map_df['CMO VLAN'] = vlan_map_df['CMO VLAN']
    vlan_map_df['CMO VLAN NAME'] = vlan_map_df['CMO VLAN NAME'].str.upper()
    return vlan_map_df
def create_local_vlan_map(output_dict,hostname):
    output_dict = output_dict
    hostname = hostname
    cmo_to_fmovlan_df = import_cmo_to_fmo_vlan_df()
    with open(r"textFSM_templates\\cisco_ios_show_vlan.textfsm") as template: 
        re_table = textfsm.TextFSM(template)
        #plog(re_table)
    extracted_data = re_table.ParseText(ios_show_vlan(output_dict, hostname))
    failed_vlan_mapping_temp = []
    local_vlan_map = []
    for initial_vlan_info in extracted_data:
        #print('_________________')
        #print(initial_vlan_info)
        #print(cmo_to_fmovlan_df.loc[cmo_to_fmovlan_df['CMO VLAN'] == initial_vlan_info[0]])
        try:
            #print('aaaaa')
            temp_filter1 = cmo_to_fmovlan_df.loc[cmo_to_fmovlan_df['CMO VLAN'] == initial_vlan_info[0]].reset_index(drop=True)
            #print('bbbbbbb')
            #print(initial_vlan_info[1].upper())
            cmo_vlan_name_from_output = initial_vlan_info[1].upper()
            temp_filter2 = temp_filter1.loc[temp_filter1['CMO VLAN NAME'] == cmo_vlan_name_from_output].reset_index(drop=True)
            #print('cccccccc')
            #print('*********')
            #print(temp_filter2)
            FMO_vlan = str(temp_filter2.iloc[0,2])
            if FMO_vlan == 'nan':
                FMO_vlan = "UNKNOWN FMO VLAN"
        except Exception as e:
            plog(e)
            plog(f'no match for vlan no -[{initial_vlan_info[0]}] with vlan name - [{initial_vlan_info[1]}]')
            failed_vlan_mapping_temp.append([hostname, initial_vlan_info[0], initial_vlan_info[1], 'NO MATCH IN cmo_to_fmo_vlanlist.xlsx'])
            FMO_vlan = "UNKNOWN FMO VLAN"
        local_vlan_map.append([hostname,initial_vlan_info[1],initial_vlan_info[0], FMO_vlan])
    tabul = tabulate(local_vlan_map, headers = ['hostname','local_vlan_name',"local","FMO"], tablefmt= "orgtbl")
    print(tabul)
    return local_vlan_map
def convert_vlan_to_FMO_vlan(local_vlan_map, vlan_orig):
    vlan_orig = vlan_orig.strip()
    if vlan_orig.isnumeric():
        for vlan_line in local_vlan_map:
            if vlan_orig.strip() == vlan_line[2].strip():
                return vlan_line[3]
        return f"<{vlan_orig} is not found in the 'show vlan'>"
        #return ''
    else:
        return vlan_orig
def ios_FMO_VLAN_IP_check(portmap_df, output_dict):
    '''checks FMO_VLAN_IP againts show interface status from output file'''
    plog('_'*80)
    plog("ios_FMO_VLAN_IP_check")
    portmap_df = portmap_df
    output_dict = output_dict
    data = []
    all_interface_matched= True
    for hostname in portmap_df['CMO Hostname'].unique():
        if hostname in output_dict:
            pass
        else:
            continue
        #plog(hostname)
        ########################
        local_vlan_map = create_local_vlan_map(output_dict,hostname)
        ########################
        portmap_df_filtered_by_hostname = portmap_df[portmap_df['CMO Hostname'] == hostname]
        for CMO_INTERFACE in portmap_df_filtered_by_hostname['CMO Interface']:
            data_temp = []
            if physical_interface_checker(CMO_INTERFACE) == False:
                continue
            else:    
                interface_df = portmap_df_filtered_by_hostname[portmap_df_filtered_by_hostname['CMO Interface'] == CMO_INTERFACE].reset_index()
                FMO_VLAN_IP = str(interface_df.loc[0]['FMO_VLAN_IP']).strip()
                if 'nan' == FMO_VLAN_IP:
                    FMO_VLAN_IP = ''
                CMO_INTERFACE_short = interface_to_shorcut_format(CMO_INTERFACE)
                ###########################################################
                #########################
                mode_ = ''
                #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
                not_found = False
                if ios_show_interface_switchport(output_dict, hostname).find(f'{CMO_INTERFACE_short}\n') == -1:
                    plog(f"{hostname}-[{CMO_INTERFACE_short}] not found in output file's - 'show interfaces switchport' section")
                    not_found = True
                    interface_switchport_infos = """"""
                    interface_switchport_infos_lines = interface_switchport_infos.split('\n')
                    FMO_VLAN_IP_from_outputs = 'not found in the output file'
                #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
                else:
                    interface_switchport_infos = ios_show_interface_switchport(output_dict, hostname).split(f'{CMO_INTERFACE_short}\n')[1].split('Name:')[0]
                    interface_switchport_infos_lines = interface_switchport_infos.split('\n')
                for line in interface_switchport_infos_lines:
                    #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ 
                    if not_found:
                        break
                    #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
                    if 'Administrative Mode:' in line and 'access' in line:
                        mode_ = 'access'
                        for line in interface_switchport_infos_lines:
                            if 'Access Mode VLAN:' in line:
                                FMO_VLAN_IP_from_outputs = line.split('Access Mode VLAN:')[1].split()[0]
                                FMO_VLAN_IP_from_outputs = convert_vlan_to_FMO_vlan(local_vlan_map, FMO_VLAN_IP_from_outputs)
                                #plog(FMO_VLAN_IP_from_outputs) 
                            if 'Voice VLAN:' in line:
                                voice_vlan = line.split('Voice VLAN:')[1].split()[0]
                                if voice_vlan.strip().lower() == 'none':
                                    pass
                                else:
                                    voice_vlan = convert_vlan_to_FMO_vlan(local_vlan_map, voice_vlan)
                                    FMO_VLAN_IP_from_outputs = f'{FMO_VLAN_IP_from_outputs}({voice_vlan})'
                                    #plog(FMO_VLAN_IP_from_outputs)
                        break   
                    if 'Administrative Mode:' in line and 'dynamic desirable' in line:
                        mode_ = 'dynamic desirable'
                        for line in interface_switchport_infos_lines:
                            if 'Access Mode VLAN:' in line:
                                FMO_VLAN_IP_from_outputs = line.split('Access Mode VLAN:')[1].split()[0]
                                FMO_VLAN_IP_from_outputs = convert_vlan_to_FMO_vlan(local_vlan_map, FMO_VLAN_IP_from_outputs)
                                #plog(FMO_VLAN_IP_from_outputs) 
                            if 'Voice VLAN:' in line:
                                voice_vlan = line.split('Voice VLAN:')[1].split()[0]
                                if voice_vlan.strip().lower() == 'none':
                                    pass
                                else:
                                    voice_vlan = convert_vlan_to_FMO_vlan(local_vlan_map, voice_vlan)
                                    FMO_VLAN_IP_from_outputs = f'{FMO_VLAN_IP_from_outputs}({voice_vlan})'
                                    #plog(FMO_VLAN_IP_from_outputs)
                        break
                    elif 'Administrative Mode:' in line and 'dynamic auto' in line:
                        mode_ = 'dynamic auto'
                        for line in interface_switchport_infos_lines:
                            if 'Access Mode VLAN:' in line:
                                FMO_VLAN_IP_from_outputs = line.split('Access Mode VLAN:')[1].split()[0]
                                FMO_VLAN_IP_from_outputs = convert_vlan_to_FMO_vlan(local_vlan_map, FMO_VLAN_IP_from_outputs)
                                #plog(FMO_VLAN_IP_from_outputs) 
                            if 'Voice VLAN:' in line:
                                voice_vlan = line.split('Voice VLAN:')[1].split()[0]
                                if voice_vlan.strip().lower() == 'none':
                                    pass
                                else:
                                    voice_vlan = convert_vlan_to_FMO_vlan(local_vlan_map, voice_vlan)
                                    FMO_VLAN_IP_from_outputs = f'{FMO_VLAN_IP_from_outputs}({voice_vlan})'
                                    #plog(FMO_VLAN_IP_from_outputs)            
                        break
                    elif 'Administrative Mode:' in line and 'trunk' in line:
                        mode_ = 'trunk'
                        for line in interface_switchport_infos_lines:
                            if 'Trunking VLANs Enabled:' in line:
                                lines = interface_switchport_infos.split('Trunking VLANs Enabled:')[1].split('Pruning VLANs Enabled:')[0]
                                FMO_VLAN_IP_from_outputs = ''.join(lines.split())
                                print(FMO_VLAN_IP_from_outputs)
                                temp_list = []
                                print(FMO_VLAN_IP_from_outputs)
                                local_vlan_list = FMO_VLAN_IP_from_outputs.split(',')
                                ################### long sorting
                                local_vlan_list_num_temp = []
                                for vlan in local_vlan_list:
                                    if vlan.isnumeric():
                                        local_vlan_list_num_temp.append(int(vlan))
                                    elif '-' in vlan:
                                        plog('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
                                        temp_vlan_range = vlan_range_converter(str(vlan).strip())
                                        for vlan in temp_vlan_range.split(','):
                                            local_vlan_list_num_temp.append(int(vlan))
                                        plog('******************************************************')
                                    else:
                                        local_vlan_list_num_temp = []
                                        break 
                                if len(local_vlan_list_num_temp) > 0:
                                    local_vlan_list_num_temp.sort()
                                    local_vlan_list = []
                                    for vlan in local_vlan_list_num_temp:
                                        local_vlan_list.append(str(vlan))
                                #################################################
                                for vlan in local_vlan_list:
                                    vlan = convert_vlan_to_FMO_vlan(local_vlan_map, vlan)
                                    temp_list.append(vlan)
                                print(temp_list)
                                #######################################################
                                temp_list.sort(key=sort_by_special)
                                #######################################################
                                temp_list_new = []
                                for e in temp_list:
                                    if e == "":
                                        continue
                                    else:
                                        temp_list_new.append(e)
                                temp_list = temp_list_new
                                temp_list = remove_list_dups(temp_list) 
                                FMO_VLAN_IP_from_outputs = ','.join(temp_list)
                                FMO_VLAN_IP_from_outputs = F'[{FMO_VLAN_IP_from_outputs}]'
                                #plog(FMO_VLAN_IP_from_outputs)
                        break
                    else:
                        mode_ = 'no mode found'
                        FMO_VLAN_IP_from_outputs = ''
                #################################################################################
                #################################################################################
                #################################################################################
                if FMO_VLAN_IP.strip().lower() == FMO_VLAN_IP_from_outputs.strip().lower():
                    if all_interface_matched:
                        all_interface_matched = True
                    data_temp = [hostname,CMO_INTERFACE,FMO_VLAN_IP,FMO_VLAN_IP_from_outputs,'-']
                    data.append(data_temp)
                else:
                    all_interface_matched = False
                    data_temp = [hostname,CMO_INTERFACE,FMO_VLAN_IP,FMO_VLAN_IP_from_outputs,'MISMATCH']
                    data.append(data_temp)
    tabul = tabulate(data, headers = ["HOSTNAME","INTERFACE","FMO_VLAN_IP","FROM OUTPUT","STAT"], tablefmt= "orgtbl")
    tabul_mismatch = tabulate([dat for dat in data if dat[-1] == 'MISMATCH'], headers = ["HOSTNAME","INTERFACE","FMO_VLAN_IP","FROM OUTPUT","STAT"], tablefmt= "orgtbl")
    if all_interface_matched:
        plog('-ios_FMO_VLAN_IP_check all matched')
        #plog(tabul)
    else:
        plog('-ios_FMO_VLAN_IP_check MISMATCH FOUND!')
        #plog(tabul_mismatch)  
    return data

# # MAIN
# In[20]:
device_outputs_folder= get_value('output_files_folder=') #GET THE PATH TO OUTPUT FOLDERS
device_outputfiles = get_text_log_files(device_outputs_folder) #LIST THE ABSOLUTE PATH OF EACH .LOG .TXT FILE
#plog(len(device_outputfiles))
output_dict = store_all_output_text_in_dict(device_outputfiles) #STORE ALL THE OUTPUT TEXT IN DICTIONARY WITH HOSTNAMES AS KEYS
#plog(len(output_dict))
path = get_value('merged_portmap=')
cmo_hostname_list = get_cmo_hostnames_from_portmap(path)
portmap_df = import_and_clean_portmap_df()
#plog('^^^^^^')
connected_interfaces_dict = store_connected_interfaces_details_in_dict(output_dict,cmo_hostname_list)
list_of_connected_interface = verify_connected_interfaces_from_outputs(connected_interfaces_dict, portmap_df )
# In[21]:
results_dict = {}
results_dict['FMO_SPEED'] = ios_FMO_SPEED_check(portmap_df, output_dict)
results_dict['FMO_DUPLEX'] = ios_FMO_DUPLEX_check(portmap_df, output_dict)
results_dict['FMO_DESCRIPTION'] = ios_FMO_DESCRIPTION_check(portmap_df, output_dict)
results_dict['NATIVE_VLAN'] = ios_NATIVE_VLAN_check(portmap_df, output_dict)
results_dict['EN_SWITCH'] = [['','','','','']]
results_dict['FMO_VLAN_IP'] = ios_FMO_VLAN_IP_check(portmap_df, output_dict)
plog('_'*80)
df_out = result_main_report(results_dict)
result_MISMATCH_report(results_dict)
plog('-end')
