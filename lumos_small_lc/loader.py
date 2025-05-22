import os
import re
from datetime import datetime
from pathlib import Path
from typing import Union

from langchain_community.document_loaders import UnstructuredMarkdownLoader, TextLoader

from lumos_small_lc import imagex

loader = UnstructuredMarkdownLoader(
    "D:\Storage\\Notable\\Notable-Repository\\notes\CAS Feature - Small Feature Collection.md",
    # mode="elements",
    mode="single",
    strategy="fast",
)


# data = loader.load()

class NotableLoader:
    def __init__(self, file_path: Union[str, Path]):
        self.datas = TextLoader(file_path,
                                autodetect_encoding=True).load()
        self.abs_path = os.path.join(os.path.dirname(os.path.abspath(file_path)), "../")
        self.headers = []
        for i in range(len(self.datas)):
            header, body = NotableLoader.parse_header_data(self.datas[i].page_content)
            self.headers.append(header)
            self.datas[i] = self.replace_attachments(body)
            print(self.datas[i])

    def get_attachment_path(self, attachment):
        attachment_pattern = r'!\[\]\(@attachment/([^)]+)\)'
        found_attachments = re.findall(attachment_pattern, attachment)
        if len(found_attachments) > 0:
            return os.path.join(self.abs_path, 'attachments', found_attachments[0])
        else:
            return None

    def replace_attachments(self, data_string):
        attachment_pattern = r'(!\[\]\(@attachment/[^)]+)\)'
        modified_parts = []
        last_end_index = 0
        # Find all matches
        for match in re.finditer(attachment_pattern, data_string):
            found_attachment = match.group(0)
            start_index = match.start()  # Start index of the full match
            end_index = match.end()  # End index of the full match
            modified_parts.append(data_string[last_end_index:start_index])
            last_end_index = end_index

            context_start_index = max(start_index - 125, 0)
            context_end_index = min(end_index + 125, len(data_string))
            attachment_path = self.get_attachment_path(found_attachment)
            if attachment_path:
                encoded_attachment = imagex.local_image_to_base64(attachment_path)
                description = imagex.describe_image(encoded_attachment,
                                                    f"Context: {data_string[context_start_index: context_end_index]}")
                modified_parts.append(f"===Image Description Begin===\n{description}\n===Image Description End===")
            else:
                modified_parts.append(found_attachment)
        modified_parts.append(data_string[last_end_index:])
        return "".join(modified_parts)

    @staticmethod
    def parse_header_data(data_string):
        parsed_data = {}

        parts = data_string.split('---', 2)
        if len(parts) < 3:
            return parsed_data
        data_string = parts[1].strip()
        # Regex for attachments (list of items in brackets)
        # It looks for "attachments: [" followed by anything not "]" until "]"
        match_attachments = re.search(r"attachments:\s*\[([^\]]+?)\]", data_string)
        if match_attachments:
            # Split the captured content by comma and strip whitespace
            attachments_str = match_attachments.group(1)
            parsed_data['attachments'] = [item.strip() for item in attachments_str.split(',') if item.strip()]

        # Regex for tags (similar to attachments)
        match_tags = re.search(r"tags:\s*\[([^\]]+?)\]", data_string)
        if match_tags:
            tags_str = match_tags.group(1)
            parsed_data['tags'] = [item.strip() for item in tags_str.split(',') if item.strip()]

        # Regex for general key-value pairs
        # (\w+):           - Matches a word as the key, followed by a colon
        # \s* - Matches any whitespace (0 or more)
        # (?:              - Non-capturing group for the value
        #    '[^']+'      - Matches content inside single quotes (for dates)
        #    |             - OR
        #    [^\[\]']+?   - Matches anything that's not a bracket or a quote, non-greedily
        # )
        # This regex is an attempt to capture values until the next key or end of string.
        # It's challenging for single-line, mixed-format strings.
        # A better approach might be to remove the list parts first, then parse the rest.

        # Let's refine for title, created, modified by removing list parts first
        temp_string = data_string
        if match_attachments:
            temp_string = re.sub(re.escape(match_attachments.group(0)), "", temp_string).strip()
        if match_tags:
            temp_string = re.sub(re.escape(match_tags.group(0)), "", temp_string).strip()

        # Regex for the remaining key-value pairs (title, created, modified)
        # This will work better now that the lists are gone.
        # It captures key (\w+), then a colon, then value,
        # stopping before the next key pattern or end of string.
        # It handles quoted values (like dates) and unquoted values.
        # This pattern needs to be carefully crafted to account for spaces within values.

        # A more robust regex for remaining key-value pairs, allowing spaces in values.
        # It looks for a key (word characters), then a colon, then whitespace,
        # then captures the value. The value capture is tricky:
        # It's either text enclosed in single quotes, or
        # any characters until another word followed by a colon (next key), or the end of the string.

        # This is a bit more complex, and often a loop with a simpler regex is clearer.
        # Let's try iterating through simple key-value matches.

        # Key: Value pattern for remaining parts
        # \s*(\w+):\s* -> Optional leading whitespace, key (word), colon, whitespace
        # (                           -> Start capturing value
        #    '[^']+'                  -> Quoted string (e.g., for dates)
        #    |                        -> OR
        #    (?:(?!\s*\w+:).)*?      -> Any character non-greedily, as long as it's not followed by a new key pattern
        # )

        # This still can be problematic if values themselves contain colons or look like keys.
        # For this specific structure, a simpler iterative approach after removing lists might be best.

        # Let's try matching specific known keys with a more defined value pattern:

        # Title:
        match_title = re.search(r"title:\s*([^c]+?)(?=\s*created:|\s*$)", temp_string)
        if match_title:
            parsed_data['title'] = match_title.group(1).strip()
            # Remove the title part to simplify for created/modified
            temp_string = re.sub(re.escape(match_title.group(0)), "", temp_string).strip()

        # Created and Modified dates
        # Matches 'key: ' then captures the content within single quotes.
        match_dates = re.findall(r"(created|modified):\s*'([^']+?)'", data_string)
        for key, value_str in match_dates:
            try:
                # Dates are UTC, replace 'Z' with '+00:00' for datetime.fromisoformat
                parsed_data[key] = datetime.fromisoformat(value_str.replace('Z', '+00:00'))
            except ValueError:
                parsed_data[key] = value_str  # Fallback to string if parse fails

        return parsed_data, parts[2].strip()


loader2 = NotableLoader("D:\Storage\\Notable\\Notable-Repository\\notes\CAS Feature - Small Feature Collection.md")
print(1)
