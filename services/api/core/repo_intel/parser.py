import ast
import re
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ExtractedSymbol(BaseModel):
    name: str
    symbol_type: str  # 'function', 'class', 'method', 'interface', 'variable'
    start_line: int
    end_line: int
    docstring: Optional[str] = None
    signature: Optional[str] = None


class ExtractedImport(BaseModel):
    source_file: str
    imported_module: str
    imported_symbols: List[str] = []


class PythonASTVisitor(ast.NodeVisitor):
    def __init__(self, code_lines: List[str]):
        self.code_lines = code_lines
        self.symbols: List[ExtractedSymbol] = []
        self.imports: List[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        doc = ast.get_docstring(node)
        start_line = node.lineno
        end_line = getattr(node, 'end_lineno', node.lineno)
        signature = f"class {node.name}"
        if node.bases:
            base_names = [b.id if isinstance(b, ast.Name) else "object" for b in node.bases]
            signature += f"({', '.join(base_names)})"

        self.symbols.append(ExtractedSymbol(
            name=node.name,
            symbol_type="class",
            start_line=start_line,
            end_line=end_line,
            docstring=doc,
            signature=signature
        ))

        # Visit inner methods
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                m_doc = ast.get_docstring(item)
                m_start = item.lineno
                m_end = getattr(item, 'end_lineno', item.lineno)
                args = [a.arg for a in item.args.args]
                m_sig = f"def {item.name}({', '.join(args)})"

                self.symbols.append(ExtractedSymbol(
                    name=f"{node.name}.{item.name}",
                    symbol_type="method",
                    start_line=m_start,
                    end_line=m_end,
                    docstring=m_doc,
                    signature=m_sig
                ))

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Top level function only
        if isinstance(getattr(node, 'parent', None), ast.ClassDef):
            return
        doc = ast.get_docstring(node)
        start_line = node.lineno
        end_line = getattr(node, 'end_lineno', node.lineno)
        args = [a.arg for a in node.args.args]
        signature = f"def {node.name}({', '.join(args)})"

        self.symbols.append(ExtractedSymbol(
            name=node.name,
            symbol_type="function",
            start_line=start_line,
            end_line=end_line,
            docstring=doc,
            signature=signature
        ))
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        doc = ast.get_docstring(node)
        start_line = node.lineno
        end_line = getattr(node, 'end_lineno', node.lineno)
        args = [a.arg for a in node.args.args]
        signature = f"async def {node.name}({', '.join(args)})"

        self.symbols.append(ExtractedSymbol(
            name=node.name,
            symbol_type="function",
            start_line=start_line,
            end_line=end_line,
            docstring=doc,
            signature=signature
        ))
        self.generic_visit(node)


class CodeParser:
    """
    Language-agnostic code parser extracting symbols and import relationships.
    """

    @staticmethod
    def parse_python(code_content: str) -> Dict[str, Any]:
        lines = code_content.splitlines()
        try:
            tree = ast.parse(code_content)
            
            # Attach parent references to distinguish top-level functions from methods
            for parent in ast.walk(tree):
                for child in ast.iter_child_nodes(parent):
                    child.parent = parent

            visitor = PythonASTVisitor(lines)
            visitor.visit(tree)
            return {
                "symbols": visitor.symbols,
                "imports": list(set(visitor.imports))
            }
        except SyntaxError as e:
            logger.warning(f"[CodeParser] Python SyntaxError: {e}")
            return {"symbols": [], "imports": []}

    @staticmethod
    def parse_typescript(code_content: str) -> Dict[str, Any]:
        """
        Regex & tokenizer-based symbol extractor for TS/JS/TSX/JSX files.
        """
        lines = code_content.splitlines()
        symbols: List[ExtractedSymbol] = []
        imports: List[str] = []

        # Extract import modules: import { x } from 'y'; import y from 'y';
        import_regex = re.compile(r"import\s+.*?from\s+['\"](.*?)['\"]")
        for match in import_regex.finditer(code_content):
            imports.append(match.group(1))

        # Extract functions / components: export function Foo(), const Foo = () =>
        func_regex = re.compile(
            r"(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_]+)\s*\((.*?)\)"
        )
        const_func_regex = re.compile(
            r"(?:export\s+)?const\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[A-Za-z0-9_]+)\s*=>"
        )
        class_regex = re.compile(
            r"(?:export\s+)?class\s+([A-Za-z0-9_]+)"
        )
        interface_regex = re.compile(
            r"(?:export\s+)?interface\s+([A-Za-z0-9_]+)"
        )

        for idx, line in enumerate(lines, start=1):
            m_func = func_regex.search(line)
            if m_func:
                name = m_func.group(1)
                symbols.append(ExtractedSymbol(
                    name=name,
                    symbol_type="function",
                    start_line=idx,
                    end_line=idx,
                    signature=line.strip()
                ))
                continue

            m_const = const_func_regex.search(line)
            if m_const:
                name = m_const.group(1)
                symbols.append(ExtractedSymbol(
                    name=name,
                    symbol_type="function",
                    start_line=idx,
                    end_line=idx,
                    signature=line.strip()
                ))
                continue

            m_class = class_regex.search(line)
            if m_class:
                name = m_class.group(1)
                symbols.append(ExtractedSymbol(
                    name=name,
                    symbol_type="class",
                    start_line=idx,
                    end_line=idx,
                    signature=line.strip()
                ))
                continue

            m_iface = interface_regex.search(line)
            if m_iface:
                name = m_iface.group(1)
                symbols.append(ExtractedSymbol(
                    name=name,
                    symbol_type="interface",
                    start_line=idx,
                    end_line=idx,
                    signature=line.strip()
                ))

        return {
            "symbols": symbols,
            "imports": list(set(imports))
        }

    @classmethod
    def parse_file(cls, file_path: str, code_content: str) -> Dict[str, Any]:
        """
        Routes file parsing based on extension.
        """
        if file_path.endswith(".py"):
            return cls.parse_python(code_content)
        elif file_path.endswith((".ts", ".tsx", ".js", ".jsx")):
            return cls.parse_typescript(code_content)
        else:
            return {"symbols": [], "imports": []}
