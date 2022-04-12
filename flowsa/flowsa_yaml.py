from typing import IO, Any
import yaml
import flowsa.settings
from os import path


class FlowsaLoader(yaml.SafeLoader):
    '''
    Custom YAML loader implementing !include: tag to allow inheriting
    arbitrary nodes from other yaml files.
    '''
    def __init__(self, stream: IO) -> None:
        super().__init__(stream)
        self.add_multi_constructor('!include:', self.include)
        self.add_constructor('!external_config', self.external_config)
        self.external_config_paths = []

    @staticmethod
    def include(loader: 'FlowsaLoader', suffix: str, node: yaml.Node) -> dict:
        file, *keys = suffix.split(':')

        for folder in [
            *loader.external_config_paths,
            flowsa.settings.sourceconfigpath,
            flowsa.settings.flowbysectormethodpath
        ]:
            if path.exists(path.join(folder, file)):
                file = path.join(folder, file)
                break
        else:
            raise FileNotFoundError

        with open(file) as f:
            branch = load(f)

        while keys:
            branch = branch[keys.pop(0)]

        if isinstance(node, yaml.MappingNode):
            if isinstance(branch, dict):
                context = loader.construct_mapping(node)
                branch.update(context)
            else:
                raise TypeError(f'{suffix} is not a mapping/dict')

        elif isinstance(node, yaml.SequenceNode):
            if isinstance(branch, list):
                context = loader.construct_sequence(node)
                branch.extend(context)
            else:
                raise TypeError(f'{suffix} is not a sequence/list')

        return branch

    @staticmethod
    def external_config(loader: 'FlowsaLoader', node: yaml.Node) -> str:
        if isinstance(node, yaml.SequenceNode):
            paths = loader.construct_sequence(node)
            loader.external_config_paths.extend(paths)
            return paths
        elif isinstance(node, yaml.ScalarNode):
            path = loader.construct_scalar(node)
            loader.external_config_paths.append(path)
            return path
        else:
            raise TypeError('Cannot tag a mapping node with !external_config')


def load(stream: IO) -> dict:
    loader = FlowsaLoader(stream)
    try:
        return loader.get_single_data()
    finally:
        loader.dispose()
