import json
import re
import ast
from pathlib import Path
from typing import Any, Dict, List, Optional
import os

class TemplateLoader:
    """
    Service to load and parse curriculum templates from the filesystem.
    Supports JSON and pseudo-Python/Markdown formats used in templates/new-templates.
    """

    def __init__(self, templates_dir: str = "templates/new-templates"):
        # adjustments for running in backend container vs local
        # Assuming the app runs with CWD as project root or backend/
        # We'll try to find the absolute path relative to project root
        self.base_path = self._find_templates_dir(templates_dir)
        self._cache: Dict[str, Any] = {}

    def _find_templates_dir(self, relative_path: str) -> Path:
        """Locate the templates directory."""
        # Try current working directory
        cwd = Path(os.getcwd())
        candidate = cwd / relative_path
        if candidate.exists():
            return candidate
        
        # Try going up one level (if in backend/)
        candidate = cwd.parent / relative_path
        if candidate.exists():
            return candidate
            
        # Try typical absolute path for this user
        candidate = Path("/Users/kabo/Desktop/projects/youtube-transcript") / relative_path
        if candidate.exists():
            return candidate

        return Path(relative_path) # Fallback

    def list_templates(self) -> List[Dict[str, str]]:
        """List available templates."""
        results = []
        if not self.base_path.exists():
            print(f"Warning: Templates dir not found at {self.base_path}")
            return []

        for f in self.base_path.glob("*"):
            if f.suffix in ['.json', '.md', '.py']:
                # Try to extract a name/title
                name = f.stem.replace("_", " ").title()
                try:
                    # Quick load to get the title - potentially expensive but necessary
                    # Optimization: In real prod, cache this index metadata
                    content = self.get_template(f.stem)
                    if content:
                        extracted = self._extract_name_from_data(content)
                        if extracted:
                            name = extracted
                except Exception:
                    pass

                results.append({
                    "id": f.stem,
                    "filename": f.name,
                    "format": f.suffix,
                    "name": name
                })
        return results

    def get_template(self, template_id: str) -> Optional[Any]:
        """Load a specific template by ID (filename without extension)."""
        if template_id in self._cache:
            return self._cache[template_id]

        file_path = self._find_file(template_id)
        if not file_path:
            return None

        content = self._load_file(file_path)
        if content:
            self._cache[template_id] = content
        
        return content

    def _find_file(self, template_id: str) -> Optional[Path]:
        """Find the file corresponding to the template ID."""
        for ext in ['.json', '.md', '.py']:
            f = self.base_path / f"{template_id}{ext}"
            if f.exists():
                return f
        return None

    def _load_file(self, file_path: Path) -> Any:
        try:
            if file_path.suffix == '.json':
                with open(file_path, 'r') as f:
                    return json.load(f)
            
            elif file_path.suffix == '.md' or file_path.suffix == '.py':
                return self._parse_python_struct_from_text(file_path.read_text())
                
        except Exception as e:
            print(f"Error loading template {file_path}: {e}")
            return None

    def _parse_python_struct_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract Python dictionaries from text. 
        Handles the format seen in gemini.md where dicts are assigned to vars.
        """
        data = {}
        
        # Combined heuristic:
        # Regex to find variable assignments: VAR_NAME = {
        # output a dict of {VAR_NAME: parsed_dict}
        
        assignments = {}
        
        # Pattern for "NAME = {" or "json_structure {" roughly
        variable_pattern = re.compile(r'^([A-Z_][A-Z0-9_]*)\s*=\s*\{|^\s*\{', re.MULTILINE)
        
        for match in variable_pattern.finditer(text):
            var_name = match.group(1) or "ANONYMOUS_BLOCK"
            start_index = match.start()
            
            # Find the assignment part
            assignment_text = text[start_index:]
            # We need to extract just the dict part "{" ... "}"
            # Find the first {
            dict_start = assignment_text.find('{')
            if dict_start == -1: continue
            
            # Balance braces
            open_braces = 0
            dict_end = -1
            in_string = False
            escape = False
            quote_char = None
            
            for i, char in enumerate(assignment_text[dict_start:]):
                # Handle strings to ignore braces inside
                if in_string:
                    if char == '\\':
                        escape = not escape
                    elif char == quote_char and not escape:
                        in_string = False
                    else:
                        escape = False
                    continue
                
                if char in ['"', "'"]:
                     # Note: this is a simple parser, doesn't fully handle triple quotes or comments perfectly
                     # But ast.literal_eval is robust if we isolate the string correctly
                    in_string = True
                    quote_char = char
                    continue 
                    
                if char == '{':
                    open_braces += 1
                elif char == '}':
                    open_braces -= 1
                    if open_braces == 0:
                        dict_end = dict_start + i + 1
                        break
            
            if dict_end != -1:
                dict_str = assignment_text[dict_start:dict_end]
                try:
                    # literal_eval is safe
                    parsed = ast.literal_eval(dict_str)
                    if var_name == "ANONYMOUS_BLOCK":
                        # Generate a unique key for anonymous blocks
                        assignments[f"ANONYMOUS_{start_index}"] = parsed
                    else:
                        assignments[var_name] = parsed
                except Exception as e:
                    # Ignore parsing errors for partial blocks
                    pass
                    
        return assignments

    def find_exercise_by_id(self, exercise_id: str) -> Optional[Dict[str, Any]]:
        """Search for an exercise with the given ID across all templates."""
        templates = self.list_templates()
        for tmpl in templates:
            data = self.get_template(tmpl['id'])
            if not data: continue
            
            # Traverse data (could be dict or dict of dicts)
            found = self._search_recursive(data, "id", exercise_id)
            if found:
                return found
        return None

    def _search_recursive(self, data: Any, key: str, value: str) -> Optional[Dict[str, Any]]:
        if isinstance(data, dict):
            if data.get(key) == value:
                return data
            for k, v in data.items():
                found = self._search_recursive(v, key, value)
                if found: return found
                
        elif isinstance(data, list):
            for item in data:
                found = self._search_recursive(item, key, value)
                if found: return found
                
        return None

    def _extract_name_from_data(self, data: Any) -> Optional[str]:
        """Try to find a name or title in the template data struct"""
        if isinstance(data, dict):
            # Direct keys
            for key in ['title', 'name', 'curriculum_name', 'objective']:
                if key in data and isinstance(data[key], str):
                    return data[key]
            
            # Check for nested structure like {"My Curriculum": {...}}
            if len(data) == 1:
                key = next(iter(data))
                val = data[key]
                if isinstance(val, dict) and ('modules' in val or 'lessons' in val):
                    return key
            
            # Check values if they are dicts
            for k, v in data.items():
                if isinstance(v, dict) and ('modules' in v or 'lessons' in v):
                     # If the value looks like a curriculum, maybe the key is the name
                     if 'title' in v: return v['title']
                     return k
                
        return None

# Global instance
template_loader = TemplateLoader()
