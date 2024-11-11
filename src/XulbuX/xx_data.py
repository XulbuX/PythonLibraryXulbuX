import math as _math
import re as _re




class Data:

    @staticmethod
    def chars_count(data:list|tuple|set|frozenset|dict) -> int:
        """The sum of all the characters including the keys in dictionaries."""
        if isinstance(data, dict):
            return sum(len(str(k)) + len(str(v)) for k, v in data.items())
        return sum(len(str(item)) for item in data)

    @staticmethod
    def strip(data:list|tuple|dict) -> list|tuple|dict:
        if isinstance(data, dict):
            return {k: v.strip() if isinstance(v, str) else Data.strip(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            stripped = [item.strip() if isinstance(item, str) else Data.strip(item) for item in data]
            return tuple(stripped) if isinstance(data, tuple) else stripped
        return data.strip() if isinstance(data, str) else data

    @staticmethod
    def remove(data:list|tuple|dict, items:list[str]) -> list|tuple|dict:
        """Remove multiple items from lists and tuples or keys from dictionaries."""
        if isinstance(data, (list, tuple)):
            result = [k for k in data if k not in items]
            return result if isinstance(data, list) else tuple(result)
        elif isinstance(data, dict):
            return {k: v for k, v in data.items() if k not in items}

    @staticmethod
    def remove_empty_items(data:list|tuple|dict, spaces_are_empty:bool = False) -> list|tuple|dict:
        if isinstance(data, dict):
            filtered_dict = {}
            for key, value in data.items():
                if isinstance(value, (list, tuple, dict)):
                    filtered_value = Data.remove_empty_items(value, spaces_are_empty)
                    if filtered_value: filtered_dict[key] = filtered_value
                elif value not in (None, '') and not ((spaces_are_empty and isinstance(value, str)) and value.strip() in (None, '')):
                    filtered_dict[key] = value
            return filtered_dict
        filtered = []
        for item in data:
            if isinstance(item, (list, tuple, dict)):
                deduped_item = Data.remove_empty_items(item, spaces_are_empty)
                if deduped_item:
                    if isinstance(item, tuple):
                        deduped_item = tuple(deduped_item)
                    filtered.append(deduped_item)
            elif item not in (None, '') and not ((spaces_are_empty and isinstance(item, str)) and item.strip() in (None, '')):
                filtered.append(item)
        return tuple(filtered) if isinstance(data, tuple) else filtered

    @staticmethod
    def remove_duplicates(data:list|tuple|dict) -> list|tuple|dict:
        if isinstance(data, dict):
            return {k: Data.remove_duplicates(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            unique_items = []
            for item in data:
                if isinstance(item, (list, tuple, set, dict)):
                    deduped_item = Data.remove_duplicates(item)
                    if deduped_item not in unique_items:
                        unique_items.append(deduped_item)
                elif item not in unique_items:
                    unique_items.append(item)
            return tuple(unique_items) if isinstance(data, tuple) else unique_items
        return data

    @staticmethod
    def remove_comments(data:list|tuple|dict, comment_start:str = '>>', comment_end:str = '<<', comment_sep:str = '') -> list|tuple|dict:
        """Remove comments from a list, tuple or dictionary.\n
        -----------------------------------------------------------------------------------------------------------------
        The `data` parameter is your list, tuple or dictionary, where the comments should get removed from.<br>
        The `comment_start` parameter is the string that marks the start of a comment inside `data`. (default: `>>`)<br>
        The `comment_end` parameter is the string that marks the end of a comment inside `data`. (default: `<<`)<br>
        The `comment_sep` parameter is a string with which a comment will be replaced, if it is between strings.\n
        -----------------------------------------------------------------------------------------------------------------
        Examples:\n
        ```python\n data = {
            'key1': [
                '>> COMMENT IN THE BEGINNING OF THE STRING <<  value1',
                'value2  >> COMMENT IN THE END OF THE STRING',
                'val>> COMMENT IN THE MIDDLE OF THE STRING <<ue3',
                '>> FULL VALUE IS A COMMENT  value4'
            ],
            '>> FULL KEY + ALL ITS VALUES ARE A COMMENT  key2': [
                'value',
                'value',
                'value'
            ],
            'key3': '>> ALL THE KEYS VALUES ARE COMMENTS  value'
        }
        processed_data = Data.remove_comments(data, comment_start='>>', comment_end='<<', comment_sep='__')\n```
        -----------------------------------------------------------------------------------------------------------------
        For this example, `processed_data` will be:
        ```python\n {
            'key1': [
                'value1',
                'value2',
                'val__ue3'
            ],
            'key3': None
        }\n```
        For `key1`, all the comments will just be removed, except at `value3` and `value4`:<br>
         `value3` The comment is removed and the parts left and right are joined through `comment_sep`.<br>
         `value4` The whole value is removed, since the whole value was a comment.<br>
        For `key2`, the key, including its whole values will be removed.<br>
        For `key3`, since all its values are just comments, the key will still exist, but with a value of `None`."""
        def process_item(item:dict|list|tuple|str) -> dict|list|tuple|str|None:
            if isinstance(item, dict):
                processed_dict = {}
                for key, val in item.items():
                    processed_key = process_item(key)
                    if processed_key is not None:
                        processed_val = process_item(val)
                        if isinstance(val, (list, tuple, dict)):
                            if processed_val: processed_dict[processed_key] = processed_val
                        elif processed_val is not None:
                            processed_dict[processed_key] = processed_val
                        else:
                            processed_dict[processed_key] = None
                return processed_dict
            elif isinstance(item, list):
                return [v for v in (process_item(val) for val in item) if v is not None]
            elif isinstance(item, tuple):
                return tuple(v for v in (process_item(val) for val in item) if v is not None)
            elif isinstance(item, str):
                if comment_end:
                    no_comments = _re.sub(rf'^((?:(?!{_re.escape(comment_start)}).)*){_re.escape(comment_start)}(?:(?:(?!{_re.escape(comment_end)}).)*)(?:{_re.escape(comment_end)})?(.*?)$',
                        lambda m: f'{m.group(1).strip()}{comment_sep if (m.group(1).strip() not in ["", None]) and (m.group(2).strip() not in ["", None]) else ""}{m.group(2).strip()}', item)
                else:
                    no_comments = None if item.lstrip().startswith(comment_start) else item
                return no_comments.strip() if no_comments and no_comments.strip() != '' else None
            else:
                return item
        return process_item(data)

    @staticmethod
    def is_equal(data1:list|tuple|dict, data2:list|tuple|dict, ignore_paths:str|list[str] = '', comment_start:str = '>>', comment_end:str = '<<', sep:str = '->') -> bool:
        """Compares two structures and returns `True` if they are equal and `False` otherwise.\n
        ⇾ **Will not detect, if a key-name has changed, only if removed or added.**\n
        ------------------------------------------------------------------------------------------------
        Ignores the specified (found) key/s or item/s from `ignore_paths`. Comments are not ignored<br>
        when comparing. `comment_start` and `comment_end` are only used for key recognition.\n
        ------------------------------------------------------------------------------------------------
        The paths from `ignore_paths` work exactly the same way as the paths from `value_paths`<br>
        in the function `Data.get_path_id()`, just like the `sep` parameter. For more detailed<br>
        explanation, see the documentation of the function `Data.get_path_id()`."""
        def process_ignore_paths(ignore_paths:str|list[str]) -> list[list[str]]:
            if isinstance(ignore_paths, str):
                ignore_paths = [ignore_paths]
            return [path.split(sep) for path in ignore_paths if path]
        def compare(d1:dict|list|tuple, d2:dict|list|tuple, ignore_paths:list[list[str]], current_path:list = []) -> bool:
            if ignore_paths and any(current_path == path[:len(current_path)] and len(current_path) == len(path) for path in ignore_paths):
                return True
            if isinstance(d1, dict) and isinstance(d2, dict):
                if set(d1.keys()) != set(d2.keys()):
                    return False
                return all(compare(d1[key], d2[key], ignore_paths, current_path + [key]) for key in d1)
            elif isinstance(d1, (list, tuple)) and isinstance(d2, (list, tuple)):
                if len(d1) != len(d2):
                    return False
                return all(compare(item1, item2, ignore_paths, current_path + [str(i)]) for i, (item1, item2) in enumerate(zip(d1, d2)))
            else:
                return d1 == d2
        return compare(Data.remove_comments(data1, comment_start, comment_end), Data.remove_comments(data2, comment_start, comment_end), process_ignore_paths(ignore_paths))

    @staticmethod
    def get_fingerprint(data:list|tuple|dict) -> list|tuple|dict|None:
        if isinstance(data, dict):
            return {i: type(v).__name__ for i, v in enumerate(data.values())}
        elif isinstance(data, (list, tuple)):
            return {i: type(v).__name__ for i, v in enumerate(data)}
        return None

    @staticmethod
    def get_path_id(data:list|tuple|dict, value_paths:str|list[str], sep:str = '->', ignore_not_found:bool = False) -> str|list[str]:
        """Generates a unique ID based on the path to a specific value within a nested data structure.\n
        -------------------------------------------------------------------------------------------------
        The `data` parameter is the list, tuple, or dictionary, which the id should be generated for.\n
        -------------------------------------------------------------------------------------------------
        The param `value_path` is a sort of path (or a list of paths) to the value/s to be updated.<br>
        In this example:
        ```\n {
          'healthy': {
            'fruit': ['apples', 'bananas', 'oranges'],
            'vegetables': ['carrots', 'broccoli', 'celery']
          }
        }\n```
        ... if you want to change the value of `'apples'` to `'strawberries'`, `value_path`<br>
        would be `healthy->fruit->apples` or if you don't know that the value is `apples`<br>
        you can also use the position of the value, so `healthy->fruit->0`.\n
        -------------------------------------------------------------------------------------------------
        The `sep` param is the separator between the keys in the path<br>
        (default is `->` just like in the example above).\n
        -------------------------------------------------------------------------------------------------
        If `ignore_not_found` is `True`, the function will return `None` if the value is not<br>
        found instead of raising an error."""
        if isinstance(value_paths, str): value_paths = [value_paths]
        path_ids = []
        for path in value_paths:
            keys = [k.strip() for k in path.split(str(sep).strip()) if k.strip() != '']
            id_part_len, _path_ids, _obj = 0, [], data
            try:
                for k in keys:
                    if isinstance(_obj, dict):
                        if k.isdigit():
                            raise TypeError(f'Key \'{k}\' is invalid for a dict type.')
                        try:
                            idx = list(_obj.keys()).index(k)
                            _path_ids.append(idx)
                            _obj = _obj[k]
                        except KeyError:
                            if ignore_not_found:
                                _path_ids = None
                                break
                            raise KeyError(f'Key \'{k}\' not found in dict.')
                    elif isinstance(_obj, (list, tuple)):
                        try:
                            idx = int(k)
                            _path_ids.append(idx)
                            _obj = _obj[idx]
                        except ValueError:
                            try:
                                idx = _obj.index(k)
                                _path_ids.append(idx)
                                _obj = _obj[idx]
                            except ValueError:
                                if ignore_not_found:
                                    _path_ids = None
                                    break
                                raise ValueError(f'Value \'{k}\' not found in list/tuple.')
                    else:
                        break
                    if _path_ids:
                        id_part_len = max(id_part_len, len(str(_path_ids[-1])))
                if _path_ids is not None:
                    path_ids.append(f'{id_part_len}>{"".join([str(id).zfill(id_part_len) for id in _path_ids])}')
                elif ignore_not_found:
                    path_ids.append(None)
            except (KeyError, ValueError, TypeError) as e:
                if ignore_not_found:
                    path_ids.append(None)
                else: raise e
        return path_ids if len(path_ids) > 1 else path_ids[0] if len(path_ids) == 1 else None

    @staticmethod
    def get_value_by_path_id(data:list|tuple|dict, path_id:str, get_key:bool = False) -> any:
        """Retrieves the value from `data` using the provided `path_id`.\n
        ------------------------------------------------------------------------------------
        Input a list, tuple or dict as `data`, along with `path_id`, which is a path-id<br>
        that was created before using `Object.get_path_id()`. If `get_key` is True<br>
        and the final item is in a dict, it returns the key instead of the value.\n
        ------------------------------------------------------------------------------------
        The function will return the value (or key) from the path-id location, as long as<br>
        the structure of `data` hasn't changed since creating the path-id to that value."""
        def get_nested(data:list|tuple|dict, path:list[int], get_key:bool) -> any:
            parent = None
            for i, idx in enumerate(path):
                if isinstance(data, dict):
                    keys = list(data.keys())
                    if i == len(path) - 1 and get_key:
                        return keys[idx]
                    parent = data
                    data = data[keys[idx]]
                elif isinstance(data, (list, tuple)):
                    if i == len(path) - 1 and get_key:
                        if parent is None or not isinstance(parent, dict):
                            raise ValueError('Cannot get key from list or tuple without a parent dictionary')
                        return next(key for key, value in parent.items() if value is data)
                    parent = data
                    data = data[idx]
                else:
                    raise TypeError(f'Unsupported type {type(data)} at path {path[:i+1]}')
            return data
        path = Data._sep_path_id(path_id)
        return get_nested(data, path, get_key)

    @staticmethod
    def set_value_by_path_id(data:list|tuple|dict, update_values:str|list[str], sep:str = '::') -> list|tuple|dict:
        """Updates the value/s from `update_values` in the `data`.\n
        --------------------------------------------------------------------------------
        Input a list, tuple or dict as `data`, along with `update_values`, which is<br>
        a path-id that was created before using `Object.get_path_id()`, together<br>
        with the new value to be inserted where the path-id points to. The path-id<br>
        and the new value are separated by `sep`, which per default is `::`.\n
        --------------------------------------------------------------------------------
        The value from path-id will be changed to the new value, as long as the<br>
        structure of `data` hasn't changed since creating the path-id to that value."""
        def update_nested(data:list|tuple|dict, path:list[int], value:any) -> list|tuple|dict:
            if len(path) == 1:
                if isinstance(data, dict):
                    keys = list(data.keys())
                    data[keys[path[0]]] = value
                elif isinstance(data, (list, tuple)):
                    data = list(data)
                    data[path[0]] = value
                    data = type(data)(data)
            elif isinstance(data, dict):
                keys = list(data.keys())
                key = keys[path[0]]
                data[key] = update_nested(data[key], path[1:], value)
            elif isinstance(data, (list, tuple)):
                data = list(data)
                data[path[0]] = update_nested(data[path[0]], path[1:], value)
                data = type(data)(data)
            return data
        if isinstance(update_values, str):
            update_values = [update_values]
        valid_entries = [(parts[0].strip(), parts[1]) for update_value in update_values if len(parts := update_value.split(str(sep).strip())) == 2]
        if not valid_entries:
            raise ValueError(f'No valid update_values found: {update_values}')
        path, new_values = (zip(*valid_entries) if valid_entries else ([], []))
        for path_id, new_val in zip(path, new_values):
            path = Data._sep_path_id(path_id)
            data = update_nested(data, path, new_val)
        return data

    @staticmethod
    def print(data:list|tuple|dict, indent:int = 2, compactness:int = 1, sep:str = ', ', max_width:int = 140, as_json:bool = False, end:str = '\n') -> None:
      """Print nicely formatted data structures.\n
      ------------------------------------------------------------------------------------
      The indentation spaces-amount can be set with with `indent`.<br>
      There are three different levels of `compactness`:<br>
      `0` expands everything possible<br>
      `1` only expands if there's other lists, tuples or dicts inside of data or,<br>
       ⠀if the data's content is longer than `max_width`<br>
      `2` keeps everything collapsed (all on one line)\n
      ------------------------------------------------------------------------------------
      If `as_json` is set to `True`, the output will be in valid JSON format."""
      print(Data.to_str(data, indent, compactness, sep, max_width, as_json), end=end, flush=True)

    @staticmethod
    def to_str(data:list|tuple|dict, indent:int = 2, compactness:int = 1, sep:str = ', ', max_width:int = 140, as_json:bool = False) -> str:
        """Get nicely formatted data structure-strings.\n
        ------------------------------------------------------------------------------------
        The indentation spaces-amount can be set with with `indent`.<br>
        There are three different levels of `compactness`:<br>
        `0` expands everything possible<br>
        `1` only expands if there's other lists, tuples or dicts inside of data or,<br>
         ⠀if the data's content is longer than `max_width`<br>
        `2` keeps everything collapsed (all on one line)\n
        ------------------------------------------------------------------------------------
        If `as_json` is set to `True`, the output will be in valid JSON format."""
        def escape_string(s:str, str_quotes:str = '"') -> str:
            s = s.replace('\\', r'\\').replace('\n', r'\n').replace('\r', r'\r').replace('\t', r'\t').replace('\b', r'\b').replace('\f', r'\f').replace('\a', r'\a')
            if str_quotes == '"': s = s.replace(r"\\'", "'").replace(r'"', r'\"')
            elif str_quotes == "'": s = s.replace(r'\\"', '"').replace(r"'", r"\'")
            return s
        def format_value(value:any, current_indent:int) -> str:
            if isinstance(value, dict):
                return format_dict(value, current_indent + indent)
            elif hasattr(value, '__dict__'):
                return format_dict(value.__dict__, current_indent + indent)
            elif isinstance(value, (list, tuple, set, frozenset)):
                return format_sequence(value, current_indent + indent)
            elif isinstance(value, bool):
                return str(value).lower() if as_json else str(value)
            elif isinstance(value, (int, float)):
                return 'null' if as_json and (_math.isinf(value) or _math.isnan(value)) else str(value)
            elif isinstance(value, complex):
                return f'[{value.real}, {value.imag}]' if as_json else str(value)
            elif value is None:
                return 'null' if as_json else 'None'
            else:
                return '"' + escape_string(str(value), '"') + '"' if as_json else "'" + escape_string(str(value), "'") + "'"
        def should_expand(seq:list|tuple|dict) -> bool:
            if compactness == 0: return True
            if compactness == 2: return False
            complex_items = sum(1 for item in seq if isinstance(item, (list, tuple, dict, set, frozenset)))
            return complex_items > 1 or (complex_items == 1 and len(seq) > 1) or Data.chars_count(seq) + (len(seq) * len(sep)) > max_width
        def format_key(k:any) -> str:
            return '"' + escape_string(str(k), '"') + '"' if as_json else "'" + escape_string(str(k), "'") + "'" if isinstance(k, str) else str(k)
        def format_dict(d:dict, current_indent:int) -> str:
            if not d or compactness == 2:
                return '{' + sep.join(f'{format_key(k)}: {format_value(v, current_indent)}' for k, v in d.items()) + '}'
            if not should_expand(d.values()):
                return '{' + sep.join(f'{format_key(k)}: {format_value(v, current_indent)}' for k, v in d.items()) + '}'
            items = []
            for key, value in d.items():
                formatted_value = format_value(value, current_indent)
                items.append(f'{" " * (current_indent + indent)}{format_key(key)}: {formatted_value}')
            return '{\n' + ',\n'.join(items) + f'\n{" " * current_indent}}}'
        def format_sequence(seq, current_indent:int) -> str:
            if as_json:
                seq = list(seq)
            if not seq or compactness == 2:
                return '[' + sep.join(format_value(item, current_indent) for item in seq) + ']' if isinstance(seq, list) else '(' + sep.join(format_value(item, current_indent) for item in seq) + ')'
            if not should_expand(seq):
                return '[' + sep.join(format_value(item, current_indent) for item in seq) + ']' if isinstance(seq, list) else '(' + sep.join(format_value(item, current_indent) for item in seq) + ')'
            items = [format_value(item, current_indent) for item in seq]
            formatted_items = ',\n'.join(f'{" " * (current_indent + indent)}{item}' for item in items)
            if isinstance(seq, list):
                return '[\n' + formatted_items + f'\n{" " * current_indent}]'
            else:
                return '(\n' + formatted_items + f'\n{" " * current_indent})'
        return format_dict(data, 0) if isinstance(data, dict) else format_sequence(data, 0)

    @staticmethod
    def _is_key(data:list|tuple|dict, path_id:str) -> bool:
        """Returns `True` if the path-id points to a key in `data` and `False` otherwise.\n
        ------------------------------------------------------------------------------------
        Input a list, tuple or dict as `data`, along with `path_id`, which is a path-id<br>
        that was created before using `Object.get_path_id()`."""
        def check_nested(data:list|tuple|dict, path:list[int]) -> bool:
            for i, idx in enumerate(path):
                if isinstance(data, dict):
                    keys = list(data.keys())
                    if i == len(path) - 1:
                        return True
                    data = data[keys[idx]]
                elif isinstance(data, (list, tuple)):
                    return False
                else:
                    raise TypeError(f'Unsupported type {type(data)} at path {path[:i+1]}')
            return False
        if isinstance(data, (list, tuple)):
            return False
        path = Data._sep_path_id(path_id)
        return check_nested(data, path)

    @staticmethod
    def _sep_path_id(path_id:str) -> list[int]:
        if path_id.count('>') != 1:
            raise ValueError(f'Invalid path-id: {path_id}')
        id_part_len, path_ids_str = int(path_id.split('>')[0]), path_id.split('>')[1]
        return [int(path_ids_str[i:i+id_part_len]) for i in range(0, len(path_ids_str), id_part_len)]
