import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from enum import Enum, auto


@dataclass
class Comment:
    """Represents a comment in the header file."""
    text: str
    line_number: int
    is_multiline: bool


@dataclass
class StructMember:
    """Represents a member of a C struct."""
    name: str
    type_name: str
    is_array: bool
    array_size: Optional[int]
    comment: Optional[str]
    line_number: int
    nested_struct_members: Optional[List['StructMember']] = None


@dataclass
class StructDefinition:
    """Represents a complete C struct definition."""
    name: str
    members: List[StructMember]
    comment: Optional[str]
    line_number: int


class CommentExtractor:
    """Handles the extraction and processing of comments from C code."""

    @staticmethod
    def extract_comments(content: str) -> Dict[int, str]:
        """
        Extracts all comments from the source code and maps them to line numbers.

        Args:
            content: The source code content

        Returns:
            Dictionary mapping line numbers to comments
        """
        comments = {}

        # Find single-line comments
        for match in re.finditer(r'//([^\n]*)', content):
            line_no = content[:match.start()].count('\n') + 1
            comments[line_no] = match.group(1).strip()

        # Find multi-line comments
        for match in re.finditer(r'/\*.*?\*/', content, re.DOTALL):
            start_line = content[:match.start()].count('\n') + 1
            comments[start_line] = match.group(0)[2:-2].strip()

        return comments


class TypeProcessor:
    """Handles C type processing and mapping."""

    def __init__(self):
        self.type_mapping = {
            'int8_t': 'INT8',
            'uint8_t': 'UINT8',
            'int16_t': 'INT16',
            'uint16_t': 'UINT16',
            'int32_t': 'INT32',
            'uint32_t': 'UINT32',
            'int64_t': 'INT64',
            'uint64_t': 'UINT64',
            'float': 'FLOAT',
            'double': 'DOUBLE',
            'char': 'CHAR',
            'bool': 'BOOL'
        }

    def map_c_type_to_python(self, c_type: str) -> Optional[str]:
        """Maps a C type to its corresponding Python type."""
        return self.type_mapping.get(c_type)

    def is_valid_c_type(self, type_name: str) -> bool:
        """Checks if a given type name is a valid C type."""
        return type_name in self.type_mapping


class StructMemberParser:
    """Handles parsing of individual struct members."""

    def __init__(self, type_processor: TypeProcessor):
        self.type_processor = type_processor

    def parse_member(self, line: str, comment: Optional[str], line_number: int) -> Optional[StructMember]:
        """Parses a regular struct member (non-nested)."""
        # Parse arrays
        array_match = re.match(r'(\w+)\s+(\w+)\[(\d+)\]', line.strip())
        if array_match:
            type_name, var_name, array_size = array_match.groups()
            if self.type_processor.is_valid_c_type(type_name):
                return StructMember(
                    name=var_name,
                    type_name=type_name,
                    is_array=True,
                    array_size=int(array_size),
                    comment=comment,
                    line_number=line_number
                )

        # Parse regular variables
        var_match = re.match(r'(\w+)\s+(\w+)', line.strip())
        if var_match:
            type_name, var_name = var_match.groups()
            if self.type_processor.is_valid_c_type(type_name):
                return StructMember(
                    name=var_name,
                    type_name=type_name,
                    is_array=False,
                    array_size=None,
                    comment=comment,
                    line_number=line_number
                )

        return None

    def parse_nested_struct(self, content: str, start_line: int, comments: Dict[int, str]) -> Tuple[
        List[StructMember], str, int]:
        """
        Parses a nested struct definition.

        Returns:
            Tuple of (list of members, struct name, end line number)
        """
        members = []
        brace_count = 1
        current_line = start_line
        nested_content = []

        # Split content into lines and process
        lines = content.split('\n')
        i = 0

        # Skip until we find the opening brace
        while i < len(lines) and '{' not in lines[i]:
            i += 1

        if i < len(lines):
            i += 1  # Skip the line with opening brace

        # Collect lines until matching closing brace
        while i < len(lines) and brace_count > 0:
            line = lines[i].strip()
            if '{' in line:
                brace_count += 1
            if '}' in line:
                brace_count -= 1
            if brace_count > 0:  # Don't include the closing brace line
                nested_content.append(lines[i])
            i += 1

        # Find struct name from the closing line
        while i < len(lines):
            name_match = re.search(r'}\s*(\w+);', lines[i])
            if name_match:
                struct_name = name_match.group(1)
                break
            i += 1
        else:
            struct_name = "anonymous"

        # Parse the members
        for line in nested_content:
            line = line.strip()
            if not line or line.endswith('{'):
                continue

            # Remove trailing semicolon if present
            if line.endswith(';'):
                line = line[:-1]

            comment = comments.get(current_line)
            member = self.parse_member(line, comment, current_line)
            if member:
                members.append(member)

            current_line += 1

        return members, struct_name, current_line


class HeaderFileParser:
    """Main class for parsing C header files."""

    def __init__(self):
        self.type_processor = TypeProcessor()
        self.member_parser = StructMemberParser(self.type_processor)
        self.comment_extractor = CommentExtractor()

    def parse_content(self, content: str) -> List[StructDefinition]:
        """Parses header file content and extracts struct definitions."""
        comments = self.comment_extractor.extract_comments(content)

        # Find all top-level struct definitions
        structs = []
        pattern = r'typedef\s+struct\s*{([^}]+)}\s*(\w+);'

        for match in re.finditer(pattern, content, re.DOTALL):
            struct_content = match.group(1)
            struct_name = match.group(2)
            struct_start = content[:match.start()].count('\n') + 1

            # Get struct comment
            struct_comment = comments.get(struct_start - 1)

            members = []
            current_line = struct_start
            lines = struct_content.split('\n')
            i = 0

            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    current_line += 1
                    continue

                # Check for nested struct
                if line.startswith('struct'):
                    nested_content = '\n'.join(lines[i:])
                    nested_members, nested_name, end_line = self.member_parser.parse_nested_struct(
                        nested_content, current_line, comments
                    )

                    members.append(StructMember(
                        name=nested_name,
                        type_name='struct',
                        is_array=False,
                        array_size=None,
                        comment=comments.get(current_line),
                        line_number=current_line,
                        nested_struct_members=nested_members
                    ))

                    # Skip the lines we've processed
                    while i < len(lines) and nested_name not in lines[i]:
                        i += 1
                        current_line += 1
                    i += 1
                    current_line += 1
                else:
                    # Regular member
                    if line.endswith(';'):
                        line = line[:-1]
                    comment = comments.get(current_line)
                    member = self.member_parser.parse_member(line, comment, current_line)
                    if member:
                        members.append(member)
                    i += 1
                    current_line += 1

            structs.append(StructDefinition(
                name=struct_name,
                members=members,
                comment=struct_comment,
                line_number=struct_start
            ))

        return structs


class HeaderFileParser:
    """Main class for parsing C header files."""

    def __init__(self):
        self.type_processor = TypeProcessor()
        self.member_parser = StructMemberParser(self.type_processor)
        self.comment_extractor = CommentExtractor()

    def parse_content(self, content: str) -> List[StructDefinition]:
        """Parses header file content and extracts struct definitions."""
        comments = self.comment_extractor.extract_comments(content)

        # Find all top-level struct definitions
        structs = []
        pattern = r'typedef\s+struct\s*{([^}]+)}\s*(\w+);'

        for match in re.finditer(pattern, content, re.DOTALL):
            struct_content = match.group(1)
            struct_name = match.group(2)
            struct_start = content[:match.start()].count('\n') + 1

            # Get struct comment
            struct_comment = comments.get(struct_start - 1)

            members = []
            lines = struct_content.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    continue

                # Check for nested struct
                if line.startswith('struct') and '{' in line:
                    nested_content = '\n'.join(lines[i:])
                    nested_members, nested_name, end_line = self.member_parser.parse_nested_struct(
                        nested_content, struct_start + i, comments
                    )

                    members.append(StructMember(
                        name=nested_name,
                        type_name='struct',
                        is_array=False,
                        array_size=None,
                        comment=comments.get(struct_start + i),
                        line_number=struct_start + i,
                        nested_struct_members=nested_members
                    ))

                    i = end_line
                else:
                    # Regular member
                    comment = comments.get(struct_start + i)
                    member = self.member_parser.parse_member(line, comment, struct_start + i)
                    if member:
                        members.append(member)
                    i += 1

            structs.append(StructDefinition(
                name=struct_name,
                members=members,
                comment=struct_comment,
                line_number=struct_start
            ))

        return structs

    def parse_file(self, file_path: str) -> List[StructDefinition]:
        """Parses a C header file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Header file not found: {file_path}")

        with open(path, 'r') as f:
            content = f.read()

        return self.parse_content(content)


def print_struct_definition(struct: StructDefinition, indent: int = 0):
    """Helper function to print struct definitions nicely."""
    indent_str = "  " * indent
    print(f"{indent_str}Struct {struct.name}:")
    if struct.comment:
        print(f"{indent_str}Documentation: {struct.comment}")

    print(f"{indent_str}Members:")
    for member in struct.members:
        member_type = f"{member.type_name}[{member.array_size}]" if member.is_array else member.type_name
        print(f"{indent_str}  {member_type} {member.name}")
        if member.comment:
            print(f"{indent_str}    Doc: {member.comment}")

        if member.nested_struct_members:
            print(f"{indent_str}    Nested members:")
            for nested_member in member.nested_struct_members:
                member_type = f"{nested_member.type_name}[{nested_member.array_size}]" if nested_member.is_array else nested_member.type_name
                print(f"{indent_str}      {member_type} {nested_member.name}")
                if nested_member.comment:
                    print(f"{indent_str}        Doc: {nested_member.comment}")
