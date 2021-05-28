import importlib

class ModuleNotFoundException(Exception):
    pass


class Importer(object):
    def __init__(self):
        pass

    def import_hook(self, module):
        if module:
            ouroboros_hook = self._import(module, description="OuroborosHooks")
            if hasattr(ouroboros_hook, "OuroborosHooks"):
                return getattr(ouroboros_hook, "OuroborosHooks")
        return None

    def _import(self, module, description=None):
        try:
            mod = importlib.import_module(module)
        except ImportError:
            msg = "{0} {1} cannot be found".format(description, module)
            raise ModuleNotFoundException(msg)
        return mod


def set_properties(old, new, self_name=None):
    """Store object for spawning new container in place of the one with outdated image"""
    properties = {
        'name': self_name if self_name else old.name,
        'hostname': old.attrs['Config']['Hostname'],
        'user': old.attrs['Config']['User'],
        'detach': True,
        'domainname': old.attrs['Config']['Domainname'],
        'tty': old.attrs['Config']['Tty'],
        'ports': None if not old.attrs['Config'].get('ExposedPorts') else [
            (p.split('/')[0], p.split('/')[1]) for p in old.attrs['Config']['ExposedPorts'].keys()
        ],
        'volumes': None if not old.attrs['Config'].get('Volumes') else [
            v for v in old.attrs['Config']['Volumes'].keys()
        ],
        'working_dir': old.attrs['Config']['WorkingDir'],
        'image': new.tags[0],
        'command': old.attrs['Config']['Cmd'],
        'host_config': old.attrs['HostConfig'],
        'labels': old.attrs['Config']['Labels'],
        'entrypoint': old.attrs['Config']['Entrypoint'],
        'environment': old.attrs['Config']['Env'],
        'healthcheck': old.attrs['Config'].get('Healthcheck', None)
    }

    return properties


def remove_sha_prefix(digest):
    if digest.startswith("sha256:"):
        return digest[7:]
    return digest


def get_digest(image):
    digest = image.attrs.get(
            "Descriptor", {}
        ).get("digest") or image.attrs.get(
            "RepoDigests"
        )[0].split('@')[1] or image.id
    return remove_sha_prefix(digest)
