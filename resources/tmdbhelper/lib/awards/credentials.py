"""Read the addon's key definitions without importing its Kodi integration."""
from pathlib import Path
import ast


class AddonCredentials:
    directory = Path(__file__).resolve().parents[1] / 'api' / 'api_keys'

    def get_api_key(self, provider):
        source = ast.parse((self.directory / f'{provider}.py').read_text(encoding='utf-8'))
        # The first branch contains TMDbHelper's internal credentials. Read only
        # its API_KEY expression; never execute the permissions or token modules.
        branch = next(node for node in source.body if isinstance(node, ast.If))
        assignment = next(
            node for node in branch.body if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == 'API_KEY' for target in node.targets))
        return self.get_key_value(assignment.value)

    @staticmethod
    def get_key_value(expression):
        if isinstance(expression, ast.Constant):
            return ast.literal_eval(expression)
        # TVDB uses load_in_data(bytes, mask).decode(). Restrict decoding to
        # that exact expression so a changed definition fails visibly.
        if not (
                isinstance(expression, ast.Call) and isinstance(expression.func, ast.Attribute)
                and expression.func.attr == 'decode' and not expression.args and not expression.keywords):
            raise ValueError('Unsupported addon API key definition')
        encoded = expression.func.value
        if not (
                isinstance(encoded, ast.Call) and isinstance(encoded.func, ast.Name)
                and encoded.func.id == 'load_in_data' and len(encoded.args) == 2 and not encoded.keywords):
            raise ValueError('Unsupported addon API key encoding')
        data, mask = (ast.literal_eval(argument) for argument in encoded.args)
        return bytes(value ^ mask[index % len(mask)] for index, value in enumerate(data)).decode()
