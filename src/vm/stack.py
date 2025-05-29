"""
PyVM栈管理模块
实现虚拟机的执行栈功能
"""

from typing import Any, List
from .instructions import DataType


class VMStack:
    """虚拟机执行栈"""
    
    def __init__(self, max_size: int = 1000):
        self.stack: List[Any] = []
        self.max_size = max_size
    
    def push(self, value: Any) -> None:
        """将值压入栈顶"""
        if len(self.stack) >= self.max_size:
            raise OverflowError("栈溢出")
        self.stack.append(value)
    
    def pop(self) -> Any:
        """弹出栈顶值"""
        if not self.stack:
            raise IndexError("栈为空")
        return self.stack.pop()
    
    def peek(self) -> Any:
        """查看栈顶值但不弹出"""
        if not self.stack:
            raise IndexError("栈为空")
        return self.stack[-1]
    
    def size(self) -> int:
        """获取栈大小"""
        return len(self.stack)
    
    def is_empty(self) -> bool:
        """检查栈是否为空"""
        return len(self.stack) == 0
    
    def clear(self) -> None:
        """清空栈"""
        self.stack.clear()
    
    def duplicate_top(self) -> None:
        """复制栈顶元素"""
        if not self.stack:
            raise IndexError("栈为空")
        self.stack.append(self.stack[-1])
    
    def get_stack_trace(self) -> List[str]:
        """获取栈内容的可读表示"""
        trace = []
        for i, value in enumerate(reversed(self.stack)):
            index = len(self.stack) - 1 - i
            trace.append(f"[{index:2d}] {self._format_value(value)}")
        return trace
    
    def _format_value(self, value: Any) -> str:
        """格式化值的显示"""
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            return repr(value)
    
    def __str__(self) -> str:
        """栈的字符串表示"""
        if not self.stack:
            return "Stack: []"
        
        items = []
        for value in self.stack:
            items.append(self._format_value(value))
        return f"Stack: [{', '.join(items)}]"
    
    def __repr__(self) -> str:
        return f"VMStack(size={len(self.stack)}, max_size={self.max_size})"


class CallFrame:
    """函数调用帧"""
    
    def __init__(self, return_address: int, local_vars: dict = None):
        self.return_address = return_address  # 返回地址
        self.local_vars = local_vars or {}    # 局部变量
    
    def get_var(self, name: str) -> Any:
        """获取局部变量"""
        if name not in self.local_vars:
            raise NameError(f"未定义的变量: {name}")
        return self.local_vars[name]
    
    def set_var(self, name: str, value: Any) -> None:
        """设置局部变量"""
        self.local_vars[name] = value
    
    def has_var(self, name: str) -> bool:
        """检查是否存在局部变量"""
        return name in self.local_vars
    
    def __str__(self) -> str:
        vars_str = ", ".join(f"{k}={v}" for k, v in self.local_vars.items())
        return f"CallFrame(ret={self.return_address}, vars={{{vars_str}}})"


class CallStack:
    """函数调用栈"""
    
    def __init__(self, max_depth: int = 1000):
        self.frames: List[CallFrame] = []
        self.max_depth = max_depth
    
    def push_frame(self, frame: CallFrame) -> None:
        """压入调用帧"""
        if len(self.frames) >= self.max_depth:
            raise RecursionError("调用栈溢出")
        self.frames.append(frame)
    
    def pop_frame(self) -> CallFrame:
        """弹出调用帧"""
        if not self.frames:
            raise IndexError("调用栈为空")
        return self.frames.pop()
    
    def current_frame(self) -> CallFrame:
        """获取当前调用帧"""
        if not self.frames:
            raise IndexError("调用栈为空")
        return self.frames[-1]
    
    def depth(self) -> int:
        """获取调用栈深度"""
        return len(self.frames)
    
    def is_empty(self) -> bool:
        """检查调用栈是否为空"""
        return len(self.frames) == 0
    
    def get_stack_trace(self) -> List[str]:
        """获取调用栈跟踪"""
        trace = []
        for i, frame in enumerate(self.frames):
            trace.append(f"Frame {i}: {frame}")
        return trace
    
    def __str__(self) -> str:
        return f"CallStack(depth={len(self.frames)})"
    
    def __repr__(self) -> str:
        return f"CallStack(depth={len(self.frames)}, max_depth={self.max_depth})"
