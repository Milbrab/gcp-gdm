# Import JSON module
import json

# Import collections modules
import collections

OPTIONAL_INSTANCE_PROPERTIES = [
    'canIpForward', 'description', 'guestAccelerators', 'labels', 'metadata',
    'minCpuPlatform', 'scheduling', 'serviceAccounts', 'tags'
]
DEFAULT_SOURCE_IMAGE = 'projects/debian-cloud/global/images/family/debian-9'
DEFAULT_NETWORK_INTERFACES = [{'network': 'global/networks/default'}]
DEFAULT_BOOT_DISK = {
    'deviceName': 'boot',
    'boot': True,
    'autoDelete': True,
    'initializeParams': {
        'sourceImage': DEFAULT_SOURCE_IMAGE
    }
}

def sort_by_key(unsorted_dict):
    """ Sorts a dictionary by key """
    sorted_dict = collections.OrderedDict(sorted(unsorted_dict.items()))

    # Sort dictionaries within the dictionary
    for key, value in \
        [(key, value) for key, value in sorted_dict.items() if isinstance(value, dict)]:  # pylint: disable=line-too-long
        sorted_dict[key] = sort_by_key(value)

    return sorted_dict

def generate_config(context):
    """ Iterates through the resource provided by context """

    machine_type = ''.join([
        'zones/', context.properties['zone'], '/machineTypes/',
        context.properties['machineType']])

    properties = {
        'zone': context.properties['zone'],
        'serviceAccounts': [{
                'email': context.properties['serviceAccount'],
                'scopes': ['https://www.googleapis.com/auth/devstorage.read_write','https://www.googleapis.com/auth/logging.write','https://www.googleapis.com/auth/monitoring.write','https://www.googleapis.com/auth/servicecontrol','https://www.googleapis.com/auth/service.management.readonly','https://www.googleapis.com/auth/trace.append','https://www.googleapis.com/auth/compute.readonly']
                }],        
        'machineType': machine_type
    }

    # If disks is not declared, default to DEFAULT_BOOT_DISK.
    if 'disks' in context.properties:
        properties['disks'] = context.properties['disks']
    else:
        properties['disks'] = [DEFAULT_BOOT_DISK]

    # If networkInterfaces hasn't been declared then default to a private
    # IP on the default network. Else use whatever has been declared.
    if 'networkInterfaces' in context.properties:
        properties['networkInterfaces'] = \
            context.properties['networkInterfaces']
    else:
        properties['networkInterfaces'] = DEFAULT_NETWORK_INTERFACES

    # Add optional properties if they have been declared.
    for _property in OPTIONAL_INSTANCE_PROPERTIES:
        if _property in context.properties:
            properties[_property] = context.properties[_property]

    # return the instance's configuration
    return {
        'resources': [{
            'name': context.env['name'],
            'type': 'compute.v1.instance',
            'properties': properties
            }]
    }


if __name__ == "__main__":
    from lib.testing import GenerateConfigTester

    GenerateConfigTester.print_config(generate_config)
