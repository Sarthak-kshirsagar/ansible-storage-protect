#!/usr/bin/python
# coding: utf-8 -*-

# (c) 2024,Sarthak Kshirsgar <sarthak.kshirsagar@ibm.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.dsmadmc_adapter import DsmadmcAdapter
from ..module_utils.dsmc_adapter import DsmcAdapter

DOCUMENTATION = '''
module: storage_agent_config
author: "Sarthak Kshirsagar (@Tompage1994)"
short_description: Configures the storage agent for LAN Free Data Movement
description:
    - Configures the storage agent and performs the necessary steps to enable the communication between client,server and storage agent
    - Validates LAN Free Data Movement
options:
    stg_agent_name:
        description:
            - Storage agent name defined on the server.
        type: str
        default: ''
    stg_agent_password:
        description:
            - Password for the storage agent.
        type: str
        default: ''
    stg_agent_hhl_add:
        description:
            - High level address of storage agent required for defining agent on server.
        type: str
        default: ''
    stg_agebt_ll_add:
        description:
            - Low level address of storage agent required for defining agent on server
        type: str
        default: ''
    copy_group_name:
        description:
            - Name of the copy group with a destination to the LAN-free capable storage pool.
        type: str
        default: ''
    policy_set_name:
        description:
            - Name of the policyset for creating copy group.
        type: str
        default: ''
    mng_class_name:
        description:
            - Name of the Management class for creating copy group.
        type: str
        default: ''
    stg_pool_name:
        description:
            - Name of the storage pool for creating copy group.
        type: str
        default: ''
    drive_number:
        description:
            - Specifies the identifier or numeric suffix for the tape drive to be defined (e.g., 'dr1', 'dr2'). This value is appended to the storage agent name when defining the drive path.
        type: str
        default: ''
    dest_type:
        description:
            - Specifies the destination type for the defined path. For tape drive definitions, this should be set to 'drive'..
        type: str
        default: ''
    library:
        description:
            - Specifies the name or identifier of the tape library that contains the drive. This value is used in the path definition to associate the drive with its library..
        type: str
        default: ''
    device:
        description:
            - Specifies the physical device path for the tape drive (e.g., '/dev/IBMtape1'). This should match the device name as identified by the storage agent.
        type: str
        default: ''
    tsm_serv_name:
        description:
            - Name of the TSM Server.
        type: str
        default: ''
    tsm_serv_password:
        description:
            - TSM Server Password.
        type: str
        default: ''
    tsm_serv_hhaddress:
        description:
            - High level address for the TSM Server.
        type: str
        default: ''
    tcp_port:
        description:
            - TCP port for of the server for configuring the dsm.sys file.
        type: str
        default: ''
    agent_lanfree_tcp_port:
        description:
            - Storage agent LAN Free TCP Port.
        type: str
        default: ''
    node_name:
        description:
            - Name of the node for validating the lan free movement
        type: str
        default: ''
    config_role:
        description:
            - Option for configuring the server and client.
        choices: [server, client]
        type: str
        default: ''
    client_options_file_path:
        description:
            - Path of the dsm.sys file on client.
        type: str
        default: '/opt/tivoli/tsm/client/ba/bin/dsm.sys'
extends_documentation_fragment: ibm.storage_protect.auth
'''

EXAMPLES='''
---
- name: Configure Storage Agent on Client and Server
  storage_agent_config:
    config_role: "{{ item }}"
    stg_agent_name: "StorageAgent1"
    stg_agent_password: "agent_password"
    stg_agent_hhl_add: "192.168.1.10"
    stg_agebt_ll_add: "1500"
    copy_group_name: "CopyGroup1"
    policy_set_name: "PolicySet1"
    mng_class_name: "ManagementClass1"
    stg_pool_name: "StoragePool1"
    drive_number: "dr1"
    dest_type: "drive"
    library: "Library1"
    device: "/dev/IBMtape1"
    tsm_serv_name: "TSMServer1"
    tsm_serv_password: "server_password"
    tsm_serv_hhaddress: "192.168.1.20"
    tcp_port: "1500"
    agent_lanfree_tcp_port: "1501"
    node_name: "ClientNode1"
    client_options_file_path: "/opt/tivoli/tsm/client/ba/bin/dsm.sys"
  loop:
    - "server"
    - "client"
'''

def execute_command(module, cmd, adapter):
    rc, stdout, stderr = adapter.run_command(cmd)
    if rc != 0:
        module.fail_json(msg=f"Command failed: {cmd}\nReason: {stderr.strip()}", rc=rc, stdout=stdout, stderr=stderr)
    return stdout.strip()

def main():
    module_args = dict(
        # Parameters for server configuration
        stg_agent_name=dict(type='str', required=True),
        stg_agent_password=dict(type='str', required=True),
        stg_agent_hhl_add=dict(type='str', required=True),
        stg_agebt_ll_add=dict(type='str', required=True),
        copy_group_name=dict(type='str', required=True),
        policy_set_name=dict(type='str', required=True),
        mng_class_name=dict(type='str', required=True),
        stg_pool_name=dict(type='str', required=True),
        drive_number=dict(type='str', required=True),
        dest_type=dict(type='str', required=True, choices=['drive']),
        library=dict(type='str', required=True),
        device=dict(type='str', required=True),
        # Parameters for client configuration
        tsm_serv_name=dict(type='str', required=True),
        tsm_serv_password=dict(type='str', required=True),
        tsm_serv_hhaddress=dict(type='str', required=True),
        tcp_port=dict(type='str', required=True),
        agent_lanfree_tcp_port=dict(type='str', required=True),
        # Node for LAN-free validation; default if not provided
        node_name=dict(type='str', required=False, default="lanfree1"),
        config_role=dict(type='str', required=True, choices=['server', 'client']),
        client_options_file_path = dict(type='str', required=True, default="/opt/tivoli/tsm/client/ba/bin/dsm.sys")
    )

    module = AnsibleModule(argument_spec=module_args)
    params = module.params
    changed = False

    dsmadmc_adapter = DsmadmcAdapter()
    dsmc_adapter = DsmcAdapter()


    outputs = []

    if params['config_role'] == 'server':
        # List of (command, error message) tuples for server configuration
        server_commands = [
            (
                f"define server {params['stg_agent_name']} "
                f"serverpassword={params['stg_agent_password']} "
                f"hladdress={params['stg_agent_hhl_add']} "
                f"lladdress={params['stg_agebt_ll_add']}",
                "Failed to define server"
            ),
            (
                f"define copygroup {params['copy_group_name']} "
                f"{params['policy_set_name']} {params['mng_class_name']} "
                f"type=backup destination={params['stg_pool_name']}",
                "Failed to create copygroup"
            ),
            (
                f"define path {params['stg_agent_name']} {params['drive_number']} "
                f"srctype=server desttype={params['dest_type']} "
                f"library={params['library']} device={params['device']}",
                "Failed to define path"
            ),
        ]
        # logic to check whether the storage agent, copygroup and path is already defined or not , to make module idempotent
        for cmd, err_msg in server_commands:
            outputs.append(execute_command(module, cmd, dsmadmc_adapter))
        changed = True

    elif params['config_role'] == 'client':

        configure_stg_agent_on_client = f"/opt/tivoli/tsm/StorageAgent/bin/dsmsta setstorageserver "
        f"myname={params['stg_agent_name']} "
        f"mypassword={params['stg_agent_password']} "
        f"myhladdress={params['stg_agent_hhl_add']} "
        f"servername={params['tsm_serv_name']} "
        f"serverpassword={params['tsm_serv_password']} "
        f"hladdress={params['tsm_serv_hhaddress']} "
        f"lladdress={params['agent_lanfree_tcp_port']}"

        rc, std_out, err = module.run_command(configure_stg_agent_on_client)
        if rc!=0:
            module.fail_json(msg="Failed to configure the storage agent", rc=rc, stdout=std_out, stderr=err)
        else:
            changed = True
            outputs.append(std_out)
        # configures dsm.sys file
        try:
            with open(params['client_options_file_path'], 'w') as f:
                f.write(f"Servername             {params['stg_agent_name']}\n")
                f.write("COMMMethod             TCPip\n")
                f.write(f"TCPPort                {params['tcp_port']}\n")
                f.write(f"TCPServeraddress       {params['tsm_serv_hhaddress']}\n")
                f.write("LANfreeCOMMmethod      tcpip\n")
                f.write("enablelanfree          yes\n")
                f.write(f"lanfreetcpport         {params['agent_lanfree_tcp_port']}\n")
        except Exception as e:
                module.fail_json(msg="Failed to update client options file", error=str(e))

        # command to validate the lan free data movement
        client_commands = [
            (
                f"validate lanfree {params['node_name']} {params['stg_agent_name']}",
                "LAN-free validation failed"
            )
        ]

        for cmd, err_msg in client_commands:
            validation_out = execute_command(module,cmd,dsmc_adapter)
        #     parsing logic to validate the output

    result = dict(changed=changed, commands_executed=outputs)
    module.exit_json(**result)

if __name__ == '__main__':
    main()
